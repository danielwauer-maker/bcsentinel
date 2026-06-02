"""add p0 product licensing tables

Revision ID: 0015_product_licensing_p0
Revises: 0014_harden_tenant_token_storage
Create Date: 2026-06-02 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0015_product_licensing_p0"
down_revision = "0014_harden_tenant_token_storage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_product_purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="manual"),
        sa.Column("provider_checkout_session_id", sa.String(length=120), nullable=True),
        sa.Column("provider_payment_intent_id", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="paid"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="EUR"),
        sa.Column("amount_total", sa.Float(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="checkout"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_product_purchases_tenant_id", "tenant_product_purchases", ["tenant_id"])
    op.create_index("ix_tenant_product_purchases_product_code", "tenant_product_purchases", ["product_code"])
    op.create_index("ix_tenant_product_purchases_provider", "tenant_product_purchases", ["provider"])
    op.create_index("ix_tenant_product_purchases_status", "tenant_product_purchases", ["status"])
    op.create_index(
        "ix_tenant_product_purchases_provider_checkout_session_id",
        "tenant_product_purchases",
        ["provider_checkout_session_id"],
        unique=True,
    )
    op.create_index(
        "ix_tenant_product_purchases_provider_payment_intent_id",
        "tenant_product_purchases",
        ["provider_payment_intent_id"],
    )

    op.create_table(
        "tenant_scan_credits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="available"),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="manual"),
        sa.Column("source_purchase_id", sa.Integer(), sa.ForeignKey("tenant_product_purchases.id"), nullable=True),
        sa.Column("consumed_scan_id", sa.String(length=50), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at_utc", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tenant_scan_credits_tenant_id", "tenant_scan_credits", ["tenant_id"])
    op.create_index("ix_tenant_scan_credits_product_code", "tenant_scan_credits", ["product_code"])
    op.create_index("ix_tenant_scan_credits_status", "tenant_scan_credits", ["status"])
    op.create_index("ix_tenant_scan_credits_source_purchase_id", "tenant_scan_credits", ["source_purchase_id"])
    op.create_index("ix_tenant_scan_credits_consumed_scan_id", "tenant_scan_credits", ["consumed_scan_id"])

    op.create_table(
        "tenant_product_entitlements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="manual"),
        sa.Column("valid_until_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenant_product_entitlements_tenant_id", "tenant_product_entitlements", ["tenant_id"])
    op.create_index("ix_tenant_product_entitlements_product_code", "tenant_product_entitlements", ["product_code"])
    op.create_index("ix_tenant_product_entitlements_status", "tenant_product_entitlements", ["status"])


def downgrade() -> None:
    op.drop_table("tenant_product_entitlements")
    op.drop_table("tenant_scan_credits")
    op.drop_table("tenant_product_purchases")
