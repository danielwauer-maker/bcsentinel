# BCSentinel AI Control Center · MVP 0.1

Read-only dashboard for the DEV-first BCSentinel project. It is **not** a customer-facing SaaS component and does not start autonomous agents.

## Sources and authority

- Master-Tracker Excel: primary planning/task authority (mounted read-only from `./data/master-tracker.xlsx`).
- GitHub: live technical PR state from `danielwauer-maker/bcsentinel` and `danielwauer-maker/bcsentinel-frontend`.
- DEV API: configured `/health/ready` endpoint, connectivity only.
- `docs/BCSENTINEL_MASTER_STATE.md` and `release/current-product-state.json` on reviewed `main`: versioned product baseline, **not necessarily current Sprint or deployed DEV truth**.
- Branches and PRs are evidence-in-progress, not a completed acceptance. **Technically finished**, **DEV accepted**, and **Go-Live approved** are independent gates. This MVP intentionally displays all gates as **not verified** until evidence-specific adapters exist.
- No product-readiness percentage inferred from counts of Excel rows or PRs. Any missing/unavailable source is **unknown**, never healthy/completed.

## Local development

```bash
cd tools/ai-control-center
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
mkdir -p data
export DASHBOARD_USER=admin
export DASHBOARD_PASSWORD='replace-with-a-long-random-secret'
export GITHUB_TOKEN='fine-grained-read-only-token'
export TRACKER_PATH="$PWD/data/master-tracker.xlsx"
export DEV_HEALTH_URL='https://dev-api.bcsentinel.com/health/ready'
python app.py
# Open http://127.0.0.1:8090 only locally or through a private TLS proxy.
```

The Python app binds to all interfaces in its own process. For local development use a firewall / Docker's loopback port mapping; do not expose the raw HTTP port to the Internet.

## Deployment candidate (NOT deployed)

```bash
cd tools/ai-control-center
mkdir -p data
# Place verified current Master-Tracker (not an older handoff copy) at:
# data/master-tracker.xlsx
# Set DASHBOARD_USER, DASHBOARD_PASSWORD, GITHUB_TOKEN in local uncommitted .env
docker compose -f compose.example.yml up -d --build
```

Use an **operator-protected HTTPS reverse proxy or VPN**; HTTP Basic auth must not be exposed over plaintext public HTTP. Do not reuse BCSentinel PROD customer credentials or database. Never place GitHub tokens, tracker files, or `.env` into Git. Fine-grained GitHub token: read-only metadata and pull requests for the two repos.

## Excel handling

The workbook is not modified. The loader reads every worksheet, finds probable header rows in the first 20 rows, and maps only recognizable task/status columns. It reports skipped sheets as `mapped: false`. Original status text is shown unmodified. Sheet mapping is a **provisional parser**, not a validated interpretation of the authoritative workbook. Once the exact latest workbook is attached/mounted, inspect its sheet names, headers, formulas, and task-ID mapping, and add fixture-based tests before treating aggregates as reliable.

The currently reported newest named file is `BCSentinel_GoLive_Master_Tracker_DEV_11112026_Sprint3B01_Update.xlsx`. The source workbook was **not accessible during implementation**; no unverified/older copy was committed. The documented planning scope from recent work contains 61 Fiverr tasks and 24 separate SaaS tasks, but these are **not** live dashboard totals until reconciled against the Excel.

## MVP boundaries / next milestones

1. Obtain and hash-verify current XLSX; map exact workbook schema and separate Fiverr vs SaaS.
2. Implement evidence-linked lifecycle states (work completed ≠ accepted ≠ production release), SHA/CI checks and master tracker synchronization rules.
3. Add time-window change report (since yesterday), branch health, release snapshot, and authenticated operator approvals.
4. Add agent-job queue with only one concurrent worker, explicit cost cap, audit logging, and no automatic production operations.
5. Add test fixtures for adapter, mocked GitHub API, auth, error states, and accessibility/UI/browser QA.

### Safety

No merges, deployments, GitHub writes, AI billing, PROD changes, or customer-data access are implemented. The public-facing webserver must never expose this dashboard without authentication and TLS. Daily refresh currently happens on page load or button click; no background cron/agent scheduler exists yet.
