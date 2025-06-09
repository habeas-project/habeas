"""create_ice_detention_facilities_table

Revision ID: 06caa82208d2
Revises: c2a8e3f9b1d0
Create Date: 2025-05-08 20:55:45.875106

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sqlalchemy import inspect
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "06caa82208d2"
down_revision: Union[str, None] = "c2a8e3f9b1d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name):
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    return table_name in tables


def upgrade() -> None:
    # Only create the table if it doesn't exist yet
    if not table_exists("ice_detention_facilities"):
        # Create ice_detention_facilities table
        op.create_table(
            "ice_detention_facilities",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(255), nullable=False, index=True),
            sa.Column("address", sa.String(), nullable=True),
            sa.Column("city", sa.String(100), nullable=True),
            sa.Column("state", sa.String(2), nullable=True),
            sa.Column("zip_code", sa.String(20), nullable=True),
            sa.Column("aor", sa.String(255), nullable=True),
            sa.Column("facility_type_detailed", sa.String(255), nullable=True),
            sa.Column("gender_capacity", sa.String(50), nullable=True),
            sa.Column("normalized_address_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

        # Create indexes only if the table was created
        op.create_index("ix_ice_detention_facilities_name", "ice_detention_facilities", ["name"], unique=False)
        op.create_index(
            "ix_ice_detention_facilities_normalized_address_id",
            "ice_detention_facilities",
            ["normalized_address_id"],
            unique=True,
        )

    # If the table already exists but normalized_address_id index is missing, add it
    bind = op.get_bind()
    inspector = inspect(bind)
    if table_exists("ice_detention_facilities"):
        indexes = [idx["name"] for idx in inspector.get_indexes("ice_detention_facilities")]
        if "ix_ice_detention_facilities_normalized_address_id" not in indexes:
            op.create_index(
                "ix_ice_detention_facilities_normalized_address_id",
                "ice_detention_facilities",
                ["normalized_address_id"],
                unique=True,
            )


def downgrade() -> None:
    # Only attempt to drop if the table exists
    if table_exists("ice_detention_facilities"):
        # First drop indexes if they exist
        bind = op.get_bind()
        inspector = inspect(bind)
        indexes = [idx["name"] for idx in inspector.get_indexes("ice_detention_facilities")]

        if "ix_ice_detention_facilities_normalized_address_id" in indexes:
            op.drop_index("ix_ice_detention_facilities_normalized_address_id", table_name="ice_detention_facilities")

        if "ix_ice_detention_facilities_name" in indexes:
            op.drop_index("ix_ice_detention_facilities_name", table_name="ice_detention_facilities")

        # Removed redundant check and drop operation for ix_ice_detention_facilities_id

        # Now drop the table
        op.drop_table("ice_detention_facilities")
