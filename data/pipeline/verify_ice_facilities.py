import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "apps" / "backend"))

# Load environment variables from .env file in the project root
# Assuming this script, when run in the container, has access to .env or the vars are already set.
dotenv_path = Path("/app") / ".env"  # Path inside container if .env is at /app/.env
if not dotenv_path.exists():
    # Fallback if .env is not where expected, or rely on pre-set env vars in container
    # For docker compose, env_file directive should handle this.
    pass
load_dotenv(
    dotenv_path=dotenv_path, override=True
)  # override is false by default. If true, it will override system env vars.


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print(
        "ERROR: DATABASE_URL environment variable not set. Ensure it is in the .env file loaded by Docker Compose or set in the service environment."
    )
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def verify_ice_facilities_table():
    db = SessionLocal()
    try:
        print("--- Verifying ice_detention_facilities table contents ---")
        result = db.execute(
            text(
                "SELECT id, name, address, city, state, zip_code, aor, facility_type_detailed, gender_capacity, normalized_address_id, court_id FROM ice_detention_facilities ORDER BY name LIMIT 20"
            )
        )
        rows = result.fetchall()
        if not rows:
            print("No data found in ice_detention_facilities table.")
            return

        print(f"Found {len(rows)} rows (showing up to 20):")
        for row in rows:
            print(f"  ID: {row.id}")
            print(f"    Name: {row.name}")
            print(f"    Address: {row.address}")
            print(f"    City: {row.city}")
            print(f"    State: {row.state}")
            print(f"    Zip Code: {row.zip_code}")
            print(f"    AOR: {row.aor}")
            print(f"    Type: {row.facility_type_detailed}")
            print(f"    Gender/Capacity: {row.gender_capacity}")
            print(f"    Normalized Address ID: {row.normalized_address_id}")
            print(f"    Court ID: {row.court_id}")
            print("    ----------")

        count_result = db.execute(
            text("SELECT COUNT(*) FROM ice_detention_facilities")
        ).scalar_one()
        print(f"Total rows in ice_detention_facilities: {count_result}")

    finally:
        db.close()


if __name__ == "__main__":
    # Adjust .env loading path for container execution if necessary
    # The `env_file` in docker-compose should make .env variables available directly.
    # If this script is run directly via `docker exec`, Python's os.getenv will pick them up.
    print(f"Attempting to load .env from: {dotenv_path}")
    print(f"Python path: {sys.path}")
    print(f"DATABASE_URL from env: {'********' if DATABASE_URL else 'Not found'}")
    verify_ice_facilities_table()
