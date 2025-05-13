"""initial schema

Revision ID: initial_schema
Revises:
Create Date: 2025-04-25 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "initial_schema"
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
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("zip_code", sa.String(10), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_attorneys_email"), "attorneys", ["email"], unique=True)
    op.create_index(op.f("ix_attorneys_zip_code"), "attorneys", ["zip_code"], unique=False)
    op.create_index(op.f("ix_attorneys_state"), "attorneys", ["state"], unique=False)

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
    op.create_index(op.f("ix_emergency_contacts_client_id"), "emergency_contacts", ["client_id"], unique=False)
    op.create_index(op.f("ix_emergency_contacts_phone_number"), "emergency_contacts", ["phone_number"], unique=False)
    op.create_index(op.f("ix_emergency_contacts_email"), "emergency_contacts", ["email"], unique=False)

    # Create courts table
    op.create_table(
        "courts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("abbreviation", sa.String(10), nullable=False),
        sa.Column("url", sa.String(255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("abbreviation"),
    )
    op.create_index(op.f("ix_courts_id"), "courts", ["id"], unique=False)
    op.create_index(op.f("ix_courts_name"), "courts", ["name"], unique=False)
    op.create_index(op.f("ix_courts_abbreviation"), "courts", ["abbreviation"], unique=True)

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
    op.create_index(
        op.f("ix_attorney_court_admissions_attorney_id"), "attorney_court_admissions", ["attorney_id"], unique=False
    )
    op.create_index(
        op.f("ix_attorney_court_admissions_court_id"), "attorney_court_admissions", ["court_id"], unique=False
    )


def downgrade() -> None:
    # Drop all tables in reverse order of creation to respect foreign key constraints

    # Drop attorney_court_admissions table and indexes
    op.drop_index(op.f("ix_attorney_court_admissions_court_id"), table_name="attorney_court_admissions")
    op.drop_index(op.f("ix_attorney_court_admissions_attorney_id"), table_name="attorney_court_admissions")
    op.drop_table("attorney_court_admissions")

    # Drop courts table and indexes
    op.drop_index(op.f("ix_courts_abbreviation"), table_name="courts")
    op.drop_index(op.f("ix_courts_name"), table_name="courts")
    op.drop_index(op.f("ix_courts_id"), table_name="courts")
    op.drop_table("courts")

    # Drop emergency_contacts table and indexes
    op.drop_index(op.f("ix_emergency_contacts_email"), table_name="emergency_contacts")
    op.drop_index(op.f("ix_emergency_contacts_phone_number"), table_name="emergency_contacts")
    op.drop_index(op.f("ix_emergency_contacts_client_id"), table_name="emergency_contacts")
    op.drop_table("emergency_contacts")

    # Drop clients table and indexes
    op.drop_index(op.f("ix_clients_student_id_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_passport_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_alien_registration_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_country_of_birth"), table_name="clients")
    op.drop_index(op.f("ix_clients_last_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_first_name"), table_name="clients")
    op.drop_table("clients")

    # Drop attorneys table and indexes
    op.drop_index(op.f("ix_attorneys_state"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_zip_code"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_email"), table_name="attorneys")
    op.drop_table("attorneys")
