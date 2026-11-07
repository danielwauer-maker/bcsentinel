"""add tenant lifecycle access states

Revision ID: 0022_tenant_access_states
Revises: 0021_pilot_interests
"""

from alembic import op
import sqlalchemy as sa

revision = "0022_tenant_access_states"
down_revision = "0021_pilot_interests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_access_states",
        sa.Column(
            "tenant_id",
            sa.String(length=50),
            sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=120), nullable=True),
        sa.Column(
            "updated_at_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_tenant_access_states_status", "tenant_access_states", ["status"])
    op.execute(
        "INSERT INTO tenant_access_states (tenant_id, status, updated_by) "
        "SELECT tenant_id, 'active', 'migration' FROM tenants"
    )


def downgrade() -> None:
    op.drop_table("tenant_access_states")
