"""consolidated_schema

Revision ID: 24c60b83757d
Revises:
Create Date: 2025-05-08 21:17:30.024425

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "24c60b83757d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============= Base Tables =============

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cognito_id", sa.String(36), nullable=False, comment="User ID from AWS Cognito"),
        sa.Column("user_type", sa.String(20), nullable=False, comment="Type of user: client, attorney, friend, admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cognito_id"),
    )
    op.create_index(op.f("ix_users_cognito_id"), "users", ["cognito_id"], unique=True)
    op.create_index(op.f("ix_users_user_type"), "users", ["user_type"], unique=False)

    # Create attorneys table
    op.create_table(
        "attorneys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("zip_code", sa.String(10), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL", name="fk_attorneys_user_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_attorneys_email"), "attorneys", ["email"], unique=True)
    op.create_index(op.f("ix_attorneys_zip_code"), "attorneys", ["zip_code"], unique=False)
    op.create_index(op.f("ix_attorneys_state"), "attorneys", ["state"], unique=False)
    op.create_index(op.f("ix_attorneys_user_id"), "attorneys", ["user_id"], unique=True)

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
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL", name="fk_clients_user_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clients_first_name"), "clients", ["first_name"], unique=False)
    op.create_index(op.f("ix_clients_last_name"), "clients", ["last_name"], unique=False)
    op.create_index(op.f("ix_clients_country_of_birth"), "clients", ["country_of_birth"], unique=False)
    op.create_index(op.f("ix_clients_alien_registration_number"), "clients", ["alien_registration_number"], unique=True)
    op.create_index(op.f("ix_clients_passport_number"), "clients", ["passport_number"], unique=True)
    op.create_index(op.f("ix_clients_student_id_number"), "clients", ["student_id_number"], unique=True)
    op.create_index(op.f("ix_clients_user_id"), "clients", ["user_id"], unique=True)

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

    # Create district_court_contacts table
    op.create_table(
        "district_court_contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("court_id", sa.Integer(), nullable=False),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("hours", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["court_id"],
            ["courts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_district_court_contacts_court_id"), "district_court_contacts", ["court_id"], unique=False)
    op.create_index(op.f("ix_district_court_contacts_id"), "district_court_contacts", ["id"], unique=False)

    # Create ice_detention_facilities table
    op.create_table(
        "ice_detention_facilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip_code", sa.String(20), nullable=True),
        sa.Column("aor", sa.String(255), nullable=True),
        sa.Column("facility_type_detailed", sa.String(255), nullable=True),
        sa.Column("gender_capacity", sa.String(50), nullable=True),
        sa.Column("court_id", sa.Integer(), nullable=True),
        sa.Column("normalized_address_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.ForeignKeyConstraint(["court_id"], ["courts.id"], name="fk_ice_facilities_court_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ice_detention_facilities_id", "ice_detention_facilities", ["id"], unique=False)
    op.create_index("ix_ice_detention_facilities_name", "ice_detention_facilities", ["name"], unique=False)
    op.create_index(
        op.f("ix_ice_detention_facilities_court_id"), "ice_detention_facilities", ["court_id"], unique=False
    )

    # Create normalized_addresses table (final structure without ice_detention_facility_id)
    op.create_table(
        "normalized_addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "api_source",
            sa.String(length=100),
            nullable=False,
            comment="Source of the geocoding API used (e.g., Positionstack)",
        ),
        sa.Column(
            "original_address_query",
            sa.Text(),
            nullable=False,
            comment="The original, full address string used for the API query",
        ),
        sa.Column("normalized_street_address", sa.String(length=255), nullable=True),
        sa.Column("normalized_city", sa.String(length=100), nullable=True),
        sa.Column("normalized_state", sa.String(length=50), nullable=True),
        sa.Column("normalized_zip_code", sa.String(length=20), nullable=True),
        sa.Column("county", sa.String(length=100), nullable=False, comment="County name returned by the geocoding API"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column(
            "api_response_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Complete JSON response from the geocoding API for reference",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_normalized_addresses_id"), "normalized_addresses", ["id"], unique=False)

    # Create relationship between ice_detention_facilities and normalized_addresses
    op.create_index(
        "ix_ice_detention_facilities_normalized_address_id",
        "ice_detention_facilities",
        ["normalized_address_id"],
        unique=True,
    )
    op.create_foreign_key(
        "fk_ice_facilities_norm_addr_id",  # Using a shorter name that is under the 63-character limit
        "ice_detention_facilities",
        "normalized_addresses",
        ["normalized_address_id"],
        ["id"],
    )


def downgrade() -> None:
    # Drop foreign keys first
    op.drop_constraint(
        "fk_ice_facilities_norm_addr_id",
        "ice_detention_facilities",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ice_facilities_court_id",
        "ice_detention_facilities",
        type_="foreignkey",
    )

    # Drop indexes
    op.drop_index("ix_ice_detention_facilities_normalized_address_id", table_name="ice_detention_facilities")
    op.drop_index(op.f("ix_ice_detention_facilities_court_id"), table_name="ice_detention_facilities")
    op.drop_index("ix_ice_detention_facilities_name", table_name="ice_detention_facilities")
    op.drop_index("ix_ice_detention_facilities_id", table_name="ice_detention_facilities")
    op.drop_index(op.f("ix_normalized_addresses_id"), table_name="normalized_addresses")

    # Drop tables in reverse order
    op.drop_table("normalized_addresses")
    op.drop_table("ice_detention_facilities")
    op.drop_index(op.f("ix_district_court_contacts_id"), table_name="district_court_contacts")
    op.drop_index(op.f("ix_district_court_contacts_court_id"), table_name="district_court_contacts")
    op.drop_table("district_court_contacts")
    op.drop_index(op.f("ix_attorney_court_admissions_court_id"), table_name="attorney_court_admissions")
    op.drop_index(op.f("ix_attorney_court_admissions_attorney_id"), table_name="attorney_court_admissions")
    op.drop_table("attorney_court_admissions")
    op.drop_index(op.f("ix_courts_abbreviation"), table_name="courts")
    op.drop_index(op.f("ix_courts_name"), table_name="courts")
    op.drop_index(op.f("ix_courts_id"), table_name="courts")
    op.drop_table("courts")
    op.drop_index(op.f("ix_emergency_contacts_email"), table_name="emergency_contacts")
    op.drop_index(op.f("ix_emergency_contacts_phone_number"), table_name="emergency_contacts")
    op.drop_index(op.f("ix_emergency_contacts_client_id"), table_name="emergency_contacts")
    op.drop_table("emergency_contacts")
    op.drop_index(op.f("ix_clients_user_id"), table_name="clients")
    op.drop_index(op.f("ix_clients_student_id_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_passport_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_alien_registration_number"), table_name="clients")
    op.drop_index(op.f("ix_clients_country_of_birth"), table_name="clients")
    op.drop_index(op.f("ix_clients_last_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_first_name"), table_name="clients")
    op.drop_table("clients")
    op.drop_index(op.f("ix_attorneys_user_id"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_state"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_zip_code"), table_name="attorneys")
    op.drop_index(op.f("ix_attorneys_email"), table_name="attorneys")
    op.drop_table("attorneys")
    op.drop_index(op.f("ix_users_user_type"), table_name="users")
    op.drop_index(op.f("ix_users_cognito_id"), table_name="users")
    op.drop_table("users")
