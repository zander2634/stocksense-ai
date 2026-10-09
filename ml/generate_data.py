"""
Generate synthetic sales data for training the XGBoost model.
Ito ay para sa demonstration - sa production, gagamitin natin ang actual sales data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_sales_data(product_id: int, days: int = 90, base_demand: int = 10):
    """Generate synthetic sales data for a product"""
    
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    
    # Base demand + weekly seasonality + trend + noise
    data = []
    for i, date in enumerate(dates):
        # Weekly seasonality (mas mataas ang sales sa weekends)
        day_of_week = date.weekday()
        weekly_factor = 1.3 if day_of_week >= 5 else 1.0
        
        # Monthly seasonality (slight increase sa dulo ng month)
        day_of_month = date.day
        monthly_factor = 1.15 if day_of_month >= 25 else 1.0
        
        # Trend (slight growth over time)
        trend = 1 + (i / days) * 0.1
        
        # Random noise
        noise = np.random.uniform(0.8, 1.2)
        
        # Compute demand
        demand = int(base_demand * weekly_factor * monthly_factor * trend * noise)
        demand = max(1, demand)  # At least 1
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "product_id": product_id,
            "quantity_sold": demand,
            "day_of_week": day_of_week,
            "day_of_month": day_of_month,
            "month": date.month
        })
    
    return data

def generate_all_products_data():
    """Generate sales data para sa 5 products"""
    
    all_data = []
    
    # Products with different demand patterns
    products = [
        {"id": 1, "base_demand": 3},   # Laptop (mababa demand, mataas price)
        {"id": 2, "base_demand": 20},  # Coca-Cola (mataas demand)
        {"id": 3, "base_demand": 8},   # T-Shirt (medium demand)
        {"id": 4, "base_demand": 5},   # Watering Can (medium-low)
        {"id": 5, "base_demand": 2},   # iPhone (mababa demand, mataas price)
    ]
    
    for product in products:
        data = generate_sales_data(
            product_id=product["id"],
            days=90,
            base_demand=product["base_demand"]
        )
        all_data.extend(data)
    
    return pd.DataFrame(all_data)

if __name__ == "__main__":
    print("Generating synthetic sales data...")
    
    df = generate_all_products_data()
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), "data", "sales_data.csv")
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {len(df)} records")
    print(f"✅ Saved to: {output_path}")
    print(f"\nFirst 5 rows:")
    print(df.head())