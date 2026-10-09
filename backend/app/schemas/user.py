from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "Inventory Manager"

# Schema for registration
class UserCreate(UserBase):
    password: str

# Schema for login
class UserLogin(BaseModel):
    username: str
    password: str

# Schema for response (walang password)
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for JWT token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Schema for token data
class TokenData(BaseModel):
    username: Optional[str] = None