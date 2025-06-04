#!/usr/bin/env python3
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, func, inspect, text


# Configure logging to both file and console
def setup_logging():
    """Set up logging to both file and console with timestamped log files."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent.parent.parent / "temp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"verify_migration_{timestamp}.log"

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

# Load environment variables
load_dotenv()

# Get the database URL from environment variables
# Use the same pattern as in the backend app/database.py
database_url = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/habeas"
)

# Get verification mode
VERIFICATION_MODE = os.getenv(
    "VERIFICATION_MODE", "full_check"
)  # Default to full_check

# Create engine
engine = sa.create_engine(database_url)
inspector = inspect(engine)

# Create MetaData object
metadata = MetaData()

logger.info("Database inspection results:")
logger.info("-" * 50)

# Check tables
tables = inspector.get_table_names()
logger.info(f"Tables in database ({len(tables)}):")
for table in tables:
    logger.info(f"- {table}")
logger.info("")

# Check alembic version
with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    versions = result.fetchall()
    logger.info(f"Alembic versions ({len(versions)}):")
    for version in versions:
        logger.info(f"- {version[0]}")
logger.info("")

# Check specific tables for our schema
# Include both schema tables and tables populated by ingestion scripts
expected_tables = [
    # Core schema tables
    "attorneys",
    "clients",
    "emergency_contacts",
    "courts",
    "attorney_court_admissions",
    # Tables populated by ingestion scripts
    "court_counties",
    "district_court_contacts",
    "ice_detention_facilities",
    "normalized_addresses",
]

logger.info("Data verification:")
all_expected_present = True
for table in expected_tables:
    if table in tables:
        logger.info(f"✓ Table '{table}' exists")
    else:
        logger.error(f"✗ Table '{table}' is missing!")
        all_expected_present = False

# Check data in tables populated by ingestion scripts
table_counts = {}
try:
    with engine.connect() as conn:
        for table_name in [
            "courts",
            "court_counties",
            "district_court_contacts",
            "ice_detention_facilities",
            "normalized_addresses",
        ]:
            if table_name in tables:
                # Reflect the table dynamically
                dynamic_table = Table(table_name, metadata, autoload_with=engine)
                # Build the query using SQLAlchemy expression language
                query = sa.select(func.count()).select_from(dynamic_table)
                result = conn.execute(query)
                count = result.scalar()
                table_counts[table_name] = count

                # Check if count is not None before comparing
                if (
                    VERIFICATION_MODE != "schema_only"
                ):  # Only check counts if not in schema_only mode
                    if count is not None and count > 0:
                        logger.info(f"✓ Table '{table_name}' has {count} rows")
                    elif count == 0:
                        logger.warning(f"⚠ Table '{table_name}' exists but has 0 data!")
                        # Define which tables are critical for each verification mode
                        critical_for_basic_data = [
                            "courts",
                            "court_counties",
                            "district_court_contacts",
                        ]
                        critical_for_full_check = critical_for_basic_data + [
                            "ice_detention_facilities"
                        ]

                        # In basic_data mode, only fail if basic data tables are empty
                        if (
                            VERIFICATION_MODE == "basic_data"
                            and table_name in critical_for_basic_data
                        ):
                            all_expected_present = False
                        # In full_check mode, fail if any critical table is empty (except normalized_addresses which depends on API)
                        elif (
                            VERIFICATION_MODE == "full_check"
                            and table_name in critical_for_full_check
                        ):
                            all_expected_present = False
                    else:
                        logger.warning(
                            f"⚠ Could not determine row count for table '{table_name}'."
                        )
                        all_expected_present = False
                elif (
                    table_name in tables
                ):  # In schema_only mode, just acknowledge it exists if we got this far
                    logger.info(
                        f"✓ Table '{table_name}' exists (row count not checked in schema_only mode)"
                    )

        # Special checks for important tables
        if (
            VERIFICATION_MODE != "schema_only" and "court_counties" in tables
        ):  # Only run these detailed checks in full_check mode
            # Check if court_counties has proper foreign key relationships
            logger.info("Checking court_counties relationships...")

            # Check orphaned records (court_counties records with no matching court)
            orphaned_query = text(
                """
                SELECT COUNT(*)
                FROM court_counties cc
                LEFT JOIN courts c ON cc.court_id = c.id
                WHERE c.id IS NULL
            """
            )
            orphaned_count = conn.execute(orphaned_query).scalar()

            # Check if orphaned_count is not None before comparing
            if orphaned_count is not None and orphaned_count > 0:
                logger.error(
                    f"⚠ Found {orphaned_count} court_counties records with invalid court_id!"
                )
                all_expected_present = False
            elif orphaned_count == 0:
                logger.info("✓ All court_counties records have valid court references")
            else:
                logger.warning("⚠ Could not determine orphaned court_counties count.")
                all_expected_present = False

            # Check court coverage (courts that have counties mapped to them)
            coverage_query = text(
                """
                SELECT COUNT(DISTINCT court_id)
                FROM court_counties
            """
            )
            courts_with_counties = conn.execute(coverage_query).scalar()

            total_courts = table_counts.get("courts", 0)
            if total_courts > 0:
                coverage_pct = (courts_with_counties / total_courts) * 100
                logger.info(
                    f"✓ Court county coverage: {courts_with_counties}/{total_courts} courts ({coverage_pct:.1f}%)"
                )

                # Consider warning if coverage is low
                if coverage_pct < 80:
                    logger.warning(
                        f"⚠ Low county coverage for courts: only {coverage_pct:.1f}% of courts have counties"
                    )

except Exception as e:
    logger.error(f"Error checking table data: {str(e)}")
    all_expected_present = False

logger.info("")
if all_expected_present:
    logger.info("Verification status: SUCCESS")
    exit_code = 0
else:
    logger.error("Verification status: FAILED")
    exit_code = 1

sys.exit(exit_code)
