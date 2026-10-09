"""
Reset sales data at mag-import ng synthetic data mula sa CSV.
Ito ang tama na paraan para magkaroon ng 90 days ng historical data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from datetime import datetime
from app.database import SessionLocal
from app.models.user import User          # ← IDAGDAG
from app.models.category import Category  # ← IDAGDAG
from app.models.supplier import Supplier  # ← IDAGDAG
from app.models.product import Product
from app.models.sale import Sale

def reset_and_seed():
    db = SessionLocal()
    
    try:
        # 1. Delete all existing sales
        count = db.query(Sale).count()
        db.query(Sale).delete()
        db.commit()
        print(f"🗑️  Deleted {count} existing sales records")
        
        # 2. Get all products
        products = db.query(Product).all()
        product_map = {p.id: p for p in products}
        print(f"📦 Found {len(products)} products: {sorted(product_map.keys())}")
        
        # 3. Load CSV
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "ml", "data", "sales_data.csv"
        )
        
        if not os.path.exists(csv_path):
            print(f"❌ CSV not found at {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        print(f"📂 Loaded {len(df)} records from CSV")
        
        # 4. Import sales
        imported = 0
        skipped = 0
        for _, row in df.iterrows():
            product_id = int(row['product_id'])
            
            if product_id not in product_map:
                skipped += 1
                continue
            
            product = product_map[product_id]
            quantity = int(row['quantity_sold'])
            unit_price = product.price
            total_price = unit_price * quantity
            sale_date = datetime.strptime(row['date'], "%Y-%m-%d")
            
            sale = Sale(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                sale_date=sale_date,
                notes="Synthetic data"
            )
            db.add(sale)
            imported += 1
        
        db.commit()
        print(f"✅ Imported {imported} sales records (skipped {skipped})")
        
        # 5. Update product stock
        for product in products:
            product.stock_quantity = product.reorder_level * 10
        db.commit()
        print(f"📊 Updated stock levels for all products")
        
        # 6. Summary
        total = db.query(Sale).count()
        print(f"\n📈 Total sales: {total}")
        
        print("\n✅ DONE! Restart the backend and refresh Forecast page.")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()