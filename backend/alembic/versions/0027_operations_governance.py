"""add support, feature flag, data lifecycle and telemetry governance

Revision ID: 0027_operations_governance
Revises: 0026_customer_lifecycle_billing_diagnostics
"""

from alembic import op
import sqlalchemy as sa

revision = "0027_operations_governance"
down_revision = "0026_customer_lifecycle_billing_diagnostics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_support_access_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("access_mode", sa.String(length=30), nullable=False, server_default="diagnostics"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("valid_from_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("granted_by_user_identity_id", sa.Integer(), sa.ForeignKey("user_identities.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("revoked_by_user_identity_id", sa.Integer(), sa.ForeignKey("user_identities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("revoked_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_support_access_grants_tenant_id", "tenant_support_access_grants", ["tenant_id"])
    op.create_index("ix_tenant_support_access_grants_status", "tenant_support_access_grants", ["status"])
    op.create_index("ix_tenant_support_access_grants_valid_until_utc", "tenant_support_access_grants", ["valid_until_utc"])

    op.create_table(
        "tenant_feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("flag_key", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("config_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("updated_by", sa.String(length=160), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "flag_key", name="uq_tenant_feature_flag"),
    )
    op.create_index("ix_tenant_feature_flags_tenant_id", "tenant_feature_flags", ["tenant_id"])
    op.create_index("ix_tenant_feature_flags_flag_key", "tenant_feature_flags", ["flag_key"])

    op.create_table(
        "tenant_data_lifecycle_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="requested"),
        sa.Column("requested_by_user_identity_id", sa.Integer(), sa.ForeignKey("user_identities.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("requested_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_json", sa.Text(), nullable=True),
    )
    op.create_index("ix_tenant_data_lifecycle_requests_tenant_id", "tenant_data_lifecycle_requests", ["tenant_id"])
    op.create_index("ix_tenant_data_lifecycle_requests_request_type", "tenant_data_lifecycle_requests", ["request_type"])
    op.create_index("ix_tenant_data_lifecycle_requests_status", "tenant_data_lifecycle_requests", ["status"])
    op.create_index("ix_tenant_data_lifecycle_requests_requested_at_utc", "tenant_data_lifecycle_requests", ["requested_at_utc"])

    op.create_table(
        "product_telemetry_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_name", sa.String(length=100), nullable=False),
        sa.Column("outcome", sa.String(length=30), nullable=False, server_default="info"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("occurred_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_product_telemetry_events_tenant_id", "product_telemetry_events", ["tenant_id"])
    op.create_index("ix_product_telemetry_events_event_name", "product_telemetry_events", ["event_name"])
    op.create_index("ix_product_telemetry_events_outcome", "product_telemetry_events", ["outcome"])
    op.create_index("ix_product_telemetry_events_occurred_at_utc", "product_telemetry_events", ["occurred_at_utc"])


def downgrade() -> None:
    op.drop_table("product_telemetry_events")
    op.drop_table("tenant_data_lifecycle_requests")
    op.drop_table("tenant_feature_flags")
    op.drop_table("tenant_support_access_grants")
