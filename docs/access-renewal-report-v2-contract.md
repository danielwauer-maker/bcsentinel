# BCSentinel – Access Renewal / Reports v2 (implementation contract)

Status: **proposed / not deployed**. Do not enable in production until migrations, API guards, Extension, frontend, email, and integration tests are finished.

## Customer journey

1. **Free:** One full technical Deep Scan per tenant; original Free Report remains available indefinitely. The account never expires. Never reveal paid findings in a Free response.
2. **Full Assessment:** Reveal the results of the existing scan for **14 days**; **no additional scan**.
3. **Access Renewal:** Add another **14 days** of premium visibility over all existing paid scan data; **no scan**.
4. **Access Renewal + Validation:** Same **14 days** and **exactly one** additional Deep Scan credit; generate a Full and comparative Validation Report from the authorized new scan.
5. **Monitoring:** Premium access during an active subscription with manual and scheduled Deep Scans subject to concurrency/rate-limit fair-use safeguards.

**Quick Assessment and customer dashboard are disabled for go-live**; retain underlying implementation behind server-side flags. Stop dashboard invite emails on tenant registration. Report viewer must remain available independently of dashboard.

## Access after expiry

- Original Free Report: always accessible to authenticated tenant.
- Premium Findings, action lists, Full / Validation / Monitoring online reports and new PDF download links: locked until premium pass or monitoring becomes active.
- Persist historical scan evidence and report archive. Reactivation re-exposes historical premium records, with per-scan tenant + BC company ownership checks.
- A PDF already downloaded cannot be technically revoked; communicate this honestly to customers.
- A credit that includes a new validation scan is separate from the premium access duration and must be consumed atomically at start.
- When premium is still active, a renewal **adds** 14 days from the existing expiry; when expired, it starts from activation (UTC). Choose and persist an activation/deadline policy for paid-but-unactivated purchases before implementing checkout.
- Explicit authorization must be checked on **every** report/archive/PDF/export endpoint, not only in BC UI. Time-limited share codes must not bypass expiry.

## Immutable scan + report architecture

- One technical Deep Scan, multiple report projections.
- Separate authenticated report routes: free, full, validation, monitoring. Do not use Full v6 route for validation.
- Original Free scan is an immutable reference; only that scan can produce the permanently visible original Free Report.
- A Full Report needs verified company/LCY/scope provenance, but a Validation scan should not be reclassified as an original Full baseline.
- Validation compares to last **comparable** scan by default, also references initial baseline. Matching tenant, company, scope/check version, currency and scan completeness is mandatory. Record immutable chosen comparison IDs and report version.
- Scheduler results and manual results share the same history. Monitoring report assembles history/trends.
- Old reports are archived but hidden whenever premium is expired.

## Engineering gates

1. Add versioned access-pass and purchased-product representation; migrate legacy 7-day entitlements without silently extending/refunding/shortening existing customer grants. Make payment/webhook/grant idempotent.
2. Add renewal product variants (no-scan / one Validation scan); separate access grant from scan credit creation. Use database transactions and audit events.
3. Replace 7-day calculation for **new** products only and stack active renewals. Do not retroactively recalculate old access from historic purchases/credits.
4. Explicit per-report authorization, including archived/PDF and share-link redemption. Ensure Free responses never expose paid fields, including guessed URLs.
5. BC AL: separate Open Free / Full / Validation / Monitoring report actions, conditionally hide Quick and Analytics Dashboard. Apply license refresh expiry and denial in both AL and backend.
6. SaaS: hide dashboard routes, disable dashboard invitations at registration. Keep report viewer and registered tenant identity working.
7. Integration tests: Free one-shot, no free reset on re-registration, Full no additional scan, two Renewal variants, 14-day inclusive/exclusive time boundaries, stacking, expiry locks reports, restore after renewal, Validation cross-company isolation, Monitoring manual/scheduler, race/replay/idempotency, legacy purchases, non-SUPER, tenant isolation, no unearned paid data, PDF token expiry.
8. DEV only: schema migration dry run, backups, report viewer deployed and working, new Scan Scope capture + validation binding, integration tests, then deliberate production release.

## Current DEV observations (2026-11-08)

- Tenant identity bound (Entra, BC environment, company) after safe legacy re-registration.
- New Validation Deep Scan succeeded, scan ID RUN_20261108_000001_02ECEDD11B45460D899B2B4FA8A0D, LCY EUR.
- No assessment scope snapshot and no validation scope binding for that scan. Full v6 returns HTTP 409; do not fake baseline or backfill unverified scope.
- Earlier BC actions still open legacy Executive HTML/PDF. Customer dashboard/menu and dashboard invitation email remain enabled. These are go-live blockers.
