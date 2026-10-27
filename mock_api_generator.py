import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for realistic data generation
np.random.seed(42)
start_date = datetime(2025, 1, 1)
days = 365

# Generate Mock Ad Platform API Output (Spend & Traffic Logs)
channels = ['Meta Ads', 'Google Ads', 'TikTok Ads', 'Affiliate']
ad_data = []

for day in range(days):
    current_date = start_date + timedelta(days=day)
    for channel in channels:
        # Create realistic variations in daily ad spend
        base_spend = {'Meta Ads': 1200, 'Google Ads': 1000, 'TikTok Ads': 600, 'Affiliate': 200}[channel]
        daily_spend = max(50, int(np.random.normal(base_spend, base_spend * 0.15)))
        
        # Calculate proportional traffic metrics
        cpc = {'Meta Ads': 0.85, 'Google Ads': 1.10, 'TikTok Ads': 0.50, 'Affiliate': 0.30}[channel]
        clicks = int(daily_spend / cpc)
        impressions = clicks * int(np.random.uniform(20, 50))
        
        ad_data.append([current_date.strftime('%Y-%m-%d'), channel, daily_spend, clicks, impressions])

df_ad_spend = pd.DataFrame(ad_data, columns=['date', 'channel', 'spend', 'clicks', 'impressions'])
df_ad_spend.to_csv('api_mock_ad_spend.csv', index=False)

# Generate Mock E-commerce Transaction Logs (Shopify/CRM Output)
customer_ids = [f'CUST-{i:05d}' for i in range(1, 8000)]
order_data = []
order_id_counter = 1001

for day in range(days):
    current_date = start_date + timedelta(days=day)
    # Simulate a realistic number of daily transactions
    daily_order_count = int(np.random.poisson(lam=120)) 
    
    for _ in range(daily_order_count):
        cust_id = np.random.choice(customer_ids)
        channel = np.random.choice(channels, p=[0.4, 0.35, 0.2, 0.05]) # Channel distribution
        order_value = round(max(15.0, np.random.normal(250.0, 30.0)), 2) # Aura Ring Mini price point ($250)
        
        # Determine if customer is returning or a new acquisition
        is_first_purchase = 1 if np.random.rand() > 0.4 else 0 
        
        order_data.append([f'ORD-{order_id_counter}', cust_id, current_date.strftime('%Y-%m-%d'), channel, order_value, is_first_purchase])
        order_id_counter += 1

df_orders = pd.DataFrame(order_data, columns=['order_id', 'customer_id', 'order_date', 'acquisition_channel', 'order_value', 'is_first_purchase'])
df_orders.to_csv('api_mock_shopify_orders.csv', index=False)

print("Mock API Datasets successfully generated: 'api_mock_ad_spend.csv' and 'api_mock_shopify_orders.csv'")
