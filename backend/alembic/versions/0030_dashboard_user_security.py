"""Harden dashboard user lifecycle for pilot onboarding.

Adds persistent login throttling and one-time password reset state.
"""
from alembic import op
import sqlalchemy as sa

revision = "0030_dashboard_user_security"
down_revision = "0029_finding_identity"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dashboard_users", sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("dashboard_users", sa.Column("locked_until_utc", sa.DateTime(timezone=True), nullable=True))
    op.add_column("dashboard_users", sa.Column("password_reset_token_hash", sa.String(length=255), nullable=True))
    op.add_column("dashboard_users", sa.Column("password_reset_expires_at_utc", sa.DateTime(timezone=True), nullable=True))
    op.add_column("dashboard_users", sa.Column("password_reset_requested_at_utc", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_dashboard_users_locked_until_utc", "dashboard_users", ["locked_until_utc"], unique=False)


def downgrade():
    op.drop_index("ix_dashboard_users_locked_until_utc", table_name="dashboard_users")
    op.drop_column("dashboard_users", "password_reset_requested_at_utc")
    op.drop_column("dashboard_users", "password_reset_expires_at_utc")
    op.drop_column("dashboard_users", "password_reset_token_hash")
    op.drop_column("dashboard_users", "locked_until_utc")
    op.drop_column("dashboard_users", "failed_login_count")
