#!/usr/bin/env bash
# Private DEV operator deployment; DO NOT run in the existing BCSentinel app checkout.
set -Eeuo pipefail
umask 077

BASE="${HOME}/bcsentinel-ai-control-center"
REPO="git@github.com:danielwauer-maker/bcsentinel.git"
BRANCH="feature/ai-control-center-mvp"
ARCHIVE="${1:?Usage: ./install-on-server.sh /path/to/master-tracker.xlsx}"
EXPECTED="c1978141c8ee70f52be07ba64df765364a56cb16fe51dea4b084951ade60142a"

if [[ ! -f "$ARCHIVE" ]]; then echo "Excel missing: $ARCHIVE" >&2; exit 1; fi
ACTUAL="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "Refusing import: workbook SHA mismatch; got $ACTUAL" >&2; exit 2
fi
command -v docker >/dev/null || { echo "Docker missing" >&2; exit 1; }
docker compose version >/dev/null || { echo "Docker Compose missing" >&2; exit 1; }

if [[ -e "$BASE" ]]; then
  echo "Target exists: $BASE. No automatic overwrite or git reset allowed." >&2
  exit 3
fi
mkdir -p "$BASE"
trap 'echo "Install interrupted; inspect $BASE before retry" >&2' ERR
git clone --depth=1 --branch "$BRANCH" "$REPO" "$BASE/repo"
cd "$BASE/repo/tools/ai-control-center"
mkdir -p data state
cp "$ARCHIVE" data/master-tracker.xlsx
chmod 600 data/master-tracker.xlsx
sudo chown 10001:10001 state
chmod 700 state
if [[ ! -f .env ]]; then
  cat > .env <<'ENVFILE'
# Replace secrets locally; NEVER commit this file.
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=REPLACE_ME_WITH_RANDOM_PASSWORD
# Optional read-only fine-grained GitHub token with read access to core + frontend.
GITHUB_TOKEN=
ENVFILE
  chmod 600 .env
fi

cat <<'INFO'
Staged private AI Control Center checkout.
Before running:
  1. Edit .env and set a strong DASHBOARD_PASSWORD. Optionally a read-only GITHUB_TOKEN.
  2. Keep 127.0.0.1:8090 private; only access with SSH tunnel or an HTTPS-authenticated VPN.
  3. Inspect compose.example.yml and Dockerfile.
  4. Run: docker compose -f compose.example.yml up -d --build
  5. Run: docker compose -f compose.example.yml exec ai-control-center python project_store.py import
  6. Verify: docker compose -f compose.example.yml exec ai-control-center python project_store.py status

Nothing was deployed by this script. No BCSentinel service or existing checkout was modified.
INFO
