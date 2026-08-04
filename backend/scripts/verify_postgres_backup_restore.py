from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT.parent / "build" / "p0-05" / "backup-restore.json"
DEFAULT_MARKDOWN = ROOT.parent / "build" / "p0-05" / "backup-restore.md"


def _database_name(url: str) -> str:
    normalized = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return urlparse(normalized).path.lstrip("/")


def _libpq_url(url: str) -> str:
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def _assert_safe_pair(source_url: str, restore_url: str, allow_unsafe: bool) -> None:
    for label, url in (("source", source_url), ("restore", restore_url)):
        if not url.startswith(("postgresql://", "postgresql+psycopg://")):
            raise RuntimeError(f"P0-05 requires PostgreSQL URLs; {label} is invalid.")
        name = _database_name(url).lower()
        if not allow_unsafe and not any(token in name for token in ("test", "p0_05", "p005", "restore", "backup")):
            raise RuntimeError(
                f"Refusing P0-05 against {label} database '{name}'. "
                "Use dedicated test databases or --allow-unsafe-database explicitly."
            )
    if _database_name(source_url) == _database_name(restore_url):
        raise RuntimeError("Source and restore databases must be different.")


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _table_snapshot(url: str) -> dict[str, int]:
    engine = create_engine(url, pool_pre_ping=True)
    try:
        inspector = inspect(engine)
        snapshot: dict[str, int] = {}
        with engine.connect() as connection:
            for table_name in sorted(name for name in inspector.get_table_names() if name != "alembic_version"):
                quoted = connection.dialect.identifier_preparer.quote(table_name)
                snapshot[table_name] = int(connection.execute(text(f"SELECT COUNT(*) FROM {quoted}")).scalar_one())
        return snapshot
    finally:
        engine.dispose()


def _revision(url: str) -> str | None:
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            return connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
    finally:
        engine.dispose()


def _critical_smoke(url: str) -> dict[str, bool]:
    engine = create_engine(url, pool_pre_ping=True)
    required = {
        "tenants",
        "dashboard_users",
        "dashboard_user_tenant_memberships",
        "scans",
        "scan_issues",
        "tenant_scan_credits",
        "tenant_product_entitlements",
    }
    try:
        tables = set(inspect(engine).get_table_names())
        result = {name: name in tables for name in sorted(required)}
        if not all(result.values()):
            missing = [name for name, present in result.items() if not present]
            raise RuntimeError(f"Restored database is missing critical tables: {missing}")
        return result
    finally:
        engine.dispose()


def _write_reports(result: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(
        "# P0-05 PostgreSQL Backup and Restore\n\n"
        f"- **Status:** {result['status']}\n"
        f"- **Started:** {result['started_at_utc']}\n"
        f"- **Source database:** `{result['source_database']}`\n"
        f"- **Restore database:** `{result['restore_database']}`\n"
        f"- **Source revision:** `{result['source_revision']}`\n"
        f"- **Restored revision:** `{result['restored_revision']}`\n"
        f"- **Backup SHA-256:** `{result['backup_sha256']}`\n"
        f"- **Backup size:** {result['backup_size_bytes']} bytes\n"
        f"- **Tables compared:** {result['table_count']}\n"
        f"- **Backup duration:** {result['backup_duration_seconds']:.2f} seconds\n"
        f"- **Restore duration:** {result['restore_duration_seconds']:.2f} seconds\n"
        f"- **Total duration:** {result['duration_seconds']:.2f} seconds\n\n"
        "## Checks\n\n"
        "- Source and restore databases are isolated.\n"
        "- Custom-format `pg_dump` completed successfully.\n"
        "- Restore database was cleaned before `pg_restore`.\n"
        "- Alembic revision is identical after restore.\n"
        "- Row counts for every application table are identical.\n"
        "- Critical tenant, membership, scan, finding, credit and entitlement tables exist.\n",
        encoding="utf-8",
    )


def run(source_url: str, restore_url: str, json_path: Path, markdown_path: Path, allow_unsafe: bool = False) -> dict[str, Any]:
    _assert_safe_pair(source_url, restore_url, allow_unsafe)
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    source_revision = _revision(source_url)
    source_snapshot = _table_snapshot(source_url)

    with tempfile.TemporaryDirectory(prefix="bcsentinel-p0-05-") as temp_dir:
        dump_path = Path(temp_dir) / "bcsentinel.dump"
        backup_started = time.monotonic()
        _run([
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(dump_path),
            _libpq_url(source_url),
        ])
        backup_duration = time.monotonic() - backup_started
        if not dump_path.exists() or dump_path.stat().st_size == 0:
            raise RuntimeError("Backup file was not created or is empty.")

        restore_started = time.monotonic()
        _run([
            "pg_restore",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "--exit-on-error",
            "--dbname",
            _libpq_url(restore_url),
            str(dump_path),
        ])
        restore_duration = time.monotonic() - restore_started

        restored_revision = _revision(restore_url)
        restored_snapshot = _table_snapshot(restore_url)
        if source_revision != restored_revision:
            raise RuntimeError(
                f"Alembic revision mismatch after restore: {source_revision!r} != {restored_revision!r}"
            )
        if source_snapshot != restored_snapshot:
            differing = sorted(
                set(source_snapshot) ^ set(restored_snapshot)
                | {name for name in set(source_snapshot) & set(restored_snapshot) if source_snapshot[name] != restored_snapshot[name]}
            )
            raise RuntimeError(f"Table count mismatch after restore: {differing}")
        smoke = _critical_smoke(restore_url)

        result = {
            "status": "PASS",
            "started_at_utc": started_at,
            "source_database": _database_name(source_url),
            "restore_database": _database_name(restore_url),
            "source_revision": source_revision,
            "restored_revision": restored_revision,
            "backup_sha256": _sha256(dump_path),
            "backup_size_bytes": dump_path.stat().st_size,
            "table_count": len(source_snapshot),
            "critical_tables": smoke,
            "backup_duration_seconds": backup_duration,
            "restore_duration_seconds": restore_duration,
            "duration_seconds": time.monotonic() - started,
        }
        _write_reports(result, json_path, markdown_path)
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify P0-05 PostgreSQL backup and isolated restore.")
    parser.add_argument("--source-url", default=os.getenv("BCSENTINEL_P0_05_SOURCE_DATABASE_URL"))
    parser.add_argument("--restore-url", default=os.getenv("BCSENTINEL_P0_05_RESTORE_DATABASE_URL"))
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--allow-unsafe-database", action="store_true")
    args = parser.parse_args()
    if not args.source_url or not args.restore_url:
        parser.error("source and restore database URLs are required")
    result = run(args.source_url, args.restore_url, args.json_out, args.markdown_out, args.allow_unsafe_database)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
