import datetime

from typing import Optional

from pydantic import BaseModel


# Base schema for IceDetentionFacility - common fields
class IceDetentionFacilityBase(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None  # Simplified to Optional[str], DB enforces length
    zip_code: Optional[str] = None
    aor: Optional[str] = None
    facility_type_detailed: Optional[str] = None
    gender_capacity: Optional[str] = None


# Schema for creating an IceDetentionFacility
class IceDetentionFacilityCreate(IceDetentionFacilityBase):
    pass


# Schema for updating an IceDetentionFacility - all fields optional
class IceDetentionFacilityUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None  # Simplified
    zip_code: Optional[str] = None
    aor: Optional[str] = None
    facility_type_detailed: Optional[str] = None
    gender_capacity: Optional[str] = None


# Schema for reading/returning an IceDetentionFacility - includes ID and timestamps
class IceDetentionFacilityResponse(IceDetentionFacilityBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True  # For Pydantic V1, use from_attributes = True for V2
