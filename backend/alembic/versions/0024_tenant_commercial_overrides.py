"""add tenant commercial overrides and pilot sponsorships

Revision ID: 0024_tenant_commercial_overrides
Revises: 0023_multitenant_accounts
"""

from alembic import op
import sqlalchemy as sa

revision = "0024_tenant_commercial_overrides"
down_revision = "0023_multitenant_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_commercial_overrides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("override_type", sa.String(length=30), nullable=False),
        sa.Column("value_number", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="EUR"),
        sa.Column("valid_from_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("uses_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("allow_promotion_code_stack", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("internal_note", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=160), nullable=False),
        sa.Column("updated_by", sa.String(length=160), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_commercial_overrides_tenant_id", "tenant_commercial_overrides", ["tenant_id"])
    op.create_index("ix_tenant_commercial_overrides_product_code", "tenant_commercial_overrides", ["product_code"])
    op.create_index("ix_tenant_commercial_overrides_override_type", "tenant_commercial_overrides", ["override_type"])
    op.create_index("ix_tenant_commercial_overrides_valid_from_utc", "tenant_commercial_overrides", ["valid_from_utc"])
    op.create_index("ix_tenant_commercial_overrides_valid_until_utc", "tenant_commercial_overrides", ["valid_until_utc"])
    op.create_index("ix_tenant_commercial_overrides_status", "tenant_commercial_overrides", ["status"])

    op.create_table(
        "tenant_pilot_sponsorships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("valid_from_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("created_by", sa.String(length=160), nullable=False),
        sa.Column("revoked_by", sa.String(length=160), nullable=True),
        sa.Column("revoked_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "product_code", "valid_from_utc", name="uq_pilot_sponsorship_start"),
    )
    op.create_index("ix_tenant_pilot_sponsorships_tenant_id", "tenant_pilot_sponsorships", ["tenant_id"])
    op.create_index("ix_tenant_pilot_sponsorships_product_code", "tenant_pilot_sponsorships", ["product_code"])
    op.create_index("ix_tenant_pilot_sponsorships_valid_from_utc", "tenant_pilot_sponsorships", ["valid_from_utc"])
    op.create_index("ix_tenant_pilot_sponsorships_valid_until_utc", "tenant_pilot_sponsorships", ["valid_until_utc"])
    op.create_index("ix_tenant_pilot_sponsorships_status", "tenant_pilot_sponsorships", ["status"])


def downgrade() -> None:
    op.drop_table("tenant_pilot_sponsorships")
    op.drop_table("tenant_commercial_overrides")
