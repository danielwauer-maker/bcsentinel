#!/usr/bin/env bash
set -euo pipefail

DUMP_PATH="${1:?Usage: restore_postgres.sh <dump-path>}"
: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGUSER:?PGUSER is required}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

if [[ ! -f "$DUMP_PATH" ]]; then
  echo "Backup artifact not found: $DUMP_PATH" >&2
  exit 2
fi
if [[ ! -f "${DUMP_PATH}.sha256" ]]; then
  echo "Checksum file not found: ${DUMP_PATH}.sha256" >&2
  exit 2
fi

(
  cd "$(dirname "$DUMP_PATH")"
  sha256sum --check "$(basename "${DUMP_PATH}.sha256")"
)

pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --dbname="$PGDATABASE" \
  "$DUMP_PATH"

psql \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --dbname="$PGDATABASE" \
  --set=ON_ERROR_STOP=1 \
  --command='SELECT version_num FROM alembic_version LIMIT 1;'
