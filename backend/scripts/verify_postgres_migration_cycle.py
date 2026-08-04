from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import MetaData, Table, create_engine, inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float, Integer, Numeric

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT.parent / "build" / "p0-04" / "migration-cycle.json"
DEFAULT_MARKDOWN = ROOT.parent / "build" / "p0-04" / "migration-cycle.md"
SENTINEL_TENANT_ID = "ten_p0_04_migration_cycle"


def _database_name(url: str) -> str:
    return urlparse(url.replace("postgresql+psycopg://", "postgresql://", 1)).path.lstrip("/")


def _assert_safe_database(url: str, allow_unsafe: bool) -> None:
    if not url.startswith(("postgresql://", "postgresql+psycopg://")):
        raise RuntimeError("P0-04 requires a PostgreSQL DATABASE_URL.")
    database = _database_name(url).lower()
    if not allow_unsafe and not any(token in database for token in ("test", "p0_04", "p004", "migration")):
        raise RuntimeError(
            f"Refusing migration cycle against database '{database}'. "
            "Use a dedicated test database or pass --allow-unsafe-database explicitly."
        )


def _alembic_config(url: str) -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _revision_info(config: Config) -> tuple[str, str]:
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Expected exactly one Alembic head, found {heads!r}.")
    head = script.get_revision(heads[0])
    if head is None or head.down_revision is None:
        raise RuntimeError("The Alembic head has no downgrade target.")
    if isinstance(head.down_revision, tuple):
        raise RuntimeError("The current head is a merge revision; P0-04 needs an explicit rollback target.")
    return head.revision, str(head.down_revision)


def _normalise(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalise(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple, set)):
        return sorted((_normalise(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, default=str))
    return str(value) if value is not None else None


def _schema_snapshot(engine: Engine) -> dict[str, Any]:
    inspector = inspect(engine)
    result: dict[str, Any] = {}
    for table_name in sorted(name for name in inspector.get_table_names() if name != "alembic_version"):
        result[table_name] = {
            "columns": [
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column.get("nullable"),
                    "default": column.get("default"),
                }
                for column in inspector.get_columns(table_name)
            ],
            "pk": inspector.get_pk_constraint(table_name),
            "foreign_keys": inspector.get_foreign_keys(table_name),
            "unique_constraints": inspector.get_unique_constraints(table_name),
            "indexes": inspector.get_indexes(table_name),
        }
    return _normalise(result)


