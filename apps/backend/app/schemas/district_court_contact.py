import datetime

from typing import Optional

from pydantic import BaseModel, EmailStr


# Base schema for DistrictCourtContact - common fields
class DistrictCourtContactBase(BaseModel):
    location_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    hours: Optional[str] = None
    court_id: int


# Schema for creating a DistrictCourtContact - inherits from Base
# All fields are required for creation unless they have a default or are auto-generated
class DistrictCourtContactCreate(DistrictCourtContactBase):
    pass  # For now, all fields from base are needed for creation, or are optional in base


# Schema for updating a DistrictCourtContact - inherits from Base, all fields optional
class DistrictCourtContactUpdate(BaseModel):
    location_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    hours: Optional[str] = None
    court_id: Optional[int] = None  # Allow updating court_id if necessary, though usually stable


# Schema for reading/returning a DistrictCourtContact - includes fields from DB model
class DistrictCourtContactResponse(DistrictCourtContactBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True  # For Pydantic V1, use from_attributes = True for V2
        # For Pydantic V2, replace orm_mode with from_attributes = True
        # Remove this comment after checking Pydantic version in pyproject.toml if needed.
