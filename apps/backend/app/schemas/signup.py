from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.admin import AdminBase
from app.schemas.attorney import AttorneyBase
from app.schemas.client import ClientBase
from app.schemas.user import UserResponse


class AttorneySignupRequest(AttorneyBase):
    """Schema for attorney signup request - combines attorney data with password"""

    password: str = Field(
        ..., min_length=8, description="Password for the attorney account", examples=["SecurePassword123!"]
    )

    # Override to add password-specific validation if needed
    # The attorney fields (name, phone_number, email, zip_code, state) are inherited from AttorneyBase


class AttorneySignupResponse(BaseModel):
    """Schema for attorney signup response - returns both user and attorney info"""

    # User information
    user: UserResponse

    # Attorney information (without sensitive data)
    attorney: "AttorneyInfo"

    # Authentication token (for mock/test scenarios)
    access_token: Optional[str] = Field(None, description="Access token (mock auth only)")
    token_type: Optional[str] = Field(None, description="Token type (mock auth only)")

    model_config = ConfigDict(from_attributes=True)


class AttorneyInfo(BaseModel):
    """Schema for attorney information in signup response"""

    id: int
    name: str
    phone_number: str
    email: EmailStr
    zip_code: str
    state: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientSignupRequest(ClientBase):
    """Schema for client signup request - combines client data with password"""

    password: str = Field(
        ..., min_length=8, description="Password for the client account", examples=["SecurePassword123!"]
    )

    # The client fields (first_name, last_name, country_of_birth, birth_date, etc.) are inherited from ClientBase


class ClientSignupResponse(BaseModel):
    """Schema for client signup response - returns both user and client info"""

    # User information
    user: UserResponse

    # Client information (without sensitive data)
    client: "ClientInfo"

    # Authentication token (for mock/test scenarios)
    access_token: Optional[str] = Field(None, description="Access token (mock auth only)")
    token_type: Optional[str] = Field(None, description="Token type (mock auth only)")

    model_config = ConfigDict(from_attributes=True)


class ClientInfo(BaseModel):
    """Schema for client information in signup response"""

    id: int
    first_name: str
    last_name: str
    country_of_birth: str
    nationality: Optional[str]
    birth_date: date
    alien_registration_number: Optional[str]
    passport_number: Optional[str]
    school_name: Optional[str]
    student_id_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminSignupRequest(AdminBase):
    """Schema for admin signup request - combines admin data with password"""

    password: str = Field(
        ..., min_length=8, description="Password for the admin account", examples=["SecurePassword123!"]
    )

    # The admin fields (name, email, department, role) are inherited from AdminBase


class AdminSignupResponse(BaseModel):
    """Schema for admin signup response - returns both user and admin info"""

    # User information
    user: UserResponse

    # Admin information (without sensitive data)
    admin: "AdminInfo"

    # Authentication token (for mock/test scenarios)
    access_token: Optional[str] = Field(None, description="Access token (mock auth only)")
    token_type: Optional[str] = Field(None, description="Token type (mock auth only)")

    model_config = ConfigDict(from_attributes=True)


class AdminInfo(BaseModel):
    """Schema for admin information in signup response"""

    id: int
    name: str
    email: EmailStr
    department: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Update forward references
AttorneySignupResponse.model_rebuild()
ClientSignupResponse.model_rebuild()
AdminSignupResponse.model_rebuild()
