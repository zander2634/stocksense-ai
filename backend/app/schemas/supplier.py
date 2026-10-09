from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base schema
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: int = Field(7, ge=0)

# Schema for creating
class SupplierCreate(SupplierBase):
    pass

# Schema for updating
class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: Optional[int] = Field(None, ge=0)

# Schema for response
class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True