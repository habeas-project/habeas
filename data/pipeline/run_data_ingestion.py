#!/usr/bin/env python3
import logging
import os
import subprocess  # nosec B404
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


# Configure logging to both file and console
def setup_logging():
    """Set up logging to both file and console with timestamped log files."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent.parent / "temp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"data_ingestion_{timestamp}.log"

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


def run_script(script_path, env_vars=None):
    """Run a Python script and return the exit code, optionally with temporary environment variables."""
    start_time = time.time()
    logger.info(f"Running script: {script_path} with env_vars: {env_vars}")

    # Get current environment and update with any temporary ones for this run
    current_env = os.environ.copy()
    if env_vars:
        current_env.update(env_vars)

    # Use subprocess.run with the modified environment
    result = subprocess.run(
        [sys.executable, str(script_path)], check=False, env=current_env
    )  # nosec B603
    execution_time = time.time() - start_time

    if result.returncode != 0:
        logger.error(f"Script {script_path} failed with exit code {result.returncode}")
    else:
        logger.info(
            f"Script {script_path} completed successfully in {execution_time:.2f} seconds"
        )

    return result.returncode


def verify_required_tables(verification_script, mode="full_check"):
    """Run verification script to ensure required tables exist before import."""
    logger.info(f"Verifying database with mode: {mode}...")
    # Set VERIFICATION_MODE environment variable for the script's execution context
    result = run_script(verification_script, env_vars={"VERIFICATION_MODE": mode})
    if result != 0:
        logger.error(
            f"Database verification (mode: {mode}) failed. Required tables may be missing or empty."
        )
        if mode == "schema_only":
            logger.error("Ensure migrations have run properly and created the schema.")
        return False
    logger.info(f"Database verification (mode: {mode}) successful.")
    return True


def check_geocoded_data_exists():
    """Check if geocoded CSV file exists, if not run geocoding script."""
    base_dir = Path(__file__).resolve().parent
    static_assets_dir = base_dir.parent / "static_assets"
    geocoded_file = static_assets_dir / "2025_ice_detention_facilities_geocoded.csv"

    if geocoded_file.exists():
        logger.info(f"Geocoded CSV file found: {geocoded_file}")
        return True
    else:
        logger.info(f"Geocoded CSV file not found: {geocoded_file}")
        logger.info("Running geocoding script to create geocoded data...")

        # Run the geocoding script
        ingestion_dir = base_dir / "3_ingestion_scripts"
        geocoding_script = ingestion_dir / "geocode_csv_facilities.py"

        if not geocoding_script.exists():
            logger.error(f"Geocoding script not found: {geocoding_script}")
            return False

        exit_code = run_script(geocoding_script)
        if exit_code != 0:
            logger.error("Geocoding script failed")
            return False

        # Check if the file was created
        if geocoded_file.exists():
            logger.info("Geocoding completed successfully")
            return True
        else:
            logger.error("Geocoding script completed but geocoded file was not created")
            return False


def main():
    # Get the directory this script is in
    base_dir = Path(__file__).resolve().parent
    ingestion_dir = base_dir / "3_ingestion_scripts"
    verification_dir = base_dir / "4_verification"

    # Define verification script
    verification_script = verification_dir / "verify_migration.py"

    # Define ingestion scripts in phases
    # Phase 1: Basic data loading (no API calls)
    basic_data_scripts = [
        ingestion_dir / "import_court_data.py",
        ingestion_dir
        / "import_ice_facilities_csv.py",  # Updated to use CSV-based import
    ]

    # Phase 2: API-dependent operations (geocoding, etc.) - now handled automatically
    # The geocoding is now done as a prerequisite step before CSV import

    # Check that all basic scripts exist
    for script in basic_data_scripts + [verification_script]:
        if not script.exists():
            logger.error(f"Script not found: {script}")
            sys.exit(1)

    # First verify the database is properly set up with required tables (schema only)
    if not verify_required_tables(verification_script, mode="schema_only"):
        sys.exit(1)

    # Check and create geocoded data if needed
    logger.info("=== GEOCODING PREPARATION ===")
    if not check_geocoded_data_exists():
        logger.error("Failed to ensure geocoded data is available")
        sys.exit(1)

    # Phase 1: Run basic data ingestion scripts (using pre-geocoded CSV data)
    logger.info("=== PHASE 1: Data Loading (Using Pre-geocoded CSV) ===")
    basic_success = True
    for script in basic_data_scripts:
        exit_code = run_script(script)
        if exit_code != 0:
            basic_success = False
            logger.error(
                f"Data script {script.name} failed. Continuing with remaining scripts."
            )

    # Verify data was loaded correctly
    logger.info("Verifying data after Phase 1...")
    basic_verification_exit_code = run_script(
        verification_script, env_vars={"VERIFICATION_MODE": "basic_data"}
    )

    if not basic_success or basic_verification_exit_code != 0:
        logger.error("Phase 1 (Data Loading) completed with errors.")
        sys.exit(1)

    logger.info("Phase 1 (Data Loading) completed successfully.")

    # Final verification
    logger.info("Running final verification...")
    final_verification_exit_code = run_script(verification_script)

    # Return overall status
    if final_verification_exit_code != 0:
        logger.warning("Final verification completed with errors.")
        logger.info("Data ingestion process completed with partial success.")
        sys.exit(0)
    else:
        logger.info("Data ingestion process completed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
