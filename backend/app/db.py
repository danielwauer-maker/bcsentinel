import time
import logging
from functools import lru_cache
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.schema import DefaultClause

from app.core.settings import settings

logger = logging.getLogger(__name__)
BACKEND_DIR = Path(__file__).resolve().parents[1]
_SQLITE_DEFAULT_BACKUP_KEY = "_sqlite_server_default_backups"


class Base(DeclarativeBase):
    pass


@event.listens_for(Base.metadata, "before_create")
def _normalize_sqlite_server_defaults(metadata, connection, **_kwargs) -> None:
    """Temporarily adapt PostgreSQL defaults for ORM-created SQLite test schemas.

    Production schemas remain managed by Alembic on PostgreSQL. SQLite is used by
    the backend regression suite, where ``DEFAULT now()`` is invalid DDL. The
    original metadata defaults are restored after schema creation so metadata
    contracts continue to represent the PostgreSQL production schema exactly.
    """

    if connection.dialect.name != "sqlite":
        return

    backups: list[tuple[object, object]] = []
    for table in metadata.tables.values():
        for column in table.columns:
            server_default = column.server_default
            if server_default is None:
                continue
            default_argument = getattr(server_default, "arg", None)
            if str(default_argument).strip().lower() == "now()":
                backups.append((column, server_default))
                column.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))

    metadata.info[_SQLITE_DEFAULT_BACKUP_KEY] = backups


@event.listens_for(Base.metadata, "after_create")
def _restore_postgresql_server_defaults(metadata, connection, **_kwargs) -> None:
    """Restore production metadata after temporary SQLite DDL normalization."""

    if connection.dialect.name != "sqlite":
        return

    backups = metadata.info.pop(_SQLITE_DEFAULT_BACKUP_KEY, [])
    for column, server_default in backups:
        column.server_default = server_default


engine_kwargs = {
    "future": True,
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def wait_for_database(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return
        except OperationalError as exc:
            last_error = exc
            logger.warning(
                "Database not ready yet. Retrying.",
                extra={
                    "event": "database_wait_retry",
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "delay_seconds": delay_seconds,
                },
            )
            time.sleep(delay_seconds)

    raise RuntimeError("Database did not become ready in time.") from last_error


@lru_cache(maxsize=1)
def get_required_alembic_revision() -> str:
    alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    script = ScriptDirectory.from_config(alembic_config)
    heads = script.get_heads()

    if len(heads) != 1:
        raise RuntimeError(
            f"Expected exactly one Alembic head, found {len(heads)}: {', '.join(heads)}"
        )

    return heads[0]


def ensure_schema_is_migrated(required_revision: str | None = None) -> None:
    resolved_required_revision = required_revision or get_required_alembic_revision()
    inspector = inspect(engine)

    if "alembic_version" not in inspector.get_table_names():
        raise RuntimeError(
            "Database schema is not managed by Alembic yet. "
            "Run 'alembic upgrade head' before starting the API."
        )

    with engine.connect() as connection:
        version = connection.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar()

    if version != resolved_required_revision:
        raise RuntimeError(
            f"Database schema revision mismatch. Expected Alembic head "
            f"'{resolved_required_revision}', got '{version}'. "
            "Run 'alembic upgrade head' before starting the API."
        )
