# PR #154 – V2 Release Gate and DEV Acceptance

**Status: DRAFT / NOT PRODUCTION READY** (2026-11-09). Do not merge or install until the gates below have passed. This document is intentionally explicit about external dependencies and evidence that cannot be manufactured by unit tests.

## Implemented in PR #154

- One Free Deep Scan, original Free Report permanently accessible; original completed Free scan may be confirmed as the Full baseline after paid activation.
- Full Assessment v2: 14 days Premium, no extra scan.
- Access Renewal: +14 days Premium, no new scan.
- Renewal + Validation: +14 days Premium, exactly one scan credit. Scan credit consumption does not extend access.
- Monitoring continues as recurring access. Archive and link delivery are tenant/company/scan scoped, and expire with entitlements.
- Five new v2 data classes: <=250,000 / <=1,000,000 / <=5,000,000 / <=20,000,000 / Custom above 20m.
- New product rows are disabled and unpriced until explicitly approved.
- Immutable scope confirmation requires original persisted Free scan, verified BC company and EUR LCY; a previously confirmed baseline is not re-confirmed with changed decisions.
- New v2 scan sync transaction captures an **automatic**, unconfirmed scope after successful persistence. Confirming scope remains an explicit, separate user action.
- Validation compares the latest comparable completed scan and separately references the first confirmed baseline.
- BC Scan Monitor actions for Full scope review, Validation and Monitoring; legacy Executive buttons hidden.
- A new authenticated preflight endpoint exposes missing evidence without generating baseline, scan or report access.

## Must-pass gates before enabling V2

| Gate | Expected evidence | Status |
| --- | --- | --- |
| G1 backend regression | All new + legacy tests green on PR head | Check GitHub Actions on current HEAD |
| G2 BC AL build | AL build green, install+upgrade dry-run on existing DEV tenant | AL build run; installation still unverified |
| G3 prices & checkout | Approved amounts for every v2 SKU and data class, correctly mapped Stripe Price IDs; finance/currency checked | **BLOCKED: final prices not approved** |
| G4 webhook lifecycle | Paid, failed, replay, refund, dispute, chargeback, concurrency, out-of-order and delayed webhook events; no overgrant | **BLOCKED: refund/dispute reversal not implemented for v2** |
| G5 Free→Full real scan | Real Free scan has company GUID, EUR LCY, completed+persisted status; scope auto-created, explicit user confirmation and Full v6 report opens | **BLOCKED: end-to-end DEV real evidence not yet verified** |
| G6 Validation history | Verified comparable initial and previous scan, immutable baseline, failed/incomplete/mixed-currency excluded, Monitoring trend | Unit regression exists; real DEV acceptance missing |
| G7 browser live renderer | /report/live deployed, live flag and API URL intentionally configured, Full v6 renders; Validation & Monitoring live adapters use only verified source data | **BLOCKED: Validation/Monitoring render_vm not available; Lovable workspace out of credits** |
| G8 data isolation | Two tenants, two BC companies, cross-user attempts, guessed links, expired links, non-SUPER permissions, token expiry, browser caching | Unit coverage partial; full DEV acceptance missing |
| G9 deployment | Database backup, migration dry-run, extension upgrade compatibility and rollback plan, DEV approval, then PROD promotion | Not started |

## DEV acceptance – no new paid scan required for first Full test

1. Keep `ACCESS_MODEL_V2_ENABLED=False` until the designated DEV cutover. Verify last deployed DEV backend and original BC extension remain healthy.
2. Backup DEV DB. Check existing original Free scan `Scan`, `ScanStartRequest`/`TenantScanCredit`, `ScanRunStatus`, company GUID and LCY.
3. After approved DEV branch deployment, explicitly enable v2 on DEV only; never flip PROD by copying DEV env.
4. Retrieve `GET /scans/{scan_id}/report-preflight` with authorized tenant headers. It MUST NOT write scope or grant any access.
5. Open BC Deep Scan Monitor > **Review Scope / Full Assessment** on the original Free scan with a verified test Full Access entitlement. Inspect actual detected modules; explicitly confirm.
6. Confirm scope version remains immutable across repeated requests and that paid report can be opened with a single-use code. Check `GET /account/reports/full/{scan_id}?company_id=...` with report-scoped bearer. Verify no raw BC API token in browser, URL or PDF.
7. Expire Premium and verify Full link issuance/exchange, report reader, history and exports fail closed. Reactivate via renewal with no additional scan.
8. Use a separate paid Validation credit and a new scan only when entitlement and test approval are explicit. Compare with original baseline and last compatible scan. Verify mixed-company/currency and incomplete scans rejected.
9. Test Monitoring, scheduler, non-SUPER roles, two tenants, DE/EN and PDFs. Only then review PR for merge.

## External dependency: Lovable Report System

Lovable project ID: `2efa722e-a036-4e3e-a695-6cda46f88541`. The route `src/routes/report.live.tsx` already exists in project source, but live rendering is gated by build-time `VITE_BCSENTINEL_LIVE_REPORTS` and `VITE_BCSENTINEL_REPORT_API_BASE_URL`. Do **not** enable until verified backend and frontend are deployed.

The current frontend `src/report-system/live/bridge.ts` intentionally blocks raw Validation and Monitoring because `render_vm` is null and baseline/methodology evidence is insufficient. **Do not infer values from fixtures or bypass validation to force a green screen.** As of Nov 9, 2026, the Lovable workspace has no remaining credits; the requested frontend changes could not be made.

## Commercial/Stripe signoff

Do not silently treat the earlier **EUR 79** access-only Renewal suggestion as final or copy the historical 7-day product prices. Full Assessment starts from EUR 249, Renewal+Validation from EUR 129, Monitoring from EUR 199/mo in the agreed product plan; actual amounts must be set per approved data class before Stripe Price creation. The remaining new SKU price rows should stay inactive.

## Production invariant

The PR is not "complete", approved or deployable merely because backend regression and AL compilation are green. Real scan scope, signed viewer presentation, money/currency integrity, refund safety, live rendering and customer acceptance require independent evidence.
