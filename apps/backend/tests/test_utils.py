"""
Test utility functions for database setup and other common test operations.
"""

from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.database import Base
from app.models.attorney import Attorney
from app.models.client import Client
from app.models.court import Court

# Import all models explicitly to ensure they are registered with Base.metadata
# This is essential for proper table creation
from app.models.user import User


def create_all_tables(engine: Engine) -> list[str]:
    """
    Explicitly create all tables needed for tests and verify they were created.

    Args:
        engine: SQLAlchemy engine to use for table creation

    Returns:
        List of table names that were created
    """
    # Create all tables registered in metadata
    Base.metadata.create_all(bind=engine)

    # Get list of created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # Print for debugging
    print(f"\nTables in test database: {tables}\n")

    # Verify critical tables exist
    required_tables = ["users", "attorneys", "courts", "attorney_court_admissions", "clients"]
    missing_tables = [table for table in required_tables if table not in tables]
    if missing_tables:
        print(f"WARNING: Missing required tables: {missing_tables}")

        # Attempt to create missing tables directly
        for missing in missing_tables:
            if missing == "users" and "User" in globals():
                print(f"Attempting to create missing table: {missing}")
                User.__table__.create(bind=engine, checkfirst=True)
            elif missing == "attorneys" and "Attorney" in globals():
                print(f"Attempting to create missing table: {missing}")
                Attorney.__table__.create(bind=engine, checkfirst=True)
            elif missing == "courts" and "Court" in globals():
                print(f"Attempting to create missing table: {missing}")
                Court.__table__.create(bind=engine, checkfirst=True)
            elif missing == "clients" and "Client" in globals():
                print(f"Attempting to create missing table: {missing}")
                Client.__table__.create(bind=engine, checkfirst=True)

        # Re-check tables
        tables = inspect(engine).get_table_names()
        print(f"Tables after manual creation: {tables}")

    return tables
