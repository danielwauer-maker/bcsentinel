"""bind Validation scans to immutable confirmed assessment scopes

Revision ID: 0034_validation_scope_binding
Revises: 0033_assessment_scope_v1
"""

from alembic import op
import sqlalchemy as sa

revision = "0034_validation_scope_binding"
down_revision = "0033_assessment_scope_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "validation_scope_bindings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("validation_scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id"), nullable=False),
        sa.Column("baseline_scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id"), nullable=False),
        sa.Column("scope_snapshot_id", sa.Integer(), sa.ForeignKey("assessment_scope_snapshots.id"), nullable=False),
        sa.Column("scope_version", sa.Integer(), nullable=False),
        sa.Column("bound_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("validation_scan_id", name="uq_validation_scope_validation_scan"),
    )
    op.create_index("ix_validation_scope_bindings_tenant_id", "validation_scope_bindings", ["tenant_id"])
    op.create_index("ix_validation_scope_bindings_validation_scan_id", "validation_scope_bindings", ["validation_scan_id"])
    op.create_index("ix_validation_scope_bindings_baseline_scan_id", "validation_scope_bindings", ["baseline_scan_id"])
    op.create_index("ix_validation_scope_bindings_scope_snapshot_id", "validation_scope_bindings", ["scope_snapshot_id"])


def downgrade() -> None:
    op.drop_index("ix_validation_scope_bindings_scope_snapshot_id", table_name="validation_scope_bindings")
    op.drop_index("ix_validation_scope_bindings_baseline_scan_id", table_name="validation_scope_bindings")
    op.drop_index("ix_validation_scope_bindings_validation_scan_id", table_name="validation_scope_bindings")
    op.drop_index("ix_validation_scope_bindings_tenant_id", table_name="validation_scope_bindings")
    op.drop_table("validation_scope_bindings")
