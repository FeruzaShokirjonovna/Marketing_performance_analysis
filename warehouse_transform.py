import duckdb

# Connect to a local data warehouse file
conn = duckdb.connect('aura_ring_warehouse.db')

print("Creating staging tables from raw API outputs...")
