"""Add opt-in pilot enrollment, one-use hash and append-only lifecycle events.

Revision ID: 0041_pilot_enrollment
Revises: 0040_scan_record_identity_evidence
"""
from alembic import op
import sqlalchemy as sa

revision = "0041_pilot_enrollment"
down_revision = "0040_scan_record_identity_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pilot_enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("contact_email", sa.String(255), nullable=False),
        sa.Column("authorized_email", sa.String(255), nullable=False),
        sa.Column("identity_key", sa.String(64), nullable=False),
        sa.Column("commercial_profile", sa.String(60), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=True),
        sa.Column("token_expires_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("registered_tenant_id", sa.String(50), sa.ForeignKey("tenants.tenant_id"), nullable=True),
        sa.Column("registered_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_pilot_enrollment_token_hash"),
        sa.UniqueConstraint("identity_key", name="uq_pilot_enrollment_identity_key"),
    )
    op.create_index("ix_pilot_enrollments_identity_key", "pilot_enrollments", ["identity_key"])
    op.create_table(
        "pilot_enrollment_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("enrollment_id", sa.Integer(), sa.ForeignKey("pilot_enrollments.id"), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pilot_enrollment_audit_enrollment_id", "pilot_enrollment_audit", ["enrollment_id"])


def downgrade() -> None:
    # Enrollment/audit evidence is not disposable customer data.
    if op.get_bind().execute(sa.text("SELECT 1 FROM pilot_enrollments LIMIT 1")).first():
        raise RuntimeError("Refusing to drop nonempty pilot enrollment history")
    op.drop_index("ix_pilot_enrollment_audit_enrollment_id", table_name="pilot_enrollment_audit")
    op.drop_table("pilot_enrollment_audit")
    op.drop_index("ix_pilot_enrollments_identity_key", table_name="pilot_enrollments")
    op.drop_table("pilot_enrollments")
