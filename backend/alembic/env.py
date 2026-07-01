from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Column, MetaData, String, Table, engine_from_config, inspect, pool

from app.core.settings import settings
from app.db import Base
from app import models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
VERSION_TABLE_NAME = "alembic_version"
VERSION_NUM_LENGTH = 255


def ensure_version_table_supports_long_revisions(connection) -> None:
    inspector = inspect(connection)

    if VERSION_TABLE_NAME in inspector.get_table_names():
        return

    version_metadata = MetaData()
    version_table = Table(
        VERSION_TABLE_NAME,
        version_metadata,
        Column("version_num", String(VERSION_NUM_LENGTH), primary_key=True, nullable=False),
    )
    version_table.create(connection)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        ensure_version_table_supports_long_revisions(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            version_table=VERSION_TABLE_NAME,
            version_table_pk=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
