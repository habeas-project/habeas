"""refactor_models_and_update_relationships

Revision ID: a1b2c3d4e5f6
Revises: d3a7f8c9b2e1
Create Date: 2025-05-08 15:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "d3a7f8c9b2e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands for IceDetentionFacility ###
    # Add normalized_address_id column
    op.add_column("ice_detention_facilities", sa.Column("normalized_address_id", sa.Integer(), nullable=True))
    # Create index for normalized_address_id (unique as per model)
    op.create_index(
        "ix_ice_detention_facilities_normalized_address_id",
        "ice_detention_facilities",
        ["normalized_address_id"],
        unique=True,
    )
    # Create foreign key from ice_detention_facilities.normalized_address_id to normalized_addresses.id
    op.create_foreign_key(
        "fk_ice_detention_facilities_normalized_address_id_normalized_addresses",  # Constraint name
        "ice_detention_facilities",  # Source table
        "normalized_addresses",  # Remote table
        ["normalized_address_id"],  # Local columns
        ["id"],  # Remote columns
    )

    # ### commands for NormalizedAddress ###
    # Drop foreign key constraint on normalized_addresses.ice_detention_facility_id
    # Assuming the constraint was named conventionally. If not, this name might need adjustment.
    op.drop_constraint(
        "fk_normalized_addresses_ice_detention_facility_id_ice_detention_facilities",
        "normalized_addresses",
        type_="foreignkey",
    )
    # Drop index for ice_detention_facility_id
    op.drop_index("ix_normalized_addresses_ice_detention_facility_id", table_name="normalized_addresses")
    # Drop the ice_detention_facility_id column
    op.drop_column("normalized_addresses", "ice_detention_facility_id")


def downgrade() -> None:
    # ### commands for NormalizedAddress (reverse of upgrade) ###
    # Add ice_detention_facility_id column back (was nullable=False, unique=True, index=True)
    op.add_column(
        "normalized_addresses",
        sa.Column("ice_detention_facility_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    # Recreate index for ice_detention_facility_id (unique)
    op.create_index(
        "ix_normalized_addresses_ice_detention_facility_id",
        "normalized_addresses",
        ["ice_detention_facility_id"],
        unique=True,
    )
    # Recreate foreign key from normalized_addresses.ice_detention_facility_id to ice_detention_facilities.id
    op.create_foreign_key(
        "fk_normalized_addresses_ice_detention_facility_id_ice_detention_facilities",
        "normalized_addresses",
        "ice_detention_facilities",
        ["ice_detention_facility_id"],
        ["id"],
    )

    # ### commands for IceDetentionFacility (reverse of upgrade) ###
    # Drop foreign key constraint on ice_detention_facilities.normalized_address_id
    op.drop_constraint(
        "fk_ice_detention_facilities_normalized_address_id_normalized_addresses",
        "ice_detention_facilities",
        type_="foreignkey",
    )
    # Drop index for normalized_address_id
    op.drop_index("ix_ice_detention_facilities_normalized_address_id", table_name="ice_detention_facilities")
    # Drop the normalized_address_id column
    op.drop_column("ice_detention_facilities", "normalized_address_id")
