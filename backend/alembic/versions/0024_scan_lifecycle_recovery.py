"""Add terminal scan lifecycle, worker leases, and recovery metadata.

Revision ID: 0024_scan_lifecycle_recovery
Revises: 0023_atomic_scan_credit
"""

from alembic import op
import sqlalchemy as sa


revision = "0024_scan_lifecycle_recovery"
down_revision = "0023_atomic_scan_credit"
branch_labels = None
depends_on = None


def _assert_no_duplicates(table: str, columns: str, label: str) -> None:
    duplicate = op.get_bind().execute(
        sa.text(
            f"SELECT {columns}, COUNT(*) AS row_count FROM {table} "
            f"GROUP BY {columns} HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError(
            f"Cannot install terminal scan lifecycle: duplicate {label} exists ({duplicate!r}). "
            "Resolve the legacy duplicate explicitly before retrying."
        )


def upgrade() -> None:
    _assert_no_duplicates("scan_issues", "scan_id, code", "scan finding code")
    _assert_no_duplicates("scan_run_modules", "run_id, name", "scan module")

    with op.batch_alter_table("scan_run_statuses") as batch_op:
        batch_op.add_column(sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("lease_owner", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("lease_token", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("lease_expires_at_utc", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("execution_attempt", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("next_retry_at_utc", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("correlation_id", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("recovery_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("lifecycle_version", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("result_persisted_at_utc", sa.DateTime(timezone=True), nullable=True))

    op.execute("UPDATE scan_run_statuses SET created_at_utc = updated_at_utc WHERE created_at_utc IS NULL")
    with op.batch_alter_table("scan_run_statuses") as batch_op:
        batch_op.alter_column("created_at_utc", nullable=False)
        batch_op.create_unique_constraint("uq_scan_run_statuses_lease_token", ["lease_token"])
        batch_op.create_index("ix_scan_run_statuses_created_at_utc", ["created_at_utc"])
        batch_op.create_index("ix_scan_run_statuses_lease_owner", ["lease_owner"])
        batch_op.create_index("ix_scan_run_statuses_lease_token", ["lease_token"])
        batch_op.create_index("ix_scan_run_statuses_lease_expires_at_utc", ["lease_expires_at_utc"])
        batch_op.create_index("ix_scan_run_statuses_next_retry_at_utc", ["next_retry_at_utc"])
        batch_op.create_index("ix_scan_run_statuses_correlation_id", ["correlation_id"])
        batch_op.create_index("ix_scan_run_statuses_status_lease", ["status", "lease_expires_at_utc"])
        batch_op.create_index("ix_scan_run_statuses_status_retry", ["status", "next_retry_at_utc"])

    with op.batch_alter_table("scan_run_events") as batch_op:
        batch_op.add_column(sa.Column("event_type", sa.String(length=40), nullable=False, server_default="scan_progress"))
        batch_op.add_column(sa.Column("attempt", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("worker_id", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("correlation_id", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("metadata_json", sa.Text(), nullable=True))
        batch_op.create_index("ix_scan_run_events_event_type", ["event_type"])
        batch_op.create_index("ix_scan_run_events_correlation_id", ["correlation_id"])

    with op.batch_alter_table("scan_run_modules") as batch_op:
        batch_op.create_unique_constraint("uq_scan_run_modules_run_name", ["run_id", "name"])
    with op.batch_alter_table("scan_issues") as batch_op:
        batch_op.create_unique_constraint("uq_scan_issues_scan_code", ["scan_id", "code"])


def downgrade() -> None:
    with op.batch_alter_table("scan_issues") as batch_op:
        batch_op.drop_constraint("uq_scan_issues_scan_code", type_="unique")
    with op.batch_alter_table("scan_run_modules") as batch_op:
        batch_op.drop_constraint("uq_scan_run_modules_run_name", type_="unique")
    with op.batch_alter_table("scan_run_events") as batch_op:
        batch_op.drop_index("ix_scan_run_events_correlation_id")
        batch_op.drop_index("ix_scan_run_events_event_type")
        batch_op.drop_column("metadata_json")
        batch_op.drop_column("correlation_id")
        batch_op.drop_column("worker_id")
        batch_op.drop_column("attempt")
        batch_op.drop_column("event_type")
    with op.batch_alter_table("scan_run_statuses") as batch_op:
        batch_op.drop_index("ix_scan_run_statuses_status_retry")
        batch_op.drop_index("ix_scan_run_statuses_status_lease")
        batch_op.drop_index("ix_scan_run_statuses_correlation_id")
        batch_op.drop_index("ix_scan_run_statuses_next_retry_at_utc")
        batch_op.drop_index("ix_scan_run_statuses_lease_expires_at_utc")
        batch_op.drop_index("ix_scan_run_statuses_lease_token")
        batch_op.drop_index("ix_scan_run_statuses_lease_owner")
        batch_op.drop_index("ix_scan_run_statuses_created_at_utc")
        batch_op.drop_constraint("uq_scan_run_statuses_lease_token", type_="unique")
        batch_op.drop_column("result_persisted_at_utc")
        batch_op.drop_column("lifecycle_version")
        batch_op.drop_column("recovery_count")
        batch_op.drop_column("correlation_id")
        batch_op.drop_column("next_retry_at_utc")
        batch_op.drop_column("retry_count")
        batch_op.drop_column("execution_attempt")
        batch_op.drop_column("lease_expires_at_utc")
        batch_op.drop_column("lease_token")
        batch_op.drop_column("lease_owner")
        batch_op.drop_column("created_at_utc")
