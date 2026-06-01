"""harden tenant token storage

Revision ID: 0014_harden_tenant_token_storage
Revises: 0013_scan_stability_layer
Create Date: 2026-06-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0014_harden_tenant_token_storage"
down_revision = "0013_scan_stability_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.alter_column(
            "api_token",
            existing_type=sa.String(length=80),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.alter_column(
            "api_token",
            existing_type=sa.String(length=80),
            nullable=False,
        )
