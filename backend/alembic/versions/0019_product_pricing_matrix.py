"""add product pricing matrix

Revision ID: 0019_product_pricing_matrix
Revises: 0018_landingpage_page_visibility
Create Date: 2026-06-16 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0019_product_pricing_matrix"
down_revision = "0018_landingpage_page_visibility"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_pricing_matrix_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_key", sa.String(length=50), nullable=False),
        sa.Column("pricing_tier", sa.String(length=30), nullable=False),
        sa.Column("max_records", sa.Integer(), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("billing_interval", sa.String(length=20), nullable=False, server_default="one_time"),
        sa.Column("display_name_de", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("display_name_en", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("stripe_price_id", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_key", "pricing_tier", name="uq_product_pricing_matrix_product_tier"),
    )
    op.create_index(op.f("ix_product_pricing_matrix_config_id"), "product_pricing_matrix_config", ["id"], unique=False)
    op.create_index(op.f("ix_product_pricing_matrix_config_product_key"), "product_pricing_matrix_config", ["product_key"], unique=False)
    op.create_index(op.f("ix_product_pricing_matrix_config_pricing_tier"), "product_pricing_matrix_config", ["pricing_tier"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_product_pricing_matrix_config_pricing_tier"), table_name="product_pricing_matrix_config")
    op.drop_index(op.f("ix_product_pricing_matrix_config_product_key"), table_name="product_pricing_matrix_config")
    op.drop_index(op.f("ix_product_pricing_matrix_config_id"), table_name="product_pricing_matrix_config")
    op.drop_table("product_pricing_matrix_config")
