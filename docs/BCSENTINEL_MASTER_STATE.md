# BCSentinel Master State

Last updated: 2026-11-01

This document is the human-readable authority entry point for the current BCSentinel product state. The machine-readable companion is [`release/current-product-state.json`](../release/current-product-state.json).

## Authority

- `danielwauer-maker/bcsentinel/main` is canonical Core/Backend/Extension and release/product truth after reviewed merges.
- `danielwauer-maker/bcsentinel-frontend/main` is canonical deployed customer-frontend truth.
- `danielwauer-maker/bcsentinel-product-system/main` is normative product/UX truth.
- Feature, staging, acceptance and release-candidate branches are work/evidence only until reviewed and merged.
- PROD is promoted manually from an immutable reviewed release ref; newest `main` is not automatically the deployed PROD release.

## Frozen product model

BCSentinel targets Microsoft Dynamics 365 Business Central Online and is positioned as **Data Health + Business Impact** with the claim **“Clean Data – Higher Impact”**.

Canonical customer ladder:

**Free Health Check → Quick Assessment → Full Assessment → Validation → Monitoring later**

There is only one customer-facing initial scan engine/depth: the full BCSentinel Data Health / Deep Scan. Free, Quick and Full Assessment differ by result access, not scan depth.

### Free Health Check

- A newly registered tenant receives exactly one initial `free_entry` scan credit.
- The first scan executes the full enabled Data Health / Deep Scan.
- The full result is stored server-side.
- Free surfaces expose aggregate-only information: score/counts/severity/risk areas/impact band.
- Free must not expose finding titles, issue codes, root-cause detail, full recommendations, record-level detail or concrete financial EUR values.
- After the initial Free Entry credit is consumed, a second unpaid scan is blocked.

### Quick Assessment

- Product code: `quick_assessment`.
- Quick Assessment is an open-ended disclosure entitlement and never creates a new scan credit.
- It may be granted **before or after** the customer's first scan. This supports the Fiverr flow `purchase → install/register → initial included scan → Quick reveal` without a separate paid scan.
- Canonical Quick access has **no automatic expiry**. New Quick grants use `valid_until_utc = null` and remain active until explicit revoke.
- If a qualifying scan already exists at grant time, Quick reveals that scan immediately. If no scan exists yet, the entitlement is staged and the first completed qualifying scan becomes viewable at Quick level automatically.
- It exposes at most the five highest-priority findings.
- Quick findings may expose title, severity, affected-record count, risk area, impact band and a concise next step.
- Exact modeled EUR values, issue codes, full root-cause analysis, record-level drilldown, complete recommendation/remediation detail and the full Assessment report remain blocked.
- Ranking is deterministic and may use modeled impact internally; hidden financial values do not enter the Quick report contract.
- The Quick JSON/HTML/PDF/report-share contract is separate and enforces a hard maximum of five findings.
- Quick Assessment does **not** qualify as a Validation baseline.
- Secure share/email tokens may have their own short security TTL, but token expiry does not expire the underlying Quick entitlement. The customer can reopen/regenerate the report through BCSentinel while the Quick entitlement remains active.

### Full Assessment

- Product code: `assessment`.
- Full Assessment unlocks the same qualifying initial scan; canonical Fiverr/operator Assessment does **not** create a new scan credit.
- A customer may buy Full Assessment directly without buying Quick first.
- Full detail/report access is fixed to 7 days after activation.
- It exposes all qualifying findings, exact modeled financial impact, root-cause context, prioritized remediation and the full Assessment Report.
- The stored scan remains after expiry and can be used as Validation baseline/history because a paid Full Assessment existed.
- After Full expiry, live detail access falls back to a still-active purchased Quick layer when one exists; otherwise it falls back to Free aggregate access.
- One +7-day Assessment extension is allowed for the same entitlement; it does not create a new scan.

### Validation

- Validation requires evidence of a prior paid **Full Assessment** baseline. Quick alone is insufficient.
- Validation grants exactly one new `validation_check` scan credit.
- Grant/purchase alone does not unlock Validation detail access.
- The customer runs a new full Data Health Scan after remediation.
- Consuming the Validation credit anchors the 7-day Validation result/comparison window at `consumed_at`.
- Validation Report accepts only a scan that actually consumed a Validation credit and compares it with the recorded paid Full Assessment baseline.
- Comparison classes are Resolved / Improved / Remaining / Regressed / New.

