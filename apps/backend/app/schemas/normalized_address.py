"""Pydantic schemas for NormalizedAddress."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class NormalizedAddressBase(BaseModel):
    """Base schema for normalized address information."""

    api_source: str
    original_address_query: str
    normalized_street_address: Optional[str] = None
    normalized_city: Optional[str] = None
    normalized_state: Optional[str] = None
    normalized_zip_code: Optional[str] = None
    county: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    api_response_json: Optional[Dict[str, Any]] = None


class NormalizedAddressCreate(NormalizedAddressBase):
    """Schema for creating a new normalized address."""

    pass  # No longer needs ice_detention_facility_id at creation


class NormalizedAddressUpdate(NormalizedAddressBase):
    """Schema for updating an existing normalized address. All fields are optional for update."""

    api_source: Optional[str] = None
    original_address_query: Optional[str] = None
    county: Optional[str] = None
    # ice_detention_facility_id is typically not updatable after creation


class NormalizedAddressResponse(NormalizedAddressBase):
    """Schema for returning normalized address information in API responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
