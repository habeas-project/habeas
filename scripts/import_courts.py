import logging
import sys
from pathlib import Path
from typing import List

import pandas as pd

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "apps" / "backend"))

from app.database import SessionLocal
from app.models.court import Court

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def import_courts(csv_path: str) -> List[Court]:
    """Import courts from CSV file."""
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} courts from {csv_path}")

        # Create database session
        db = SessionLocal()

        # Import each court
        imported_courts = []
        for _, row in df.iterrows():
            try:
                court = Court(
                    name=row["court"], abbreviation=row["abbreviation"], url=row["url"]
                )
                db.add(court)
                imported_courts.append(court)
                logger.info(f"Added court: {court.name} ({court.abbreviation})")
            except Exception as e:
                logger.error(f"Error importing court {row['court']}: {str(e)}")

        # Commit changes
        db.commit()
        logger.info(f"Successfully imported {len(imported_courts)} courts")
        return imported_courts

    except Exception as e:
        logger.error(f"Error importing courts: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    csv_path = Path(__file__).parent / "output" / "district_courts.csv"
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)

    try:
        import_courts(str(csv_path))
    except Exception as e:
        logger.error(f"Failed to import courts: {str(e)}")
        sys.exit(1)
