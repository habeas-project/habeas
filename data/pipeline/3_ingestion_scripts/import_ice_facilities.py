import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import requests
from sqlalchemy.orm import Session

# Add the backend directory to the Python path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "apps" / "backend"))

from app.database import SessionLocal
from app.models.court import Court
from app.models.court_county import CourtCounty
from app.models.ice_detention_facility import IceDetentionFacility
from app.models.normalized_address import NormalizedAddress

# Instead of importing from app.config, get the API key directly from environment
POSITIONSTACK_KEY = os.environ.get("POSITIONSTACK_KEY")
SKIP_API_CALLS = os.environ.get("SKIP_API_CALLS", "false").lower() == "true"


# Configure logging to both file and console
def setup_logging():
    """Set up logging to both file and console with timestamped log files."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent.parent.parent / "temp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"import_ice_facilities_{timestamp}.log"

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
logger.info("IMPORT_ICE_FACILITIES.PY SCRIPT STARTED")

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


def import_ice_facilities_data(db: Session, excel_file_path: Path) -> int:
    """Import raw ICE detention facility data from an Excel file."""
    logger.info("ENTERING import_ice_facilities_data function NOW")
    try:
        facilities_df = pd.read_excel(excel_file_path, engine="openpyxl", header=6)
        logger.info(
            f"Read {len(facilities_df)} facilities from {excel_file_path} using header row 7"
        )
        logger.info(f"Excel columns: {facilities_df.columns.tolist()}")
    except FileNotFoundError:
        logger.error(
            f"File not found: {excel_file_path}. Aborting ICE facility import."
        )
        return 0
    except Exception as e:
        logger.error(f"Error reading Excel file {excel_file_path}: {str(e)}")
        return 0

    imported_facilities_count = 0
    updated_facilities_count = 0

    for row_index, row in facilities_df.iterrows():
        try:
            facility_name = row.get("Name")
            if (
                pd.isna(facility_name) or not str(facility_name).strip()
            ):  # Check for NaN or empty
                logger.warning(
                    f"Skipping row due to missing facility name (row index: {row_index}). Columns: {row.index.tolist()}"
                )
                continue
            facility_name = str(facility_name).strip()

            original_address_raw = row.get("Address")
            original_address = (
                str(original_address_raw).strip()
                if pd.notna(original_address_raw) and str(original_address_raw).strip()
                else None
            )

            city_raw = row.get("City")
            city = (
                str(city_raw).strip()
                if pd.notna(city_raw) and str(city_raw).strip()
                else None
            )

            state_raw = row.get("State")
            state = (
                str(state_raw).strip()
                if pd.notna(state_raw) and str(state_raw).strip()
                else None
            )

            zip_code_raw = row.get("Zip Code")
            zip_code = (
                str(zip_code_raw).strip()
                if pd.notna(zip_code_raw) and str(zip_code_raw).strip()
                else None
            )

            aor_raw = row.get("AOR")
            aor = (
                str(aor_raw).strip()
                if pd.notna(aor_raw) and str(aor_raw).strip()
                else None
            )

            facility_type_raw = row.get("Type Detailed")
            facility_type = (
                str(facility_type_raw).strip()
                if pd.notna(facility_type_raw) and str(facility_type_raw).strip()
                else None
            )

            gender_capacity_raw = row.get("Male/Female")
            gender_capacity = (
                str(gender_capacity_raw).strip()
                if pd.notna(gender_capacity_raw) and str(gender_capacity_raw).strip()
                else None
            )

            existing_facility = (
                db.query(IceDetentionFacility)
                .filter(IceDetentionFacility.name == facility_name)
                .first()
            )

            if existing_facility:
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
        except Exception as e:
            logger.error(
                f"Error processing facility row (Name: {row.get('Name', 'Unknown')}): {str(e)}",
                exc_info=True,
            )
            db.rollback()
            continue
    try:
        db.commit()
        logger.info(
            f"Raw facility data import finished. Added: {imported_facilities_count}, Updated: {updated_facilities_count}"
        )
        return imported_facilities_count + updated_facilities_count
    except Exception as e:
        logger.error(f"Failed to commit changes after raw facility import: {str(e)}")
        db.rollback()
        return 0


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

            time.sleep(1)  # Add a 1-second delay
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


def run_ice_facilities_import_pipeline(
    db: Session,
    excel_file_path: Path,
    positionstack_api_key: str | None,
    skip_api: bool = False,
) -> None:
    """Runs the full ICE facility import pipeline: data import, then geocoding/mapping."""
    logger.info("Starting ICE facility data import phase...")
    facilities_processed_count = import_ice_facilities_data(db, excel_file_path)
    logger.info(
        f"ICE facility data import phase finished. Processed {facilities_processed_count} facilities."
    )

    if facilities_processed_count > 0 and not skip_api:
        if positionstack_api_key:
            logger.info("Starting geocoding and court mapping phase...")
            geocoded_count, mapped_count = geocode_and_map_facilities(
                db, positionstack_api_key
            )
            logger.info(
                f"Geocoding and court mapping phase finished. Geocoded: {geocoded_count}, Mapped: {mapped_count}."
            )
        else:
            logger.warning(
                "POSITIONSTACK_KEY not found. Skipping geocoding and court mapping phase."
            )
    elif skip_api:
        logger.info("Skipping API operations (SKIP_API_CALLS=true)")
    else:
        logger.info("No facilities imported, skipping geocoding and mapping phase.")

    logger.info("ICE detention facility import pipeline finished.")


if __name__ == "__main__":
    # Check if we should skip API calls
    if SKIP_API_CALLS:
        logger.info(
            "SKIP_API_CALLS is set to true - will only import basic facility data"
        )

    # Find the Excel file in the static assets directory
    excel_file = (
        Path(__file__).resolve().parent.parent.parent
        / "static_assets"
        / "2025_ice_detention_facilities.xlsx"
    )

    if not excel_file.exists():
        logger.error(f"ICE detention facilities Excel file not found: {excel_file}")
        sys.exit(1)

    # POSITIONSTACK_KEY is now read globally at the top of the file.
    # The geocode_and_map_facilities function and the pipeline runner will check for its presence.

    db_session = SessionLocal()
    try:
        logger.info("Starting ICE detention facility import process...")
        run_ice_facilities_import_pipeline(
            db_session, excel_file, POSITIONSTACK_KEY, skip_api=SKIP_API_CALLS
        )  # Pass the key and skip_api flag
        logger.info("ICE detention facility import process completed successfully.")
    except Exception as e:
        logger.error(
            f"Unhandled error during ICE facility import process: {str(e)}",
            exc_info=True,
        )
        db_session.rollback()
        sys.exit(1)
    finally:
        db_session.close()
