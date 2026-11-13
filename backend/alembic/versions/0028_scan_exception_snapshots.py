"""add immutable per-scan exception snapshots

Revision ID: 0028_scan_exception_snapshots
Revises: 0027_operations_governance
"""

from alembic import op
import sqlalchemy as sa

revision = "0028_scan_exception_snapshots"
down_revision = "0027_operations_governance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_exception_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(length=100), nullable=True),
        sa.Column("source_exception_entry_no", sa.Integer(), nullable=False),
        sa.Column("table_id", sa.Integer(), nullable=False),
        sa.Column("record_system_id", sa.String(length=40), nullable=True),
        sa.Column("record_no", sa.String(length=50), nullable=True),
        sa.Column("record_caption", sa.String(length=150), nullable=True),
        sa.Column("issue_code", sa.String(length=80), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("exception_created_by", sa.String(length=100), nullable=True),
        sa.Column("exception_created_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("captured_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("scan_id", "source_exception_entry_no", name="uq_scan_exception_snapshot_source"),
    )
    op.create_index("ix_scan_exception_snapshots_scan_id", "scan_exception_snapshots", ["scan_id"])
    op.create_index("ix_scan_exception_snapshots_tenant_id", "scan_exception_snapshots", ["tenant_id"])
    op.create_index("ix_scan_exception_snapshots_company_id", "scan_exception_snapshots", ["company_id"])
    op.create_index("ix_scan_exception_snapshots_issue_code", "scan_exception_snapshots", ["issue_code"])
    op.create_index("ix_scan_exception_snapshots_captured_at_utc", "scan_exception_snapshots", ["captured_at_utc"])


def downgrade() -> None:
    op.drop_table("scan_exception_snapshots")
