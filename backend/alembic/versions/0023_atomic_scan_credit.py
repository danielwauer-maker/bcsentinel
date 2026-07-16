"""Add atomic scan-start idempotency and immutable credit ledger.

Revision ID: 0023_atomic_scan_credit
Revises: 0022_tenant_registration_identity
"""

from alembic import op
import sqlalchemy as sa


revision = "0023_atomic_scan_credit"
down_revision = "0022_tenant_registration_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    duplicate = connection.execute(
        sa.text(
            "SELECT consumed_scan_id, COUNT(*) AS row_count "
            "FROM tenant_scan_credits WHERE consumed_scan_id IS NOT NULL "
            "GROUP BY consumed_scan_id HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError(
            "Cannot install atomic scan charging: duplicate legacy credit consumption "
            f"exists for scan_id {duplicate[0]!r}. Resolve it explicitly before retrying."
        )

    with op.batch_alter_table("tenant_scan_credits") as batch_op:
        batch_op.create_unique_constraint(
            "uq_tenant_scan_credits_consumed_scan_id", ["consumed_scan_id"]
        )

    op.create_table(
        "scan_start_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("client_request_id", sa.String(length=36), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("scan_id", sa.String(length=50), nullable=False),
        sa.Column("requested_scan_mode", sa.String(length=30), nullable=False),
        sa.Column("resolved_product_code", sa.String(length=50), nullable=True),
        sa.Column("credit_id", sa.Integer(), sa.ForeignKey("tenant_scan_credits.id"), nullable=True),
        sa.Column("free_scan_slot", sa.String(length=30), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="accepted"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "client_request_id", name="uq_scan_start_tenant_client_request"),
        sa.UniqueConstraint("tenant_id", "free_scan_slot", name="uq_scan_start_tenant_free_slot"),
        sa.UniqueConstraint("scan_id", name="uq_scan_start_requests_scan_id"),
    )
    for name, columns in (
        ("ix_scan_start_requests_tenant_id", ["tenant_id"]),
        ("ix_scan_start_requests_client_request_id", ["client_request_id"]),
        ("ix_scan_start_requests_scan_id", ["scan_id"]),
        ("ix_scan_start_requests_resolved_product_code", ["resolved_product_code"]),
        ("ix_scan_start_requests_credit_id", ["credit_id"]),
        ("ix_scan_start_requests_status", ["status"]),
        ("ix_scan_start_requests_created_at_utc", ["created_at_utc"]),
    ):
        op.create_index(name, "scan_start_requests", columns)

    op.create_table(
        "credit_ledger_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id"), nullable=False),
        sa.Column("credit_id", sa.Integer(), sa.ForeignKey("tenant_scan_credits.id"), nullable=True),
        sa.Column("source_purchase_id", sa.Integer(), sa.ForeignKey("tenant_product_purchases.id"), nullable=True),
        sa.Column("scan_start_request_id", sa.Integer(), sa.ForeignKey("scan_start_requests.id"), nullable=True),
        sa.Column("scan_id", sa.String(length=50), nullable=True),
        sa.Column("product_code", sa.String(length=50), nullable=True),
        sa.Column("operation_type", sa.String(length=30), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=True),
        sa.Column("reason", sa.String(length=160), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("scan_start_request_id", "operation_type", name="uq_credit_ledger_request_operation"),
        sa.UniqueConstraint("scan_id", "operation_type", name="uq_credit_ledger_scan_operation"),
    )
    for name, columns in (
        ("ix_credit_ledger_entries_tenant_id", ["tenant_id"]),
        ("ix_credit_ledger_entries_credit_id", ["credit_id"]),
        ("ix_credit_ledger_entries_source_purchase_id", ["source_purchase_id"]),
        ("ix_credit_ledger_entries_scan_start_request_id", ["scan_start_request_id"]),
        ("ix_credit_ledger_entries_scan_id", ["scan_id"]),
        ("ix_credit_ledger_entries_product_code", ["product_code"]),
        ("ix_credit_ledger_entries_operation_type", ["operation_type"]),
        ("ix_credit_ledger_entries_created_at_utc", ["created_at_utc"]),
    ):
        op.create_index(name, "credit_ledger_entries", columns)

    connection.execute(
        sa.text(
            "INSERT INTO credit_ledger_entries "
            "(tenant_id, credit_id, source_purchase_id, scan_id, product_code, operation_type, "
            "amount, reason, created_at_utc) "
            "SELECT tenant_id, id, source_purchase_id, consumed_scan_id, product_code, 'MIGRATION', "
            "0, 'Legacy credit imported without inferred accounting event', created_at_utc "
            "FROM tenant_scan_credits"
        )
    )


def downgrade() -> None:
    op.drop_table("credit_ledger_entries")
    op.drop_table("scan_start_requests")
    with op.batch_alter_table("tenant_scan_credits") as batch_op:
        batch_op.drop_constraint("uq_tenant_scan_credits_consumed_scan_id", type_="unique")
