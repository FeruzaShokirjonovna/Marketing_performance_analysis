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