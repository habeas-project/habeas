from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, HttpUrl


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
    # Use Any for relationship to avoid circular import
    admitted_attorneys: List[Any] = []

    model_config = {"from_attributes": True}  # Updated from older Config.orm_mode
