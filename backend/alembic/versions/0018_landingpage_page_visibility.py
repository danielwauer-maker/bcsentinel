"""add landingpage page visibility

Revision ID: 0018_landingpage_page_visibility
Revises: 0017_tenant_preferred_language
Create Date: 2026-06-14 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0018_landingpage_page_visibility"
down_revision = "0017_tenant_preferred_language"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "landingpage_page_visibility",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("page_key", sa.String(length=80), nullable=False),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("page_key"),
    )
    op.create_index(
        op.f("ix_landingpage_page_visibility_id"),
        "landingpage_page_visibility",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_landingpage_page_visibility_page_key"),
        "landingpage_page_visibility",
        ["page_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_landingpage_page_visibility_page_key"), table_name="landingpage_page_visibility")
    op.drop_index(op.f("ix_landingpage_page_visibility_id"), table_name="landingpage_page_visibility")
    op.drop_table("landingpage_page_visibility")
