"""add applied exception count to scans

Revision ID: 0028_exception_count
Revises: 0027_check_catalog
Create Date: 2026-07-22 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0028_exception_count"
down_revision = "0027_check_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scans",
        sa.Column("applied_exception_count", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("scans", "applied_exception_count")
