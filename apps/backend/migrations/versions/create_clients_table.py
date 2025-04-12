"""Create clients table

Revision ID: create_clients_table
Revises: d603150f160a
Create Date: 2024-04-11 18:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "create_clients_table"
down_revision: Union[str, None] = "d603150f160a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("country_of_birth", sa.String(100), nullable=False),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("alien_registration_number", sa.String(20), nullable=True),
        sa.Column("passport_number", sa.String(20), nullable=True),
        sa.Column("school_name", sa.String(255), nullable=True),
        sa.Column("student_id_number", sa.String(50), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for common search fields
    op.create_index(op.f("ix_clients_first_name"), "clients", ["first_name"], unique=False)
    op.create_index(op.f("ix_clients_last_name"), "clients", ["last_name"], unique=False)
    op.create_index(op.f("ix_clients_country_of_birth"), "clients", ["country_of_birth"], unique=False)
    op.create_index(op.f("ix_clients_alien_registration_number"), "clients", ["alien_registration_number"], unique=True)
    op.create_index(op.f("ix_clients_passport_number"), "clients", ["passport_number"], unique=True)
    op.create_index(op.f("ix_clients_student_id_number"), "clients", ["student_id_number"], unique=True)

    # Create emergency_contacts table
    op.create_table(
        "emergency_contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("relationship", sa.String(50), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
    )

    # Create indexes for emergency contacts
    op.create_index(op.f("ix_emergency_contacts_client_id"), "emergency_contacts", ["client_id"], unique=False)
    op.create_index(op.f("ix_emergency_contacts_phone_number"), "emergency_contacts", ["phone_number"], unique=False)
    op.create_index(op.f("ix_emergency_contacts_email"), "emergency_contacts", ["email"], unique=False)


def downgrade() -> None:
    # Drop emergency_contacts table and its indexes
    op.drop_index(op.f("ix_emergency_contacts_email"), table_name="emergency_contacts")
    op.drop_index(op.f("ix_emergency_contacts_phone_number"), table_name="emergency_contacts")
    op.drop_index(op.f("ix_emergency_contacts_client_id"), table_name="emergency_contacts")
    op.drop_table("emergency_contacts")

    # Drop clients table and its indexes
    op.drop_index(op.f("ix_clients_student_id_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_passport_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_alien_registration_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_country_of_birth"), table_name="clients")
    op.drop_index(op.f("ix_clients_last_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_first_name"), table_name="clients")
    op.drop_table("clients")
