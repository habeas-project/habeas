"""increase_district_contact_phone_length

Revision ID: phone_length_fix
Revises: add_court_counties_table
Create Date: 2025-05-29 06:58:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "phone_length_fix"
down_revision: Union[str, None] = "add_court_counties_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter the phone column to allow 255 characters
    op.alter_column(
        "district_court_contacts",
        "phone",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Revert back to 50 characters (this may cause data loss if there are longer values)
    op.alter_column(
        "district_court_contacts",
        "phone",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
