"""Add DEV-only one-time sandbox QA scan grants.

Revision ID: 0042_sandbox_qa_scan_grants
Revises: 0041_pilot_enrollment
"""
from alembic import op
import sqlalchemy as sa

revision = "0042_sandbox_qa_scan_grants"
down_revision = "0041_pilot_enrollment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sandbox_qa_scan_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("company_id", sa.String(50), nullable=False),
        sa.Column("environment_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column("expires_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_by", sa.String(100), nullable=False),
        sa.Column("consumed_scan_id", sa.String(50), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "company_id", "environment_name", name="uq_sandbox_qa_grant_binding"),
        sa.UniqueConstraint("consumed_scan_id", name="uq_sandbox_qa_grant_consumed_scan"),
    )
    op.create_index("ix_sandbox_qa_grants_available", "sandbox_qa_scan_grants", ["tenant_id", "company_id", "environment_name", "status"])
    op.create_index("ix_sandbox_qa_scan_grants_tenant_id", "sandbox_qa_scan_grants", ["tenant_id"])
    op.create_index("ix_sandbox_qa_scan_grants_expires_at_utc", "sandbox_qa_scan_grants", ["expires_at_utc"])


def downgrade() -> None:
    op.drop_index("ix_sandbox_qa_scan_grants_expires_at_utc", table_name="sandbox_qa_scan_grants")
    op.drop_index("ix_sandbox_qa_scan_grants_tenant_id", table_name="sandbox_qa_scan_grants")
    op.drop_index("ix_sandbox_qa_grants_available", table_name="sandbox_qa_scan_grants")
    op.drop_table("sandbox_qa_scan_grants")