### Monitoring

- Monitoring permits recurring full scans and continuing paid-detail access while the subscription is active.
- Monitoring remains a later product stage and is not a Fiverr controlled-pilot blocker unless selected pilot scope requires it.

## Canonical report resolution

Report selection is backend authority and scan-aware. Channels and the BC Extension must not maintain their own competing entitlement hierarchy.

For a concrete scan, the canonical resolver returns the highest valid report in this order:

**Validation (only for the Validation-consumed scan) → Assessment → Quick Assessment → Free Health**

The authenticated endpoint is `GET /reports/{scan_id}/preferred-variant`. `/license/status` additionally exposes the tenant-level `preferred_report_variant` for observability, while the scan-aware endpoint remains authoritative for the selected scan.

This guarantees that the same Business Central Extension supports Fiverr, direct and future channels without product forks. A Quick buyer can therefore install the standard app, run the included initial scan, and use the primary **Open BCSentinel Report** action without choosing Free versus Quick manually.

## Canonical analyzed-record classes

The authoritative record class is derived from persisted `Scan.total_records` after analysis, not from a buyer estimate.

| Class | Analyzed records |
|---|---:|
| Micro | 0–100,000 |
| Small | 100,001–250,000 |
| Medium | 250,001–1,000,000 |
| Large | 1,000,001–5,000,000 |
| Enterprise | 5,000,001–20,000,000 |
| Custom | >20,000,000 |

These classes are shared commercial metadata. They do not themselves grant entitlements or scan credits.

## Pricing truth for direct BCSentinel

The existing direct/Stripe EUR pricing remains unchanged by F8 until separately reviewed:

| Record class | Assessment | Validation | Monitoring monthly | Monitoring annual |
|---|---:|---:|---:|---:|
| ≤250k | €249 | €129 | €199 | €1,990 |
| ≤1m | €399 | €199 | €299 | €2,990 |
| ≤5m | €699 | €349 | €499 | €4,990 |
| ≤20m | €1,190 | €590 | €799 | €7,990 |
| >20m | Custom | Custom | Custom | Custom |

The six F8 record classes map through a compatibility layer to this existing direct pricing table. F8 does not silently change direct/Stripe prices.

## Fiverr pricing truth

Fiverr is a sales channel only. Current controlled-pilot recommendations are:

| Analyzed records | Quick Assessment | Full Assessment | Validation |
|---|---:|---:|---:|
| ≤100,000 | $129 | $299 | $149 |
| 100,001–250,000 | $169 | $349 | $179 |
| 250,001–1,000,000 | $229 | $449 | $229 |
| 1,000,001–5,000,000 | $349 | $649 | $329 |
| 5,000,001–20,000,000 | Custom Offer | Custom Offer | Custom Offer |
| >20,000,000 | Individual review | Individual review | Individual review |

Fiverr Premium / Assessment Plus is a commercial wrapper around Full Assessment plus the one allowed 7-day extension. It is not a separate core entitlement and does not create another scan.

## Fiverr channel architecture

- One standard BCSentinel Extension/backend serves Fiverr, direct, partner and future marketplace channels.
- Generic commercial products include `quick_assessment`, `assessment` and `validation_check`; Monitoring remains generic as well.
- Sales origin is separate metadata such as `fiverr`, `direct`, `malt`, `contra`, `appsource`, `partner` or `support`.
- External order references are audit metadata, not entitlements.
- Fiverr payment/contract remains on Fiverr; do not redirect Fiverr-origin purchases to off-platform payment and do not scrape Fiverr order/chat state.
- Controlled pilot permits one manual operator action after payment confirmation. For Quick, that grant may occur before the first scan; everything after entitlement/credit grant is automated.
- Free Health Check is the BCSentinel aggregate entry layer; Fiverr Basic is Quick Assessment, not a paid Free report.

## Extension state

Current source target: **1.0.2.29**, BC Online / BC 27.x, runtime 16.0.

