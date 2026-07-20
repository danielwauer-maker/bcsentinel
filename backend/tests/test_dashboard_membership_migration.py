from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _run_alembic(database_path: Path, *args: str, expect_success: bool = True):
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if expect_success:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0
    return result


def _seed_legacy(connection: sqlite3.Connection, *, second_case_variant: bool = False) -> None:
    tenants = [
        ("ten_legacy_one", "Legacy Production"),
        ("ten_legacy_two", "Legacy Sandbox"),
    ]
    connection.executemany(
        "INSERT INTO tenants (tenant_id, environment_name, app_version, created_at_utc, "
        "current_plan, license_status, preferred_language) VALUES (?, ?, '1.0.2.4', "
        "'2026-01-01T00:00:00Z', 'free', 'trial', 'en')",
        tenants,
    )
    connection.execute(
        "INSERT INTO dashboard_users (tenant_id, email, status, must_change_password, "
        "created_at_utc, updated_at_utc, invite_mail_status) VALUES "
        "('ten_legacy_one', 'legacy@example.com', 'active', 0, "
        "'2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', 'sent')"
    )
    if second_case_variant:
        connection.execute(
            "INSERT INTO dashboard_users (tenant_id, email, status, must_change_password, "
            "created_at_utc, updated_at_utc, invite_mail_status) VALUES "
            "('ten_legacy_two', 'Legacy@Example.com', 'active', 0, "
            "'2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', 'sent')"
        )
    connection.commit()


def test_membership_migration_backfills_and_safe_downgrade_restores_legacy_shape(tmp_path):
    database_path = tmp_path / "membership-upgrade.sqlite3"
    _run_alembic(database_path, "upgrade", "0024_scan_lifecycle_recovery")
    with sqlite3.connect(database_path) as connection:
        _seed_legacy(connection)

    _run_alembic(database_path, "upgrade", "head")
    with sqlite3.connect(database_path) as connection:
        user = connection.execute(
            "SELECT id, email, normalized_email FROM dashboard_users"
        ).fetchone()
        membership = connection.execute(
            "SELECT dashboard_user_id, tenant_id, role, is_active "
            "FROM dashboard_user_tenant_memberships"
        ).fetchone()
        assert user[1:] == ("legacy@example.com", "legacy@example.com")
        assert membership == (user[0], "ten_legacy_one", "owner", 1)
        assert connection.execute("SELECT COUNT(*) FROM tenants").fetchone()[0] == 2

    _run_alembic(database_path, "downgrade", "0024_scan_lifecycle_recovery")
    with sqlite3.connect(database_path) as connection:
        restored = connection.execute("SELECT tenant_id, email FROM dashboard_users").fetchone()
        assert restored == ("ten_legacy_one", "legacy@example.com")


def test_membership_migration_aborts_case_insensitive_email_conflict_without_values(tmp_path):
    database_path = tmp_path / "membership-conflict.sqlite3"
    _run_alembic(database_path, "upgrade", "0024_scan_lifecycle_recovery")
    with sqlite3.connect(database_path) as connection:
        _seed_legacy(connection, second_case_variant=True)

    result = _run_alembic(database_path, "upgrade", "head", expect_success=False)
    output = result.stdout + result.stderr
    assert "normalized_email_conflicts=1" in output
    assert "legacy@example.com" not in output.lower()


def test_membership_downgrade_aborts_when_user_has_multiple_tenants(tmp_path):
    database_path = tmp_path / "membership-unsafe-downgrade.sqlite3"
    _run_alembic(database_path, "upgrade", "0024_scan_lifecycle_recovery")
    with sqlite3.connect(database_path) as connection:
        _seed_legacy(connection)
    _run_alembic(database_path, "upgrade", "head")

    with sqlite3.connect(database_path) as connection:
        user_id = connection.execute("SELECT id FROM dashboard_users").fetchone()[0]
        connection.execute(
            "INSERT INTO dashboard_user_tenant_memberships "
            "(dashboard_user_id, tenant_id, role, is_active, created_at_utc, updated_at_utc) "
            "VALUES (?, 'ten_legacy_two', 'owner', 1, '2026-01-02T00:00:00Z', '2026-01-02T00:00:00Z')",
            (user_id,),
        )
        connection.commit()

    result = _run_alembic(
        database_path,
        "downgrade",
        "0024_scan_lifecycle_recovery",
        expect_success=False,
    )
    assert "cannot represent the current memberships" in (result.stdout + result.stderr)
