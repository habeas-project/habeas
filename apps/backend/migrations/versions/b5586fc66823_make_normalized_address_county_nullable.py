"""make_normalized_address_county_nullable

Revision ID: b5586fc66823
Revises: fix_location_name_length
Create Date: 2025-05-28 23:30:24.328189

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5586fc66823"
down_revision: Union[str, None] = "fix_location_name_length"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make the county field nullable in normalized_addresses table
    # This allows for cases where geocoding fails or doesn't return county information
    op.alter_column(
        "normalized_addresses",
        "county",
        existing_type=sa.String(length=100),
        nullable=True,
        existing_comment="County name returned by the geocoding API",
    )


def downgrade() -> None:
    # Revert the county field back to non-nullable
    # Note: This might fail if there are NULL values in the county field
    op.alter_column(
        "normalized_addresses",
        "county",
        existing_type=sa.String(length=100),
        nullable=False,
        existing_comment="County name returned by the geocoding API",
    )
