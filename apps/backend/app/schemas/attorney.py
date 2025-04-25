import re

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from .court import Court  # Import Court schema for relationship

# Configure PhoneNumber format globally
PhoneNumber.phone_format = "E164"  #'INTERNATIONAL', 'NATIONAL'


class AttorneyBase(BaseModel):
    """Base schema for Attorney data"""

    name: str = Field(min_length=1, max_length=255, examples=["Jane Doe"])
    phone_number: str = Field(examples=["+15551234567"])
    email: EmailStr = Field(examples=["jane.doe@example.com"])
    zip_code: str = Field(min_length=5, max_length=10, examples=["12345", "12345-6789"])
    state: str = Field(min_length=2, max_length=2, examples=["CA"])

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: PhoneNumber) -> PhoneNumber:
        """Validate phone number format: must be in E164 format (+1 followed by 10 digits)"""
        phone_str = str(v)
        if not re.match(r"^\+1\d{10}$", phone_str):
            raise ValueError("Phone number must be in E164 format: +1 followed by 10 digits (e.g., +15551234567)")
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_us_zip_code(cls, v: str) -> str:
        """Validate US ZIP code format: either 5 digits or 5+4 digits with a hyphen"""
        if not re.match(r"^\d{5}(-\d{4})?$", v):
            raise ValueError("US ZIP code must be 5 digits or 5+4 digits (e.g., 12345 or 12345-6789)")
        return v

    @field_validator("state")
    @classmethod
    def validate_us_state(cls, v: str) -> str:
        """Validate US state code format: two uppercase letters"""
        if not re.match(r"^[A-Z]{2}$", v):
            raise ValueError("State must be a two-letter code (e.g., CA, NY)")
        return v


class AttorneyCreate(AttorneyBase):
    """Schema for creating a new Attorney"""

    pass


class AttorneyUpdate(BaseModel):
    """Schema for updating an Attorney"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None
    zip_code: Optional[str] = Field(None, min_length=5, max_length=10)
    state: Optional[str] = Field(None, min_length=2, max_length=2)

    # Validator for optional phone number
    @field_validator("phone_number")
    @classmethod
    def validate_optional_phone_number(cls, v: Optional[PhoneNumber]) -> Optional[PhoneNumber]:
        if v is None:
            return v
        phone_str = str(v)
        if not re.match(r"^\+1\d{10}$", phone_str):
            raise ValueError("Phone number must be in E164 format: +1 followed by 10 digits (e.g., +15551234567)")
        return v

    # Validator for optional ZIP code
    @field_validator("zip_code")
    @classmethod
    def validate_optional_us_zip_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^\d{5}(-\d{4})?$", v):
            raise ValueError("US ZIP code must be 5 digits or 5+4 digits (e.g., 12345 or 12345-6789)")
        return v

    # Validator for optional state
    @field_validator("state")
    @classmethod
    def validate_optional_us_state(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^[A-Z]{2}$", v):
            raise ValueError("State must be a two-letter code (e.g., CA, NY)")
        return v


class Attorney(AttorneyBase):
    """Schema for an Attorney with ID and timestamps"""

    id: int
    created_at: datetime
    updated_at: datetime
    # Add the relationship to courts
    admitted_courts: List[Court] = []

    model_config = {"from_attributes": True}
