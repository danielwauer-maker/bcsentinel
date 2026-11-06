# BCSentinel Fiverr — Manual Acceptance Runbook

Status: **manual execution required after automatic preflight PASS**  
Date: 2026-11-03  
Candidate Extension: **1.0.2.30**  
Target: first controlled paid Fiverr pilot.

## Purpose

This runbook is the manual handoff after repository automation. Work from top to bottom. Do not skip a P0 failure by granting SUPER, changing tenant scope, disabling checks, bypassing Fiverr payment rules or testing a different code ref.

For each block record:

- result: PASS / FAIL / BLOCKED;
- date/time;
- tester;
- exact Extension version / backend ref / frontend ref;
- non-secret IDs: Fiverr order ID, tenant label, company, scan ID, entitlement/credit reference where applicable;
- screenshots or logs;
- defect/fix reference if a retry was needed.

Never store passwords, API tokens, SMTP credentials or other secrets in screenshots/evidence.

---

# A — Freeze the test candidate

## A1. Confirm automatic preflight

- [ ] `Fiverr Automatic Go-Live Preflight` is green on the intended core ref.
- [ ] `Fiverr Landing Quality Gate` is green on the intended frontend ref.
- [ ] No newer unreviewed code will be substituted during this acceptance run.

Evidence:
- core commit/ref:
- frontend commit/ref:
- workflow run IDs:

PASS criterion: all automatic gates green for the refs under test.

---

# B — Real Business Central Online Extension acceptance

## B1. Build/package candidate

Build the `.app` from the frozen core ref.

Verify manifest:

- [ ] version = `1.0.2.30`
- [ ] runtime = `16.0`
- [ ] application/platform = BC 27.x
- [ ] privacy URL = `https://bcsentinel.com/datenschutz`

Evidence:
- artifact filename/hash:
- build log:

## B2. Install / upgrade in real BC Online

- [ ] Install the candidate `.app` in the intended sandbox/test tenant.
- [ ] If upgrading, verify upgrade completes cleanly and existing setup is preserved where expected.
- [ ] Open Extension Management and capture the installed version.

Evidence screenshot: **BC-01 Extension Management**.

PASS criterion: candidate is installed and accessible without install/upgrade errors.

---

# C — Non-SUPER acceptance

## C1. Create/select pilot user

Assign only:

- **BCSENTINEL PILOT**
- normal Business Central permissions the user already needs for the source business data

Do **not** assign SUPER to solve BCSentinel permission errors.

Evidence screenshot: **BC-02 Permission assignment**, showing BCSENTINEL PILOT and no SUPER.

## C2. Setup actions without SUPER

Using the pilot user:

- [ ] open **BCSentinel Setup**;
- [ ] edit allowed setup fields;
- [ ] Data Processing Consent works;
- [ ] Registration Invite Code can be entered;
- [ ] Register Tenant works;
- [ ] Test BCSentinel Connection works;
- [ ] Refresh Product Access works;
- [ ] Scan History opens;
- [ ] Start Scan can be invoked when access allows it;
- [ ] report actions can be opened.

PASS criterion: approved controlled-pilot journey succeeds without SUPER.

---

# D — Initial tenant registration and scan

## D1. Configure onboarding

- [ ] API Base URL points to the intended environment.
- [ ] Data Processing Notice reviewed.
- [ ] Data Processing Consent enabled.
- [ ] invite code entered if required.
- [ ] report/notification email configured through the accepted flow.
- [ ] preferred language configured.

Evidence screenshots: **BC-03 Setup**, **BC-04 Consent/onboarding**.

## D2. Register

- [ ] Register Tenant.
- [ ] registration confirmation appears.
- [ ] Test BCSentinel Connection succeeds.
- [ ] Product Access can be refreshed.

Evidence: **BC-05 Registration**, connection result.

## D3. Initial full Data Health Scan

- [ ] verify intended standard modules are enabled;
- [ ] start scan;
- [ ] capture running state;
- [ ] wait for successful completion;
- [ ] confirm executed standard scope/modules/checks;
- [ ] record `Scan.total_records` / authoritative Fiverr volume class;
- [ ] confirm only one initial scan exists at this point.

Evidence: **BC-06 modules**, **BC-07 running scan**, **BC-08 completed scan**.

Record:
- scan ID:
- total records:
- volume class:
- modules/checks executed:

---

# E — Report Visual QA on real data

Perform this on the same completed initial scan unless the report contract explicitly requires the later Validation scan.

## E1. Free Health

Check HTML and PDF:

