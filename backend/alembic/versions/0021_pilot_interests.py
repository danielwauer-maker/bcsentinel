"""add pilot interest intake

Revision ID: 0021_pilot_interests
Revises: 0020_product_migration_metadata
"""

from alembic import op
import sqlalchemy as sa

revision = "0021_pilot_interests"
down_revision = "0020_product_migration_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pilot_interests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contact_name", sa.String(length=120), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("company_name", sa.String(length=160), nullable=True),
        sa.Column("bc_context", sa.String(length=80), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("preferred_language", sa.String(length=10), nullable=False, server_default="de"),
        sa.Column("source_page", sa.String(length=120), nullable=False, server_default="pilot"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pilot_interests_contact_email", "pilot_interests", ["contact_email"])
    op.create_index("ix_pilot_interests_status", "pilot_interests", ["status"])
    op.create_index("ix_pilot_interests_created_at_utc", "pilot_interests", ["created_at_utc"])


def downgrade() -> None:
    op.drop_table("pilot_interests")
