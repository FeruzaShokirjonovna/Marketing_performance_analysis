import duckdb

# Connect to a local data warehouse file
conn = duckdb.connect('aura_ring_warehouse.db')

print("Creating staging tables from raw API outputs...")

# Ingest CSV files directly into relation tables
conn.execute("""
    CREATE OR REPLACE TABLE stg_meta_spend AS 
    SELECT * FROM read_csv_auto('api_mock_ad_spend.csv');
""")

conn.execute("""
    CREATE OR REPLACE TABLE stg_shopify_orders AS 
    SELECT * FROM read_csv_auto('api_mock_shopify_orders.csv');
""")

print("Architecting fct_marketing_performance core star schema table...")

# Execute SQL Metrics Transformation
transformation_sql = """
CREATE OR REPLACE TABLE fct_marketing_performance AS
WITH daily_spend_summary AS (
    SELECT 
        CAST(date AS DATE) AS event_date,
        channel,
        SUM(spend) AS total_ad_spend,
        SUM(clicks) AS total_clicks,
        SUM(impressions) AS total_impressions
    FROM stg_meta_spend
    GROUP BY 1, 2
),
daily_order_summary AS (
    SELECT 
        CAST(order_date AS DATE) AS event_date,
        acquisition_channel AS channel,
        SUM(order_value) AS gross_revenue,
        COUNT(DISTINCT order_id) AS total_order_volume,
        COUNT(DISTINCT CASE WHEN is_first_purchase = 1 THEN customer_id END) AS new_customers_acquired
    FROM stg_shopify_orders
    GROUP BY 1, 2
),

cohort_lifespan_base AS (
    -- Advanced window functions to determine Customer Lifetime Revenue per channel
    SELECT 
        acquisition_channel AS channel,
        SUM(order_value) / COUNT(DISTINCT customer_id) AS historical_clv
    FROM stg_shopify_orders
    GROUP BY 1
    SELECT 
    s.event_date,
    s.channel,
    s.total_ad_spend,
    s.total_clicks,
    s.total_impressions,
    COALESCE(o.gross_revenue, 0) AS gross_revenue,
    COALESCE(o.total_order_volume, 0) AS total_order_volume,
    COALESCE(o.new_customers_acquired, 0) AS new_customers_acquired,
    
    -- Calculated Enterprise Performance Metrics
    CASE WHEN COALESCE(o.new_customers_acquired, 0) > 0 THEN s.total_ad_spend / o.new_customers_acquired ELSE 0 END AS cac,
    CASE WHEN s.total_ad_spend > 0 THEN o.gross_revenue / s.total_ad_spend ELSE 0 END AS roas,
    c.historical_clv,
    CASE WHEN (s.total_ad_spend / NULLIF(o.new_customers_acquired, 0)) > 0 THEN c.historical_clv / (s.total_ad_spend / o.new_customers_acquired) ELSE 0 END AS clv_to_cac_ratio
FROM daily_spend_summary s
LEFT JOIN daily_order_summary o ON s.event_date = o.event_date AND s.channel = o.channel
LEFT JOIN cohort_lifespan_base c ON s.channel = c.channel;
"""

conn.execute(transformation_sql)