"""Seal declared scan expectations at scan acceptance; no historic backfill.

Revision ID: 0039_scan_expectation_snapshot
Revises: 0038_scan_execution_evidence
"""
from alembic import op
import sqlalchemy as sa

revision = "0039_scan_expectation_snapshot"
down_revision = "0038_scan_execution_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_expectation_snapshots",
        sa.Column("scan_id", sa.String(50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tenant_id", sa.String(50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("payload_sha256", sa.String(64), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute("CREATE FUNCTION validate_scan_expectation_binding() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NOT EXISTS (SELECT 1 FROM scans s JOIN tenants t ON s.tenant_id = t.tenant_id WHERE s.scan_id = NEW.scan_id AND s.tenant_id = NEW.tenant_id AND t.bc_company_id = NEW.company_id) THEN RAISE EXCEPTION 'scan expectation binding mismatch'; END IF; RETURN NEW; END; $$")
        op.execute("CREATE TRIGGER scan_expectation_binding BEFORE INSERT ON scan_expectation_snapshots FOR EACH ROW EXECUTE FUNCTION validate_scan_expectation_binding()")
        op.execute("CREATE FUNCTION prevent_scan_expectation_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF TG_OP = 'DELETE' AND pg_trigger_depth() > 1 THEN RETURN OLD; END IF; RAISE EXCEPTION 'scan expectation is immutable'; END; $$")
        op.execute("CREATE TRIGGER scan_expectation_immutable BEFORE UPDATE OR DELETE ON scan_expectation_snapshots FOR EACH ROW EXECUTE FUNCTION prevent_scan_expectation_mutation()")
    elif dialect == "sqlite":
        op.execute("CREATE TRIGGER scan_expectation_binding BEFORE INSERT ON scan_expectation_snapshots WHEN NOT EXISTS (SELECT 1 FROM scans s JOIN tenants t ON s.tenant_id = t.tenant_id WHERE s.scan_id = NEW.scan_id AND s.tenant_id = NEW.tenant_id AND t.bc_company_id = NEW.company_id) BEGIN SELECT RAISE(ABORT, 'scan expectation binding mismatch'); END")
        op.execute("CREATE TRIGGER scan_expectation_immutable BEFORE UPDATE ON scan_expectation_snapshots BEGIN SELECT RAISE(ABORT, 'scan expectation is immutable'); END")
        op.execute("CREATE TRIGGER scan_expectation_nodelete BEFORE DELETE ON scan_expectation_snapshots WHEN EXISTS (SELECT 1 FROM scans WHERE scan_id = OLD.scan_id) BEGIN SELECT RAISE(ABORT, 'scan expectation is immutable'); END")


def downgrade() -> None:
    if op.get_bind().execute(sa.text("SELECT 1 FROM scan_expectation_snapshots LIMIT 1")).first():
        raise RuntimeError("Refusing to drop nonempty scan expectation snapshots")
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER scan_expectation_immutable ON scan_expectation_snapshots")
        op.execute("DROP FUNCTION prevent_scan_expectation_mutation()")
        op.execute("DROP TRIGGER scan_expectation_binding ON scan_expectation_snapshots")
        op.execute("DROP FUNCTION validate_scan_expectation_binding()")
    op.drop_table("scan_expectation_snapshots")
