"""update_ice_facility_model_fields

Revision ID: c9f8d1e2a5b4
Revises: b5586fc66823
Create Date: 2025-05-29 07:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9f8d1e2a5b4"
down_revision: Union[str, None] = "b5586fc66823"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename address column to original_address
    op.alter_column(
        "ice_detention_facilities",
        "address",
        new_column_name="original_address",
        existing_type=sa.String(),
        existing_nullable=True,
    )

    # Rename facility_type_detailed to facility_type
    op.alter_column(
        "ice_detention_facilities",
        "facility_type_detailed",
        new_column_name="facility_type",
        existing_type=sa.String(length=255),
        existing_nullable=True,
    )

    # Add new columns for capacity and inspection data
    op.add_column("ice_detention_facilities", sa.Column("mandatory", sa.Integer(), nullable=True))
    op.add_column("ice_detention_facilities", sa.Column("guaranteed_minimum", sa.Integer(), nullable=True))
    op.add_column("ice_detention_facilities", sa.Column("last_inspection_type", sa.String(length=255), nullable=True))
    op.add_column(
        "ice_detention_facilities", sa.Column("last_inspection_end_date", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "ice_detention_facilities", sa.Column("pending_fy25_inspection", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "ice_detention_facilities", sa.Column("last_inspection_standard", sa.String(length=255), nullable=True)
    )
    op.add_column("ice_detention_facilities", sa.Column("last_final_rating", sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove added columns
    op.drop_column("ice_detention_facilities", "last_final_rating")
    op.drop_column("ice_detention_facilities", "last_inspection_standard")
    op.drop_column("ice_detention_facilities", "pending_fy25_inspection")
    op.drop_column("ice_detention_facilities", "last_inspection_end_date")
    op.drop_column("ice_detention_facilities", "last_inspection_type")
    op.drop_column("ice_detention_facilities", "guaranteed_minimum")
    op.drop_column("ice_detention_facilities", "mandatory")

    # Rename columns back
    op.alter_column(
        "ice_detention_facilities",
        "facility_type",
        new_column_name="facility_type_detailed",
        existing_type=sa.String(length=255),
        existing_nullable=True,
    )

    op.alter_column(
        "ice_detention_facilities",
        "original_address",
        new_column_name="address",
        existing_type=sa.String(),
        existing_nullable=True,
    )
