"""bind validation credits to an immutable baseline scan

Revision ID: 0032_validation_baseline_binding
Revises: 0031_operator_commercial_actions
"""

from alembic import op
import sqlalchemy as sa

revision = "0032_validation_baseline_binding"
down_revision = "0031_operator_commercial_actions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_scan_credits",
        sa.Column("baseline_scan_id", sa.String(length=50), nullable=True),
    )
    op.create_index(
        "ix_tenant_scan_credits_baseline_scan_id",
        "tenant_scan_credits",
        ["baseline_scan_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tenant_scan_credits_baseline_scan_id", table_name="tenant_scan_credits")
    op.drop_column("tenant_scan_credits", "baseline_scan_id")
