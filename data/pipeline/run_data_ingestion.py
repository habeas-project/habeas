#!/usr/bin/env python3
import logging
import subprocess  # nosec B404
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def run_script(script_path):
    """Run a Python script and return the exit code."""
    start_time = time.time()
    logger.info(f"Running script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], check=False)  # nosec B603
    execution_time = time.time() - start_time

    if result.returncode != 0:
        logger.error(f"Script {script_path} failed with exit code {result.returncode}")
    else:
        logger.info(
            f"Script {script_path} completed successfully in {execution_time:.2f} seconds"
        )

    return result.returncode


def verify_required_tables(verification_script):
    """Run verification script to ensure required tables exist before import."""
    logger.info("Verifying required database tables before import...")
    result = run_script(verification_script)
    if result != 0:
        logger.error("Database verification failed. Required tables may be missing.")
        logger.error("Ensure migrations have been run properly before data ingestion.")
        return False
    logger.info("Database verification successful. Required tables exist.")
    return True


def main():
    # Get the directory this script is in
    base_dir = Path(__file__).resolve().parent
    ingestion_dir = base_dir / "3_ingestion_scripts"
    verification_dir = base_dir / "4_verification"

    # Define verification script
    verification_script = verification_dir / "verify_migration.py"

    # Define ingestion scripts in the order they should run
    ingestion_scripts = [
        ingestion_dir / "import_court_data.py",
        ingestion_dir / "import_ice_facilities.py",
    ]

    # Check that all scripts exist
    for script in ingestion_scripts + [verification_script]:
        if not script.exists():
            logger.error(f"Script not found: {script}")
            sys.exit(1)

    # First verify the database is properly set up with required tables
    if not verify_required_tables(verification_script):
        sys.exit(1)

    # Run ingestion scripts in sequence
    success = True
    logger.info("Starting data ingestion process...")
    for script in ingestion_scripts:
        exit_code = run_script(script)
        if exit_code != 0:
            success = False
            logger.error(
                f"Ingestion script {script.name} failed. Continuing with remaining scripts."
            )

    # Run verification script again to validate the data was imported correctly
    logger.info("Verifying data after import...")
    verification_exit_code = run_script(verification_script)

    # Return overall status
    if not success or verification_exit_code != 0:
        logger.error("Data ingestion process completed with errors.")
        sys.exit(1)
    else:
        logger.info("Data ingestion process completed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
