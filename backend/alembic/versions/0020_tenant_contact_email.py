"""add tenant contact email

Revision ID: 0020_tenant_contact_email
Revises: 0019_product_pricing_matrix
Create Date: 2026-06-16 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0020_tenant_contact_email"
down_revision = "0019_product_pricing_matrix"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("contact_email", sa.String(length=255), nullable=True))
    op.create_index("ix_tenants_contact_email", "tenants", ["contact_email"])


def downgrade() -> None:
    op.drop_index("ix_tenants_contact_email", table_name="tenants")
    op.drop_column("tenants", "contact_email")
