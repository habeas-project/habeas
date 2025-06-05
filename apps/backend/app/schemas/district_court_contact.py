"""Pydantic schemas for DistrictCourtContact."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class DistrictCourtContactBase(BaseModel):
    """Base schema for district court contact information."""

    location_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    hours: Optional[str] = None


class DistrictCourtContactCreate(DistrictCourtContactBase):
    """Schema for creating a new district court contact."""

    court_id: int


class DistrictCourtContactUpdate(DistrictCourtContactBase):
    """Schema for updating an existing district court contact. All fields are optional."""

    court_id: Optional[int] = None


class DistrictCourtContactResponse(DistrictCourtContactBase):
    """Schema for returning district court contact information in API responses."""

    id: int
    court_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
