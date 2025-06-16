from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminBase(BaseModel):
    """Base schema for admin data"""

    name: str = Field(..., min_length=1, max_length=255, description="Full name of the admin")
    email: EmailStr = Field(..., description="Email address of the admin")
    department: Optional[str] = Field(None, max_length=100, description="Department or division")
    role: str = Field("admin", max_length=50, description="Admin role or permission level")


class AdminCreate(AdminBase):
    """Schema for creating a new admin"""

    pass


class AdminUpdate(BaseModel):
    """Schema for updating admin data"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name of the admin")
    email: Optional[EmailStr] = Field(None, description="Email address of the admin")
    department: Optional[str] = Field(None, max_length=100, description="Department or division")
    role: Optional[str] = Field(None, max_length=50, description="Admin role or permission level")


class AdminResponse(AdminBase):
    """Schema for admin data in responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
