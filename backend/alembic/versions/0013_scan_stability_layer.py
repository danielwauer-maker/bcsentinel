"""add scan stability status tables

Revision ID: 0013_scan_stability_layer
Revises: 0012_scan_enabled_modules
Create Date: 2026-05-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0013_scan_stability_layer"
down_revision = "0012_scan_enabled_modules"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _has_table("scan_run_statuses"):
        op.create_table(
            "scan_run_statuses",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("run_id", sa.String(length=50), nullable=False),
            sa.Column("tenant_id", sa.String(length=50), nullable=False),
            sa.Column("company_name", sa.String(length=120), nullable=True),
            sa.Column("environment_name", sa.String(length=100), nullable=True),
            sa.Column("scan_mode", sa.String(length=20), nullable=False, server_default="deep"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
            sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("current_module", sa.String(length=80), nullable=True),
            sa.Column("current_step", sa.String(length=160), nullable=True),
            sa.Column("started_at_utc", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
            sa.Column("heartbeat_at_utc", sa.DateTime(timezone=True), nullable=True),
            sa.Column("completed_at_utc", sa.DateTime(timezone=True), nullable=True),
            sa.Column("failed_at_utc", sa.DateTime(timezone=True), nullable=True),
            sa.Column("error_code", sa.String(length=80), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("warning_message", sa.Text(), nullable=True),
            sa.Column("estimated_remaining_seconds", sa.Integer(), nullable=True),
            sa.Column("total_modules", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("completed_modules", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("failed_modules", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_scan_run_statuses_id", "scan_run_statuses", ["id"], unique=False)
        op.create_index("ix_scan_run_statuses_run_id", "scan_run_statuses", ["run_id"], unique=True)
        op.create_index("ix_scan_run_statuses_tenant_id", "scan_run_statuses", ["tenant_id"], unique=False)
        op.create_index("ix_scan_run_statuses_status", "scan_run_statuses", ["status"], unique=False)
        op.create_index("ix_scan_run_statuses_updated_at_utc", "scan_run_statuses", ["updated_at_utc"], unique=False)

    if not _has_table("scan_run_modules"):
        op.create_table(
            "scan_run_modules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("run_id", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
            sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("current_step", sa.String(length=160), nullable=True),
            sa.Column("started_at_utc", sa.DateTime(timezone=True), nullable=True),
            sa.Column("completed_at_utc", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["run_id"], ["scan_run_statuses.run_id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_scan_run_modules_id", "scan_run_modules", ["id"], unique=False)
        op.create_index("ix_scan_run_modules_run_id", "scan_run_modules", ["run_id"], unique=False)
        op.create_index("ix_scan_run_modules_name", "scan_run_modules", ["name"], unique=False)

    if not _has_table("scan_run_events"):
        op.create_table(
            "scan_run_events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("run_id", sa.String(length=50), nullable=False),
            sa.Column("timestamp_utc", sa.DateTime(timezone=True), nullable=False),
            sa.Column("level", sa.String(length=20), nullable=False, server_default="info"),
            sa.Column("module", sa.String(length=80), nullable=True),
            sa.Column("step", sa.String(length=160), nullable=True),
            sa.Column("message", sa.String(length=255), nullable=False),
            sa.ForeignKeyConstraint(["run_id"], ["scan_run_statuses.run_id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_scan_run_events_id", "scan_run_events", ["id"], unique=False)
        op.create_index("ix_scan_run_events_run_id", "scan_run_events", ["run_id"], unique=False)
        op.create_index("ix_scan_run_events_timestamp_utc", "scan_run_events", ["timestamp_utc"], unique=False)


def downgrade() -> None:
    if _has_table("scan_run_events"):
        op.drop_index("ix_scan_run_events_timestamp_utc", table_name="scan_run_events")
        op.drop_index("ix_scan_run_events_run_id", table_name="scan_run_events")
        op.drop_index("ix_scan_run_events_id", table_name="scan_run_events")
        op.drop_table("scan_run_events")
    if _has_table("scan_run_modules"):
        op.drop_index("ix_scan_run_modules_name", table_name="scan_run_modules")
        op.drop_index("ix_scan_run_modules_run_id", table_name="scan_run_modules")
        op.drop_index("ix_scan_run_modules_id", table_name="scan_run_modules")
        op.drop_table("scan_run_modules")
    if _has_table("scan_run_statuses"):
        op.drop_index("ix_scan_run_statuses_updated_at_utc", table_name="scan_run_statuses")
        op.drop_index("ix_scan_run_statuses_status", table_name="scan_run_statuses")
        op.drop_index("ix_scan_run_statuses_tenant_id", table_name="scan_run_statuses")
        op.drop_index("ix_scan_run_statuses_run_id", table_name="scan_run_statuses")
        op.drop_index("ix_scan_run_statuses_id", table_name="scan_run_statuses")
        op.drop_table("scan_run_statuses")
