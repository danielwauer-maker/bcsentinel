"""assessment scope v1

Revision ID: 0033_assessment_scope_v1
Revises: 0032_validation_baseline_binding
"""

from alembic import op
import sqlalchemy as sa

revision = "0033_assessment_scope_v1"
down_revision = "0032_validation_baseline_binding"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assessment_scope_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id"), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="auto"),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="usage_detection"),
        sa.Column("score_type", sa.String(length=30), nullable=False, server_default="preliminary"),
        sa.Column("score_value", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("supported_modules_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("included_modules_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unknown_modules_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unsupported_extensions_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("scan_id", "version", name="uq_assessment_scope_scan_version"),
    )
    op.create_index("ix_assessment_scope_snapshots_scan_id", "assessment_scope_snapshots", ["scan_id"])
    op.create_index("ix_assessment_scope_snapshots_tenant_id", "assessment_scope_snapshots", ["tenant_id"])
    op.create_index("ix_assessment_scope_snapshots_state", "assessment_scope_snapshots", ["state"])

    op.create_table(
        "assessment_scope_modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("snapshot_id", sa.Integer(), sa.ForeignKey("assessment_scope_snapshots.id"), nullable=False),
        sa.Column("module_code", sa.String(length=40), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        sa.Column("support_status", sa.String(length=20), nullable=False, server_default="supported"),
        sa.Column("detection_status", sa.String(length=20), nullable=False, server_default="unknown"),
        sa.Column("decision", sa.String(length=20), nullable=False, server_default="inherit"),
        sa.Column("included_in_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("detection_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("module_score", sa.Integer(), nullable=False, server_default="100"),
        sa.UniqueConstraint("snapshot_id", "module_code", name="uq_assessment_scope_module"),
    )
    op.create_index("ix_assessment_scope_modules_snapshot_id", "assessment_scope_modules", ["snapshot_id"])
    op.create_index("ix_assessment_scope_modules_module_code", "assessment_scope_modules", ["module_code"])


def downgrade() -> None:
    op.drop_index("ix_assessment_scope_modules_module_code", table_name="assessment_scope_modules")
    op.drop_index("ix_assessment_scope_modules_snapshot_id", table_name="assessment_scope_modules")
    op.drop_table("assessment_scope_modules")
    op.drop_index("ix_assessment_scope_snapshots_state", table_name="assessment_scope_snapshots")
    op.drop_index("ix_assessment_scope_snapshots_tenant_id", table_name="assessment_scope_snapshots")
    op.drop_index("ix_assessment_scope_snapshots_scan_id", table_name="assessment_scope_snapshots")
    op.drop_table("assessment_scope_snapshots")
