#!/usr/bin/env python3
"""
Import ICE detention facilities from CSV files.
This script imports from the main CSV file and uses the geocoded CSV file
to import pre-geocoded data, without any API calls.
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from sqlalchemy.orm import Session

# Add the backend directory to the Python path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "apps" / "backend"))

from app.database import SessionLocal
from app.models.court import Court
from app.models.court_county import CourtCounty
from app.models.ice_detention_facility import IceDetentionFacility
from app.models.normalized_address import NormalizedAddress


# Configure logging to both file and console
def setup_logging():
    """Set up logging to both file and console with timestamped log files."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent.parent.parent / "temp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"import_ice_facilities_csv_{timestamp}.log"

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
logger.info("IMPORT_ICE_FACILITIES_CSV.PY SCRIPT STARTED")

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


def parse_geocoded_address(normalized_address: str) -> Dict[str, str]:
    """
    Parse a normalized address string into components.
    Expected format: "Street Address, City, State ZIP, Country"
    """
    if not normalized_address:
        return {}

    # Split by commas and clean up whitespace
    parts = [part.strip() for part in normalized_address.split(",")]

    result = {}

    if len(parts) >= 1:
        result["street_address"] = parts[0]

    if len(parts) >= 2:
        result["city"] = parts[1]

    if len(parts) >= 3:
        # Parse "State ZIP" format
        state_zip = parts[2].strip()
        state_zip_parts = state_zip.split()
        if len(state_zip_parts) >= 1:
            result["state"] = state_zip_parts[0]
        if len(state_zip_parts) >= 2:
            result["zip_code"] = state_zip_parts[1]

    if len(parts) >= 4:
        result["country"] = parts[3]

    return result


# --- Main Import Logic --- #


