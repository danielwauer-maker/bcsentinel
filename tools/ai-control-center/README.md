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

## Fixed-baseline Soll/Ist timeline and legacy overall score

The top section also shows the historical Excel overall score (**65.6098%**) and the derived remainder (**34.3902%**) as a **qualitative total-project estimate, not release readiness**.

The schedule comparison is explicitly a **provisional linear capacity scenario**:
- Plan baseline date is read from the verified Excel `Dashboard!A3`: **11 November 2026**, not the current date and not an externally approved milestone.
- Initial overall score is `Dashboard!B5 + (1 - Dashboard!B5) * 5/287`, about 65.61%.
- The baseline target is **18 February 2027** (282 remaining plan hours at 20 productive hours/week, 5 working days/week, rounded up to 71 working days), **fixed** rather than moved daily.
- The planned overall score advances linearly toward 100% on working days; actual is the latest verified Excel model snapshot (currently static). Comparison in percentage points is **indicative only** while the Excel gate marks are frozen.
- The timeline intentionally shows **one actual observation point**, not a fabricated historic actual trend or fictitious future progress. Public holidays, dependencies, new scope and manual BC/Fiverr gates are not modeled.
- `remaining capacity scenario date` in the separate KPI can still move forward as the viewer date advances; the Soll/Ist baseline target **does not** move. Treat neither as a committed Go-Live date.
- If the Excel issue date is absent or invalid, the Soll/Ist timeline fails closed and shows unavailable instead of inventing a date.

Next milestone: replace the frozen actual Excel snapshot with distinct, evidence-reviewed and approved gate-history events, so historical actual milestones can be shown. PR evidence alone is not an approval. No extra AI billing is involved.

## AI-PM 1.5 – Alle 61 Fiverr-Aufgaben: Inventar und Evidenzlücken

`task_coverage.py` verknüpft den **SHA-verifizierten, schreibgeschützten Mastertracker** mit den ursprünglichen 61 Fiverr-Aufgaben in der separaten SQLite-Datenbank. Die Integration verweigert falsche Excel-Versionen, veränderte IDs, abweichende Titel, nachträglich veränderte historische Häkchen, fehlende Daten und widersprüchliche Review-/Abhängigkeitsmodelle.

**Wichtige Ehrlichkeitsregel:**
- **Inventarabdeckung 61/61**: Alle Aufgaben sind aus der verifizierten Exceldatei im Dashboard sichtbar. Das ist keine Abnahmequote.
- **Detailreviews 15/61**: Ausschließlich diese Aufgaben besitzen bisher kuratierte, quellenbasierte Abnahmeprüfungen.
- **Review-/Dependency-Status für 46/61 unbekannt**: Das System setzt für diese Aufgaben ausdrücklich *keine* Priorität, Gate-Erfüllung, Voraussetzungen oder kritischen Pfad voraus.
- Ein beobachteter PR-Link bleibt eine **Beobachtung**, nie geprüfte Evidence oder automatisch abgenommene Implementierung.
- Die bestehenden historischen Excel-Häkchen, manuelle Task-Stages und unabhängig attestierte Gates bleiben separat sichtbar; sie werden nicht durch das Inventar überschrieben.

Die neue 61-Zeilen-Ansicht bietet Aufgaben-/Sprintsuchen, Filter (alle, kuratiert, ungeprüft), verknüpfte PRs und die nächste sinnvolle Prüfung. Die bestehende 15-Knoten-Abhängigkeitsgrafik bleibt bewusst begrenzt, bis die anderen Aufgaben einzeln überprüft werden. Automatisches Inferieren nicht nachgewiesener Kanten und jede neue Freigabe sind untersagt.

Prüfbefehl (read-only):

```bash
docker compose -f compose.example.yml exec -T ai-control-center python task_coverage.py inventory
```

Erwartung bei unverändertem SHA-geprüftem Master: `state=loaded`, `total=61`, `reviewed=15`, `needs_review=46`, `dependency_modeled=15`, `dependency_unknown=46`, `global_release=NO_GO`.

Sicherer Betrieb: Vor Serverupdate SQLite online sichern; `.env`, Workbook und SQLite nicht überschreiben; nur den dedizierten Dashboard-Container neu bauen; lokalen Port `127.0.0.1:8092:8090` bewahren. Kein Merge, kein DEV/PROD-Betriebseingriff, keine künstliche Readiness-Erhöhung.

## AI-PM 1.4 – P0 Dependency Review & Next Actions (read-only)

The `blocker_plan.py` module models a **strictly curated subset of 15 Fiverr tasks** using 22 explicitly documented, acyclic prerequisite relationships. These relations are **engineering planning hypotheses** from the versioned reviews, not a complete release critical path, actual blocker durations, an approved technical architecture, or permission to promote a gate. The **other 46 Fiverr tasks are explicitly unmodeled**; the graph is not a global schedule estimate.

Three independent initial P0 review threads are suggested:
- `1.01`: Reconfirm immutable release commit/image/CI matches and deployed evidence.
- `1.02`: Reconfirm DEV backend/image, database migrations, backup/restore evidence.
- `4.01`: Prepare normative, versioned approval of Access-v2 contract, duration, pricing and legacy rights.

