# BCSentinel Fiverr Pilot Release Candidate

Status: **F8 controlled-pilot architecture in progress — manual production gates open**  
Target channel: Fiverr controlled pilot  
Product architecture: one BCSentinel SaaS/Extension stack; Fiverr is a sales channel, not a product fork.

## Frozen customer lifecycle

1. Install the normal BCSentinel Extension in Business Central Online.
2. Enter Data Processing Consent, Report & Notification Email and preferred DE/EN report language.
3. Register tenant.
4. Fresh tenant receives exactly one `free_entry` scan credit.
5. Customer runs one full initial Data Health Scan across all enabled modules/checks.
6. Full result is stored; Free surfaces expose aggregate-only data and the Free Health Report.
7. Fiverr customer may purchase **Quick Assessment** or skip it and purchase **Full Assessment** directly.
8. Quick Assessment operator grant reuses the existing initial scan for 7 days, exposes only the Quick boundary/Top 5 prioritized findings and creates no scan credit.
9. Full Assessment operator grant reuses the same initial scan for 7 days, exposes the complete paid Assessment boundary and creates no scan credit.
10. After Quick or Full expiry, live access falls back to the Free boundary; the stored scan remains available.
11. Only a **paid Full Assessment** qualifies as the Validation baseline. Quick Assessment alone does not.
12. After remediation, Validation purchase is confirmed on Fiverr.
13. Operator grants one Validation scan credit only when a qualifying paid Full Assessment baseline exists.
14. Customer runs a new full Data Health Scan. Consuming the Validation credit starts the 7-day Validation detail/comparison window.
15. Validation Report compares the new scan with the paid Full Assessment baseline.
16. Monitoring may later create recurring full scans; it is outside the initial Fiverr controlled-pilot scope.

## Fiverr package truth

Visible fixed packages use the Micro tier (≤100,000 analyzed records):

- BASIC — **Quick Assessment: $129**
- STANDARD — **Full Assessment: $299**
- PREMIUM — **Assessment Plus: $399** (Full Assessment + one allowed 7-day access extension; no new scan)

Volume pricing for the underlying products:

| Records | Quick | Full | Validation |
|---|---:|---:|---:|
| ≤100k | $129 | $299 | $149 |
| 100,001–250k | $169 | $349 | $179 |
| 250,001–1m | $229 | $449 | $229 |
| 1,000,001–5m | $349 | $649 | $329 |
| 5m–20m | Custom Offer | Custom Offer | Custom Offer |
| >20m | Individual review | Individual review | Individual review |

`Scan.total_records` from the completed scan is authoritative. Larger-than-Micro Fiverr orders are resolved through Fiverr Custom Offers; no off-platform payment path is permitted.

## Automatically verified F8 contracts through point 6

- Deep/full Data Health Scan remains the only initial customer-facing scan engine.
- Exactly one initial Free Entry scan credit is created for a fresh tenant.
- Second unpaid scan is blocked after Free Entry consumption.
- Free results remain aggregate-only.
- Quick Assessment is a separate entitlement/access layer and grants no Full Assessment rights.
- Quick Assessment creates or consumes no scan credit.
- Quick Report has its own JSON/HTML/PDF/share-link contract.
- Quick Report exposes at most five prioritized findings.
- Quick prioritization is deterministic; internal modeled impact may influence ranking but exact EUR values do not leak into Quick.
- Full Assessment and higher tiers can consume Quick-level surfaces, but Quick cannot consume Full surfaces.
- Quick operator grant requires an existing completed initial scan and records sales channel/order/audit context.
- Operator console shows authoritative analyzed record volume, record class and Fiverr price recommendations.
- Quick activation, 48-hour expiry warning and expiry lifecycle mails exist in DE/EN.
- Quick lifecycle report links use the Quick report share contract, remain revocable through current entitlement checks and do not outlive the Quick access window.
- Full Assessment operator grant unlocks the existing initial scan and grants no additional scan credit.
- Validation requires evidence of a prior paid **Full Assessment** baseline.
- Validation operator grant creates exactly one scan credit and does not unlock a second initial assessment scan.
- Validation access starts from `consumed_at` of the Validation credit.
- Assessment +7-day extension remains limited to one extension per Assessment entitlement.
- Operator commercial actions record channel, external order reference, product, scan/credit/entitlement references and actor.
- Lifecycle email outbox remains idempotent, retryable and auditable.
- Paid report endpoints re-check live entitlement on access.
- Operator console requires HTTP Basic admin authentication and CSRF protection for mutations.
- Automated tenant-security, backup/restore and release gates remain part of the acceptance chain.

## Fiverr-specific commercial rules

- Free Health Check is a **BCSentinel product layer**, not a paid Fiverr Basic package.
- A direct Fiverr buyer starts commercially with Quick Assessment or Full Assessment.
- If the buyer has no initial scan yet, the initial Free Entry scan is performed as the technical prerequisite during onboarding.
- If the buyer already has a qualifying initial scan, Quick/Full unlock that stored scan without rescanning.
- Quick may upgrade to Full without rescanning.
- Validation cannot be sold after Quick alone; Full Assessment must exist as the paid baseline.
- All Fiverr-origin payment and commercial communication remain on Fiverr.

## Manual gates before first paid Fiverr pilot customer

- Real BC Online install/upgrade of the final Extension artifact.
- SETUP runtime role acceptance without SUPER.
- Real two-tenant A/B switching and negative cross-tenant isolation evidence.
- Manual visual QA of real Free, Quick, Full Assessment and Validation HTML/PDF output with representative BC data.
- Real SMTP sender configuration and deliverability acceptance: SPF, DKIM, DMARC, inbox/spam placement and bounce handling.
- Real off-host/operational backup and restore drill using the actual PROD destination and documented procedure.
- Freeze immutable reviewed release ref and manually promote that exact ref to PROD.
- Fresh external-like PROD journey: install -> consent/email -> register -> initial Free scan -> Free boundary -> Quick grant -> Quick report -> Full Assessment upgrade -> full report -> expiry/fallback -> Validation grant -> new scan -> comparison/report.
- Separate direct-Full path: initial Free scan -> Full Assessment grant without Quick purchase -> no rescan.
- Final privacy/DPA/legal/provider-facts review.
- Publish/activate the Fiverr Gig using the F8 package copy and perform one real order dry-run through Fiverr.

## Explicit non-blockers for the controlled Fiverr pilot

AppSource submission, full public self-service Free signup, full Stripe provider E2E for Fiverr-origin purchases, Monitoring UX/report perfection, mobile dashboard polish, partner program and complete public SaaS launch automation are not blockers unless pilot scope changes.

## Operator rule

Fiverr payment/order truth remains on Fiverr. The BCSentinel operator grants only the corresponding generic product entitlement/credit after payment is confirmed. Never create Fiverr-specific product codes, scan engines or Extension branches.
