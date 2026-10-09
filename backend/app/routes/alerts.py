from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.forecast_service import forecast_product

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

# ============================================
# GET ALL ALERTS
# ============================================

@router.get("/")
def get_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active alerts (low stock, overstock, slow-moving)"""
    
    alerts = []
    
    products = db.query(Product).all()
    
    for product in products:
        # Low stock alert
        if product.stock_quantity <= 0:
            alerts.append({
                "type": "out_of_stock",
                "severity": "critical",
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "message": f"{product.name} is OUT OF STOCK!",
                "current_stock": product.stock_quantity,
                "reorder_level": product.reorder_level
            })
        elif product.stock_quantity <= product.reorder_level:
            alerts.append({
                "type": "low_stock",
                "severity": "high",
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "message": f"{product.name} is running low ({product.stock_quantity} left, reorder at {product.reorder_level})",
                "current_stock": product.stock_quantity,
                "reorder_level": product.reorder_level
            })
        
        # Overstock alert (stock > 3x reorder level)
        if product.stock_quantity > product.reorder_level * 3 and product.reorder_level > 0:
            alerts.append({
                "type": "overstock",
                "severity": "medium",
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "message": f"{product.name} is overstocked ({product.stock_quantity} units)",
                "current_stock": product.stock_quantity,
                "reorder_level": product.reorder_level
            })
    
    # Slow-moving products (walang sale sa last 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    for product in products:
        recent_sales = db.query(Sale).filter(
            Sale.product_id == product.id,
            Sale.sale_date >= cutoff
        ).count()
        
        if recent_sales == 0 and product.stock_quantity > 0:
            alerts.append({
                "type": "slow_moving",
                "severity": "low",
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "message": f"{product.name} has no sales in the last 30 days",
                "current_stock": product.stock_quantity,
                "days_without_sales": 30
            })
    
    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }

# ============================================
# LOW STOCK ALERTS
# ============================================

@router.get("/low-stock")
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get low stock alerts only"""
    
    products = db.query(Product).filter(
        Product.stock_quantity <= Product.reorder_level
    ).order_by(Product.stock_quantity).all()
    
    return {
        "total": len(products),
        "alerts": [
            {
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "current_stock": p.stock_quantity,
                "reorder_level": p.reorder_level,
                "severity": "critical" if p.stock_quantity <= 0 else "high"
            }
            for p in products
        ]
    }