- [ ] correct company/environment/date/scan context;
- [ ] no paid-only finding detail leak;
- [ ] no exact paid EUR values;
- [ ] score / severity / risk-area presentation coherent;
- [ ] no clipping, overflow, broken icons, blank labels, `None`, `undefined` or placeholder data;
- [ ] umlauts/special characters render correctly;
- [ ] share/open link works and is tenant-bound.

Result: PASS / FAIL

## E2. Quick Assessment

Grant Quick through the operator flow using a test Fiverr order reference.

Verify:

- [ ] no new scan was created;
- [ ] permanent Quick entitlement is visible;
- [ ] same initial scan resolves to Quick;
- [ ] maximum Top 5 prioritized findings;
- [ ] severity, affected records, risk area, impact band and concise next action render correctly;
- [ ] no exact EUR values / issue codes / full root cause / record drilldown;
- [ ] DE output visually accepted;
- [ ] EN output visually accepted;
- [ ] HTML/PDF/share link accepted.

Record entitlement/order ref and screenshots.

## E3. Full Assessment

Grant Full against the same qualifying initial scan.

Verify:

- [ ] no new scan was created;
- [ ] same scan now resolves to Full;
- [ ] 7-day full-detail window shown correctly;
- [ ] complete paid finding set available;
- [ ] modeled impact, root-cause context, prioritization and remediation guidance coherent;
- [ ] 4-page management report matches the frozen Lovable visual target as closely as the final implementation contract requires;
- [ ] Finding Appendix contains all findings and tolerates long titles/text, umlauts and large record/impact values;
- [ ] DE output visually accepted;
- [ ] EN output visually accepted;
- [ ] HTML/PDF/share link accepted.

Record scan ID and confirm it is identical to Quick baseline scan ID.

---

# F — Real Tenant A / Tenant B isolation

Use two genuinely separate BC SaaS tenant/company identities and their own BCSentinel registrations/tokens.

## F1. Positive controls

- [ ] Tenant A can access its own scans/reports.
- [ ] Tenant B can access its own scans/reports.

## F2. Negative controls

Attempt only safe read/access tests; do not modify other tenant data.

- [ ] Tenant A cannot read Tenant B scan/report/detail by guessed/copied ID.
- [ ] Tenant B cannot read Tenant A scan/report/detail.
- [ ] Tenant A share/report token cannot reveal Tenant B data.
- [ ] Tenant B share/report token cannot reveal Tenant A data.
- [ ] operator tenant search/grant targets the selected tenant only.
- [ ] switching BC companies/tenants does not reuse another tenant's registration token incorrectly.

PASS criterion: all cross-tenant attempts are denied/not found and no data leaks.

Evidence: response/status screenshots and non-secret IDs.

---

# G — Validation real journey

Prerequisite: paid-test Full Assessment baseline exists.

- [ ] implement at least one safe test data-quality change/remediation in BC;
- [ ] grant Validation with a test Fiverr order reference;
- [ ] exactly one new Validation scan credit appears;
- [ ] start one new full scan;
- [ ] Validation 7-day detail window anchors to credit consumption/new scan as designed;
- [ ] baseline references the paid Full Assessment scan explicitly;
- [ ] exactly two scans exist for the initial+validation journey;
- [ ] Validation classifies relevant findings as Resolved / Improved / Remaining / Regressed / New where supported;
- [ ] score/impact deltas are coherent;
- [ ] Validation HTML/PDF DE/EN visual QA passes.

Record:
- Full baseline scan ID:
- Validation scan ID:
- Validation credit/order ref:

---

# H — Lifecycle email / SMTP / DNS acceptance

Use the intended production sender/provider configuration.

## H1. DNS/provider

- [ ] SPF valid for sender domain.
- [ ] DKIM valid.
- [ ] DMARC record present and intended policy verified.
- [ ] From/Reply-To identity correct.
- [ ] provider credentials/config are production-ready and stored only in approved secret/config locations.

## H2. Delivery events

Trigger representative DE and EN messages:

- [ ] registration completed;
- [ ] scan started;
- [ ] scan completed;
- [ ] Quick activated;
- [ ] Full activated;
- [ ] Full expiring/expired where practical in a controlled test;
- [ ] Validation available;
- [ ] Validation completed;
- [ ] Validation expiring where practical.

Check:

- [ ] correct language;
- [ ] Admin Editor changes are actually reflected in delivery;
- [ ] report links work;
- [ ] Fiverr next-purchase recommendation matches actual `total_records` and current result layer;
- [ ] no secret/token leakage in visible email body/URL;
- [ ] inbox placement accepted at representative providers;
- [ ] spam placement checked;
- [ ] bounce/failure behavior documented and observable;
- [ ] retries do not silently lose queued mail.

