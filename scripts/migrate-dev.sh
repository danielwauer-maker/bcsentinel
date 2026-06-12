#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.dev.yml}"
BACKEND_SERVICE="${BACKEND_SERVICE:-backend}"
POSTGRES_SERVICE="${POSTGRES_SERVICE:-postgres}"

cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI was not found on PATH." >&2
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: Compose file '$COMPOSE_FILE' was not found in $ROOT_DIR." >&2
  exit 1
fi

if [ ! -f ".env.dev" ]; then
  echo "ERROR: .env.dev was not found in $ROOT_DIR." >&2
  exit 1
fi

echo "==> Ensuring dev database container is running"
docker compose -f "$COMPOSE_FILE" up -d "$POSTGRES_SERVICE"

echo "==> Waiting for dev database readiness"
attempt=1
while [ "$attempt" -le 30 ]; do
  if docker compose -f "$COMPOSE_FILE" exec -T "$POSTGRES_SERVICE" sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
    break
  fi
  if [ "$attempt" -eq 30 ]; then
    echo "ERROR: dev database did not become ready in time." >&2
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep 2
done

echo "==> Stopping dev backend so a schema mismatch restart loop cannot interfere"
docker compose -f "$COMPOSE_FILE" stop "$BACKEND_SERVICE" >/dev/null 2>&1 || true

if [ "${SKIP_BUILD:-0}" != "1" ]; then
  echo "==> Building backend image"
  docker compose -f "$COMPOSE_FILE" build "$BACKEND_SERVICE"
fi

echo "==> Current Alembic revision before migration"
docker compose -f "$COMPOSE_FILE" run --rm --no-deps "$BACKEND_SERVICE" python -m alembic current || true

echo "==> Running Alembic migrations"
docker compose -f "$COMPOSE_FILE" run --rm --no-deps "$BACKEND_SERVICE" python -m alembic upgrade head

echo "==> Alembic revision after migration"
docker compose -f "$COMPOSE_FILE" run --rm --no-deps "$BACKEND_SERVICE" python -m alembic current

echo "==> Starting dev backend"
docker compose -f "$COMPOSE_FILE" up -d "$BACKEND_SERVICE"

echo "==> Container status"
docker compose -f "$COMPOSE_FILE" ps

echo "Done. Verify with:"
echo "  curl http://127.0.0.1:8001/health/ready"
echo "  curl http://127.0.0.1:8001/openapi.json | grep executive"
