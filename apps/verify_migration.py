#!/usr/bin/env python3
import os

import sqlalchemy as sa
from sqlalchemy import inspect, text

# Get the database URL from environment variables
database_url = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/habeas"
)

# Create engine
engine = sa.create_engine(database_url)
inspector = inspect(engine)

print("Database inspection results:")
print("-" * 50)

# Check tables
tables = inspector.get_table_names()
print(f"Tables in database ({len(tables)}):")
for table in tables:
    print(f"- {table}")
print()

# Check alembic version
with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    versions = result.fetchall()
    print(f"Alembic versions ({len(versions)}):")
    for version in versions:
        print(f"- {version[0]}")
print()

# Check specific tables for our schema
expected_tables = [
    "attorneys",
    "clients",
    "emergency_contacts",
    "courts",
    "attorney_court_admissions",
]

print("Migration verification:")
all_expected_present = True
for table in expected_tables:
    if table in tables:
        print(f"✓ Table '{table}' exists")
    else:
        print(f"✗ Table '{table}' is missing!")
        all_expected_present = False

print()
print(f"Migration status: {'SUCCESS' if all_expected_present else 'FAILED'}")
