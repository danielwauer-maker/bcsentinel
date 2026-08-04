from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "backend/scripts/verify_postgres_migration_cycle.py"
WORKFLOW = ROOT / ".github/workflows/p0-04-postgres-migration-cycle.yml"


def test_migration_cycle_script_has_safety_and_evidence_guards():
    source = SCRIPT.read_text(encoding="utf-8")

    assert "P0-04 requires a PostgreSQL DATABASE_URL" in source
    assert "Refusing migration cycle against database" in source
    assert 'command.upgrade(config, "head")' in source
    assert "command.downgrade(config, rollback_revision)" in source
    assert source.count('command.upgrade(config, "head")') >= 2
    assert "Schema drift detected" in source
    assert "Sentinel tenant was not preserved" in source
    assert "schema_hash_before" in source
    assert "schema_hash_after" in source


def test_workflow_uses_dedicated_postgres_and_publishes_evidence():
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "postgres:16-alpine" in source
    assert "bcsentinel_p0_04_test" in source
    assert "verify_postgres_migration_cycle.py" in source
    assert "test_p0e_postgres_concurrency.py" in source
    assert "p0-04-postgres-migration-evidence" in source
    assert "retention-days: 30" in source
