"""add tenant invitations

Revision ID: 0025_tenant_invitations
Revises: 0024_tenant_commercial_overrides
"""

from alembic import op
import sqlalchemy as sa

revision = "0025_tenant_invitations"
down_revision = "0024_tenant_commercial_overrides"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="VIEWER"),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("expires_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invited_by_user_identity_id", sa.Integer(), sa.ForeignKey("user_identities.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("accepted_by_user_identity_id", sa.Integer(), sa.ForeignKey("user_identities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("token_hash", name="uq_tenant_invitation_token_hash"),
    )
    for name, columns in (
        ("ix_tenant_invitations_tenant_id", ["tenant_id"]),
        ("ix_tenant_invitations_email_normalized", ["email_normalized"]),
        ("ix_tenant_invitations_role", ["role"]),
        ("ix_tenant_invitations_token_hash", ["token_hash"]),
        ("ix_tenant_invitations_status", ["status"]),
        ("ix_tenant_invitations_expires_at_utc", ["expires_at_utc"]),
        ("ix_tenant_invitations_invited_by_user_identity_id", ["invited_by_user_identity_id"]),
        ("ix_tenant_invitations_accepted_by_user_identity_id", ["accepted_by_user_identity_id"]),
    ):
        op.create_index(name, "tenant_invitations", columns)


def downgrade() -> None:
    op.drop_table("tenant_invitations")
