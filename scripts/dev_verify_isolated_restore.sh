#!/usr/bin/env bash
# BCSentinel DEV: restore an existing PostgreSQL custom-format dump into an isolated
# throwaway PostgreSQL 15 container. No network, no volume mounts, no live DB changes.
set -euo pipefail

BACKUP_FILE="${1:-/home/daniel/bcsentinel-dev-backups/dev-pre-pr172-20261112T210953Z.dump}"
EXPECTED_SHA="540657ed371e797bde5b2463ec8f50eb87c94033ee2870bc9b869348b79592c1"
EXPECTED_MIGRATION="0040_scan_record_identity_evidence"
RESTORE_CONTAINER="bcsentinel-dev-restore-check-$$"

cleanup() {
  docker rm -f "$RESTORE_CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

if [[ ! -f "$BACKUP_FILE" || ! -r "$BACKUP_FILE" || ! -s "$BACKUP_FILE" ]]; then
  echo 'FAIL: expected readable nonempty local backup file' >&2
  exit 1
fi
ACTUAL_SHA="$(sha256sum "$BACKUP_FILE" | awk '{print $1}')"
if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
  echo 'FAIL: backup SHA256 does not match operator evidence' >&2
  exit 1
fi

echo 'backup_sha256=PASS'
echo 'isolation=network_none_no_host_ports_no_live_volumes'
docker run -d --rm --name "$RESTORE_CONTAINER" \
  --network none \
  --tmpfs /var/lib/postgresql/data:rw,size=536870912 \
  -e POSTGRES_PASSWORD=temporary-restore-test-only \
  postgres:15 >/dev/null

READY=0
for i in $(seq 1 60); do
  if docker exec "$RESTORE_CONTAINER" pg_isready -U postgres -d postgres >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done
if [[ "$READY" -ne 1 ]]; then
  echo 'FAIL: temporary PostgreSQL did not become ready' >&2
  exit 1
fi

docker exec "$RESTORE_CONTAINER" createdb -U postgres dev_restore_verify
docker exec -i "$RESTORE_CONTAINER" pg_restore \
  -U postgres -d dev_restore_verify --no-owner --no-acl \
  --exit-on-error --single-transaction < "$BACKUP_FILE"

MIGRATION="$(docker exec "$RESTORE_CONTAINER" psql -U postgres -d dev_restore_verify -Atq -c 'SELECT version_num FROM alembic_version;')"
if [[ "$MIGRATION" != "$EXPECTED_MIGRATION" ]]; then
  echo "FAIL: unexpected migration ID in restored dump: $MIGRATION" >&2
  exit 1
fi

TABLE_COUNT="$(docker exec "$RESTORE_CONTAINER" psql -U postgres -d dev_restore_verify -Atq -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")"
if ! [[ "$TABLE_COUNT" =~ ^[0-9]+$ ]] || [[ "$TABLE_COUNT" -lt 1 ]]; then
  echo 'FAIL: restored database has no public base tables' >&2
  exit 1
fi

echo 'restore_transaction=PASS'
echo "restored_migration=$MIGRATION"
echo "restored_public_table_count=$TABLE_COUNT"
echo 'temporary_container_cleanup=scheduled_on_exit'
echo 'RESTORE_TEST=PASS'
