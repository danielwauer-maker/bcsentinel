"""add lifecycle email outbox and tenant notification email

Revision ID: 0030_lifecycle_email_outbox
Revises: 0029_exception_snapshot_capture_header
"""

from alembic import op
import sqlalchemy as sa

revision = "0030_lifecycle_email_outbox"
down_revision = "0029_exception_snapshot_capture_header"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("primary_notification_email", sa.String(length=255), nullable=True))
    op.create_index("ix_tenants_primary_notification_email", "tenants", ["primary_notification_email"])

    op.create_table(
        "lifecycle_email_outbox",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("target_email", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False, server_default="en"),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("dedupe_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("scheduled_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("dedupe_key", name="uq_lifecycle_email_outbox_dedupe_key"),
    )
    op.create_index("ix_lifecycle_email_outbox_tenant_id", "lifecycle_email_outbox", ["tenant_id"])
    op.create_index("ix_lifecycle_email_outbox_event_type", "lifecycle_email_outbox", ["event_type"])
    op.create_index("ix_lifecycle_email_outbox_status", "lifecycle_email_outbox", ["status"])
    op.create_index("ix_lifecycle_email_outbox_scheduled_at_utc", "lifecycle_email_outbox", ["scheduled_at_utc"])


def downgrade() -> None:
    op.drop_table("lifecycle_email_outbox")
    op.drop_index("ix_tenants_primary_notification_email", table_name="tenants")
    op.drop_column("tenants", "primary_notification_email")
