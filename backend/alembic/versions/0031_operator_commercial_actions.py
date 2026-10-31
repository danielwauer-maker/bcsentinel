"""add operator commercial action audit

Revision ID: 0031_operator_commercial_actions
Revises: 0030_lifecycle_email_outbox
"""

from alembic import op
import sqlalchemy as sa

revision = "0031_operator_commercial_actions"
down_revision = "0030_lifecycle_email_outbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_operator_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("sales_channel", sa.String(length=30), nullable=False, server_default="direct"),
        sa.Column("external_order_reference", sa.String(length=120), nullable=True),
        sa.Column("entitlement_id", sa.Integer(), sa.ForeignKey("tenant_product_entitlements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("credit_id", sa.Integer(), sa.ForeignKey("tenant_scan_credits.id", ondelete="SET NULL"), nullable=True),
        sa.Column("related_scan_id", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="completed"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("actor", sa.String(length=120), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "sales_channel",
            "external_order_reference",
            "action_type",
            name="uq_tenant_operator_action_channel_order_action",
        ),
    )
    op.create_index("ix_tenant_operator_actions_tenant_id", "tenant_operator_actions", ["tenant_id"])
    op.create_index("ix_tenant_operator_actions_action_type", "tenant_operator_actions", ["action_type"])
    op.create_index("ix_tenant_operator_actions_sales_channel", "tenant_operator_actions", ["sales_channel"])
    op.create_index("ix_tenant_operator_actions_external_order_reference", "tenant_operator_actions", ["external_order_reference"])
    op.create_index("ix_tenant_operator_actions_created_at_utc", "tenant_operator_actions", ["created_at_utc"])


def downgrade() -> None:
    op.drop_table("tenant_operator_actions")
