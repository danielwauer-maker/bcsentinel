"""add explicit free-scan and premium entitlement state

Revision ID: 0026_license_simplification
Revises: 0025_dashboard_memberships
Create Date: 2026-07-21 00:00:00
"""

from datetime import timedelta

from alembic import op
import sqlalchemy as sa


revision = "0026_license_simplification"
down_revision = "0025_dashboard_memberships"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.add_column(
            sa.Column("free_assessment_used", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(sa.Column("premium_until_utc", sa.DateTime(timezone=True), nullable=True))

    connection = op.get_bind()
    used_tenants = connection.execute(
        sa.text(
            "SELECT DISTINCT tenant_id FROM scan_start_requests "
            "WHERE free_scan_slot = 'data_health_score' AND status = 'accepted' "
            "UNION SELECT DISTINCT tenant_id FROM scans WHERE scan_type IN ('data_health_score', 'quick')"
        )
    ).scalars().all()
    for tenant_id in used_tenants:
        connection.execute(
            sa.text("UPDATE tenants SET free_assessment_used = :used WHERE tenant_id = :tenant_id"),
            {"used": True, "tenant_id": tenant_id},
        )

    candidates: dict[str, list] = {}
    entitlement_rows = connection.execute(
        sa.text(
            "SELECT tenant_id, valid_until_utc FROM tenant_product_entitlements "
            "WHERE status = 'active' AND product_code IN ('assessment', 'full_analysis', 'validation_check') "
            "AND valid_until_utc IS NOT NULL"
        )
    ).all()
    for tenant_id, valid_until in entitlement_rows:
        candidates.setdefault(tenant_id, []).append(valid_until)

    purchase_rows = connection.execute(
        sa.text(
            "SELECT tenant_id, created_at_utc FROM tenant_product_purchases "
            "WHERE status IN ('paid', 'complete', 'completed') "
            "AND product_code IN ('assessment', 'full_analysis', 'validation_check')"
        )
    ).all()
    for tenant_id, purchased_at in purchase_rows:
        if purchased_at is not None:
            candidates.setdefault(tenant_id, []).append(purchased_at + timedelta(days=7))

    for tenant_id, values in candidates.items():
        connection.execute(
            sa.text("UPDATE tenants SET premium_until_utc = :premium_until WHERE tenant_id = :tenant_id"),
            {"premium_until": max(values), "tenant_id": tenant_id},
        )


def downgrade() -> None:
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.drop_column("premium_until_utc")
        batch_op.drop_column("free_assessment_used")
