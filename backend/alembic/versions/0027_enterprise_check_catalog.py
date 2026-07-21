"""add enterprise check catalog

Revision ID: 0027_check_catalog
Revises: 0026_license_simplification
Create Date: 2026-07-21 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0027_check_catalog"
down_revision = "0026_license_simplification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "check_definitions",
        sa.Column("check_id", sa.String(length=80), nullable=False),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("check_id"),
    )
    op.create_index("ix_check_definitions_module", "check_definitions", ["module"])
    op.create_table(
        "check_translations",
        sa.Column("check_id", sa.String(length=80), nullable=False),
        sa.Column("language_code", sa.String(length=35), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("is_customized", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["check_id"], ["check_definitions.check_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("check_id", "language_code"),
    )


def downgrade() -> None:
    op.drop_table("check_translations")
    op.drop_index("ix_check_definitions_module", table_name="check_definitions")
    op.drop_table("check_definitions")
