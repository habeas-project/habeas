from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Base schema for user data"""

    user_type: str = Field(..., description="Type of user: client, attorney, admin")
    is_active: bool = Field(True, description="Whether the user account is active")


class UserCreate(UserBase):
    """Schema for creating a new user"""

    cognito_id: str = Field(..., description="Unique identifier from AWS Cognito")


class UserUpdate(BaseModel):
    """Schema for updating user data"""

    user_type: Optional[str] = Field(None, description="Type of user: client, attorney, admin")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")


class UserResponse(UserBase):
    """Schema for user response data"""

    id: int
    cognito_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# For internal use/references only
class UserDB(UserResponse):
    """Schema for user in DB, including all fields"""

    pass
