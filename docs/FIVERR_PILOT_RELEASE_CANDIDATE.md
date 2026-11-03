# BCSentinel Fiverr Pilot Release Candidate

Status: **controlled-pilot architecture implemented — automatic repository work green, manual production gates open**  
Target channel: Fiverr controlled pilot  
Product architecture: one BCSentinel SaaS/Extension stack; Fiverr is a sales channel, not a product fork.  
Automated/manual handoff: [`FIVERR_GOLIVE_AUTOMATED_READINESS.md`](FIVERR_GOLIVE_AUTOMATED_READINESS.md)

## Frozen customer lifecycle

1. Install the normal BCSentinel Extension in Business Central Online.
2. Enter Data Processing Consent, Report & Notification Email and preferred DE/EN report language.
3. Register tenant.
4. Fresh tenant receives exactly one `free_entry` scan credit.
5. Customer runs one full initial Data Health Scan across all enabled standard modules/checks.
6. Full result is stored; Free surfaces expose aggregate-only data and the Free Health Report.
7. Fiverr customer may purchase **Quick Assessment** or skip it and purchase **Full Assessment** directly.
8. Quick Assessment operator grant reuses the existing initial scan, permanently exposes only the Quick boundary / Top 5 prioritized findings and creates no scan credit.
9. Full Assessment operator grant reuses the same initial scan for 7 days, exposes the complete paid Assessment boundary and creates no scan credit.
10. After Full expiry, access falls back to permanent Quick when Quick exists; otherwise to Free.
11. Only a **paid Full Assessment** qualifies as the Validation baseline. Quick Assessment alone does not.
12. After remediation, Validation purchase is confirmed on Fiverr.
13. Operator grants one Validation scan credit only when a qualifying paid Full Assessment baseline exists.
14. Customer runs a new full Data Health Scan. Consuming the Validation credit starts the 7-day Validation detail/comparison window.
15. Validation Report compares the new scan with the paid Full Assessment baseline.
16. Monitoring may later create recurring full scans; it is outside the initial Fiverr controlled-pilot scope.

## Frozen Fiverr launch product model

The controlled launch uses two assessment products plus a separate Validation follow-up:

- **BASIC — Quick Assessment**
- **ADVANCED — Full Assessment**
- **Validation** — separate follow-up Gig / Custom Offer after paid Full Assessment

Not sold at launch:

- Free Health Check as a paid Fiverr package;
- Assessment Plus / Premium as a separate Fiverr package;
- Monitoring.

## Frozen Fiverr pricing (USD)

| Records | Quick | Full | Validation |
|---|---:|---:|---:|
| ≤100k | $149 | $349 | $179 |
| 100,001–250k | $199 | $399 | $219 |
| 250,001–1m | $279 | $549 | $289 |
| 1,000,001–5m | $429 | $799 | $429 |
| 5m–20m | $649 | $1,199 | $649 |
| >20m | Custom Offer | Custom Offer | Custom Offer |

`Scan.total_records` from the completed scan is authoritative. Fiverr-origin commercial communication and payment remain on Fiverr.

## Product and architecture contracts

- Deep/full Data Health Scan remains the only initial customer-facing scan engine.
- Exactly one initial Free Entry scan credit is created for a fresh tenant.
- Second unpaid scan is blocked after Free Entry consumption.
- Free results remain aggregate-only.
- Quick Assessment is a separate permanent entitlement/access layer and grants no Full Assessment rights.
- Quick Assessment creates or consumes no scan credit.
- Quick Report has its own JSON/HTML/PDF/share-link contract and exposes at most five prioritized findings.
- Quick never exposes exact EUR values, issue codes, complete root-cause analysis, record drilldown or the full remediation boundary.
- Full Assessment operator grant unlocks the existing initial scan and grants no additional scan credit.
- Validation requires evidence of a prior paid **Full Assessment** baseline.
- Validation operator grant creates exactly one scan credit.
- Validation access starts from `consumed_at` of the Validation credit.
- Assessment +7-day extension remains technically limited to one extension but is not a separate Fiverr launch product.
- Operator commercial actions record channel, external order reference, product, scan/credit/entitlement references and actor.
- Lifecycle email outbox remains idempotent, retryable and auditable.
- Paid report endpoints re-check live entitlement on access.
- Operator console requires HTTP Basic admin authentication and CSRF protection for mutations.
- Automated tenant-security, backup/restore and release gates remain part of the acceptance chain.

## Fiverr-specific commercial rules

- Free Health Check is a **BCSentinel product layer**, not a paid Fiverr package.
- A direct Fiverr buyer starts commercially with Quick Assessment or Full Assessment.
- If the buyer has no initial scan yet, the initial Free Entry scan is performed as the technical prerequisite during onboarding.
- If the buyer already has a qualifying initial scan, Quick/Full unlock that stored scan without rescanning.
- Quick may upgrade to Full without rescanning.
- Validation cannot be sold after Quick alone; Full Assessment must exist as the paid baseline.
- All Fiverr-origin payment and commercial communication remain on Fiverr.
- Direct/Stripe EUR pricing remains independent from the Fiverr USD matrix.

## Automatic repository acceptance

Automatic repository work is treated as PASS only for code/content contracts that can be proven without external systems. Current automatic scope includes product/price semantics, entitlement funnel, report contracts, operator actions, lifecycle outbox, Fiverr next-purchase guidance, requirements/delivery contract, automated tenant-security gates and PostgreSQL recovery automation.

The dedicated `Fiverr Launch Contract Quality Gate` protects frozen Fiverr package names and pricing markers from documentation drift. Automatic PASS never substitutes for the manual external/runtime gates below.

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
- Publish/activate the Fiverr offer using the frozen package copy and perform one real order dry-run through Fiverr.
- Set the published Fiverr Gig URL as `VITE_FIVERR_GIG_URL`, deploy the reviewed frontend ref and verify the landing CTA.

## Explicit non-blockers for the controlled Fiverr pilot

AppSource submission, full public self-service Free signup, full Stripe provider E2E for Fiverr-origin purchases, Monitoring UX/report perfection, mobile dashboard polish, partner program and complete public SaaS launch automation are not blockers unless pilot scope changes.

## Operator rule

Fiverr payment/order truth remains on Fiverr. The BCSentinel operator grants only the corresponding generic product entitlement/credit after payment is confirmed. Never create Fiverr-specific product codes, scan engines or Extension branches.
