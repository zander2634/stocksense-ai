from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.product import Product
from app.models.sale import Sale
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# ============================================
# DASHBOARD SUMMARY
# ============================================

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall business summary para sa dashboard"""
    
    # Total counts
    total_products = db.query(func.count(Product.id)).scalar() or 0
    total_categories = db.query(func.count(Category.id)).scalar() or 0
    total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
    
    # Total inventory value
    total_inventory_value = db.query(
        func.sum(Product.stock_quantity * Product.cost)
    ).scalar() or 0.0
    
    # Total stock quantity
    total_stock = db.query(func.sum(Product.stock_quantity)).scalar() or 0
    
    # Low stock count (below reorder level)
    low_stock_count = db.query(func.count(Product.id)).filter(
        Product.stock_quantity <= Product.reorder_level
    ).scalar() or 0
    
    # Sales stats (last 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    sales_count = db.query(func.count(Sale.id)).filter(
        Sale.sale_date >= cutoff
    ).scalar() or 0
    sales_revenue = db.query(func.sum(Sale.total_price)).filter(
        Sale.sale_date >= cutoff
    ).scalar() or 0.0
    
    # Today's sales
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sales = db.query(func.sum(Sale.total_price)).filter(
        Sale.sale_date >= today_start
    ).scalar() or 0.0
    today_transactions = db.query(func.count(Sale.id)).filter(
        Sale.sale_date >= today_start
    ).scalar() or 0
    
    # Inventory Health Score (0-100)
    if total_products > 0:
        healthy_products = total_products - low_stock_count
        health_score = round((healthy_products / total_products) * 100, 1)
    else:
        health_score = 0.0
    
    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_suppliers": total_suppliers,
        "total_stock_quantity": int(total_stock),
        "total_inventory_value": round(float(total_inventory_value), 2),
        "low_stock_count": low_stock_count,
        "inventory_health_score": health_score,
        "sales_last_30_days": {
            "transactions": sales_count,
            "revenue": round(float(sales_revenue), 2)
        },
        "today": {
            "transactions": today_transactions,
            "revenue": round(float(today_sales), 2)
        }
    }

# ============================================
# TOP SELLING PRODUCTS
# ============================================

@router.get("/top-products")
def get_top_products(
    limit: int = 5,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top selling products"""
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        Product.id,
        Product.name,
        Product.sku,
        func.sum(Sale.quantity).label("total_sold"),
        func.sum(Sale.total_price).label("total_revenue")
    ).join(Sale, Sale.product_id == Product.id).filter(
        Sale.sale_date >= cutoff
    ).group_by(Product.id, Product.name, Product.sku).order_by(
        func.sum(Sale.quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "product_id": r.id,
            "name": r.name,
            "sku": r.sku,
            "total_sold": int(r.total_sold),
            "total_revenue": round(float(r.total_revenue), 2)
        }
        for r in results
    ]

# ============================================
# LOW STOCK PRODUCTS
# ============================================

@router.get("/low-stock")
def get_low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get products na mababa ang stock"""
    
    products = db.query(Product).filter(
        Product.stock_quantity <= Product.reorder_level
    ).order_by(Product.stock_quantity).all()
    
    return [
        {
            "product_id": p.id,
            "name": p.name,
            "sku": p.sku,
            "stock_quantity": p.stock_quantity,
            "reorder_level": p.reorder_level,
            "status": "critical" if p.stock_quantity <= 0 else "low"
        }
        for p in products
    ]