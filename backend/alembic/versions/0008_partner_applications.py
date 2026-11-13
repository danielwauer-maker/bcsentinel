"""partner applications intake

Revision ID: 0008_partner_applications
Revises: 0007_partner_auth_fields
Create Date: 2026-04-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_partner_applications"
down_revision = "0007_partner_auth_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partner_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=160), nullable=False),
        sa.Column("contact_name", sa.String(length=120), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=60), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=80), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("source_page", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_partner_applications_id"), "partner_applications", ["id"], unique=False)
    op.create_index(
        op.f("ix_partner_applications_contact_email"),
        "partner_applications",
        ["contact_email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_partner_applications_status"),
        "partner_applications",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_partner_applications_created_at_utc"),
        "partner_applications",
        ["created_at_utc"],
        unique=False,
    )
    op.create_index(
        op.f("ix_partner_applications_reviewed_at_utc"),
        "partner_applications",
        ["reviewed_at_utc"],
        unique=False,
    )

    # Alembic creates alembic_version.version_num as VARCHAR(32). Later
    # BCSentinel revision identifiers intentionally became more descriptive and
    # exceed 32 characters. PostgreSQL enforces that width while SQLite does
    # not, so a fresh real PostgreSQL upgrade would otherwise fail before
    # revision 0009 can even start. Expand the control column while the current
    # revision id still fits into the original width.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128)")


def downgrade() -> None:
    op.drop_index(op.f("ix_partner_applications_reviewed_at_utc"), table_name="partner_applications")
    op.drop_index(op.f("ix_partner_applications_created_at_utc"), table_name="partner_applications")
    op.drop_index(op.f("ix_partner_applications_status"), table_name="partner_applications")
    op.drop_index(op.f("ix_partner_applications_contact_email"), table_name="partner_applications")
    op.drop_index(op.f("ix_partner_applications_id"), table_name="partner_applications")
    op.drop_table("partner_applications")
