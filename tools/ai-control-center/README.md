# BCSentinel AI Control Center · MVP 0.1

Read-only dashboard for the DEV-first BCSentinel project. It is **not** a customer-facing SaaS component and does not start autonomous agents.

## Sources and authority

- Master-Tracker Excel: authoritative historical import source; after the verified one-time import, the durable project task register is the operational task authority (mounted workbook remains read-only).
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

## Phase 2: durable task register (implemented in Draft PR, NOT deployed)

The same uploaded SHA-256-verified master is imported **once** into a separate SQLite database. This does not require PostgreSQL, new server costs, any OpenAI calls, or a write connection to the BCSentinel customer DB.

Before starting Docker, create a state directory writable by the unprivileged container UID 10001 and put the *exact* uploaded XLSX under the private `data/` mount:

```bash
cd tools/ai-control-center
mkdir -p data state
sudo chown 10001:10001 state
sha256sum data/master-tracker.xlsx
# MUST match c1978141c8ee70f52be07ba64df765364a56cb16fe51dea4b084951ade60142a
# Set credentials in an uncommitted .env with chmod 600; use a read-only GitHub token
docker compose -f compose.example.yml up -d --build
docker compose -f compose.example.yml exec ai-control-center python project_store.py import
docker compose -f compose.example.yml exec ai-control-center python project_store.py status
```

Database is at `state/projects.sqlite3` and is **not in Git**; include it in encrypted/off-host backups. The import is transactional, checks 61+24 distinct IDs and refuses re-import from a changed SHA. A repeated identical import is a no-op. The source workbook stays unchanged and may be archived after the initial verified import. An updated workbook is **not** silently synchronized; reconcile it explicitly with the durable register.

Imported checkbox states are historical source metadata, **not newly granted approvals**. Human approval records are a separate table. There is **no public write API**. An operator can change ordinary task stages with the audited CLI below, but cannot mark technical acceptance, DEV acceptance or Go-Live through it. No AI agent can approve itself. GitHub PRs and workflow results are shown as observed evidence, not written to task completion gates.

The dashboard now returns a separate `project_store` object containing tasks, import provenance, immutable import audit event and approval records. The HTML shows the current database state when initialized, or a clearly labeled not-yet-imported state.

### Audited manual task update (no Excel edits)

```bash
docker compose -f compose.example.yml exec ai-control-center \
  python project_store.py set-stage \
  --task fiverr:6.02 --stage review --actor operator \
  --reason "Editorial PR complete; implementation and acceptance still pending"
```

Allowed ordinary stages: `planned`, `in_progress`, `implementation_candidate`, `review`, `blocked`. This operation appends an audit event. It **cannot** set `technical_complete`, `dev_accepted` or any Go-Live approval. The project register retains every historical Excel checkbox without treating it as a new approval.

### Access and safety before deployment

- The container has a read-only filesystem except for the isolated `/state` volume and `/tmp` tmpfs; the `/data` Excel mount is read-only.
- Only the reverse proxy/VPN may access loopback port 8090. Basic auth requires HTTPS; no public raw port exposure.
- The separate SQLite database carries project metadata, not customer ERP data. Protect the operator dashboard accordingly.
- This is an **operator-run import**, not a startup auto-import; no autonomous changes to repository or project gates occur.

## Isolated installation handoff

The project contains `install-on-server.sh`. It verifies the exact uploaded Excel SHA, clones the current feature branch into a **new separate** `~/bcsentinel-ai-control-center` directory and stages a minimal local `.env`. It **does not** deploy, change DNS, alter existing Docker services, or initialize the database automatically.

For operator use after transferring the Excel file to the server:

```bash
bash install-on-server.sh /path/to/BCSentinel_GoLive_Master_Tracker_DEV_First_v2\(1\).xlsx
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
nano .env  # replace placeholder with a strong password; set read-only GitHub token
docker compose -f compose.example.yml up -d --build
docker compose -f compose.example.yml exec ai-control-center python project_store.py import
docker compose -f compose.example.yml exec ai-control-center python project_store.py status
```

To inspect the UI without exposing it publicly, from your laptop establish an SSH tunnel:
`ssh -L 8090:127.0.0.1:8090 <ssh-user>@<server>`, then open `http://127.0.0.1:8090` locally. Avoid adding a public proxy until private HTTPS authentication, identity, and rate limiting are reviewed.

## Fiverr Go-Live Readiness / Zeitplanung (from Excel Dashboard)

The pinned top section follows the **verified DEV-first Excel dashboard formulas** rather than counting PRs as completed work:

