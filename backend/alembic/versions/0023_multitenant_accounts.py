"""add multi-tenant account foundation

Revision ID: 0023_multitenant_accounts
Revises: 0022_tenant_access_states
"""

from alembic import op
import sqlalchemy as sa

revision = "0023_multitenant_accounts"
down_revision = "0022_tenant_access_states"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_identities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("provider_subject", sa.String(length=255), nullable=False),
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_user_identity_provider_subject"),
    )
    op.create_index("ix_user_identities_provider", "user_identities", ["provider"])
    op.create_index("ix_user_identities_provider_subject", "user_identities", ["provider_subject"])
    op.create_index("ix_user_identities_email_normalized", "user_identities", ["email_normalized"])
    op.create_index("ix_user_identities_status", "user_identities", ["status"])

    op.create_table(
        "tenant_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_identity_id", sa.Integer(), sa.ForeignKey("user_identities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="VIEWER"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="invited"),
        sa.Column("invited_email_normalized", sa.String(length=320), nullable=True),
        sa.Column("invited_by", sa.String(length=160), nullable=True),
        sa.Column("invited_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_identity_id", "tenant_id", name="uq_tenant_membership_user_tenant"),
    )
    op.create_index("ix_tenant_memberships_user_identity_id", "tenant_memberships", ["user_identity_id"])
    op.create_index("ix_tenant_memberships_tenant_id", "tenant_memberships", ["tenant_id"])
    op.create_index("ix_tenant_memberships_role", "tenant_memberships", ["role"])
    op.create_index("ix_tenant_memberships_status", "tenant_memberships", ["status"])

    op.create_table(
        "tenant_bc_environments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("environment_key", sa.String(length=160), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("environment_type", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "environment_key", name="uq_tenant_bc_environment_key"),
    )
    op.create_index("ix_tenant_bc_environments_tenant_id", "tenant_bc_environments", ["tenant_id"])
    op.create_index("ix_tenant_bc_environments_status", "tenant_bc_environments", ["status"])

    op.create_table(
        "tenant_bc_companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("environment_id", sa.Integer(), sa.ForeignKey("tenant_bc_environments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_key", sa.String(length=160), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("environment_id", "company_key", name="uq_tenant_bc_company_key"),
    )
    op.create_index("ix_tenant_bc_companies_environment_id", "tenant_bc_companies", ["environment_id"])
    op.create_index("ix_tenant_bc_companies_status", "tenant_bc_companies", ["status"])


def downgrade() -> None:
    op.drop_table("tenant_bc_companies")
    op.drop_table("tenant_bc_environments")
    op.drop_table("tenant_memberships")
    op.drop_table("user_identities")
