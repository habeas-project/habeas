#!/usr/bin/env python3
"""
Geocoding script for ICE detention facilities.
This script runs API-dependent operations after basic data has been loaded.
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import requests
from sqlalchemy.orm import Session

# Add the backend directory to the Python path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "apps" / "backend"))

from app.database import SessionLocal
from app.models.court import Court
from app.models.court_county import CourtCounty
from app.models.ice_detention_facility import IceDetentionFacility
from app.models.normalized_address import NormalizedAddress

# Get the API key from environment
POSITIONSTACK_KEY = os.environ.get("POSITIONSTACK_KEY")


# Configure logging to both file and console
def setup_logging():
    """Set up logging to both file and console with timestamped log files."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent.parent.parent / "temp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"geocode_ice_facilities_{timestamp}.log"

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging to file: {log_file}")
    return logger


logger = setup_logging()
logger.info("GEOCODE_ICE_FACILITIES.PY SCRIPT STARTED")


def get_court_by_county_and_state(
    db: Session, county_name: str, state_code: str
) -> Court | None:
    """Retrieve a court by matching county name and state within CourtCounty associations."""
    court_county_entry = (
        db.query(CourtCounty)
        .filter(
            CourtCounty.county_name.ilike(f"%{county_name}%"),
            CourtCounty.state == state_code,
        )
        .first()
    )
    if court_county_entry:
        return court_county_entry.court
    return None


def geocode_address_positionstack(
    address: str, city: str, state: str, api_key: str
) -> Dict[str, Any] | None:
    """Geocode address using Positionstack API and return the first result data."""
    if not api_key:
        logger.error("Positionstack API key is not configured. Skipping geocoding.")
        return None

    query = f"{address}, {city}, {state}"
    # Explicitly type params for mypy
    params: Dict[str, str | int] = {
        "access_key": api_key,
        "query": query,
        "limit": 1,  # We only need the top result
        "country": "US",  # Assuming all facilities are in the US
        "output_format": "json",
        "county_module": 1,  # Request county information
    }
    try:
        response = requests.get(
            "http://api.positionstack.com/v1/forward",
            params=params,
            timeout=10,  # Added timeout for bandit
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data and "data" in data and data["data"]:
            # Positionstack returns a list under the "data" key
            return data["data"][0]  # Return the first result
        else:
            logger.warning(
                f"No geocoding results found for query: {query}. Response: {data}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Positionstack API request failed for query '{query}': {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(
            f"Error parsing Positionstack API response for query '{query}': {e}. Response: {response.text if response else 'No response'}"
        )
        return None


def geocode_and_map_facilities(
    db: Session, positionstack_api_key: str
) -> tuple[int, int]:
    """Geocode facilities without normalized addresses and map them to courts."""
    facilities_to_process = (
        db.query(IceDetentionFacility)
        .filter(IceDetentionFacility.normalized_address_id.is_(None))
        .all()
    )

    if not facilities_to_process:
        logger.info("No facilities found requiring geocoding or court mapping.")
        return 0, 0

    logger.info(
        f"Found {len(facilities_to_process)} facilities to geocode and potentially map."
    )

    geocoded_facilities_count = 0
    court_mappings_count = 0

    for facility in facilities_to_process:
        try:
            if not facility.address or not facility.city or not facility.state:
                logger.warning(
                    f"Skipping geocoding for facility '{facility.name}' due to missing address components (address, city, or state)."
                )
                continue

            logger.info(
                f"Attempting to geocode: {facility.name} - {facility.address}, {facility.city}, {facility.state}"
            )
            geocoded_data = geocode_address_positionstack(
                facility.address,
                facility.city,
                facility.state,
                positionstack_api_key,
            )

            current_normalized_address = None
            if geocoded_data and geocoded_data.get("county"):
                new_normalized_address = NormalizedAddress(
                    api_source="Positionstack",
                    original_address_query=f"{facility.address}, {facility.city}, {facility.state}",
                    normalized_street_address=geocoded_data.get("street"),
                    normalized_city=geocoded_data.get(
                        "locality", geocoded_data.get("administrative_area")
                    ),
                    normalized_state=geocoded_data.get("region_code"),
                    normalized_zip_code=geocoded_data.get("postal_code"),
                    county=geocoded_data["county"],
                    latitude=geocoded_data.get("latitude"),
                    longitude=geocoded_data.get("longitude"),
                    api_response_json=geocoded_data,
                )
                db.add(new_normalized_address)
                db.flush()

                facility.normalized_address_id = new_normalized_address.id
                current_normalized_address = new_normalized_address

                geocoded_facilities_count += 1
                logger.info(
                    f"Geocoded and created NormalizedAddress (ID: {new_normalized_address.id}) for: {facility.name} (County: {geocoded_data['county']})"
                )
            elif geocoded_data:
                logger.warning(
                    f"Geocoding for '{facility.name}' succeeded but county information was missing. API Response: {geocoded_data}"
                )
            else:
                logger.warning(
                    f"Geocoding failed or returned no data for facility: {facility.name} at {facility.address}, {facility.city}, {facility.state}"
                )

            if (
                current_normalized_address
                and current_normalized_address.county
                and current_normalized_address.normalized_state
                and not facility.court_id
            ):
                court_to_link = get_court_by_county_and_state(
                    db,
                    current_normalized_address.county,
                    current_normalized_address.normalized_state,
                )
                if court_to_link:
                    facility.court_id = court_to_link.id
                    court_mappings_count += 1
                    logger.info(
                        f"Mapped facility '{facility.name}' to court '{court_to_link.name}' via county '{current_normalized_address.county}'"
                    )
                else:
                    logger.warning(
                        f"Could not find court for facility '{facility.name}' based on county '{current_normalized_address.county}' and state '{current_normalized_address.normalized_state}'"
                    )

            time.sleep(1)  # Add a 1-second delay to respect API rate limits
        except Exception as e:
            logger.error(
                f"Error processing facility '{facility.name}' during geocoding/mapping: {str(e)}",
                exc_info=True,
            )
            db.rollback()
            continue
    try:
        db.commit()
        logger.info(
            f"Geocoding and mapping finished. Geocoded: {geocoded_facilities_count}, Mapped to courts: {court_mappings_count}"
        )
        return geocoded_facilities_count, court_mappings_count
    except Exception as e:
        logger.error(f"Failed to commit changes after geocoding/mapping loop: {str(e)}")
        db.rollback()
        return 0, 0


if __name__ == "__main__":
    if not POSITIONSTACK_KEY:
        logger.error(
            "POSITIONSTACK_KEY environment variable is required for geocoding operations."
        )
        sys.exit(1)

    db_session = SessionLocal()
    try:
        logger.info("Starting ICE facility geocoding and court mapping process...")
        geocoded_count, mapped_count = geocode_and_map_facilities(
            db_session, POSITIONSTACK_KEY
        )
        logger.info(
            f"Geocoding process completed successfully. Geocoded: {geocoded_count}, Mapped: {mapped_count}."
        )
    except Exception as e:
        logger.error(
            f"Unhandled error during geocoding process: {str(e)}",
            exc_info=True,
        )
        db_session.rollback()
        sys.exit(1)
    finally:
        db_session.close()
