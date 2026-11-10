#!/usr/bin/env bash
# Read-only Sprint 3A.2 DEV release preflight. Does not fetch, deploy, migrate,
# build, restart, prune, copy secrets or change nginx.
set -euo pipefail

EXPECTED_SHA="43ab35c8187bf63e71b6bfc7a6e2f8b7b8cfdb5d"
DEV_DIR="/home/daniel/data-health-management-dev"
TEST_CODE="${HOME}/bcsentinel-migration-0040-code"
BACKUP="${HOME}/bcsentinel-backups/dev/dev_before_0040_20261110_180353.dump"
BACKUP_SHA="90f8c4db7ebb71b33f4b5361790d211faf99cb1260a0b8d8d1297c2292972626"
FAILURES=0
fail() { printf 'NO-GO: %s\n' "$*" >&2; FAILURES=$((FAILURES+1)); }
ok() { printf 'PASS: %s\n' "$*"; }

[ -d "$DEV_DIR/.git" ] || [ -e "$DEV_DIR/.git" ] || fail "Missing DEV Git checkout."
[ -f "$TEST_CODE/backend/alembic/versions/0040_scan_record_identity_evidence.py" ] || fail "Missing isolated 0040 migration."
[ -f "$BACKUP" ] || fail "Missing baseline DEV backup."

if [ -f "$BACKUP" ]; then
    CHECKED_SHA=$(sha256sum "$BACKUP" | awk '{print $1}')
    [ "$CHECKED_SHA" = "$BACKUP_SHA" ] && ok "Backup SHA matches sealed baseline" || fail "Backup checksum differs."
fi

if git -C "$TEST_CODE" rev-parse --verify HEAD >/dev/null 2>&1; then
    TEST_SHA=$(git -C "$TEST_CODE" rev-parse HEAD)
    # An older 1.0.2.58 migration-test worktree is expected; do not require
    # it to equal the newer candidate. The release target MUST be pinned.
    printf 'INFO: Migration test worktree SHA %s\n' "$TEST_SHA"
else
    fail "Migration test checkout not available."
fi
printf 'INFO: Approved candidate SHA to review: %s\n' "$EXPECTED_SHA"
printf 'INFO: Remote GitHub workflow evidence must be reviewed separately.\n'

if [ -d "$DEV_DIR" ]; then
    printf 'INFO: DEV checkout HEAD: '
    git -C "$DEV_DIR" rev-parse HEAD || fail "Cannot read DEV checkout HEAD."
    printf 'INFO: DEV worktree status:\n'
    git -C "$DEV_DIR" status --short || fail "Cannot inspect DEV worktree."
    printf 'INFO: Current DEV branch: '
    git -C "$DEV_DIR" symbolic-ref --quiet --short HEAD || printf 'detached HEAD\n'
fi

for name in dhm-dev-postgres dhm-dev-backend bcs-migration-0040-test; do
    if docker container inspect "$name" >/dev/null 2>&1; then
        printf 'INFO: %s: ' "$name"
        docker inspect --format '{{.State.Status}} / {{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$name"
    else
        fail "Container $name not found."
    fi
done

if docker container inspect dhm-dev-postgres >/dev/null 2>&1; then
    DEV_REV=$(docker exec dhm-dev-postgres sh -c 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT version_num FROM alembic_version;"')
    printf 'INFO: Active DEV schema: %s\n' "$DEV_REV"
    [ "$DEV_REV" = "0037_merge_staging_report" ] && ok "DEV remains at sealed pre-migration revision" || fail "Active DEV schema changed; stop and re-plan."
fi
if docker container inspect bcs-migration-0040-test >/dev/null 2>&1; then
    COPY_REV=$(docker exec bcs-migration-0040-test psql -X -v ON_ERROR_STOP=1 -U postgres -d bcs_migration_test -Atc "SELECT version_num FROM alembic_version;")
    printf 'INFO: Isolated copy schema: %s\n' "$COPY_REV"
    [ "$COPY_REV" = "0040_scan_record_identity_evidence" ] && ok "Migrated copy is at 0040" || fail "Isolated copy is not at expected head."
fi

if curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8001/health/ready >/dev/null; then
    ok "Current DEV ready endpoint responds"
else
    fail "Current DEV backend readiness failed."
fi

if [ "$FAILURES" -eq 0 ]; then
    echo "READ-ONLY PREFLIGHT PASS. This is NOT release approval; do not deploy without explicit authorization."
else
    echo "READ-ONLY PREFLIGHT NO-GO: $FAILURES blocking check(s)." >&2
    exit 2
fi
