from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse, SalesReport
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/sales", tags=["Sales"])

# ============================================
# CREATE SALE (with auto stock deduction)
# ============================================

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a new sale and automatically deduct stock"""
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == sale_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if enough stock
    if product.stock_quantity < sale_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {sale_data.quantity}"
        )
    
    # Determine unit price (use product price kung walang binigay)
    unit_price = sale_data.unit_price if sale_data.unit_price is not None else product.price
    total_price = unit_price * sale_data.quantity
    
    # Create sale record
    new_sale = Sale(
        product_id=sale_data.product_id,
        quantity=sale_data.quantity,
        unit_price=unit_price,
        total_price=total_price,
        notes=sale_data.notes
    )
    
    # Deduct stock from product
    product.stock_quantity -= sale_data.quantity
    
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    
    return new_sale

# ============================================
# GET ALL SALES
# ============================================

@router.get("/", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    product_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all sales (with optional product filter)"""
    query = db.query(Sale)
    
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    
    sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    return sales

# ============================================
# GET ONE SALE
# ============================================

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single sale by ID"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    return sale

# ============================================
# SALES REPORT (aggregated by product)
# ============================================

@router.get("/reports/summary", response_model=List[SalesReport])
def get_sales_report(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sales report for the last N days (default: 30)"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        Sale.product_id,
        Product.name.label("product_name"),
        func.sum(Sale.quantity).label("total_quantity_sold"),
        func.sum(Sale.total_price).label("total_revenue"),
        func.count(Sale.id).label("total_transactions")
    ).join(
        Product, Sale.product_id == Product.id
    ).filter(
        Sale.sale_date >= cutoff_date
    ).group_by(
        Sale.product_id, Product.name
    ).all()
    
    return [
        SalesReport(
            product_id=r.product_id,
            product_name=r.product_name,
            total_quantity_sold=int(r.total_quantity_sold),
            total_revenue=float(r.total_revenue),
            total_transactions=int(r.total_transactions)
        )
        for r in results
    ]
    # ============================================
# DELETE SALE
# ============================================

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sale (at ibalik ang stock sa product)"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    
    # Ibalik ang stock sa product
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    if product:
        product.stock_quantity += sale.quantity
    
    db.delete(sale)
    db.commit()
    
    return None