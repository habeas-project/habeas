"""add_emergency_case_models

Revision ID: emergency_case_001
Revises: c9f8d1e2a5b4
Create Date: 2025-01-09 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "emergency_case_001"
down_revision: Union[str, None] = "c9f8d1e2a5b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create emergency_cases table
    op.create_table(
        "emergency_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("client_profile_id", sa.Integer(), nullable=False),
        sa.Column(
            "case_type", sa.String(length=20), nullable=False, comment="Type of emergency: 'self' or 'loved_one'"
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            comment="Status: active, attorney_assigned, resolved, deactivated",
        ),
        sa.Column("detention_latitude", sa.Float(), nullable=True),
        sa.Column("detention_longitude", sa.Float(), nullable=True),
        sa.Column("detention_address", sa.String(length=500), nullable=True),
        sa.Column(
            "location_description", sa.Text(), nullable=True, comment="Additional location details provided by user"
        ),
        sa.Column("assigned_court_id", sa.Integer(), nullable=True),
        sa.Column("assigned_attorney_id", sa.Integer(), nullable=True),
        sa.Column("attorney_assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("initial_notification_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalated_notification_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_attorney_id"],
            ["attorneys.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assigned_court_id"],
            ["courts.id"],
        ),
        sa.ForeignKeyConstraint(["client_profile_id"], ["client_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_emergency_cases_assigned_court_id"), "emergency_cases", ["assigned_court_id"], unique=False
    )
    op.create_index(op.f("ix_emergency_cases_case_type"), "emergency_cases", ["case_type"], unique=False)
    op.create_index(
        op.f("ix_emergency_cases_client_profile_id"), "emergency_cases", ["client_profile_id"], unique=False
    )
    op.create_index(op.f("ix_emergency_cases_id"), "emergency_cases", ["id"], unique=False)
    op.create_index(op.f("ix_emergency_cases_status"), "emergency_cases", ["status"], unique=False)
    op.create_index(op.f("ix_emergency_cases_user_id"), "emergency_cases", ["user_id"], unique=False)

    # Create attorney_notification_preferences table
    op.create_table(
        "attorney_notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attorney_id", sa.Integer(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("sms_enabled", sa.Boolean(), nullable=False),
        sa.Column("push_enabled", sa.Boolean(), nullable=False),
        sa.Column("sms_phone_number", sa.String(length=20), nullable=True),
        sa.Column("daily_digest_enabled", sa.Boolean(), nullable=False),
        sa.Column("escalated_notifications_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["attorney_id"], ["attorneys.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_attorney_notification_preferences_attorney_id"),
        "attorney_notification_preferences",
        ["attorney_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attorney_notification_preferences_id"), "attorney_notification_preferences", ["id"], unique=False
    )

    # Set default values for status and preferences
    op.execute("ALTER TABLE emergency_cases ALTER COLUMN status SET DEFAULT 'active'")
    op.execute("ALTER TABLE attorney_notification_preferences ALTER COLUMN email_enabled SET DEFAULT true")
    op.execute("ALTER TABLE attorney_notification_preferences ALTER COLUMN sms_enabled SET DEFAULT true")
    op.execute("ALTER TABLE attorney_notification_preferences ALTER COLUMN push_enabled SET DEFAULT true")
    op.execute("ALTER TABLE attorney_notification_preferences ALTER COLUMN daily_digest_enabled SET DEFAULT true")
    op.execute(
        "ALTER TABLE attorney_notification_preferences ALTER COLUMN escalated_notifications_enabled SET DEFAULT true"
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f("ix_attorney_notification_preferences_id"), table_name="attorney_notification_preferences")
    op.drop_index(
        op.f("ix_attorney_notification_preferences_attorney_id"), table_name="attorney_notification_preferences"
    )
    op.drop_table("attorney_notification_preferences")

    op.drop_index(op.f("ix_emergency_cases_user_id"), table_name="emergency_cases")
    op.drop_index(op.f("ix_emergency_cases_status"), table_name="emergency_cases")
    op.drop_index(op.f("ix_emergency_cases_id"), table_name="emergency_cases")
    op.drop_index(op.f("ix_emergency_cases_client_profile_id"), table_name="emergency_cases")
    op.drop_index(op.f("ix_emergency_cases_case_type"), table_name="emergency_cases")
    op.drop_index(op.f("ix_emergency_cases_assigned_court_id"), table_name="emergency_cases")
    op.drop_table("emergency_cases")
