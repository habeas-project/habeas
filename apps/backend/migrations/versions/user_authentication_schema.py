"""user authentication schema

Revision ID: user_authentication_schema
Revises: initial_schema
Create Date: 2025-04-25 01:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "user_authentication_schema"
down_revision: Union[str, None] = "initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

    # Add user_id column to attorneys table
    op.add_column("attorneys", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_attorneys_user_id", "attorneys", "users", ["user_id"], ["id"], ondelete="SET NULL")
    op.create_index(op.f("ix_attorneys_user_id"), "attorneys", ["user_id"], unique=True)

    # Add user_id column to clients table
    op.add_column("clients", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_clients_user_id", "clients", "users", ["user_id"], ["id"], ondelete="SET NULL")
    op.create_index(op.f("ix_clients_user_id"), "clients", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop user_id from clients
    op.drop_index(op.f("ix_clients_user_id"), table_name="clients")
    op.drop_constraint("fk_clients_user_id", "clients", type_="foreignkey")
    op.drop_column("clients", "user_id")

    # Drop user_id from attorneys
    op.drop_index(op.f("ix_attorneys_user_id"), table_name="attorneys")
    op.drop_constraint("fk_attorneys_user_id", "attorneys", type_="foreignkey")
    op.drop_column("attorneys", "user_id")

    # Drop users table
    op.drop_index(op.f("ix_users_user_type"), table_name="users")
    op.drop_index(op.f("ix_users_cognito_id"), table_name="users")
    op.drop_table("users")
