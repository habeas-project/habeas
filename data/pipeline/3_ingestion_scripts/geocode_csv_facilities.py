#!/usr/bin/env python3
"""
Geocoding script for ICE detention facilities CSV file.
This script reads the CSV file and creates a separate geocoded CSV file.
Uses Nominatim (OpenStreetMap) as primary geocoder with Positionstack API as fallback.
"""

import csv
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


def setup_logging():
    """Set up logging to both file and console with timestamped log files."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent.parent.parent / "temp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"geocode_csv_facilities_{timestamp}.log"

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
logger.info("GEOCODE_CSV_FACILITIES.PY SCRIPT STARTED")


def geocode_address_positionstack(
    address: str, city: str, state: str, api_key: str
) -> Optional[Dict[str, Any]]:
    """Geocode address using Positionstack API and return the first result data."""
    if not api_key:
        logger.warning(
            "Positionstack API key is not configured. Skipping Positionstack geocoding."
        )
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
            result_data = data["data"][0]
            return {
                "latitude": str(result_data.get("latitude", "")),
                "longitude": str(result_data.get("longitude", "")),
                "normalized_address": result_data.get("label", ""),
                "geocoding_source": "Positionstack",
                "county": result_data.get("county", ""),
                "raw_response": result_data,
            }
        else:
            logger.warning(
                f"No Positionstack geocoding results found for query: {query}. Response: {data}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Positionstack API request failed for query '{query}': {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(
            f"Error parsing Positionstack API response for query '{query}': {e}. Response: {response.text if 'response' in locals() else 'No response'}"
        )
        return None


def geocode_address_nominatim(
    geolocator: Nominatim, address: str, city: str, state: str, max_retries: int = 3
) -> Optional[Dict[str, str]]:
    """
    Geocode an address using Nominatim (OpenStreetMap) and return coordinates and normalized address.

    Args:
        geolocator: Nominatim geocoder instance
        address: Street address
        city: City name
        state: State code
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary with latitude, longitude, and normalized address components, or None if geocoding fails
    """
    # Construct the full address query
    full_address = f"{address}, {city}, {state}, USA"

    for attempt in range(max_retries):
        try:
            logger.info(
                f"Nominatim geocoding attempt {attempt + 1}/{max_retries}: {full_address}"
            )
            # Type ignore for geopy's geocode method which returns Location or None
            location = geolocator.geocode(full_address, timeout=10)  # type: ignore[arg-type]

            if location:
                result = {
                    "latitude": str(location.latitude),  # type: ignore[attr-defined]
                    "longitude": str(location.longitude),  # type: ignore[attr-defined]
                    "normalized_address": location.address,  # type: ignore[attr-defined]
                    "geocoding_source": "Nominatim/OpenStreetMap",
                }

                logger.info(
                    f"Successfully geocoded with Nominatim: {full_address} -> ({location.latitude}, {location.longitude})"  # type: ignore[attr-defined]
                )
                return result
            else:
                logger.warning(
                    f"No Nominatim geocoding results found for: {full_address}"
                )
                return None

        except GeocoderTimedOut:
            logger.warning(
                f"Nominatim geocoding timeout for {full_address} (attempt {attempt + 1}/{max_retries})"
            )
            if attempt < max_retries - 1:
                time.sleep(2**attempt)  # Exponential backoff
            continue

        except GeocoderServiceError as e:
            logger.error(f"Nominatim geocoding service error for {full_address}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2**attempt)  # Exponential backoff
            continue

        except Exception as e:
            logger.error(
                f"Unexpected error geocoding {full_address} with Nominatim: {e}"
            )
            return None

    logger.error(
        f"Failed to geocode with Nominatim after {max_retries} attempts: {full_address}"
    )
    return None


def geocode_address_with_fallback(
    geolocator: Nominatim,
    address: str,
    city: str,
    state: str,
    positionstack_api_key: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    """
    Geocode an address using Nominatim as primary and Positionstack as fallback.

    Args:
        geolocator: Nominatim geocoder instance
        address: Street address
        city: City name
        state: State code
        positionstack_api_key: Optional Positionstack API key for fallback

    Returns:
        Dictionary with geocoding results or None if both methods fail
    """
    # Try Nominatim first
    result = geocode_address_nominatim(geolocator, address, city, state)

    if result:
        return result

    # If Nominatim fails and we have a Positionstack API key, try that
    if positionstack_api_key:
        logger.info(
            f"Nominatim failed, trying Positionstack fallback for: {address}, {city}, {state}"
        )
        positionstack_result = geocode_address_positionstack(
            address, city, state, positionstack_api_key
        )

        if positionstack_result:
            logger.info(
                f"Successfully geocoded with Positionstack fallback: {address}, {city}, {state}"
            )
            return positionstack_result

    logger.warning(
        f"Both Nominatim and Positionstack failed for: {address}, {city}, {state}"
    )
    return None


def geocode_csv_file(
    input_csv_path: Path,
    output_csv_path: Path,
    positionstack_api_key: Optional[str] = None,
) -> int:
    """
    Read the ICE facilities CSV file, geocode each facility, and write to a new CSV file.

    Args:
        input_csv_path: Path to the input CSV file
        output_csv_path: Path to the output geocoded CSV file
        positionstack_api_key: Optional Positionstack API key for fallback geocoding

    Returns:
        Number of successfully geocoded facilities
    """
    # Initialize the geocoder with a user agent
    geolocator = Nominatim(user_agent="habeas-ice-facilities-geocoder")

    geocoded_count = 0
    total_count = 0

    try:
        with (
            open(input_csv_path, "r", encoding="utf-8") as input_file,
            open(output_csv_path, "w", encoding="utf-8", newline="") as output_file,
        ):
            reader = csv.DictReader(input_file)

            # Ensure fieldnames is not None and create output fieldnames
            if reader.fieldnames is None:
                logger.error("CSV file has no header row")
                return 0

            output_fieldnames = list(reader.fieldnames) + [
                "latitude",
                "longitude",
                "normalized_address",
                "geocoding_source",
                "geocoding_timestamp",
            ]

            writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                total_count += 1

                # Get address components
                facility_name = row.get("Name", "").strip()
                address = row.get("Address", "").strip()
                city = row.get("City", "").strip()
                state = row.get("State", "").strip()

                if not facility_name:
                    logger.warning(
                        f"Skipping row {total_count} due to missing facility name"
                    )
                    continue

                if not address or not city or not state:
                    logger.warning(
                        f"Skipping geocoding for '{facility_name}' due to missing address components"
                    )
                    # Still write the row but without geocoding data
                    row.update(
                        {
                            "latitude": "",
                            "longitude": "",
                            "normalized_address": "",
                            "geocoding_source": "",
                            "geocoding_timestamp": datetime.now().isoformat(),
                        }
                    )
                    writer.writerow(row)
                    continue

                logger.info(f"Processing facility {total_count}: {facility_name}")

                # Attempt to geocode with fallback
                geocode_result = geocode_address_with_fallback(
                    geolocator, address, city, state, positionstack_api_key
                )

                if geocode_result:
                    # Add geocoding data to the row
                    row.update(
                        {
                            "latitude": geocode_result["latitude"],
                            "longitude": geocode_result["longitude"],
                            "normalized_address": geocode_result["normalized_address"],
                            "geocoding_source": geocode_result["geocoding_source"],
                            "geocoding_timestamp": datetime.now().isoformat(),
                        }
                    )
                    geocoded_count += 1
                else:
                    # Add empty geocoding fields
                    row.update(
                        {
                            "latitude": "",
                            "longitude": "",
                            "normalized_address": "",
                            "geocoding_source": "Failed",
                            "geocoding_timestamp": datetime.now().isoformat(),
                        }
                    )

                writer.writerow(row)

                # Add a small delay to be respectful to the geocoding services
                time.sleep(1)

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_csv_path}")
        return 0
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        return 0

    logger.info(
        f"Geocoding complete. Successfully geocoded {geocoded_count} out of {total_count} facilities."
    )
    return geocoded_count


def main():
    """Main function to run the geocoding process."""
    # Define file paths
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    input_csv_path = (
        project_root / "data" / "static_assets" / "2025_ice_detention_facilities.csv"
    )
    output_csv_path = (
        project_root
        / "data"
        / "static_assets"
        / "2025_ice_detention_facilities_geocoded.csv"
    )

    # Get Positionstack API key from environment (optional)
    positionstack_api_key = os.environ.get("POSITIONSTACK_KEY")

    if positionstack_api_key:
        logger.info("Positionstack API key found - will use as fallback geocoder")
    else:
        logger.info("No Positionstack API key found - using only Nominatim geocoder")

    logger.info(f"Input CSV: {input_csv_path}")
    logger.info(f"Output CSV: {output_csv_path}")

    if not input_csv_path.exists():
        logger.error(f"Input CSV file does not exist: {input_csv_path}")
        sys.exit(1)

    # Run the geocoding process
    geocoded_count = geocode_csv_file(
        input_csv_path, output_csv_path, positionstack_api_key
    )

    if geocoded_count > 0:
        logger.info(
            f"Geocoding completed successfully. {geocoded_count} facilities geocoded."
        )
        logger.info(f"Geocoded data saved to: {output_csv_path}")
    else:
        logger.error("Geocoding failed or no facilities were geocoded.")
        sys.exit(1)


if __name__ == "__main__":
    main()
