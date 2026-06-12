"""add product pricing config

Revision ID: 0016_product_pricing_config
Revises: 0015_product_licensing_p0
Create Date: 2026-06-08 00:00:00
"""
from alembic import op
from datetime import datetime, timezone
import sqlalchemy as sa

revision = "0016_product_pricing_config"
down_revision = "0015_product_licensing_p0"
branch_labels = None
depends_on = None


DEFAULT_PRODUCT_PRICING = [
    ("assessment", "Assessment", 7900, "EUR", "one_time"),
    ("validation_check", "Validation Check", 4900, "EUR", "one_time"),
    ("monitoring_monthly", "Monitoring Monthly", 9900, "EUR", "month"),
    ("monitoring_annual", "Monitoring Annual", 99000, "EUR", "year"),
]


def upgrade() -> None:
    op.create_table(
        "product_pricing_config",
        sa.Column("product_key", sa.String(length=50), primary_key=True),
        sa.Column("display_name", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("price_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("billing_interval", sa.String(length=20), nullable=False, server_default="one_time"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    product_pricing = sa.table(
        "product_pricing_config",
        sa.column("product_key", sa.String),
        sa.column("display_name", sa.String),
        sa.column("price_cents", sa.Integer),
        sa.column("currency", sa.String),
        sa.column("billing_interval", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("updated_at_utc", sa.DateTime(timezone=True)),
    )
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        product_pricing,
        [
            {
                "product_key": product_key,
                "display_name": display_name,
                "price_cents": price_cents,
                "currency": currency,
                "billing_interval": billing_interval,
                "is_active": True,
                "updated_at_utc": now,
            }
            for product_key, display_name, price_cents, currency, billing_interval in DEFAULT_PRODUCT_PRICING
        ],
    )


def downgrade() -> None:
    op.drop_table("product_pricing_config")
