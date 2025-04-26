from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from pydantic_extra_types.phone_numbers import PhoneNumber


class EmergencyContactBase(BaseModel):
    """
    Base schema for emergency contact with common fields
    """

    full_name: str = Field(..., min_length=1, max_length=255, description="Full name of the emergency contact")
    relationship: str = Field(..., min_length=1, max_length=50, description="Relationship to the client")
    phone_number: str = Field(..., description="Phone number of the emergency contact")
    email: Optional[EmailStr] = Field(None, description="Email address of the emergency contact")
    address: Optional[str] = Field(None, max_length=255, description="Physical address of the emergency contact")
    notes: Optional[str] = Field(None, description="Additional notes about the emergency contact")

    @computed_field(repr=False)  # type: ignore[misc]
    @property
    def formatted_phone(self) -> str:
        """Returns the phone number in E.164 format"""
        return str(self.phone_number)

    @computed_field(repr=False)  # type: ignore[misc]
    @property
    def display_name(self) -> str:
        """Returns a display-friendly name with relationship"""
        return f"{self.full_name} ({self.relationship})"


class EmergencyContactCreate(EmergencyContactBase):
    """
    Schema for creating a new emergency contact
    """

    client_id: int = Field(..., description="ID of the associated client")


class EmergencyContactUpdate(EmergencyContactBase):
    """
    Schema for updating an existing emergency contact
    All fields are optional to allow partial updates
    """

    full_name: Optional[str] = None
    relationship: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class EmergencyContactResponse(EmergencyContactBase):
    """
    Schema for emergency contact response
    Includes read-only fields like id and timestamps
    """

    id: int = Field(..., description="Unique identifier for the emergency contact")
    client_id: int = Field(..., description="ID of the associated client")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated")

    model_config = ConfigDict(from_attributes=True)