1.0.2.29 retains initial Free Entry and the existing report family, adds native `quick-assessment` report-link support and introduces a server-backed scan-aware primary action:

- **Open BCSentinel Report** resolves the highest valid report for the selected scan via the backend.
- **Open BCSentinel PDF** uses the same resolver for PDF.
- Explicit Free / Quick / Assessment / Validation actions remain available for support/manual use.
- The Extension does not duplicate product hierarchy or decide entitlement precedence locally.

Last previously verified real BC artifact/runtime evidence predates 1.0.2.29. Therefore 1.0.2.29 is **source-complete but still requires real BC SaaS artifact/runtime acceptance before paid pilot launch**.

Known prior real non-SUPER evidence: SCAN PASS (10/10 modules, 199/199 checks) and VIEWER PASS. SETUP still needs final real runtime acceptance. SCHEDULER/ADMIN can be deferred for a one-off Free/Quick/Assessment/Validation Fiverr pilot unless used by the selected workflow.

## Report family – automatic implementation complete

Separate product report contracts now exist for:

- **Free Health Report**: aggregate-safe JSON/HTML/PDF + secure share links.
- **Quick Assessment Report**: JSON/HTML/PDF + secure share links; maximum five prioritized findings and no exact EUR/root-cause/record-level/full-remediation leakage.
- **Assessment Report**: full-detail Assessment JSON/HTML/PDF + secure share links; legacy Executive route retained for compatibility.
- **Validation Report**: true before/after model with resolved, improved, remaining, regressed and new findings plus score/issue/exposure deltas.
- Monitoring report remains existing/later polish and is not required for the first one-off Fiverr pilot.

Free and Quick redaction are enforced by server-side contracts rather than CSS hiding.

## Lifecycle email – automatic implementation with permanent-Quick alignment

Backend-owned transactional lifecycle email infrastructure includes tenant lifecycle profile, DE/EN language, idempotent retryable outbox, internal worker, concurrency-safe claims, stale-claim recovery and signed report links without API tokens.

Canonical new-product lifecycle behavior is:

- registration and scan start/completion/failure messages remain transactional;
- permanent Quick grants schedule activation only and do **not** schedule Quick expiry-warning/expiry mail;
- legacy Quick expiry event constants may remain for backward compatibility with historical finite grants, but they are not part of new Quick commercial semantics;
- Assessment activation/expiry warning/expiry/extension and Validation availability/completion/expiry warning remain time-bound;
- secure report links may expire independently for security while the underlying Quick entitlement remains permanent.

Real sender DNS/provider acceptance (SPF/DKIM/DMARC, bounce and spam placement) remains manual.

## Operator/Admin – automatic implementation complete

The channel-neutral operator console at `/admin/operator` supports tenant/environment/email/order search, Grant Quick Assessment, Grant Assessment, Extend Assessment, Grant Validation, targeted revoke and lifecycle-mail resend. Writes are CSRF-protected and the console requires admin Basic auth.

The operator displays authoritative analyzed records, F8 record class and Fiverr price recommendations for Quick / Full / Validation when a qualifying scan exists. It does not guess analyzed-volume pricing when no scan exists.

Canonical operator semantics:

- Quick: may be granted before or after the first scan; permanent/open-ended until explicit revoke; no scan credit; no Full rights.
- Full Assessment: existing scan + fixed 7 days, no credit.
- Validation: prior paid Full Assessment prerequisite + exactly one scan credit, no premature detail access.
- Assessment extension: maximum once, +7 days, old scheduled expiry mails suppressed/replaced.

The old internal `admin_manual` credit grant retains narrowly scoped compatibility behavior for legacy internal tests/tools. It is not the canonical Fiverr/direct commercial grant path.

## Security and recovery evidence

Automated gates repeatedly verify tenant ownership/isolation contracts, Free/Quick/Full/Validation boundaries, operator auth/CSRF, backend compile/Alembic graph, dashboard build, report/lifecycle contracts and PostgreSQL backup/checksum/isolated restore/data-probe automation.

Automated evidence does not replace the required real two-tenant BC SaaS test or real off-host PROD restore drill.

## F8 frozen funnel regression

The canonical automatic product-funnel proof is now:

