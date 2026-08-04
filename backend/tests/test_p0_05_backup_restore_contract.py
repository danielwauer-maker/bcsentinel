from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "backend/scripts/verify_postgres_backup_restore.py"
WORKFLOW = ROOT / ".github/workflows/p0-05-postgres-backup-restore.yml"


def test_backup_restore_script_has_safety_integrity_and_smoke_guards():
    source = SCRIPT.read_text(encoding="utf-8")

    assert "Source and restore databases must be different" in source
    assert "Refusing P0-05" in source
    assert '"pg_dump"' in source
    assert '"--format=custom"' in source
    assert '"pg_restore"' in source
    assert '"--clean"' in source
    assert '"--exit-on-error"' in source
    assert "Alembic revision mismatch after restore" in source
    assert "Table count mismatch after restore" in source
    assert "backup_sha256" in source
    assert "critical_tables" in source


def test_workflow_uses_separate_source_and_restore_databases_and_publishes_evidence():
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "bcsentinel_p0_05_source_test" in source
    assert "bcsentinel_p0_05_restore_test" in source
    assert "createdb" in source
    assert "verify_postgres_backup_restore.py" in source
    assert "test_p0e_postgres_concurrency.py" in source
    assert "p0-05-postgres-backup-restore-evidence" in source
    assert "retention-days: 30" in source
