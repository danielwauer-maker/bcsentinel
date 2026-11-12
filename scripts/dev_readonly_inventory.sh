#!/usr/bin/env bash
# Read-only DEV pre-deployment inventory. No credentials/values printed or modified.
# Run on the Hetzner host as the normal DEV deploy user.
set -euo pipefail

ROOT="${1:-/home/daniel/data-health-management-dev}"
cd "$ROOT"
COMPOSE=(docker compose -f docker-compose.dev.yml --env-file .env.dev)
printf 'inventory_timestamp_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'checkout=%s\n' "$(pwd -P)"
printf 'git_head=%s\n' "$(git rev-parse HEAD)"
printf 'git_branch=%s\n' "$(git branch --show-current)"
if test -n "$(git status --porcelain --untracked-files=no)"; then
  echo 'working_tree_tracked=DIRTY'
else
  echo 'working_tree_tracked=CLEAN'
fi
printf '\n=== services ===\n'
"${COMPOSE[@]}" ps --format 'table {{.Service}}\t{{.Image}}\t{{.Status}}' || true
printf '\n=== selected container image IDs ===\n'
for name in dhm-dev-backend dhm-dev-postgres; do
  if docker container inspect "$name" >/dev/null 2>&1; then
    docker inspect --format 'name={{.Name}} image_id={{.Image}} status={{.State.Status}}' "$name"
  else
    printf 'name=%s status=NOT_FOUND\n' "$name"
  fi
done
printf '\n=== backend readiness (no body dump) ===\n'
if curl --max-time 8 --fail --silent --output /dev/null http://127.0.0.1:8001/health/ready; then
  echo 'backend_ready=PASS'
else
  echo 'backend_ready=FAIL'
fi
printf '\n=== migration head (no credentials output) ===\n'
# Runs a read-only alembic current in the existing backend container; does not upgrade.
if docker container inspect dhm-dev-backend >/dev/null 2>&1; then
  docker exec dhm-dev-backend alembic current || echo 'alembic_current=NOT_AVAILABLE'
else
  echo 'alembic_current=NOT_AVAILABLE'
fi
printf '\n=== configured feature flag NAMES only ===\n'
# Do not print .env.dev values or secret configuration.
if test -f .env.dev; then
  grep -E '^[[:space:]]*(ACCESS_MODEL_V2_ENABLED|ACCESS_V2_PAID_CHECKOUT_ENABLED)=' .env.dev \
     | sed -E 's/=.*/=<REDACTED>/' || true
fi
printf '\n=== nginx validation (read-only) ===\n'
if command -v nginx >/dev/null 2>&1; then
  if sudo -n nginx -t >/dev/null 2>&1; then
    echo 'nginx_config_syntax=PASS'
  else
    echo 'nginx_config_syntax=UNVERIFIED'
  fi
fi
echo 'inventory_mode=READ_ONLY'