def _schema_hash(snapshot: dict[str, Any]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _current_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()


def _generic_value(column: Any) -> Any:
    if isinstance(column.type, Boolean):
        return False
    if isinstance(column.type, (Integer, Float, Numeric)):
        return 0
    if isinstance(column.type, DateTime):
        return datetime.now(timezone.utc)
    return f"p0_04_{column.name}"[: max(1, getattr(column.type, "length", 120) or 120)]


def _insert_sentinel_tenant(engine: Engine) -> None:
    metadata = MetaData()
    tenants = Table("tenants", metadata, autoload_with=engine)
    values: dict[str, Any] = {}
    for column in tenants.columns:
        if column.name == "tenant_id":
            values[column.name] = SENTINEL_TENANT_ID
        elif column.primary_key and (column.autoincrement is True or column.autoincrement == "auto"):
            continue
        elif column.server_default is not None or column.default is not None or column.nullable:
            continue
        else:
            values[column.name] = _generic_value(column)
    with engine.begin() as connection:
        connection.execute(tenants.delete().where(tenants.c.tenant_id == SENTINEL_TENANT_ID))
        connection.execute(tenants.insert().values(**values))


def _assert_sentinel_tenant(engine: Engine) -> None:
    metadata = MetaData()
    tenants = Table("tenants", metadata, autoload_with=engine)
    with engine.connect() as connection:
        found = connection.execute(
            select(tenants.c.tenant_id).where(tenants.c.tenant_id == SENTINEL_TENANT_ID)
        ).scalar_one_or_none()
    if found != SENTINEL_TENANT_ID:
        raise RuntimeError("Sentinel tenant was not preserved across downgrade/upgrade.")


def _delete_sentinel_tenant(engine: Engine) -> None:
    metadata = MetaData()
    tenants = Table("tenants", metadata, autoload_with=engine)
    with engine.begin() as connection:
        connection.execute(tenants.delete().where(tenants.c.tenant_id == SENTINEL_TENANT_ID))


def _write_reports(result: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(
        "# P0-04 PostgreSQL Migration Cycle\n\n"
        f"- **Status:** {result['status']}\n"
        f"- **Started:** {result['started_at_utc']}\n"
        f"- **Head revision:** `{result['head_revision']}`\n"
        f"- **Rollback revision:** `{result['rollback_revision']}`\n"
        f"- **Final revision:** `{result['final_revision']}`\n"
        f"- **Schema SHA-256 before:** `{result['schema_hash_before']}`\n"
        f"- **Schema SHA-256 after:** `{result['schema_hash_after']}`\n"
        f"- **Tables verified:** {result['table_count']}\n"
        f"- **Sentinel tenant preserved:** {result['sentinel_preserved']}\n"
        f"- **Duration:** {result['duration_seconds']:.2f} seconds\n\n"
        "## Cycle\n\n"
        "1. Upgrade dedicated PostgreSQL database to `head`.\n"
        "2. Capture deterministic schema fingerprint.\n"
        "3. Insert a non-production sentinel tenant.\n"
        "4. Downgrade to the direct parent of `head`.\n"
        "5. Upgrade to `head` again.\n"
        "6. Confirm revision, schema equality and sentinel preservation.\n",
        encoding="utf-8",
    )


def run(url: str, json_path: Path, markdown_path: Path, allow_unsafe: bool = False) -> dict[str, Any]:
    _assert_safe_database(url, allow_unsafe)
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    config = _alembic_config(url)
    head_revision, rollback_revision = _revision_info(config)
    engine = create_engine(url, pool_pre_ping=True)
    sentinel_preserved = False
    try:
        command.upgrade(config, "head")
        if _current_revision(engine) != head_revision:
            raise RuntimeError("Initial upgrade did not reach the expected Alembic head.")
        before = _schema_snapshot(engine)
        before_hash = _schema_hash(before)
        _insert_sentinel_tenant(engine)

        command.downgrade(config, rollback_revision)
        if _current_revision(engine) != rollback_revision:
            raise RuntimeError("Downgrade did not reach the expected rollback revision.")

        command.upgrade(config, "head")
        final_revision = _current_revision(engine)
        if final_revision != head_revision:
            raise RuntimeError("Final upgrade did not return to the expected Alembic head.")
        after = _schema_snapshot(engine)
        after_hash = _schema_hash(after)
        if before != after:
            raise RuntimeError("Schema drift detected after upgrade/downgrade/upgrade cycle.")
        _assert_sentinel_tenant(engine)
        sentinel_preserved = True

        result = {
            "status": "PASS",
            "started_at_utc": started_at,
            "head_revision": head_revision,
            "rollback_revision": rollback_revision,
            "final_revision": final_revision,
            "schema_hash_before": before_hash,
            "schema_hash_after": after_hash,
            "table_count": len(after),
            "sentinel_preserved": sentinel_preserved,
            "duration_seconds": time.monotonic() - started,
        }
        _write_reports(result, json_path, markdown_path)
        return result
    finally:
        if sentinel_preserved:
            _delete_sentinel_tenant(engine)
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the P0-04 PostgreSQL Alembic migration cycle.")
    parser.add_argument("--database-url", default=os.getenv("BCSENTINEL_P0_04_DATABASE_URL"))
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--allow-unsafe-database", action="store_true")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or BCSENTINEL_P0_04_DATABASE_URL is required")
    result = run(args.database_url, args.json_out, args.markdown_out, args.allow_unsafe_database)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
