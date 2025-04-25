from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .attorney import Attorney  # Import Attorney schema for relationship (will create a circular import)


class CourtBase(BaseModel):
    """Base schema for Court data"""

    name: str
    abbreviation: str  # Will be validated by constr in the model
    url: HttpUrl


class CourtCreate(CourtBase):
    """Schema for creating a new Court"""

    pass


class CourtUpdate(BaseModel):
    """Schema for updating a Court"""

    name: Optional[str] = None
    abbreviation: Optional[str] = None  # Will be validated by constr in the model
    url: Optional[HttpUrl] = None


class Court(CourtBase):
    """Schema for a Court with ID and timestamps"""

    id: int
    created_at: datetime
    updated_at: datetime
    # Add the relationship to attorneys - but need to handle circular import
    # This will be populated by the API but defined as empty list in schema
    admitted_attorneys: List["Attorney"] = []

    model_config = {"from_attributes": True}  # Updated from older Config.orm_mode


# Import here to avoid circular import issues
# from .attorney import Attorney
