"""increase_district_contact_phone_length

Revision ID: phone_length_fix
Revises: add_court_counties_table
Create Date: 2025-05-29 06:58:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "phone_length_fix"
down_revision: Union[str, None] = "add_court_counties_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration was originally for phone length increase
    # but the actual change was already handled in the consolidated schema
    pass


def downgrade() -> None:
    pass
