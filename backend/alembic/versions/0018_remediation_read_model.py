"""add remediation read model

Revision ID: 0018_remediation_read_model
Revises: 0017_tenant_preferred_language
"""

from alembic import op
import sqlalchemy as sa

revision = "0018_remediation_read_model"
down_revision = "0017_tenant_preferred_language"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "remediation_actions_read",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action_id", sa.String(length=50), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("company_id", sa.String(length=100), nullable=False),
        sa.Column("finding_key", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("recommendation_ref", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("owner_principal_id", sa.String(length=50), nullable=True),
        sa.Column("owner_display_name", sa.String(length=100), nullable=True),
        sa.Column("due_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("blocked_reason", sa.String(length=250), nullable=True),
        sa.Column("completion_note", sa.String(length=250), nullable=True),
        sa.Column("validation_result_ref", sa.String(length=100), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="manual"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "action_id", name="uq_remediation_action_tenant_action"),
    )
    for name, cols in [
        ("ix_remediation_actions_read_tenant_id", ["tenant_id"]),
        ("ix_remediation_actions_read_action_id", ["action_id"]),
        ("ix_remediation_actions_read_company_id", ["company_id"]),
        ("ix_remediation_actions_read_status", ["status"]),
        ("ix_remediation_actions_read_priority", ["priority"]),
        ("ix_remediation_actions_read_updated_at_utc", ["updated_at_utc"]),
    ]:
        op.create_index(name, "remediation_actions_read", cols)

    op.create_table(
        "remediation_audit_read",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action_id", sa.String(length=50), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("company_id", sa.String(length=100), nullable=False),
        sa.Column("changed_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changed_by_principal_id", sa.String(length=50), nullable=True),
        sa.Column("changed_field_or_status", sa.String(length=100), nullable=False),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
    )
    op.create_index("ix_remediation_audit_read_tenant_id", "remediation_audit_read", ["tenant_id"])
    op.create_index("ix_remediation_audit_read_action_id", "remediation_audit_read", ["action_id"])
    op.create_index("ix_remediation_audit_read_changed_at_utc", "remediation_audit_read", ["changed_at_utc"])


def downgrade() -> None:
    op.drop_table("remediation_audit_read")
    op.drop_table("remediation_actions_read")
