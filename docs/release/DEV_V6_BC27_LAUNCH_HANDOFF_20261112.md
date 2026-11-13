# DEV Full-v6 report launch – BC27 handoff (2026-11-12)

**Status: Draft, no deployment, no merge, no BC27 acceptance.**

## Verified source baseline

- Exact DEV backend / BC source: `a8b870eb41d29913cc0837a558c30637be8c57f2`; AL extension `1.0.2.58`.
- Candidate: `1.0.2.59`, only edits `DHSetup.Page.al` latest-report dispatch and the two AL version manifests.
- Historical latest-report action forwarded to `DH Deep Scan Monitor.OpenExecutiveHtmlReport()` and therefore issued a legacy `/reports/executive/{scan_id}/share-link`, not a Full-v6 link.
- The existing v2 backend `POST /reports/executive/{scan_id}/v6-link` and `POST /reports/live/{variant}/{scan_id}/link` return 503 `REPORT_VIEWER_UNAVAILABLE` when `REPORT_V6_VIEWER_BASE_URL` is missing/invalid. Operator previously verified missing in DEV; recheck configuration read-only before change.

## Current BC27 behavior in this PR

- For original Free/Deep first scan (AL modes `data_health_score`, `free`, `free_deep`), the latest-report action goes through `ReviewScopeAndOpenFullV6`. It calls read-only preflight, verifies paid access and original baseline, confirms scope where required, and ultimately asks for a fresh single-use Full URL. Ineligible Free users must see an explicit denial; this is **not a Free Report viewer implementation**.
- For Validation and Monitoring scan modes, the latest-report action calls `OpenReportVariantV2` and the backend remains authoritative for permissions/provenance.
- Unsupported/unknown scan modes reject without any legacy share-link fallback.
- All product rights, company, evidence, exception and credit decisions must remain server-side. No silent conversion of a Free scan into a paid report.

## Unimplemented requirement: native Free report link

The v2 single-use link contract accepts only `full`, `validation`, `monitoring`, while Free/Quick do not receive that grant. Therefore a universal `Free → Free Report` flow cannot be claimed done. Design a separate read-only, tenant/company/scan-scoped Free grant and viewer route only after contract/security review; no premium leakage or legacy replayable share-link. Until then BC latest-report action deliberately fails closed for unpaid Free users. Record as a separate P0 product requirement, not a passed gate.

## Deployment dependencies (no execution)

1. Frontend main-safe integration candidate: `danielwauer-maker/bcsentinel-frontend#13`; the original report branch removed landing/dashboard routes and is unsafe for direct DEV replacement.
2. Verify frontend `/report/live` is reachable in a separately approved isolated DEV deployment, while existing `/`, `/overview`, privacy/imprint remain unchanged.
3. Verify actual accessible image bytes behind `.asset.json` URL references; successful build does not prove runtime asset availability.
4. Build DEV frontend with `VITE_BCSENTINEL_LIVE_REPORTS=true` and `VITE_BCSENTINEL_REPORT_API_BASE_URL=https://dev-api.bcsentinel.com` only with approval. These are build-time flags; existing default must stay disabled.
5. **After** deployed viewer readiness and CORS/HTTPS checks, set `REPORT_V6_VIEWER_BASE_URL=https://dev.bcsentinel.com` on DEV backend only with config snapshot and rollback. No backend schema migration.
6. After approved Sandbox in-place upgrade to `1.0.2.59`, verify registration/history preserved; real original Free scope, Full link (fresh code, one-use exchange, correct company), Validation/Monitoring evidence blocks, expired and foreign links, and Non-SUPER permissions.
7. Compare candidate against exactly installed BC27 schema; CI compiler success is not an actual SaaS upgrade test.
8. Preserve DEV image/extension rollback artifacts. Never downgrade backend schema blindly and never delete tenants to make test results green.

## Current release gates

- GitHub AL compiler may pass independently; record exact current-head workflow URL.
- Real BC27 upgrade, user authorization, CORS, browsers, print/PDF and historical scan provenance not yet verified.
- No LIVE GO and no customer-facing commitments.
