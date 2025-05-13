"""Add court_counties table

Revision ID: add_court_counties_table
Revises: 24c60b83757d
Create Date: 2025-05-11 04:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_court_counties_table"
down_revision: Union[str, None] = "24c60b83757d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the court_counties table
    op.create_table(
        "court_counties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("county_name", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("court_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["court_id"],
            ["courts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_court_counties_county_name"), "court_counties", ["county_name"], unique=False)
    op.create_index(op.f("ix_court_counties_court_id"), "court_counties", ["court_id"], unique=False)
    op.create_index(op.f("ix_court_counties_id"), "court_counties", ["id"], unique=False)
    op.create_index(op.f("ix_court_counties_state"), "court_counties", ["state"], unique=False)


def downgrade() -> None:
    # Drop the court_counties table
    op.drop_index(op.f("ix_court_counties_state"), table_name="court_counties")
    op.drop_index(op.f("ix_court_counties_id"), table_name="court_counties")
    op.drop_index(op.f("ix_court_counties_court_id"), table_name="court_counties")
    op.drop_index(op.f("ix_court_counties_county_name"), table_name="court_counties")
    op.drop_table("court_counties")
