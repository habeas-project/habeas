#!/usr/bin/env python3
import logging
import os
import sys

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, func, inspect, text

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the database URL from environment variables
# Use the same pattern as in the backend app/database.py
database_url = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/habeas"
)

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
                if count is not None and count > 0:
                    logger.info(f"✓ Table '{table_name}' has {count} rows")
                elif count == 0:
                    logger.warning(f"⚠ Table '{table_name}' exists but has 0 data!")
                    if table_name != "normalized_addresses":
                        all_expected_present = False
                else:
                    logger.warning(
                        f"⚠ Could not determine row count for table '{table_name}'."
                    )
                    all_expected_present = False

        # Special checks for important tables
        if "court_counties" in tables:
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
