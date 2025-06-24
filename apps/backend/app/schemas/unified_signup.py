from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.admin import AdminBase
from app.schemas.attorney import AttorneyBase
from app.schemas.client_profile import ClientProfileBase
from app.schemas.user import UserResponse


class UnifiedSignupRequest(BaseModel):
    """Base signup request with email, password, and role selection"""

    email: EmailStr = Field(..., description="Email address for the account")
    password: str = Field(..., min_length=8, description="Password for the account")
    primary_role: str = Field(..., description="Primary role: attorney, client_helper, or admin")


class RoleSpecificData(BaseModel):
    """Container for role-specific data - only one should be provided based on primary_role"""

    attorney_data: Optional[AttorneyBase] = Field(None, description="Attorney-specific information")
    client_profile_data: Optional[ClientProfileBase] = Field(None, description="Client profile information")
    admin_data: Optional[AdminBase] = Field(None, description="Admin-specific information")


class UnifiedSignupResponse(BaseModel):
    """Response from unified signup containing user info and role-specific data"""

    user: UserResponse

    # Role-specific response data (one will be populated based on role)
    attorney: Optional[dict] = Field(None, description="Attorney information if role is attorney")
    client_profile: Optional[dict] = Field(None, description="Client profile information if role is client_helper")
    admin: Optional[dict] = Field(None, description="Admin information if role is admin")

    # Authentication tokens
    access_token: Optional[str] = Field(None, description="Access token (for testing)")
    token_type: Optional[str] = Field(None, description="Token type (for testing)")

    model_config = ConfigDict(from_attributes=True)


class StepwiseSignupData(BaseModel):
    """For multi-step signup flow - tracks progress through signup steps"""

    step: str = Field(..., description="Current step: role_selection, basic_info, role_specific, confirmation")
    selected_role: Optional[str] = Field(None, description="Selected role from role_selection step")
    basic_info: Optional[dict] = Field(None, description="Basic account info (email, password)")
    role_specific_data: Optional[dict] = Field(None, description="Role-specific information")
    completed_steps: list[str] = Field(default_factory=list, description="List of completed steps")


class MultiProfileSignupRequest(BaseModel):
    """Extended signup request that supports creating multiple client profiles during signup"""

    # Basic account info
    email: EmailStr = Field(..., description="Email address for the account")
    password: str = Field(..., min_length=8, description="Password for the account")
    primary_role: str = Field(
        default="client_helper", description="Primary role (typically client_helper for multi-profile)"
    )

    # Multiple client profiles
    client_profiles: list[ClientProfileBase] = Field(..., description="List of client profiles to create")

    # Optional attorney data if user can also provide legal help
    attorney_data: Optional[AttorneyBase] = Field(None, description="Attorney information if user is also an attorney")


class MultiProfileSignupResponse(BaseModel):
    """Response from multi-profile signup"""

    user: UserResponse
    client_profiles: list[dict] = Field(description="Created client profiles")
    attorney: Optional[dict] = Field(None, description="Attorney information if applicable")

    # Authentication tokens
    access_token: Optional[str] = Field(None, description="Access token (for testing)")
    token_type: Optional[str] = Field(None, description="Token type (for testing)")

    model_config = ConfigDict(from_attributes=True)
