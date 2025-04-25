"""merge_heads

Revision ID: de9828777a67
Revises: ab12cd34ef56, initial_schema
Create Date: 2025-04-25 01:31:53.458122

"""

from typing import Sequence, Tuple, Union

# revision identifiers, used by Alembic.
revision: str = "de9828777a67"
down_revision: Tuple[str, str] = ("ab12cd34ef56", "initial_schema")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
