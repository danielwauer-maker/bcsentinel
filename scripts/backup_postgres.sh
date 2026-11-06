#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:-./artifacts/recovery}"
mkdir -p "$OUTPUT_DIR"

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGUSER:?PGUSER is required}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DUMP_NAME="bcsentinel-${STAMP}.dump"
DUMP_PATH="$OUTPUT_DIR/$DUMP_NAME"
SHA_PATH="${DUMP_PATH}.sha256"
MANIFEST_PATH="${DUMP_PATH}.manifest.json"

pg_dump \
  --format=custom \
  --no-owner \
  --no-privileges \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --dbname="$PGDATABASE" \
  --file="$DUMP_PATH"

# Keep the checksum entry relocatable: an off-host backup directory may be
# moved to another path before verification/restore.
(
  cd "$OUTPUT_DIR"
  sha256sum "$DUMP_NAME" > "${DUMP_NAME}.sha256"
)
ALEMBIC_VERSION="$(psql --host="$PGHOST" --port="$PGPORT" --username="$PGUSER" --dbname="$PGDATABASE" --tuples-only --no-align --command='SELECT version_num FROM alembic_version LIMIT 1;' | tr -d '[:space:]')"
DUMP_SHA="$(cut -d' ' -f1 "$SHA_PATH")"
DUMP_SIZE="$(stat -c%s "$DUMP_PATH")"

python - "$MANIFEST_PATH" "$STAMP" "$PGDATABASE" "$ALEMBIC_VERSION" "$DUMP_SHA" "$DUMP_SIZE" <<'PY'
import json
import sys
from pathlib import Path

path, stamp, database, alembic, sha256, size = sys.argv[1:]
manifest = {
    "schema_version": "1.0.0",
    "created_at_utc": stamp,
    "database": database,
    "alembic_version": alembic,
    "sha256": sha256,
    "size_bytes": int(size),
    "format": "postgresql-custom",
}
Path(path).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

printf '%s\n' "$DUMP_PATH"