The graph ranks **review preparation**, not implementation prohibitions. Later nodes (BC27 upgrade, check coverage and provenance, Full/Validation/Monitoring E2E, Fiverr sales and landing copy) show direct prerequisites and unique downstream tasks. A reviewer may run independent development tasks in parallel. Only independent, explicit technical + DEV attestations change a *review signal* for prerequisites; **they do not prove commercial contract signoff or release**, and the graph never inserts such attestations. Historical Excel checkmarks, PR links, CI green and merges do not automatically clear edges.

Dashboard shows three initial review streams, a searchable 15-task dependency table with the number of affected downstream tasks and suggested next evidence. If the review source changes, tasks disappear or model cycles appear, the graph **fails closed** and shows unavailable. It does not write project SQLite, change the 65.6% historical estimate, task stages, approvals or PROD. No AI model/API fees. Review suggestions are not the legal/commercial final authority.

Operator check (read-only):

```bash
docker compose -f compose.example.yml exec -T ai-control-center python blocker_plan.py plan
```

Expected: `state=loaded`, `modeled_tasks=15`, `unmodeled_fiverr_tasks=46`, `global_release=NO_GO`, and three initial `upstream_p0_reviews`. Before VPS rollout, use SQLite online backup and preserve the host-only compose mapping `127.0.0.1:8092:8090`. Restart **only** `ai-control-center` service after fast-forward update; no merge/deploy to customer-facing DEV/PROD.

## AI-PM 1.3 – priorisierte evidenzbasierte Abnahmeprüfung (read-only)

Der neue `acceptance_review.py`-Dienst erzeugt eine **read-only Prüfliste** aus `data/evidence-status.json`, den tatsächlich importierten Fiverr-Aufgaben und vorhandenen `pr_task_link`-Verknüpfungen. Die Liste enthält **15 dokumentierte Aufgaben** und weist die übrigen **46/61 ausdrücklich als ohne Detailreview** aus. Es sind keine 61/61 Vollreviews oder Laufzeitabnahmen.

Die Prüfliste unterscheidet:
- **P0**: Release-Hashes/BC27-Upgrade, 199 Check-Lifecycle, Scanprovenance und Full/Validation/Monitoring, normative Access-v2-Verträge und Operator-Grants;
- **P1**: Website-/Fiverr-Redaktion und echte UI/Customer-Journey-Abnahme;
- **historisch abgehakt** bedeutet nur Excel-Ausgangsstand, kein neuer Nachweis;
- **editorial** bedeutet Textdokumentation vorhanden, jedoch keine Website-/Fiverr-Live-Abnahme;
- **blocked / candidate** basieren auf versioniertem Reviewtext, nicht auf aktuellen BC-/CI-Tests.
- Alle Prüfkriterien werden bewusst als **offen** dargestellt. Selbst ein verlinkter PR, grüner CI-Lauf oder GitHub-Merge setzt kein Häkchen.

Die Datenquelle `docs/fiverr/SPRINT703_EDITORIAL_QA_AND_RELEASE_GATES.md` in PR #165 benennt die noch ausstehende Preis-/Vertragsentscheidung, Fiverr-Editor-Validierung, Recht/Datenschutz und BC27 E2E. PR #166 (`FRONTEND_DESIGN_AUDIT.md`) benennt unverifizierte DSGVO-/Trust-Claims, beispielhafte Euro-Werte und ausstehende Mobile/Visual-QA. PR #164 dokumentiert acht Access-v2-Vertragsdrifts. PR #162 dokumentiert begrenzte Scanvergleichs-Evidence, aber keine positive freigegebene BC27 Runtime-/Validation-/Monitoring-E2E. Diese source-basierten Befunde rechtfertigen Prüfaufgaben, **keine pauschalen PASS-Klassifikationen**.

Der Review ist bewusst reproduzierbar und ohne Modellaufrufe. Bei fehlendem oder geänderten Source-Schema, unvollständiger Fiverr-Datenbank oder unbekannten Task-IDs werden keine zusätzlichen Fortschrittsprozente erzeugt. Geprüfte Unterlagen sind vom **11.11.2026**; die Quelle kann seitdem veraltet sein. Pull-Request-Status aus der SQLite-Sync-Tabelle ist lediglich beobachtete Metadaten und kein aktueller CI-/BC-Sandbox-PASS. Der neue Abschnitt im Dashboard zeigt P0/P1, offene Kriterien, alter der Quelle und relevante GitHub-Links. Er verändert weder task stages noch `approval`, `progress_event` oder `go_live`.

Prüfbefehl ohne Mutation:

```bash
docker compose -f compose.example.yml exec -T ai-control-center python acceptance_review.py review
```

**Wichtig:** Evidence-Review ist eine Vorstufe. Eine technische/DEV-Aufgabenabnahme wird weiterhin separat im unabhängigen `progress_history.py record --confirm` dokumentiert, erst **nach** realen Prüfungen. Es gibt weiterhin keine automatische Fiverr-Publikation, PROD-/DEV-Deployment oder globale Release-Freigabe.

