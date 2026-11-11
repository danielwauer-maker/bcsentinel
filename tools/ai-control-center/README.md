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

The workbook is not modified. The parser uses the verified DEV-first v2 tabs and exact ranges: `Sprint-Tracker!A3:X63` (IDs in A, technical mark U, acceptance mark V) and `SaaS-Stripe Roadmap!A9:M32` (technical mark J, acceptance mark K). It requires 61/24 tasks and exact SHA-256. Future workbook revisions must be reconciled and their hash updated deliberately. Evidence overlays provide **review notes**, never spreadsheet writes.

The actual latest uploaded Excel was inspected on **2026-11-11**:
`BCSentinel_GoLive_Master_Tracker_DEV_First_v2(1).xlsx`.
SHA-256: `c1978141c8ee70f52be07ba64df765364a56cb16fe51dea4b084951ade60142a`.
Verified tabs: Dashboard, Sprint-Tracker, Anleitung & Gates, Parallelplan, SaaS-Stripe Roadmap, DEV-Release-Regeln.
Canonical counts: **61 Fiverr tasks**, with **2 technical and 2 separate acceptance checkmarks**; **24 SaaS tasks**, with zero checkmarks. The Excel is the authoritative planning source. To avoid committing an internal binary workbook, the exact source file is mounted read-only as `data/master-tracker.xlsx` on the operator server. The repo includes a **clearly labeled immutable review snapshot** and curated GitHub evidence in `data/evidence-status.json`. Without the mounted Excel the dashboard displays snapshot counts rather than claiming live synchronization.

## Evidence reconciliation (11 November 2026)

- `6.02`: PR #166 documents DE/EN website content, report samples, 42-row content mapping and design audit. **Editorial complete; implementation, visual QA and release open**.
- `7.03`: PR #165 documents complete DE/EN Fiverr Buyer Kit and buyer journey. **Editorial complete; Fiverr/editor/customer E2E and launch open**.
- `4.01`: PR #164 documents Access-v2 contract audit. **Audit Draft; contract approval and regression open**.
- `2.01` / 3B.01: feature branch includes 199-check coverage matrix, lifecycle report and reported local backend suite (961 passed, 22 skipped, 2 xfailed); **final-SHA CI/AL and BC27 tests still block technical completion**.
- `2.02` and 3A.2: PRs #159/#162 provide partial evidence/Provenance architecture; real BC upgrade and scan comparison open.
- `4.02–4.04,4.06`: Access-v2/operator implementation drafts #154/#156; no release contract/BC E2E acceptance.
- `1.01/1.02`: Excel already contains checked technical and acceptance cells; they remain verbatim, with documented need to recheck artifacts and current DEV deployment before the next BC step.

The dashboard **never converts GitHub progress into Excel checkmarks** and never equates documentation readiness with technical or Go-Live readiness.

## MVP boundaries / next milestones

1. Copy the verified, uploaded XLSX to the private server as `data/master-tracker.xlsx` (read-only). Confirm hash and verify UI with live workbook loaded.
2. Implement evidence-linked lifecycle states (work completed ≠ accepted ≠ production release), SHA/CI checks and master tracker synchronization rules.
3. Add time-window change report (since yesterday), branch health, release snapshot, and authenticated operator approvals.
4. Add agent-job queue with only one concurrent worker, explicit cost cap, audit logging, and no automatic production operations.
5. Add test fixtures for adapter, mocked GitHub API, auth, error states, and accessibility/UI/browser QA.

### Safety

No merges, deployments, GitHub writes, AI billing, PROD changes, or customer-data access are implemented. The public-facing webserver must never expose this dashboard without authentication and TLS. Daily refresh currently happens on page load or button click; no background cron/agent scheduler exists yet.
