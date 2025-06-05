from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Placeholder for a minimal Court schema that would typically be in schemas.court
# This is to allow CourtCountyResponse to be fully defined here.
# In a real scenario, this would be imported from .court
class CourtMinimalResponse(BaseModel):
    id: int
    name: str
    abbreviation: str

    model_config = {"from_attributes": True}


class CourtCountyBase(BaseModel):
    county_name: str
    state: str
    court_id: int


class CourtCountyCreate(CourtCountyBase):
    pass


class CourtCountyUpdate(BaseModel):
    county_name: Optional[str] = None
    state: Optional[str] = None
    court_id: Optional[int] = None


class CourtCountyInDBBase(CourtCountyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourtCountyResponse(CourtCountyInDBBase):
    court: Optional[CourtMinimalResponse] = None  # Include related court information


# If you need a schema for reading a list of counties, e.g. for a Court response
class CourtCountyForCourtResponse(BaseModel):
    id: int
    county_name: str
    state: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
