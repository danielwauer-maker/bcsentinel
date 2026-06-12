"""add tenant preferred language

Revision ID: 0017_tenant_preferred_language
Revises: 0016_product_pricing_config
Create Date: 2026-06-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0017_tenant_preferred_language"
down_revision = "0016_product_pricing_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column("preferred_language", sa.String(length=2), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("tenants", "preferred_language")
