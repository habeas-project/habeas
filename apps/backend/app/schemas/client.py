from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Shared properties
class ClientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Client's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Client's last name")
    country_of_birth: str = Field(..., min_length=1, max_length=100, description="Client's country of birth")
    nationality: Optional[str] = Field(None, max_length=100, description="Client's nationality")
    birth_date: date = Field(..., description="Client's birth date")
    alien_registration_number: Optional[str] = Field(None, max_length=20, description="Client's A-Number")
    passport_number: Optional[str] = Field(None, max_length=20, description="Client's passport number")
    school_name: Optional[str] = Field(None, max_length=255, description="Client's school name")
    student_id_number: Optional[str] = Field(None, max_length=50, description="Client's student ID number")


# Properties to receive via API on creation
class ClientCreate(ClientBase):
    pass  # All required fields are in ClientBase for this model


# Properties to receive via API on update, all optional
class ClientUpdate(ClientBase):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's last name")
    country_of_birth: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's country of birth")
    birth_date: Optional[date] = Field(None, description="Client's birth date")
    # Optional fields remain optional


# Properties to return via API, includes read-only fields like id and timestamps
class ClientResponse(ClientBase):
    id: int = Field(..., description="Unique identifier for the client")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated")

    model_config = ConfigDict(from_attributes=True)
