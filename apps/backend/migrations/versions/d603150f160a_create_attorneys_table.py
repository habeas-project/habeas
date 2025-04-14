"""Create attorneys table

Revision ID: d603150f160a
Revises:
Create Date: 2023-04-10 21:24:20.244551

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "d603150f160a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create attorneys table
    op.create_table(
        "attorneys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("zip_code", sa.String(10), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    # Create index for email and zip_code for faster lookups
    op.create_index(op.f("ix_attorneys_email"), "attorneys", ["email"], unique=True)
    op.create_index(op.f("ix_attorneys_zip_code"), "attorneys", ["zip_code"], unique=False)
    op.create_index(op.f("ix_attorneys_state"), "attorneys", ["state"], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f("ix_attorneys_state"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_zip_code"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_email"), table_name="attorneys")
    # Drop the attorneys table
    op.drop_table("attorneys")
