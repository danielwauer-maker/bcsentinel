"""Store completed source-record identity evidence without historical backfills.

Revision ID: 0040_scan_record_identity_evidence
Revises: 0039_scan_expectation_snapshot
"""
from alembic import op
import sqlalchemy as sa

revision = "0040_scan_record_identity_evidence"
down_revision = "0039_scan_expectation_snapshot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_record_identity_evidence",
        sa.Column("scan_id", sa.String(50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tenant_id", sa.String(50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(64), nullable=False),
        sa.Column("check_code", sa.String(50), primary_key=True),
        sa.Column("schema_version", sa.String(80), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("payload_sha256", sa.String(64), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(payload_sha256) = 64", name="ck_record_evidence_sha256_length"),
        sa.CheckConstraint("schema_version = 'bc-record-evidence-v1'", name="ck_record_evidence_schema"),
        sa.CheckConstraint("check_code = 'CUSTOMERS_DUPLICATE_VAT'", name="ck_record_evidence_check"),
    )
    # The logical parent is a finalized, fully evidenced scan; not an arbitrary
    # historical scan ID. Do not accept a payload for a different BC company.
    binding = (
        "SELECT 1 FROM scans s "
        "JOIN tenants t ON t.tenant_id = s.tenant_id "
        "JOIN scan_run_statuses r ON r.run_id = s.scan_id AND r.tenant_id = s.tenant_id "
        "JOIN scan_expectation_snapshots e ON e.scan_id = s.scan_id AND e.tenant_id = s.tenant_id "
        "JOIN scan_execution_evidence x ON x.scan_id = s.scan_id AND x.tenant_id = s.tenant_id "
        "WHERE s.scan_id = NEW.scan_id AND s.tenant_id = NEW.tenant_id "
        "AND s.bc_company_id = NEW.company_id AND t.bc_company_id = NEW.company_id "
        "AND e.company_id = NEW.company_id AND x.company_id = NEW.company_id "
        "AND r.status = 'completed' AND r.result_persisted_at_utc IS NOT NULL"
    )
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE FUNCTION validate_scan_record_identity_binding() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NOT EXISTS (" + binding + ") THEN RAISE EXCEPTION 'scan record identity binding mismatch'; END IF; RETURN NEW; END; $$")
        op.execute("CREATE TRIGGER scan_record_identity_binding BEFORE INSERT ON scan_record_identity_evidence FOR EACH ROW EXECUTE FUNCTION validate_scan_record_identity_binding()")
        op.execute("CREATE FUNCTION prevent_scan_record_identity_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF TG_OP = 'DELETE' AND pg_trigger_depth() > 1 THEN RETURN OLD; END IF; RAISE EXCEPTION 'scan record identity evidence is immutable'; END; $$")
        op.execute("CREATE TRIGGER scan_record_identity_immutable BEFORE UPDATE OR DELETE ON scan_record_identity_evidence FOR EACH ROW EXECUTE FUNCTION prevent_scan_record_identity_mutation()")
    elif op.get_bind().dialect.name == "sqlite":
        op.execute("CREATE TRIGGER scan_record_identity_binding BEFORE INSERT ON scan_record_identity_evidence WHEN NOT EXISTS (" + binding + ") BEGIN SELECT RAISE(ABORT, 'scan record identity binding mismatch'); END")
        op.execute("CREATE TRIGGER scan_record_identity_immutable BEFORE UPDATE ON scan_record_identity_evidence BEGIN SELECT RAISE(ABORT, 'scan record identity evidence is immutable'); END")
        op.execute("CREATE TRIGGER scan_record_identity_nodelete BEFORE DELETE ON scan_record_identity_evidence WHEN EXISTS (SELECT 1 FROM scans WHERE scan_id = OLD.scan_id) BEGIN SELECT RAISE(ABORT, 'scan record identity evidence is immutable'); END")


def downgrade() -> None:
    if op.get_bind().execute(sa.text("SELECT 1 FROM scan_record_identity_evidence LIMIT 1")).first():
        raise RuntimeError("Refusing to drop nonempty scan record identity evidence")
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER scan_record_identity_immutable ON scan_record_identity_evidence")
        op.execute("DROP FUNCTION prevent_scan_record_identity_mutation()")
        op.execute("DROP TRIGGER scan_record_identity_binding ON scan_record_identity_evidence")
        op.execute("DROP FUNCTION validate_scan_record_identity_binding()")
    op.drop_table("scan_record_identity_evidence")
