"""Bind report scans to their Business Central company and local currency.

Revision ID: 0035_scan_company_lcy
Revises: 0034_validation_scope_binding
"""
from alembic import op
import sqlalchemy as sa

revision = "0035_scan_company_lcy"
down_revision = "0034_validation_scope_binding"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("bc_company_id", sa.String(length=64), nullable=True))
    op.add_column("scans", sa.Column("lcy_code", sa.String(length=3), nullable=True))
    op.create_index("ix_scans_bc_company_id", "scans", ["bc_company_id"])


def downgrade() -> None:
    op.drop_index("ix_scans_bc_company_id", table_name="scans")
    op.drop_column("scans", "lcy_code")
    op.drop_column("scans", "bc_company_id")