def import_ice_facilities_from_csv(
    db: Session, csv_file_path: Path, geocoded_csv_path: Path
) -> int:
    """Import ICE detention facility data from CSV files with pre-geocoded data."""
    logger.info("ENTERING import_ice_facilities_from_csv function")

    # Load geocoded data if available
    geocoded_data = {}
    if geocoded_csv_path.exists():
        logger.info(f"Loading geocoded data from: {geocoded_csv_path}")
        try:
            with open(geocoded_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    facility_name = row.get("Name", "").strip()
                    if facility_name:
                        # Convert coordinates to float, handle empty/failed values
                        latitude = row.get("latitude", "").strip()
                        longitude = row.get("longitude", "").strip()

                        # Only include geocoded data if we have valid coordinates
                        if (
                            latitude
                            and longitude
                            and latitude != ""
                            and longitude != ""
                        ):
                            try:
                                lat_float = float(latitude)
                                lon_float = float(longitude)
                                geocoded_data[facility_name] = {
                                    "latitude": lat_float,
                                    "longitude": lon_float,
                                    "normalized_address": str(
                                        row.get("normalized_address", "")
                                    ).strip(),
                                    "geocoding_source": str(
                                        row.get("geocoding_source", "Static CSV")
                                    ).strip(),
                                }
                            except (ValueError, TypeError) as e:
                                logger.warning(
                                    f"Invalid coordinates for {facility_name}: Coordinates are not valid - {e}"
                                )
                                continue
                        else:
                            logger.warning(f"Missing coordinates for {facility_name}")
                            continue
            logger.info(f"Loaded geocoded data for {len(geocoded_data)} facilities")
        except Exception as e:
            logger.error(f"Error loading geocoded data: {e}")
    else:
        logger.warning(f"Geocoded CSV file not found: {geocoded_csv_path}")

    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            facilities_data = list(reader)
        logger.info(f"Read {len(facilities_data)} facilities from {csv_file_path}")
        logger.info(
            f"CSV columns: {facilities_data[0].keys() if facilities_data else 'No data'}"
        )
    except FileNotFoundError:
        logger.error(f"File not found: {csv_file_path}. Aborting ICE facility import.")
        return 0
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file_path}: {str(e)}")
        return 0

    imported_facilities_count = 0
    updated_facilities_count = 0
    geocoded_count = 0

    for row_index, row in enumerate(facilities_data):
        try:
            facility_name = row.get("Name")
            if not facility_name or not str(facility_name).strip():
                logger.warning(
                    f"Skipping row due to missing facility name (row index: {row_index})"
                )
                continue
            facility_name = str(facility_name).strip()

            # Extract basic facility data
            original_address = str(row.get("Address", "")).strip() or None
            city = str(row.get("City", "")).strip() or None
            state = str(row.get("State", "")).strip() or None
            zip_code = str(row.get("Zip", "")).strip() or None
            aor = str(row.get("AOR", "")).strip() or None
            facility_type = str(row.get("Type Detailed", "")).strip() or None
            gender_capacity = str(row.get("Male/Female", "")).strip() or None

            # Handle mandatory field
            mandatory_raw = row.get("Mandatory", "")
            try:
                mandatory = (
                    int(float(str(mandatory_raw).replace(",", "")))
                    if mandatory_raw and str(mandatory_raw).strip() not in ["", "N/A"]
                    else None
                )
            except (ValueError, TypeError):
                mandatory = None

            # Handle guaranteed minimum
            guaranteed_minimum_raw = row.get("Guaranteed Minimum", "")
            try:
                guaranteed_minimum = (
                    int(float(str(guaranteed_minimum_raw).replace(",", "")))
                    if guaranteed_minimum_raw
                    and str(guaranteed_minimum_raw).strip() not in ["", "N/A"]
                    else None
                )
            except (ValueError, TypeError):
                guaranteed_minimum = None

            # Additional fields
            last_inspection_type = (
                str(row.get("Last Inspection Type", "")).strip() or None
            )
            last_inspection_end_date = (
                str(row.get("Last Inspection End Date", "")).strip() or None
            )
            pending_fy25_inspection = (
                str(row.get("Pending FY25 Inspection", "")).strip() or None
            )
            last_inspection_standard = (
                str(row.get("Last Inspection Standard", "")).strip() or None
            )
            last_final_rating = str(row.get("Last Final Rating", "")).strip() or None

            # Check if facility already exists
            existing_facility = (
                db.query(IceDetentionFacility)
                .filter(IceDetentionFacility.name == facility_name)
                .first()
            )

            if existing_facility:
                logger.info(f"Updating existing facility: {facility_name}")
                # Update fields
                existing_facility.original_address = original_address
                existing_facility.city = city
                existing_facility.state = state
                existing_facility.zip_code = zip_code
                existing_facility.aor = aor
                existing_facility.facility_type = facility_type
                existing_facility.gender_capacity = gender_capacity
                existing_facility.mandatory = mandatory
                existing_facility.guaranteed_minimum = guaranteed_minimum
                existing_facility.last_inspection_type = last_inspection_type
                existing_facility.last_inspection_end_date = last_inspection_end_date
                existing_facility.pending_fy25_inspection = pending_fy25_inspection
                existing_facility.last_inspection_standard = last_inspection_standard
                existing_facility.last_final_rating = last_final_rating
                updated_facilities_count += 1
                facility = existing_facility
            else:
                # Create new facility
                facility = IceDetentionFacility(
                    name=facility_name,
                    original_address=original_address,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    aor=aor,
                    facility_type=facility_type,
                    gender_capacity=gender_capacity,
                    mandatory=mandatory,
                    guaranteed_minimum=guaranteed_minimum,
                    last_inspection_type=last_inspection_type,
                    last_inspection_end_date=last_inspection_end_date,
                    pending_fy25_inspection=pending_fy25_inspection,
                    last_inspection_standard=last_inspection_standard,
                    last_final_rating=last_final_rating,
                )
                db.add(facility)
                logger.info(f"Added new facility: {facility_name}")
                imported_facilities_count += 1

            # Add geocoded data if available
            if facility_name in geocoded_data:
                geocoded_info = geocoded_data[facility_name]

                # Parse the normalized address into components
                normalized_address_value = str(
                    geocoded_info.get("normalized_address", "")
                )
                address_components = parse_geocoded_address(normalized_address_value)

                # Check if normalized address already exists
                existing_address = (
                    db.query(NormalizedAddress)
                    .filter(
                        NormalizedAddress.latitude == geocoded_info["latitude"],
                        NormalizedAddress.longitude == geocoded_info["longitude"],
                    )
                    .first()
                )

                if not existing_address:
                    normalized_address = NormalizedAddress(
                        api_source=geocoded_info.get("geocoding_source", "Static CSV"),
                        original_address_query=f"{original_address}, {city}, {state}",
                        latitude=geocoded_info["latitude"],
                        longitude=geocoded_info["longitude"],
                        normalized_street_address=address_components.get(
                            "street_address"
                        ),
                        normalized_city=address_components.get("city"),
                        normalized_state=address_components.get("state"),
                        normalized_zip_code=address_components.get("zip_code"),
                        county=None,  # Will be parsed from normalized address if available
                    )
                    db.add(normalized_address)
                    db.flush()  # Get the ID
                    facility.normalized_address_id = normalized_address.id
                    logger.info(f"Added geocoded data for facility: {facility_name}")
                    geocoded_count += 1
                else:
                    facility.normalized_address_id = existing_address.id
                    logger.info(
                        f"Using existing geocoded data for facility: {facility_name}"
                    )
                    geocoded_count += 1

            db.commit()

        except Exception as e:
            logger.error(
                f"Error processing facility '{facility_name}' at row {row_index}: {str(e)}"
            )
            db.rollback()
            continue

    logger.info(
        f"CSV facility import finished. Added: {imported_facilities_count}, Updated: {updated_facilities_count}, Geocoded: {geocoded_count}"
    )
    return imported_facilities_count + updated_facilities_count


def run_ice_facilities_import_pipeline(db: Session) -> None:
    """Run the complete ICE facilities import pipeline using CSV files."""
    # Define file paths - fix the path calculation
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    csv_file_path = (
        base_dir / "data" / "static_assets" / "2025_ice_detention_facilities.csv"
    )
    geocoded_csv_path = (
        base_dir
        / "data"
        / "static_assets"
        / "2025_ice_detention_facilities_geocoded.csv"
    )

    logger.info(f"Main CSV file: {csv_file_path}")
    logger.info(f"Geocoded CSV file: {geocoded_csv_path}")

    if geocoded_csv_path.exists():
        logger.info("Geocoded CSV file found - will use pre-geocoded data")
    else:
        logger.warning("Geocoded CSV file not found - will import without geocoding")

    # Import facilities from CSV
    total_imported = import_ice_facilities_from_csv(
        db, csv_file_path, geocoded_csv_path
    )
    logger.info(f"Processed {total_imported} facilities from CSV")

    logger.info("CSV import process completed successfully.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_ice_facilities_import_pipeline(db)
    except Exception as e:
        logger.error(f"Ice facilities import failed: {str(e)}")
        raise
    finally:
        db.close()
