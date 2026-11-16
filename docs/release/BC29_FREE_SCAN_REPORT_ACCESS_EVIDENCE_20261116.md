# BC29 Free Scan headline and report access — curated evidence

**Status:** source candidate; no deployment, installation, merge, backend change, database change or PROD action.

**Branch:** `codex/bc29-free-scan-report-access` (based on `origin/staging` at `f46e77c`).

## Diagnosed cause

1. `DH Deep Scan Runner` persisted the completion headline through a function that did not receive the run or its `Scan Mode`. Its four completion labels therefore always said `Validation Check`, including an original Free (`data_health_score`) run.
2. `DH Report Link Mgt.` classified `data_health_score`, `free` and `free_deep` as `full`. The Scan History, Scan Monitor and Setup therefore exposed the Full-v6 action. That action correctly calls `POST /reports/executive/{scan_id}/v6-link`, where Access-v2 correctly returns `402 FULL_ACCESS_INACTIVE` to a Free tenant.

## Product and access contract verified from source

- The implemented Free contract is `free-health-report-v1`, not Full-v6: `GET/POST /reports/free-health/{scan_id}` and `POST /reports/free-health/{scan_id}/share-link`.
- The Free route authenticates tenant ownership and, under Access-v2, requires `is_original_free_scan`; it does not grant a second or arbitrary Free report.
- `access_renewal_policy.report_visible()` preserves only an original Free report after paid-access expiry.
- Full-v6 remains a separately guarded paid route: `issue_full_link()` returns `402 FULL_ACCESS_INACTIVE` when `has_paid_full_access()` is false.
- The change does not alter Euro-impact fields, report payload composition, the Full endpoint, entitlement rules, backend source, schema, or any other extension.

## Implemented source changes

- Completion, running and start headlines are selected from the persisted scan mode: Free, Full Assessment, Validation Check or Monitoring Scan.
- Free modes now resolve to the `free` report variant.
- A dedicated `OpenFreeHealthReport` AL procedure posts authenticated JSON `{ "report_type": "html" }` to the Free share-link endpoint and opens only the returned short-lived URL.
- Scan History, Scan Monitor and Setup show/use the Free action for Free runs. Full, Validation and Monitoring actions remain variant-specific.
- New source-contract regressions cover headline routing, Free route selection, original-Free guard, and continued Full 402 paid-access guard.

## Executed evidence

| Check | Result |
|---|---|
| `backend/.venv/bin/python -m pytest -q backend/tests/test_bc29_free_scan_report_access_contract.py backend/tests/test_free_health_report.py backend/tests/test_access_renewal_policy.py backend/tests/test_gl01f_fix02_free_access.py` | **PASS — 33 passed** (warnings only) |
| `python3 scripts/validate_bc_extension.py` | **PASS — 134 AL objects; ranges and analyzer configuration valid** |
| `git diff --check` | **PASS** |

## Open acceptance / blockers

- **BC29 compiler verification is NOT VERIFIED.** No `alc` executable or BC29 symbol packages are present in this workspace; no build or installation was attempted.
- **BC29 sandbox runtime verification is NOT EXECUTED.** Required manual acceptance includes Free scan headline, Free report opening, Full 402 preservation, Validation/Monitoring actions, and no impact-display regression on the exact built app.
- `python3 scripts/check_al_localization.py` is **BLOCKED by pre-existing baseline violations** in `DHNotificationI18nMgt.Codeunit.al` and `DHSalesLineIssueWorklist.Page.al`; neither file was changed. New English UI strings require normal BC translation-file generation during the unavailable BC29 compile step before release packaging.
- No GitHub Actions run was triggered. This document is source/test evidence only and is not a Go-Live, deployment or entitlement approval.
