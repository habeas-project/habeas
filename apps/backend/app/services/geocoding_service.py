"""
Geocoding service for converting coordinates to addresses and determining court jurisdictions.
"""

import logging
import time

from typing import Any, Dict, Optional, Tuple

import requests

from sqlalchemy.orm import Session

from app.models.court import Court
from app.models.court_county import CourtCounty

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding coordinates and determining court jurisdictions."""

    def __init__(self, db: Session):
        self.db = db
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.request_timeout = 10
        self.rate_limit_delay = 1  # Nominatim requires 1 request per second

    def reverse_geocode_coordinates(self, latitude: float, longitude: float) -> Optional[Dict[str, str]]:
        """
        Reverse geocode GPS coordinates to get address information.

        Args:
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate

        Returns:
            Dictionary with address components or None if geocoding fails
        """
        try:
            # Rate limiting for Nominatim
            time.sleep(self.rate_limit_delay)

            # Nominatim reverse geocoding API
            url = f"{self.nominatim_base_url}/reverse"
            params: Dict[str, Any] = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "addressdetails": 1,
                "zoom": 18,  # High detail level
                "extratags": 1,
            }

            headers = {"User-Agent": "HabeasApp/1.0 (Emergency Legal Services)"}

            logger.info(f"Reverse geocoding coordinates: {latitude:.4f}, {longitude:.4f}")

            response = requests.get(url, params=params, headers=headers, timeout=self.request_timeout)
            response.raise_for_status()

            data = response.json()

            if not data or "error" in data:
                logger.warning(f"No geocoding results for coordinates: {latitude}, {longitude}")
                return None

            address = data.get("address", {})

            # Extract relevant address components
            result = {
                "formatted_address": data.get("display_name", ""),
                "city": self._extract_city(address),
                "county": address.get("county", ""),
                "state": self._extract_state(address),
                "country": address.get("country", ""),
                "postal_code": address.get("postcode", ""),
                "latitude": str(latitude),
                "longitude": str(longitude),
                "geocoding_source": "Nominatim/OpenStreetMap",
            }

            logger.info(f"Successfully geocoded to: {result['city']}, {result['state']}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {e}")
            return None

    def _extract_city(self, address: Dict) -> str:
        """Extract city name from Nominatim address components."""
        # Try different city-level keys in order of preference
        city_keys = ["city", "town", "village", "municipality", "hamlet"]
        for key in city_keys:
            if key in address and address[key]:
                return address[key]
        return ""

    def _extract_state(self, address: Dict) -> str:
        """Extract state from Nominatim address components."""
        state = address.get("state", "")
        # Convert full state names to abbreviations if needed
        # For now, return as-is - could add state name mapping later
        return state

    def determine_court_jurisdiction(
        self, latitude: float, longitude: float, address_data: Optional[Dict[str, str]] = None
    ) -> Optional[Court]:
        """
        Determine the federal district court jurisdiction for given coordinates.

        Args:
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate
            address_data: Optional pre-geocoded address data

        Returns:
            Court object for the jurisdiction or None if not found
        """
        try:
            # Get address data if not provided
            if not address_data:
                address_data = self.reverse_geocode_coordinates(latitude, longitude)

            if not address_data:
                logger.warning("Cannot determine jurisdiction without address data")
                return None

            state = address_data.get("state", "")
            county = address_data.get("county", "")

            if not state:
                logger.warning("Cannot determine jurisdiction without state information")
                return None

            # First try to find court by county and state
            if county:
                court = self._find_court_by_county_state(county, state)
                if court:
                    logger.info(f"Found court by county: {court.name} for {county}, {state}")
                    return court

            # Fallback: find court by state (for states with single districts)
            court = self._find_court_by_state(state)
            if court:
                logger.info(f"Found court by state: {court.name} for {state}")
                return court

            logger.warning(f"No court jurisdiction found for {county}, {state}")
            return None

        except Exception as e:
            logger.error(f"Error determining court jurisdiction: {e}")
            return None

    def _find_court_by_county_state(self, county: str, state: str) -> Optional[Court]:
        """Find court by county and state mapping."""
        try:
            # Clean up county name (remove "County" suffix if present)
            clean_county = county.replace(" County", "").strip()

            # Query for court by county and state
            court_county = (
                self.db.query(CourtCounty)
                .filter(CourtCounty.county_name.ilike(f"%{clean_county}%"), CourtCounty.state.ilike(f"%{state}%"))
                .first()
            )

            if court_county:
                court = self.db.query(Court).filter(Court.id == court_county.court_id).first()
                return court

            return None

        except Exception as e:
            logger.error(f"Error finding court by county/state: {e}")
            return None

    def _find_court_by_state(self, state: str) -> Optional[Court]:
        """Find court by state for single-district states."""
        try:
            # For states with single federal districts, find by state name in court name
            # This is a simplified approach - could be enhanced with a state mapping table
            courts = self.db.query(Court).filter(Court.name.ilike(f"%{state}%")).all()

            # If only one court found for the state, return it
            if len(courts) == 1:
                return courts[0]

            # For multiple courts, try to find the main district
            for court in courts:
                if "District" in court.name and state in court.name:
                    return court

            return None

        except Exception as e:
            logger.error(f"Error finding court by state: {e}")
            return None

    def geocode_and_determine_jurisdiction(
        self, latitude: float, longitude: float
    ) -> Tuple[Optional[Dict[str, str]], Optional[Court]]:
        """
        Complete geocoding and jurisdiction determination in one call.

        Args:
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate

        Returns:
            Tuple of (address_data, court) or (None, None) if failed
        """
        try:
            # First, reverse geocode the coordinates
            address_data = self.reverse_geocode_coordinates(latitude, longitude)
            if not address_data:
                return None, None

            # Then determine the court jurisdiction
            court = self.determine_court_jurisdiction(latitude, longitude, address_data)

            return address_data, court

        except Exception as e:
            logger.error(f"Error in geocoding and jurisdiction determination: {e}")
            return None, None

    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate that coordinates are within reasonable bounds.

        Args:
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate

        Returns:
            True if coordinates are valid, False otherwise
        """
        # Basic coordinate validation for continental US + territories
        # Latitude: roughly 24°N to 49°N (with some buffer)
        # Longitude: roughly 125°W to 66°W (with some buffer)

        if not (-90 <= latitude <= 90):
            return False
        if not (-180 <= longitude <= 180):
            return False

        # More specific validation for US territories if needed
        # For now, accept any valid global coordinates
        return True
