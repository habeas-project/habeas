"""Add attorney_court_admissions table and relationships

Revision ID: ab12cd34ef56
Revises: # Update this with the ID of the most recent migration
Create Date: 2025-01-01

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ab12cd34ef56"
down_revision: Union[str, None] = None  # Update this with the ID of the most recent migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create attorney_court_admissions table
    op.create_table(
        "attorney_court_admissions",
        sa.Column("attorney_id", sa.Integer(), nullable=False),
        sa.Column("court_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["attorney_id"],
            ["attorneys.id"],
        ),
        sa.ForeignKeyConstraint(
            ["court_id"],
            ["courts.id"],
        ),
        sa.PrimaryKeyConstraint("attorney_id", "court_id"),
    )
    # Optional: Add indexes if needed
    op.create_index(
        op.f("ix_attorney_court_admissions_attorney_id"), "attorney_court_admissions", ["attorney_id"], unique=False
    )
    op.create_index(
        op.f("ix_attorney_court_admissions_court_id"), "attorney_court_admissions", ["court_id"], unique=False
    )


def downgrade() -> None:
    # Drop indexes first (if created)
    op.drop_index(op.f("ix_attorney_court_admissions_court_id"), table_name="attorney_court_admissions")
    op.drop_index(op.f("ix_attorney_court_admissions_attorney_id"), table_name="attorney_court_admissions")
    # Drop the junction table
    op.drop_table("attorney_court_admissions")
