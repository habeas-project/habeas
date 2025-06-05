"""fix location_name column length

Revision ID: fix_location_name_length
Revises: phone_length_fix
Create Date: 2025-05-28 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fix_location_name_length"
down_revision: Union[str, None] = "phone_length_fix"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter the location_name column to allow 255 characters
    op.alter_column(
        "district_court_contacts",
        "location_name",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Revert back to 50 characters (this may cause data loss if there are longer values)
    op.alter_column(
        "district_court_contacts",
        "location_name",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
