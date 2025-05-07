import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "apps" / "backend"))

from app.database import SessionLocal
from app.models.court import Court
from app.models.court_county import CourtCounty

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_court_by_abbreviation(db: Session, abbreviation: str) -> Court | None:
    """Retrieve a court by its abbreviation."""
    return db.query(Court).filter(Court.abbreviation == abbreviation).first()


def import_court_data(
    db: Session,
    district_courts_csv_path: Path,
    court_counties_csv_path: Path,
    court_contact_csv_path: Path,
) -> None:
    """Import data from all relevant CSV files into the database."""

    # 1. Import District Courts
    try:
        courts_df = pd.read_csv(district_courts_csv_path)
        logger.info(f"Read {len(courts_df)} courts from {district_courts_csv_path}")
        imported_courts_count = 0
        for _, row in courts_df.iterrows():
            try:
                existing_court = get_court_by_abbreviation(db, row["abbreviation"])
                if existing_court:
                    # Update existing court if necessary (e.g., URL)
                    if (
                        existing_court.name != row["court"]
                        or existing_court.url != row["url"]
                    ):
                        existing_court.name = row["court"]
                        existing_court.url = row["url"]
                        logger.info(
                            f"Updated court: {existing_court.name} ({existing_court.abbreviation})"
                        )
                else:
                    court = Court(
                        name=row["court"],
                        abbreviation=row["abbreviation"],
                        url=row["url"],
                    )
                    db.add(court)
                    imported_courts_count += 1
                    logger.info(f"Added court: {court.name} ({court.abbreviation})")
            except Exception as e:
                logger.error(
                    f"Error processing court {row.get('court', 'Unknown')}: {str(e)}"
                )
        db.commit()
        logger.info(f"Successfully added {imported_courts_count} new courts.")
    except FileNotFoundError:
        logger.error(
            f"File not found: {district_courts_csv_path}. Skipping court import."
        )
    except Exception as e:
        logger.error(
            f"Error importing courts from {district_courts_csv_path}: {str(e)}"
        )
        db.rollback()  # Rollback on error for this section

    # 2. Import Court Counties
    try:
        counties_df = pd.read_csv(court_counties_csv_path)
        logger.info(
            f"Read {len(counties_df)} county entries from {court_counties_csv_path}"
        )
        imported_counties_count = 0
        for _, row in counties_df.iterrows():
            try:
                court = get_court_by_abbreviation(db, row["court_abbreviation"])
                if court:
                    # Check if this county association already exists for this court
                    existing_county_assoc = (
                        db.query(CourtCounty)
                        .filter(
                            CourtCounty.court_id == court.id,
                            CourtCounty.county_name == row["county_name"],
                            CourtCounty.state == row["state"],
                        )
                        .first()
                    )
                    if not existing_county_assoc:
                        court_county = CourtCounty(
                            court_id=court.id,
                            county_name=row["county_name"],
                            state=row["state"],
                        )
                        db.add(court_county)
                        imported_counties_count += 1
                    # else:
                    # logger.debug(f"County association already exists for {row['county_name']}, {row['state']} with court {court.abbreviation}")
                else:
                    logger.warning(
                        f"Court with abbreviation '{row['court_abbreviation']}' not found. Skipping county: {row['county_name']}"
                    )
            except Exception as e:
                logger.error(
                    f"Error processing county {row.get('county_name', 'Unknown')} for court {row.get('court_abbreviation', 'Unknown')}: {str(e)}"
                )
        db.commit()
        logger.info(
            f"Successfully imported {imported_counties_count} new court-county associations."
        )
    except FileNotFoundError:
        logger.error(
            f"File not found: {court_counties_csv_path}. Skipping county import."
        )
    except Exception as e:
        logger.error(
            f"Error importing court counties from {court_counties_csv_path}: {str(e)}"
        )
        db.rollback()

    # 3. Process Court Contact Information
    try:
        contact_df = pd.read_csv(court_contact_csv_path)
        logger.info(
            f"Read {len(contact_df)} contact entries from {court_contact_csv_path}"
        )
        logger.info(
            "Processing court contact information. (Note: DistrictCourtContact model not yet implemented, logging data for now)"
        )
        for _, row in contact_df.iterrows():
            try:
                court = get_court_by_abbreviation(db, row["court_abbreviation"])
                if court:
                    # Placeholder for creating DistrictCourtContact object
                    logger.info(
                        f"Would create DistrictCourtContact for court '{court.abbreviation}': "
                        f"Location: {row.get('location_name', 'N/A')}, Address: {row.get('address', 'N/A')}, "
                        f"Phone: {row.get('phone', 'N/A')}, Email: {row.get('email', 'N/A')}, Hours: {row.get('hours', 'N/A')}"
                    )
                else:
                    logger.warning(
                        f"Court with abbreviation '{row['court_abbreviation']}' not found. Skipping contact: {row.get('location_name', 'N/A')}"
                    )
            except Exception as e:
                logger.error(
                    f"Error processing contact for court {row.get('court_abbreviation', 'Unknown')}: {str(e)}"
                )
        # No db.commit() here as we are not saving contact data yet
    except FileNotFoundError:
        logger.error(
            f"File not found: {court_contact_csv_path}. Skipping contact processing."
        )
    except Exception as e:
        logger.error(
            f"Error processing court contacts from {court_contact_csv_path}: {str(e)}"
        )


if __name__ == "__main__":
    # The script is in data/pipeline/3_ingestion_scripts/
    # CSVs are in data/pipeline/2_staging_data/
    base_staging_data_dir = Path(__file__).resolve().parent.parent / "2_staging_data"

    district_courts_csv = base_staging_data_dir / "uscourts_foundations.csv"
    court_counties_csv = base_staging_data_dir / "pacer_court_counties.csv"
    court_contact_csv = base_staging_data_dir / "pacer_court_contacts.csv"

    # Check if all necessary CSV files exist
    files_ok = True
    for f_path, f_name in [
        (district_courts_csv, "District Courts CSV"),
        (court_counties_csv, "Court Counties CSV"),
        (court_contact_csv, "Court Contact CSV"),
    ]:
        if not f_path.exists():
            logger.error(f"{f_name} file not found: {f_path}")
            files_ok = False

    if not files_ok:
        logger.error("One or more required CSV files are missing. Aborting import.")
        sys.exit(1)

    db_session = SessionLocal()
    try:
        logger.info("Starting court data import process...")
        import_court_data(
            db_session,
            district_courts_csv,
            court_counties_csv,
            court_contact_csv,
        )
        logger.info("Court data import process finished.")
    except Exception as e:
        logger.error(f"Failed to import court data: {str(e)}")
        db_session.rollback()
        sys.exit(1)
    finally:
        db_session.close()
