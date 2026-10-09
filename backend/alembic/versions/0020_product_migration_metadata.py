"""add product migration metadata

Revision ID: 0020_product_migration_metadata
Revises: 0019_notification_read_model
"""

from alembic import op
import sqlalchemy as sa

revision = "0020_product_migration_metadata"
down_revision = "0019_notification_read_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_migration_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("legacy_code", sa.String(length=80), nullable=False),
        sa.Column("commercial_offer_id", sa.String(length=40), nullable=True),
        sa.Column("billing_variant", sa.String(length=30), nullable=True),
        sa.Column("resolution", sa.String(length=40), nullable=False),
        sa.Column("rights_preserved", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("migrated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", name="uq_product_migration_entity"),
    )
    for name, cols in [
        ("ix_product_migration_records_entity_type", ["entity_type"]),
        ("ix_product_migration_records_entity_id", ["entity_id"]),
        ("ix_product_migration_records_tenant_id", ["tenant_id"]),
        ("ix_product_migration_records_legacy_code", ["legacy_code"]),
        ("ix_product_migration_records_commercial_offer_id", ["commercial_offer_id"]),
        ("ix_product_migration_records_billing_variant", ["billing_variant"]),
        ("ix_product_migration_records_resolution", ["resolution"]),
        ("ix_product_migration_records_migrated_at_utc", ["migrated_at_utc"]),
    ]:
        op.create_index(name, "product_migration_records", cols)


def downgrade() -> None:
    op.drop_table("product_migration_records")
