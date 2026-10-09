from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.forecast import ForecastResponse, ReorderRecommendation
from app.services.auth_service import get_current_user
from app.services.forecast_service import forecast_product, get_reorder_recommendation

router = APIRouter(prefix="/api/forecast", tags=["AI Forecasting"])

# ============================================
# FORECAST ONE PRODUCT
# ============================================

@router.get("/{product_id}", response_model=ForecastResponse)
def get_product_forecast(
    product_id: int,
    days: int = Query(7, ge=1, le=30, description="Number of days to forecast (1-30)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI demand forecast for a product"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        forecast = forecast_product(db, product_id, days_ahead=days)
        return forecast
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

# ============================================
# REORDER RECOMMENDATION
# ============================================

@router.get("/{product_id}/reorder", response_model=ReorderRecommendation)
def get_product_reorder(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get smart reorder recommendation for a product"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        recommendation = get_reorder_recommendation(db, product)
        return recommendation
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

# ============================================
# FORECAST ALL PRODUCTS (Dashboard)
# ============================================

@router.get("/", response_model=List[ForecastResponse])
def get_all_forecasts(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get forecasts for all products"""
    
    products = db.query(Product).all()
    
    forecasts = []
    for product in products:
        try:
            forecast = forecast_product(db, product.id, days_ahead=days)
            forecasts.append(forecast)
        except Exception:
            continue
    
    return forecasts