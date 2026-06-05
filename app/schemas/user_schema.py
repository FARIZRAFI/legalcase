from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique login identifier name")
    email: EmailStr = Field(..., description="Primary electronic mailing address")
    full_name: str = Field(..., min_length=1, max_length=100, description="The true first and last name of the individual")
    phone_number: Optional[str] = Field(None, description="The phone number formatted internationally for WhatsApp communications (e.g., +1234567890)")
    role: str = Field(default="Client", description="System access tier permissions (e.g., Lawyer, Client, Admin)")
    is_active: bool = Field(default=True, description="Toggle indicating whether account has login capabilities")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Raw plaintext password to be securely hashed via the Auth service")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True