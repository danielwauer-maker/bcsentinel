# BCSentinel Fiverr Pilot Release Candidate

Status: **automatic RC complete — manual production gates open**  
Target channel: Fiverr controlled pilot  
Product architecture: one BCSentinel SaaS/Extension stack; Fiverr is a sales channel, not a product fork.

## Frozen customer lifecycle

1. Install BCSentinel Extension in Business Central Online.
2. Enter Data Processing Consent, Report & Notification Email and preferred DE/EN report language.
3. Register tenant.
4. Fresh tenant receives exactly one `free_entry` scan credit.
5. Customer runs one full Data Health / Deep Scan across all enabled modules/checks.
6. Full result is stored; Free surfaces expose aggregate-only data and Free Health Report.
7. Assessment purchase is confirmed externally (Fiverr in pilot).
8. Operator grants Assessment with Fiverr Order ID. Existing Free scan is unlocked for a fixed 7-day full-access window. No new scan credit is created.
9. After expiry, live detail access falls back to Free; stored scan remains available as Validation baseline/history.
10. Validation purchase is confirmed externally.
11. Operator grants one Validation scan credit only when a prior paid Assessment baseline exists.
12. Customer runs a new full Data Health Scan. Consuming the Validation credit starts the 7-day Validation detail/comparison window.
13. Validation Report compares the new scan to the recorded paid Assessment baseline.

## Automatically verified product contracts

- Deep Scan is the only customer-facing scan depth.
- Exactly one initial Free Entry scan credit is created for a fresh tenant.
- Second unpaid scan is blocked after Free Entry consumption.
- Free results are aggregate-only; paid finding titles, exact financial values, recommendations/root-cause detail and record-level drilldown remain blocked.
- Free Health Report is available without paid access.
- Assessment Report is available only during qualifying paid access.
- Assessment operator grant unlocks the existing scan and grants no additional scan credit.
- Validation requires evidence of a prior paid Assessment baseline.
- Validation operator grant creates exactly one scan credit but does not unlock paid result detail before consumption.
- Validation access starts from `consumed_at` of the Validation credit.
- Validation Report only accepts a scan that actually consumed a Validation credit.
- Assessment +7-day extension is limited to one extension per Assessment entitlement.
- Operator commercial actions record sales channel, external order reference, product, scan/credit/entitlement references and actor.
- Fiverr Order ID/action reuse is rejected.
- Lifecycle email outbox is idempotent, retryable and auditable.
- Transactional lifecycle mail supports DE/EN.
- Report links do not expose API tokens and paid report endpoints re-check live entitlement on every access.
- Operator console requires HTTP Basic admin authentication and CSRF protection for mutations.
- Automated tenant-security attack matrix remains green.
- Automated PostgreSQL backup/restore drill validates migrations, checksum, isolated restore and data probe.

## Automatic RC acceptance

The final F5 head passed backend compile, Alembic single-head validation, full backend regression, dashboard typecheck/build, Contract/AL regression, report/lifecycle regressions, recovery automation, synthetic pilot journey, Fiverr pilot lifecycle contract and release-candidate preparation gates.

A green automatic RC **does not** close the manual production gates below.

## Manual gates before first paid Fiverr pilot customer

- Real BC Online install/upgrade of the final Extension artifact.
- SETUP runtime role acceptance without SUPER. SCHEDULER/ADMIN can be deferred for the one-off Assessment/Validation pilot unless used by the selected workflow.
- Real two-tenant A/B switching and negative cross-tenant isolation evidence.
- Manual visual QA of real Free, Assessment and Validation HTML/PDF output with representative BC data.
- Real SMTP sender configuration and deliverability acceptance: SPF, DKIM, DMARC, inbox/spam placement and bounce handling.
- Real off-host/operational backup and restore drill using the actual PROD backup destination and documented operator procedure.
- Freeze immutable reviewed release ref and manually promote that exact ref to PROD.
- Fresh external-like PROD journey: install -> consent/email -> register -> initial Free scan -> 199/199 checks -> Free report -> paid detail blocked -> Fiverr Assessment grant -> Assessment report -> expiry/fallback -> Validation grant -> new scan -> comparison/report.
- Final privacy/DPA/legal/provider-facts review.
- Publish/activate the Fiverr Gig and perform one real order dry-run through Fiverr.

## Explicit non-blockers for the controlled Fiverr pilot

AppSource submission, full public self-service signup, full Stripe provider E2E for Fiverr-origin purchases, Monitoring UX/report perfection, mobile dashboard polish, partner program and complete public SaaS launch automation are not blockers unless pilot scope changes.

## Operator rule

Fiverr payment/order truth remains on Fiverr. The BCSentinel operator only grants the corresponding generic product entitlement/credit after payment is confirmed. Do not scrape Fiverr and do not create Fiverr-specific product codes or Extension branches.
