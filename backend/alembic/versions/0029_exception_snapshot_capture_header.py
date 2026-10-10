"""add exception snapshot capture header

Revision ID: 0029_exception_snapshot_capture_header
Revises: 0028_scan_exception_snapshots
"""

from alembic import op
import sqlalchemy as sa

revision = "0029_exception_snapshot_capture_header"
down_revision = "0028_scan_exception_snapshots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_exception_snapshot_captures",
        sa.Column("scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(length=100), nullable=True),
        sa.Column("exception_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("captured_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scan_exception_snapshot_captures_tenant_id", "scan_exception_snapshot_captures", ["tenant_id"])
    op.create_index("ix_scan_exception_snapshot_captures_company_id", "scan_exception_snapshot_captures", ["company_id"])
    op.create_index("ix_scan_exception_snapshot_captures_captured_at_utc", "scan_exception_snapshot_captures", ["captured_at_utc"])


def downgrade() -> None:
    op.drop_table("scan_exception_snapshot_captures")
