"""Store source-attested partial check observations without backfilling history.

Revision ID: 0038_scan_execution_evidence
Revises: 0037_merge_staging_report
"""
from alembic import op
import sqlalchemy as sa

revision = "0038_scan_execution_evidence"
down_revision = "0037_merge_staging_report"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_execution_evidence",
        sa.Column("scan_id", sa.String(50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tenant_id", sa.String(50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(64), nullable=False),
        sa.Column("schema_version", sa.String(80), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("payload_sha256", sa.String(64), nullable=False),
        sa.Column("sync_sha256", sa.String(64), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute("CREATE FUNCTION validate_scan_evidence_binding() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NOT EXISTS (SELECT 1 FROM scans WHERE scan_id = NEW.scan_id AND tenant_id = NEW.tenant_id AND bc_company_id = NEW.company_id) THEN RAISE EXCEPTION 'scan execution evidence binding mismatch'; END IF; RETURN NEW; END; $$")
        op.execute("CREATE TRIGGER scan_execution_evidence_binding BEFORE INSERT ON scan_execution_evidence FOR EACH ROW EXECUTE FUNCTION validate_scan_evidence_binding()")
        op.execute("CREATE FUNCTION prevent_scan_evidence_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF TG_OP = 'DELETE' AND pg_trigger_depth() > 1 THEN RETURN OLD; END IF; RAISE EXCEPTION 'scan execution evidence is immutable'; END; $$")
        op.execute("CREATE TRIGGER scan_execution_evidence_immutable BEFORE UPDATE OR DELETE ON scan_execution_evidence FOR EACH ROW EXECUTE FUNCTION prevent_scan_evidence_update()")
    elif dialect == "sqlite":
        op.execute("CREATE TRIGGER scan_execution_evidence_binding BEFORE INSERT ON scan_execution_evidence WHEN NOT EXISTS (SELECT 1 FROM scans WHERE scan_id = NEW.scan_id AND tenant_id = NEW.tenant_id AND bc_company_id = NEW.company_id) BEGIN SELECT RAISE(ABORT, 'scan execution evidence binding mismatch'); END")
        op.execute("CREATE TRIGGER scan_execution_evidence_immutable BEFORE UPDATE ON scan_execution_evidence BEGIN SELECT RAISE(ABORT, 'scan execution evidence is immutable'); END")
        op.execute("CREATE TRIGGER scan_execution_evidence_nodelete BEFORE DELETE ON scan_execution_evidence WHEN EXISTS (SELECT 1 FROM scans WHERE scan_id = OLD.scan_id) BEGIN SELECT RAISE(ABORT, 'scan execution evidence is immutable'); END")


def downgrade() -> None:
    # Preserve captured evidence: downgrade only if this new table is empty.
    if op.get_bind().execute(sa.text("SELECT 1 FROM scan_execution_evidence LIMIT 1")).first():
        raise RuntimeError("Refusing to drop nonempty scan execution evidence")
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER scan_execution_evidence_immutable ON scan_execution_evidence")
        op.execute("DROP FUNCTION prevent_scan_evidence_update()")
        op.execute("DROP TRIGGER scan_execution_evidence_binding ON scan_execution_evidence")
        op.execute("DROP FUNCTION validate_scan_evidence_binding()")
    op.drop_table("scan_execution_evidence")
