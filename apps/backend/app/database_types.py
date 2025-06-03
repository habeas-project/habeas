"""
Database type compatibility utilities.

This module provides database-agnostic type definitions that work with both
PostgreSQL (production) and SQLite (testing).
"""

from typing import Type, Union

from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine


class JSONType(TypeDecorator):
    """A database-agnostic JSON type.

    Uses JSONB for PostgreSQL and JSON for other databases (like SQLite).
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


def get_json_type(engine: Union[Engine, None] = None) -> Type:
    """Get the appropriate JSON type for the given engine/dialect.

    Args:
        engine: SQLAlchemy engine (optional)

    Returns:
        JSONB for PostgreSQL, JSON for others
    """
    if engine and engine.dialect.name == "postgresql":
        return JSONB
    return JSON
