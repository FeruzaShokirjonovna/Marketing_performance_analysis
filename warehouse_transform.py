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
