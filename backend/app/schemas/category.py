from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base schema
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

# Schema for creating
class CategoryCreate(CategoryBase):
    pass

# Schema for updating
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Schema for response
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True