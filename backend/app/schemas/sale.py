from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Schema for creating a sale
class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)  # Must be greater than 0
    unit_price: Optional[float] = None  # Kung None, gamitin ang product price
    notes: Optional[str] = None

# Schema for response
class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    sale_date: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema for sales report
class SalesReport(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_revenue: float
    total_transactions: int