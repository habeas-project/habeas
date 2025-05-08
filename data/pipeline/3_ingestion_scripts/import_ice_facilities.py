import logging
import sys
from pathlib import Path
from typing import Any, Dict

import pandas as pd  # type: ignore
import requests
from sqlalchemy.orm import Session

# Add the backend directory to the Python path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "apps" / "backend"))

from app.config import settings  # For POSITIONSTACK_KEY
from app.database import SessionLocal  # noqa: E402
from app.models.court import Court  # noqa: E402
from app.models.court_county import CourtCounty  # noqa: E402
from app.models.ice_detention_facility import IceDetentionFacility  # noqa: E402
from app.models.normalized_address import NormalizedAddress  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Helper Functions --- #


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


# --- Main Import Logic --- #


def import_ice_facilities(
    db: Session,
    excel_file_path: Path,
    positionstack_api_key: str,
) -> None:
    """Import ICE detention facilities from an Excel file, geocode them, and map to courts."""

    try:
        facilities_df = pd.read_excel(excel_file_path, engine="openpyxl")
        logger.info(f"Read {len(facilities_df)} facilities from {excel_file_path}")
    except FileNotFoundError:
        logger.error(
            f"File not found: {excel_file_path}. Aborting ICE facility import."
        )
        return
    except Exception as e:
        logger.error(f"Error reading Excel file {excel_file_path}: {str(e)}")
        return

    imported_facilities_count = 0
    updated_facilities_count = 0
    geocoded_facilities_count = 0
    court_mappings_count = 0

    for _, row in facilities_df.iterrows():
        try:
            facility_name = row.get("Facility Name")
            if not facility_name:
                logger.warning("Skipping row due to missing facility name.")
                continue

            # Phase 1: Initial Import of IceDetentionFacility
            existing_facility = (
                db.query(IceDetentionFacility)
                .filter(IceDetentionFacility.name == facility_name)
                .first()
            )

            original_address = row.get("Address")
            city = row.get("City")
            state = row.get("State")  # Expecting 2-letter code
            zip_code = (
                str(row.get("Zip Code")) if pd.notna(row.get("Zip Code")) else None
            )
            aor = row.get("AOR")
            facility_type = row.get("Facility Type-Detailed")
            gender_capacity = row.get("Gender/Capacity")

            if existing_facility:
                # Basic update if needed, more complex updates could be added
                changed = False
                if existing_facility.address != original_address:
                    existing_facility.address = original_address
                    changed = True
                if existing_facility.city != city:
                    existing_facility.city = city
                    changed = True
                if existing_facility.state != state:
                    existing_facility.state = state
                    changed = True
                if existing_facility.zip_code != zip_code:
                    existing_facility.zip_code = zip_code
                    changed = True
                if existing_facility.aor != aor:
                    existing_facility.aor = aor
                    changed = True
                if existing_facility.facility_type_detailed != facility_type:
                    existing_facility.facility_type_detailed = facility_type
                    changed = True
                if existing_facility.gender_capacity != gender_capacity:
                    existing_facility.gender_capacity = gender_capacity
                    changed = True

                if changed:
                    logger.info(f"Updating existing facility: {facility_name}")
                    updated_facilities_count += 1
                facility = existing_facility
            else:
                facility = IceDetentionFacility(
                    name=facility_name,
                    address=original_address,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    aor=aor,
                    facility_type_detailed=facility_type,
                    gender_capacity=gender_capacity,
                )
                db.add(facility)
                imported_facilities_count += 1
                logger.info(f"Added new facility: {facility_name}")

            db.flush()  # Ensure facility.id is available for NormalizedAddress

            # Phase 2: Geocode, Populate NormalizedAddress, and Map to Courts
            # Only geocode if we don't have normalized info or if key address parts changed (optional)
            if (
                not facility.normalized_address_info
                and original_address
                and city
                and state
            ):
                geocoded_data = geocode_address_positionstack(
                    original_address, city, state, positionstack_api_key
                )

                if geocoded_data and geocoded_data.get("county"):
                    normalized_address = NormalizedAddress(
                        ice_detention_facility_id=facility.id,
                        api_source="Positionstack",
                        original_address_query=f"{original_address}, {city}, {state}",
                        normalized_street_address=geocoded_data.get(
                            "street"
                        ),  # Positionstack uses 'street' for street address
                        normalized_city=geocoded_data.get(
                            "locality", geocoded_data.get("administrative_area")
                        ),  # Or other relevant fields
                        normalized_state=geocoded_data.get(
                            "region_code"
                        ),  # Positionstack uses 'region_code' for state
                        normalized_zip_code=geocoded_data.get("postal_code"),
                        county=geocoded_data["county"],
                        latitude=geocoded_data.get("latitude"),
                        longitude=geocoded_data.get("longitude"),
                        api_response_json=geocoded_data,
                    )
                    db.add(normalized_address)
                    facility.normalized_address_info = (
                        normalized_address  # Establish relationship
                    )
                    geocoded_facilities_count += 1
                    logger.info(
                        f"Geocoded and created NormalizedAddress for: {facility_name} (County: {geocoded_data['county']}) "
                    )

                    # Map to Court using county and state from normalized address
                    if (
                        facility.normalized_address_info.county
                        and facility.normalized_address_info.normalized_state
                        and not facility.court_id
                    ):
                        court_to_link = get_court_by_county_and_state(
                            db,
                            facility.normalized_address_info.county,
                            facility.normalized_address_info.normalized_state,
                        )
                        if court_to_link:
                            facility.court_id = court_to_link.id
                            court_mappings_count += 1
                            logger.info(
                                f"Mapped facility '{facility_name}' to court '{court_to_link.name}' via county '{facility.normalized_address_info.county}'"
                            )
                        else:
                            logger.warning(
                                f"Could not find court for facility '{facility_name}' based on county '{facility.normalized_address_info.county}' and state '{facility.normalized_address_info.normalized_state}'"
                            )
                elif geocoded_data:
                    logger.warning(
                        f"Geocoding for '{facility_name}' succeeded but county information was missing. API Response: {geocoded_data}"
                    )
                else:
                    logger.warning(
                        f"Geocoding failed or returned no data for facility: {facility_name} at {original_address}, {city}, {state}"
                    )
            elif (
                facility.normalized_address_info and not facility.court_id
            ):  # Already geocoded, try to map if not already mapped
                if (
                    facility.normalized_address_info.county
                    and facility.normalized_address_info.normalized_state
                ):
                    court_to_link = get_court_by_county_and_state(
                        db,
                        facility.normalized_address_info.county,
                        facility.normalized_address_info.normalized_state,
                    )
                    if court_to_link:
                        facility.court_id = court_to_link.id
                        court_mappings_count += 1
                        logger.info(
                            f"Mapped existing facility '{facility_name}' to court '{court_to_link.name}' via county '{facility.normalized_address_info.county}'"
                        )
                    else:
                        logger.warning(
                            f"Could not find court for existing facility '{facility_name}' based on county '{facility.normalized_address_info.county}' and state '{facility.normalized_address_info.normalized_state}'"
                        )

        except Exception as e:
            logger.error(
                f"Error processing facility row (Name: {row.get('Facility Name', 'Unknown')}): {str(e)}",
                exc_info=True,
            )
            db.rollback()  # Rollback this specific facility to continue with others
            continue  # Continue to the next row

    try:
        db.commit()  # Commit all changes at the end of the loop
        logger.info("Facility import process finished.")
        logger.info(
            f"Summary: Added {imported_facilities_count} new facilities, Updated {updated_facilities_count} existing facilities, Geocoded {geocoded_facilities_count} facilities, Mapped {court_mappings_count} facilities to courts."
        )
    except Exception as e:
        logger.error(f"Failed to commit changes after facility import loop: {str(e)}")
        db.rollback()


if __name__ == "__main__":
    # Path to the Excel file - relative to this script's location
    # Script is in data/pipeline/3_ingestion_scripts/
    # Excel file is in data/static_assets/
    excel_file = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "static_assets"
        / "2025_ice_detention_facilities.xlsx"
    )

    if not excel_file.exists():
        logger.error(f"ICE detention facilities Excel file not found: {excel_file}")
        sys.exit(1)

    if not settings.POSITIONSTACK_KEY:
        logger.error(
            "POSITIONSTACK_KEY environment variable not set. This is required for geocoding."
        )
        # Decide if to exit or proceed without geocoding. For now, let's exit.
        sys.exit(1)

    db_session = SessionLocal()
    try:
        logger.info("Starting ICE detention facility import process...")
        import_ice_facilities(db_session, excel_file, settings.POSITIONSTACK_KEY)
    except Exception as e:
        logger.error(
            f"Unhandled error during ICE facility import process: {str(e)}",
            exc_info=True,
        )
        db_session.rollback()
        sys.exit(1)
    finally:
        db_session.close()
