from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.emergency_contact import EmergencyContactResponse


class ClientProfileBase(BaseModel):
    """Base schema for client profile with common fields"""

    profile_name: str = Field(
        ..., min_length=1, max_length=255, description="Display name for profile (e.g., 'John Doe', 'My Son')"
    )
    is_self: bool = Field(default=False, description="True if this profile represents the account holder")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    country_of_birth: str = Field(..., min_length=1, max_length=100, description="Country of birth")
    nationality: Optional[str] = Field(None, max_length=100, description="Nationality")
    birth_date: date = Field(..., description="Date of birth")
    alien_registration_number: Optional[str] = Field(
        None, max_length=20, description="Alien registration number (A-Number)"
    )
    passport_number: Optional[str] = Field(None, max_length=20, description="Passport number")
    school_name: Optional[str] = Field(None, max_length=255, description="School name")
    student_id_number: Optional[str] = Field(None, max_length=50, description="Student ID number")


class ClientProfileCreate(ClientProfileBase):
    """Schema for creating a new client profile"""

    user_id: int = Field(..., description="ID of the user this profile belongs to")


class ClientProfileUpdate(BaseModel):
    """Schema for updating an existing client profile"""

    profile_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_self: Optional[bool] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    country_of_birth: Optional[str] = Field(None, min_length=1, max_length=100)
    nationality: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    alien_registration_number: Optional[str] = Field(None, max_length=20)
    passport_number: Optional[str] = Field(None, max_length=20)
    school_name: Optional[str] = Field(None, max_length=255)
    student_id_number: Optional[str] = Field(None, max_length=50)


class ClientProfileResponse(ClientProfileBase):
    """Schema for client profile response with metadata"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    emergency_contacts: list[EmergencyContactResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ClientProfileListResponse(BaseModel):
    """Schema for listing client profiles with pagination"""

    profiles: list[ClientProfileResponse]
    total: int
    page: int = 1
    page_size: int = 50

    model_config = ConfigDict(from_attributes=True)


class ClientProfileList(BaseModel):
    """Schema for client profile in list responses"""

    id: int
    profile_name: str
    is_self: bool
    first_name: str
    last_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