## AI-PM 1.2 – auditable historical progress (explicit operator actions)

**This phase is code in Draft PR #167 until independently deployed and tested on the operator VPS.** The current spreadsheet remains a locked historical planning snapshot; it is never rewritten by this feature.

### Immutable baseline, run exactly once

Use the **same** SHA-verified Excel (61 Fiverr tasks, 287 Fiverr hours, two historical technical and two historical gate ticks). The baseline module checks the workbook SHA against the already imported task database and validates all 61 task keys and imported flags. Initializing it inserts no approvals and does not change any task stage or release gate:

```bash
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
docker compose -f compose.example.yml exec -T ai-control-center python progress_history.py init
docker compose -f compose.example.yml exec -T ai-control-center python progress_history.py history
```

Idempotent reinitialization with the same workbook is a no-op. Source SHA or date changes fail closed; manual reconciliation is necessary. Backup the SQLite DB with its online-backup API *before* the first initialization, and retain an encrypted off-host backup.

### Explicit independently reviewed gate history

No browser API, GitHub PR, agent, CI or scheduler can create events. A trusted operator must run the CLI **deliberately** with `--confirm`, actor, independent reviewer, a concrete HTTPS evidence link and a meaningful written reason. Reviewer and actor must be distinct for technical, DEV and task Go-Live gates. The software checks that gate order is respected (DEV follows technical; task Go-Live follows DEV), and duplicate gates are rejected:

```bash
# Example only. DO NOT execute until a real review of task 3.02 has happened:
docker compose -f compose.example.yml exec -T ai-control-center \
  python progress_history.py record --task fiverr:3.02 --gate technical \
  --actor 'implementer' --reviewer 'independent-reviewer' \
  --evidence 'https://github.com/danielwauer-maker/bcsentinel/pull/155' \
  --reason 'Independent evidence review and BC sandbox acceptance documented' \
  --confirm
```

`implementation` is an optional observation and does **not** count as an approval; `technical`, `dev`, and `go_live` create explicit audit and approval records. Actor/reviewer fields are operator-attested strings, **not an identity-provider signature**. The evidence URI is syntactically checked, **not automatically proven to satisfy BC27 acceptance**. The operator must verify identities, test reports, evidence quality, scope and dependencies outside the tool. Only use this after a real review. Recordings are immutable; corrections and revocation workflows are a future sprint. Because that workflow is not yet present, do not record uncertain approvals.

### What readiness actually measures

- Excel planning baseline: 65% legacy prior work + weighted 5/287 confirmed historical hours = about 65.61%, with imported checkboxes preserved.
- The technical readiness percentage increases only for newly explicitly technical-attested Fiverr task hours; DEV percentage reflects explicitly DEV-attested hours (Excel contains no separate historic DEV approvals).
- Fiverr gate readiness and overall legacy score rise only for *task Go-Live gate events* that have passed a separate DEV gate and have an independent reviewer. They are **not** global launch authorization.
- Actual timeline records **one baseline point + one point per new dated attested event/day**. It never retrospectively invents a historic trend. Linear plan trajectory stays fixed to 11 November 2026 baseline; the dynamic remaining-hours scenario adapts to new approved task gates.
- The dashboard displays the number and evidence links for the most recent events, with current overall/technical/DEV/gate fractions. A GitHub PR merge alone never changes these figures.
- Even 61/61 task gates do not authorize Fiverr, BC PROD, or deployment. Global Go-Live remains `NO_GO`, requiring a distinct later release workflow.

New database tables are isolated inside `state/projects.sqlite3` (`progress_baseline`, `progress_meta`, `progress_event`). Nothing is migrated in BCSentinel customer databases.

## AI-PM 1.1 – evidence mapping and review queue

Versioned `data/evidence-status.json` references are used as **reviewed source-level attribution**, not as gate approvals. A PR may legitimately support multiple Fiverr tasks; the link table `pr_task_link` stores all independently reviewable PR-to-task links with provenance (`reviewed_reference` or `explicit_sprint_marker`). Exact direct sprint tokens are accepted only from PR titles/branch names; incidental body mentions, duplicate identifiers, conflicting codes, unrelated historical PRs and missing tasks do not acquire automatic links. No semantic/LLM guessing is used.

The separate `pr_match_review` records reasons for conflict/unmatched PRs. The dashboard shows a compact reviewed-reference count and a collapsible triage list; actual conflicting markers are prioritized before historical unmatched PRs. The existing 30-minute read-only sync is idempotent, retains past evidence if GitHub is down, and does not promote task stages, CI status, approvals, pricing, product contracts or release gates.

The old `pr_observation.task_key` is retained for backward compatibility when exactly one link exists; multi-task links live in `pr_task_link`. This is a migration-in-place of *only* the separate project SQLite store, with `CREATE TABLE IF NOT EXISTS`; no customer DB migrations. During the first new sync, the mapping tables are initialized. Back up your database before container recreation. The first enriched sync can update evidence mapping without being misreported as fresh PR code changes.

The timeline chart now suppresses the middle date tick if today's label would overlap the baseline/target date. This is UI-only; the fixed date and historical readines model are unchanged.

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
