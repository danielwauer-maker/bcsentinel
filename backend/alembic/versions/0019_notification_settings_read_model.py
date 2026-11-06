"""add notification settings read model

Revision ID: 0019_notification_settings_read_model
Revises: 0018_remediation_read_model
"""

from alembic import op
import sqlalchemy as sa

revision = "0019_notification_settings_read_model"
down_revision = "0018_remediation_read_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_settings_read",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("company_id", sa.String(length=100), nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("preferred_language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("configured_event_types_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("enabled_event_types_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("recipient_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled_recipient_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("channels_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("template_languages_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("sent_deliveries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_deliveries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("suppressed_deliveries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_successful_delivery_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failed_delivery_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("safe_last_failure_summary", sa.String(length=250), nullable=True),
        sa.Column("bc_updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "company_id", name="uq_notification_settings_tenant_company"),
    )
    op.create_index("ix_notification_settings_read_tenant_id", "notification_settings_read", ["tenant_id"])
    op.create_index("ix_notification_settings_read_company_id", "notification_settings_read", ["company_id"])
    op.create_index("ix_notification_settings_read_bc_updated_at_utc", "notification_settings_read", ["bc_updated_at_utc"])
    op.create_index("ix_notification_settings_read_synced_at_utc", "notification_settings_read", ["synced_at_utc"])


def downgrade() -> None:
    op.drop_table("notification_settings_read")
