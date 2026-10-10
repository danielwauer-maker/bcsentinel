"""add customer lifecycle, billing identity and connection diagnostics

Revision ID: 0026_customer_lifecycle_billing_diagnostics
Revises: 0025_tenant_invitations
"""

from alembic import op
import sqlalchemy as sa

revision = "0026_customer_lifecycle_billing_diagnostics"
down_revision = "0025_tenant_invitations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_customer_lifecycles",
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("state", sa.String(length=30), nullable=False, server_default="onboarding"),
        sa.Column("effective_from_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("grace_until_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pilot_until_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=160), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_customer_lifecycles_state", "tenant_customer_lifecycles", ["state"])

    op.create_table(
        "tenant_billing_profiles",
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("legal_company_name", sa.String(length=200), nullable=False),
        sa.Column("billing_email", sa.String(length=320), nullable=False),
        sa.Column("address_line1", sa.String(length=200), nullable=False),
        sa.Column("address_line2", sa.String(length=200), nullable=True),
        sa.Column("postal_code", sa.String(length=30), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("vat_id", sa.String(length=40), nullable=True),
        sa.Column("tax_treatment", sa.String(length=40), nullable=False, server_default="provider_determined"),
        sa.Column("provider_customer_id", sa.String(length=120), nullable=True),
        sa.Column("provider_tax_evidence_json", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.String(length=160), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_billing_profiles_provider_customer_id", "tenant_billing_profiles", ["provider_customer_id"])

    op.create_table(
        "tenant_connection_diagnostics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("environment_name", sa.String(length=160), nullable=True),
        sa.Column("company_name", sa.String(length=160), nullable=True),
        sa.Column("extension_version", sa.String(length=40), nullable=True),
        sa.Column("bc_version", sa.String(length=40), nullable=True),
        sa.Column("api_reachable", sa.String(length=10), nullable=False, server_default="unknown"),
        sa.Column("permissions_ok", sa.String(length=10), nullable=False, server_default="unknown"),
        sa.Column("compatibility_status", sa.String(length=30), nullable=False, server_default="unknown"),
        sa.Column("upgrade_required", sa.String(length=10), nullable=False, server_default="false"),
        sa.Column("diagnostic_code", sa.String(length=80), nullable=True),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("observed_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_connection_diagnostics_tenant_id", "tenant_connection_diagnostics", ["tenant_id"])
    op.create_index("ix_tenant_connection_diagnostics_observed_at_utc", "tenant_connection_diagnostics", ["observed_at_utc"])


def downgrade() -> None:
    op.drop_table("tenant_connection_diagnostics")
    op.drop_table("tenant_billing_profiles")
    op.drop_table("tenant_customer_lifecycles")
