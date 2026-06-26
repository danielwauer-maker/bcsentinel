"""add dashboard users

Revision ID: 0021_dashboard_users
Revises: 0020_tenant_contact_email
Create Date: 2026-06-26 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0021_dashboard_users"
down_revision = "0020_tenant_contact_email"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dashboard_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("invite_token_hash", sa.String(length=255), nullable=True),
        sa.Column("invite_expires_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("must_change_password", sa.Boolean(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_invited_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invite_mail_status", sa.String(length=20), nullable=False),
        sa.Column("invite_mail_error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_dashboard_users_tenant_email"),
    )
    op.create_index(op.f("ix_dashboard_users_id"), "dashboard_users", ["id"], unique=False)
    op.create_index(op.f("ix_dashboard_users_tenant_id"), "dashboard_users", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_dashboard_users_email"), "dashboard_users", ["email"], unique=False)
    op.create_index(op.f("ix_dashboard_users_status"), "dashboard_users", ["status"], unique=False)
    op.create_index(op.f("ix_dashboard_users_created_at_utc"), "dashboard_users", ["created_at_utc"], unique=False)
    op.create_index(op.f("ix_dashboard_users_last_invited_at_utc"), "dashboard_users", ["last_invited_at_utc"], unique=False)
    op.create_index(op.f("ix_dashboard_users_invite_mail_status"), "dashboard_users", ["invite_mail_status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dashboard_users_invite_mail_status"), table_name="dashboard_users")
    op.drop_index(op.f("ix_dashboard_users_last_invited_at_utc"), table_name="dashboard_users")
    op.drop_index(op.f("ix_dashboard_users_created_at_utc"), table_name="dashboard_users")
    op.drop_index(op.f("ix_dashboard_users_status"), table_name="dashboard_users")
    op.drop_index(op.f("ix_dashboard_users_email"), table_name="dashboard_users")
    op.drop_index(op.f("ix_dashboard_users_tenant_id"), table_name="dashboard_users")
    op.drop_index(op.f("ix_dashboard_users_id"), table_name="dashboard_users")
    op.drop_table("dashboard_users")