| KPI | Excel source and calculation | Source value on 2026-11-11 |
| --- | --- | --- |
| Technical readiness | SUM(F for U=✓) / SUM(F), only `Sprint-Tracker` rows 3–63 | 5 / 287 h = 1.74% |
| Fiverr acceptance-gate readiness | SUM(F for BOTH U=✓ and V=✓) / SUM(F); equivalent to spreadsheet H completed | 5 / 287 h = 1.74% |
| Gate count | Tasks with BOTH U and V checked / 61 | 2 / 61 |
| Outstanding planned effort | 287h minus completed gate-plan-hours | 282 h |
| Weekly capacity | `Dashboard!B7` | 20 productive h / week |
| Capacity-only scenario | 282h / 20h/wk = 14.1 weeks; 5 workdays / week, rounded up | 71 working days, ~2027-02-18 as of 2026-11-11 |
| Legacy total-project estimate | `Dashboard!B5` + (1 - `Dashboard!B5`) × accepted hours / total hours | 65.61% (NOT Fiverr launch readiness) |

The actual widget reads these from the mounted, SHA-verified workbook (including individual hours and sprint groups). It recalculates the capacity date from the **current Europe/Berlin date**, so this is a moving capacity scenario, **not a committed release date**. Assumes 5 workdays/week; public holidays, blockers, deployment and manual BC/partner checks are *not* included. Do not present the date as a reliable forecast.

The legacy project score starts at 65%, because it includes prior historic development and must NOT be used as a launch gate. All 24 SaaS/Stripe tasks and 217 SaaS hours are excluded. At 61/61 checked tasks, the display STILL says revalidation required; a human explicitly approves Go-Live via a separate release process.

**Source limitation:** The Excel checkboxes are frozen historic evidence at initial import, and GitHub sync currently tracks evidence only. Task DB stage updates and PRs do NOT increment the Excel-derived readiness yet. Future audited gate approvals must replace historical Excel-only checkboxes as the authoritative readiness input. If the Excel is missing, changed, or invalid, the UI must show unavailable metrics instead of stale or invented percentages.

## Sprint AI-PM 1.0: GitHub evidence sync + morning briefing

A separate low-resource `ai-pm-sync` container fetches GitHub pull requests every 30 minutes. It stores observed PR state and audit events in the **existing** `state/projects.sqlite3`, never in the BCSentinel customer database. GitHub data is evidence, **never task stage changes or approvals**. No paid AI model, API spend, GitHub writes, or additional server required.

Sprint matching is conservative: an explicit `Sprint 6.02` or `S6.02` marker from a PR title/body/branch must uniquely correspond to **one** imported task. Ambiguous, unmatched, and duplicate identifiers never auto-match. If GitHub is unavailable the last successful observations remain, while the briefing explicitly marks the source partial. The sync examines up to 500 recently updated PRs per repo, not full historical coverage. PRs with no explicit sprint marker are left unmatched for human triage; documentation completion is not an acceptance gate.

The dashboard includes a 24h **rule-based briefing**, searchable area/status task register, and clickable evidence per matched task. This is **not yet an LLM/agent-generated morning recommendation**. Daily use simply opens the dashboard or presses refresh, with no user edit to Excel. For manual sync/diagnostics:

```bash
docker compose -f compose.example.yml exec -T ai-pm-sync python pm_sync.py sync
docker compose -f compose.example.yml exec -T ai-control-center python pm_sync.py briefing
```

**Update an already running DEV VPS checkout safely** (review the local diff before pulling; server compose port 8092 is a local uncommitted modification):

```bash
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
docker compose -f compose.example.yml ps
git status --short
# Back up project DB OFF-BOX using encrypted backup after this local verification.
# Preserve 8092 port override as compose.override.yml or restore it after fast-forward update.
# Do not use git reset --hard or prune volumes.
```

Deployment must use the existing verified feature branch via a reviewed fast-forward-only update, preserve the local `.env` secret, bind to 127.0.0.1:8092, back up SQLite before recreation, and verify 85 persisted tasks afterwards. Do not merge into staging as a shortcut: this repo's deployment workflows might trigger.

## MVP boundaries / next milestones

1. Copy the verified, uploaded XLSX to the private server as `data/master-tracker.xlsx` (read-only). Confirm hash and verify UI with live workbook loaded.
2. Add controlled, audited operator stage transitions and independent gate approvals, with evidence-specific SHA/CI and BC runtime validation.
3. Add time-window change report (since yesterday), branch health, release snapshot, and authenticated operator approvals.
4. Add agent-job queue with only one concurrent worker, explicit cost cap, audit logging, and no automatic production operations.
5. Add test fixtures for adapter, mocked GitHub API, auth, error states, and accessibility/UI/browser QA.

### Safety

No merges, deployments, GitHub writes, AI billing, PROD changes, or customer-data access are implemented. The public-facing webserver must never expose this dashboard without authentication and TLS. Daily refresh currently happens on page load or button click; no background cron/agent scheduler exists yet.
