#!/usr/bin/env python3
"""
Custom migration script with enhanced logging and validation.
This provides more visibility into the migration process and verifies that required tables exist.
"""

import logging
import os
import sys
import time

from pathlib import Path

import alembic.command
import alembic.config
import sqlalchemy as sa

from sqlalchemy import inspect, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get the database URL from environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        # Log individual components for debugging
        logger.info("Individual database environment variables:")
        logger.info(f"  POSTGRES_USER: {os.getenv('POSTGRES_USER', 'NOT_SET')}")
        logger.info(f"  POSTGRES_PASSWORD: {'SET' if os.getenv('POSTGRES_PASSWORD') else 'NOT_SET'}")
        logger.info(f"  POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT_SET')}")
        logger.info(f"  POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'NOT_SET')}")
        logger.info(f"  POSTGRES_DB: {os.getenv('POSTGRES_DB', 'NOT_SET')}")
        sys.exit(1)

    # Validate that the URL is properly formatted
    if not db_url.startswith("postgresql://"):
        logger.error(f"Invalid DATABASE_URL format. Expected to start with 'postgresql://', got: {db_url[:20]}...")
        sys.exit(1)

    # Check for obviously malformed URLs
    if "@:/" in db_url or "****@:/" in db_url:
        logger.error("DATABASE_URL appears to be malformed - contains '@:/' pattern")
        logger.info("This usually indicates empty environment variables during URL construction")
        logger.info("Individual database environment variables:")
        logger.info(f"  POSTGRES_USER: {os.getenv('POSTGRES_USER', 'NOT_SET')}")
        logger.info(f"  POSTGRES_PASSWORD: {'SET' if os.getenv('POSTGRES_PASSWORD') else 'NOT_SET'}")
        logger.info(f"  POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT_SET')}")
        logger.info(f"  POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'NOT_SET')}")
        logger.info(f"  POSTGRES_DB: {os.getenv('POSTGRES_DB', 'NOT_SET')}")
        sys.exit(1)

    return db_url


def get_alembic_config() -> alembic.config.Config:
    """Create and return Alembic configuration."""
    current_dir = Path(__file__).resolve().parent
    alembic_cfg = alembic.config.Config(str(current_dir / "alembic.ini"))

    # Override the SQLAlchemy URL with the one from environment variables
    db_url = get_database_url()
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    return alembic_cfg


def run_migrations() -> None:
    """Run Alembic migrations with enhanced logging."""
    start_time = time.time()
    logger.info("Starting database migration process...")

    try:
        # Create Alembic configuration
        alembic_cfg = get_alembic_config()

        # Log the database URL (with password masked)
        db_url = get_database_url()
        masked_url = db_url
        if ":" in db_url and "@" in db_url:
            parts = db_url.split("@")
            prefix = parts[0].split(":")
            masked = f"{prefix[0]}:****"
            masked_url = f"{masked}@{parts[1]}"
        logger.info(f"Using database URL: {masked_url}")

        # Log what migrations directory we'll be using
        current_dir = Path(__file__).resolve().parent
        migrations_dir = current_dir / "migrations"
        logger.info(f"Using migrations from: {migrations_dir}")
        logger.info(f"Migration versions directory exists: {(migrations_dir / 'versions').exists()}")

        # List versions
        if (migrations_dir / "versions").exists():
            logger.info("Available migration versions:")
            for file in (migrations_dir / "versions").iterdir():
                if file.is_file() and file.name.endswith(".py"):
                    logger.info(f"  - {file.name}")

        # Check environment
        try:
            from alembic.script import ScriptDirectory

            config = alembic_cfg
            script = ScriptDirectory.from_config(config)
            logger.info(f"Found migration script directory: {script.dir}")
            revision = script.get_current_head()
            logger.info(f"Current migration head revision: {revision}")
        except Exception as script_error:
            logger.error(f"Error getting script info: {script_error}")

        # Try to explicitly initialize the connection
        try:
            engine = sa.create_engine(db_url)
            connection = engine.connect()
            logger.info("Database connection successful!")
            connection.close()
        except Exception as db_error:
            logger.error(f"Database connection error: {db_error}")
            raise

        # Run the migration
        logger.info("Running Alembic migrations...")
        alembic.command.upgrade(alembic_cfg, "head")

        logger.info("Migration commands executed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

    execution_time = time.time() - start_time
    logger.info(f"Migration process completed in {execution_time:.2f} seconds")


def verify_migrations() -> None:
    """Verify that migrations were applied correctly by checking for required tables."""
    required_tables = [
        "courts",
        "court_counties",
        "ice_detention_facilities",
        "district_court_contacts",
        "normalized_addresses",
    ]

    logger.info("Verifying migrations...")

    # Create SQLAlchemy engine and inspector
    db_url = get_database_url()
    engine = sa.create_engine(db_url)
    inspector = inspect(engine)

    # Get list of tables in the database
    existing_tables = inspector.get_table_names()

    # Check for required tables
    missing_tables = [table for table in required_tables if table not in existing_tables]

    if missing_tables:
        logger.error(f"Migration verification failed. Missing tables: {', '.join(missing_tables)}")
        sys.exit(1)

    # Check Alembic version
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = result.fetchall()
        if not versions:
            logger.error("No Alembic versions found in the database!")
            sys.exit(1)

        logger.info(f"Current Alembic version: {versions[0][0]}")

    logger.info("Migration verification successful. All required tables exist.")


if __name__ == "__main__":
    run_migrations()
    verify_migrations()