registration → optional/prepaid Quick entitlement before scan → one initial included scan → Quick report on the same scan with no additional credit → Quick cannot create Validation baseline → Full Assessment unlock on the same scan with no credit → Full expiry falls back to purchased Quick when present → Validation grant from paid Full baseline → exactly one new scan credit → second full scan → scan-aware Validation comparison report.

The regression explicitly asserts that Quick is open-ended until explicit revoke, there is only **one scan before Validation**, exactly **two scans after Validation**, and report resolution remains server-side and scan-aware.

## Fiverr launch assets – F8 aligned

`docs/FIVERR_GIG_LAUNCH_KIT.md` is aligned to the current funnel:

- BASIC — Quick Assessment, Micro base $129.
- STANDARD — Full Assessment, Micro base $299.
- PREMIUM — Assessment Plus, Micro base $399.
- Validation is follow-up only after paid Full Assessment, Micro base $149.
- Larger environments use the canonical volume recommendations / Fiverr Custom Offers.
- A Fiverr buyer can start with Quick or Full; the initial Data Health Scan is the technical prerequisite and is not sold as a separate paid Free package.

Actual asset export/upload and Fiverr publication remain manual because they depend on the live Fiverr form and final release approval.

## Landing / acquisition state

The customer frontend supports optional `VITE_FIVERR_GIG_URL` acquisition.

- With a real approved Gig URL, the landing hero advertises **Quick Assessment on Fiverr** and identifies the Micro base price ($129 up to 100,000 analyzed records) with larger environments via Custom Offer.
- If the variable is empty, the waitlist remains active; no fake or unpublished Fiverr URL is exposed.
- Fiverr-origin commercial communication/payment remains on Fiverr.

## Automatic sprint status

F0 through F8 are implemented to the extent they can be completed automatically in repository/code/content workflows. The permanent-Quick/report-resolution follow-up freezes the current Fiverr/direct semantics without creating a product or Extension fork.

No further automatic product-funnel sprint is required before manual controlled-pilot acceptance after the permanent-Quick/report-resolution change is reviewed and merged. Remaining P0 work requires real BC Online, infrastructure/provider, visual/legal or marketplace interaction.

## Brand freeze

Navigation `#14213D`; Interaction `#246BFD`; Success `#11A36A`; Warning `#D98E04`; Critical `#CF3A3A`; Background `#F7F9FC`; Cards `#FFFFFF`; Brand Orange `#FF921F`; Foreground on Orange `#082138`; typography Inter; claim “Clean Data – Higher Impact”.

## Manual release gates still authoritative

Before the first paid Fiverr pilot customer:

1. Build/install/upgrade final 1.0.2.29 artifact in real BC Online.
2. Complete required non-SUPER runtime role acceptance, at minimum SETUP for the selected one-off pilot flow.
3. Perform real tenant A/B switching and negative cross-tenant isolation.
4. Manually visually inspect real Free, **Quick**, Full Assessment and Validation HTML/PDF outputs with representative data.
5. Configure/test real lifecycle SMTP sender including SPF/DKIM/DMARC, bounce behavior and inbox/spam placement.
6. Perform real off-host/operational PROD backup and restore procedure.
7. Freeze immutable reviewed RC and manually promote exactly that ref to PROD.
8. Run fresh external-like PROD E2E through Fiverr Quick grant before/after registration as applicable, initial included scan, automatic Quick report resolution, Full Assessment on the same scan, Full expiry back to Quick, Validation grant, new scan and scan-aware comparison report.
9. Complete privacy/DPA/legal/provider-facts signoff.
10. Create/export the final Fiverr gallery/video/report assets from the approved launch specifications, configure the live Gig fields and publish/activate the Gig.
11. Execute one real Fiverr order dry-run through the selected pilot workflow.
12. Set the real published Fiverr Gig URL as `VITE_FIVERR_GIG_URL`, deploy the reviewed frontend ref and verify the landing CTA.
13. Publish the prepared LinkedIn launch post only after all prior launch gates are closed.

AppSource, full public Stripe E2E, public self-service, Monitoring polish, mobile polish and partner program are not controlled-pilot blockers unless scope changes.