PASS criterion: real sender is authenticated and representative lifecycle delivery is accepted.

---

# I — Backup / off-host restore acceptance

Use the actual production backup/recovery procedure, not only unit/CI automation.

- [ ] create a production-style PostgreSQL backup;
- [ ] verify checksum/integrity;
- [ ] copy/store backup in the approved off-host destination;
- [ ] restore into an isolated restore database/environment;
- [ ] verify schema/Alembic revision;
- [ ] probe representative tenants/scans/findings/config rows;
- [ ] document restore commands and operator responsible;
- [ ] confirm no destructive `down -v` or equivalent step is required.

PASS criterion: usable isolated restore proven from the off-host artifact.

---

# J — Legal / privacy / provider facts

Execute `docs/LEGAL_PRIVACY_PROVIDER_ACCEPTANCE.md`.

At minimum:

- [ ] imprint/provider facts final;
- [ ] privacy text final;
- [ ] hosting/provider facts and AVV/DPA position verified;
- [ ] retention/deletion policy verified;
- [ ] modeled-impact disclaimer verified;
- [ ] production privacy/help URLs return intended content;
- [ ] Fiverr copy does not conflict with public legal/privacy pages.

This remains a human sign-off.

---

# K — Immutable Release Candidate → PROD

Only after B–J PASS.

- [ ] record exact core commit SHA;
- [ ] record exact frontend commit SHA;
- [ ] record exact Extension artifact hash/version;
- [ ] ensure all required CI checks are green for those refs;
- [ ] create/tag the immutable RC according to the project release process;
- [ ] take pre-deploy backup;
- [ ] deploy/promote exactly the reviewed refs;
- [ ] run migrations;
- [ ] verify backend/public health/readiness;
- [ ] verify nginx/routing/TLS;
- [ ] verify privacy/help pages;
- [ ] verify operator console;
- [ ] confirm rollback ref/process.

Do not silently rebuild from a different branch/head after acceptance.

---

# L — Fresh external-like PROD E2E

Use fresh test identities and behave like a new Fiverr customer.

## L1. Quick-first path

Fiverr test order → Requirements → Extension install → BCSENTINEL PILOT → consent/email/language → registration → initial scan → authoritative volume → operator Quick grant → Quick mail → Quick report → Full upgrade/order → same scan Full unlock → Full mail/report → remediation → Validation order/grant → one new scan → Validation mail/report.

Assert:

- [ ] no second scan before Validation;
- [ ] price/add-on recommendation matches `total_records`;
- [ ] all Fiverr-origin payment/commercial actions remain on Fiverr;
- [ ] delivery PDF/report is the expected product layer;
- [ ] operator audit contains channel/order/action refs.

## L2. Direct-Full path

Fresh tenant → initial scan → Full purchased directly on Fiverr → Full operator grant → same initial scan unlocks Full without Quick purchase or rescan.

PASS criterion: both external-like paths complete without manual database edits or privilege bypasses.

---

# M — Fiverr publish/dry-run

- [ ] final Gig title/description/FAQ/package copy matches frozen contract;
- [ ] Requirements configured from `FIVERR_REQUIREMENTS_DELIVERY_FINAL.md`;
- [ ] Delivery templates configured;
- [ ] Quick/Full final Lovable Sample Reports DE/EN uploaded when ready;
- [ ] final Gig images uploaded;
- [ ] desktop/mobile Fiverr preview reviewed;
- [ ] one real Fiverr order dry-run completed;
- [ ] published Fiverr URL recorded.

---

# N — Landing CTA activation

After Fiverr URL exists:

- [ ] set `VITE_FIVERR_GIG_URL` to the real published Gig URL;
- [ ] deploy the reviewed frontend ref;
- [ ] verify desktop/mobile CTA;
- [ ] verify CTA opens the intended Fiverr Gig;
- [ ] verify public copy still says starting at $149, fixed tiers through 20m and Custom Offer above 20m;
- [ ] final privacy/imprint pages checked.

---

# Final Go/No-Go

Go only when every P0 block B–L is PASS and the intended Fiverr Gig/delivery assets are ready.

Final record:

- Core RC SHA:
- Frontend RC SHA:
- Extension version/hash:
- PROD deployment date:
- E2E scan IDs:
- Fiverr dry-run order ID:
- Legal/privacy signer/date:
- GO / NO-GO:
- Notes:
