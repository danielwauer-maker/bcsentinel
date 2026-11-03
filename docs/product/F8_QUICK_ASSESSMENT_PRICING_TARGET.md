# F8 Final Contract — Quick Assessment + Record-Volume Pricing

Status: **frozen for Fiverr launch** as of 2026-11-03.

## Final customer journey

Free Health Check → Quick Assessment → Full Assessment → Validation → Monitoring.

## Scan architecture

There remains exactly one customer-facing initial scan engine/depth: the full BCSentinel Data Health / Deep Scan.

The initial customer scan is executed once and stored in full. Free Health Check, Quick Assessment and Full Assessment are progressive access layers over that same initial scan. A new scan is created only for Validation after remediation; Monitoring later adds recurring full scans.

### Free Health Check

- Price: free.
- Exactly one initial full Data Health Scan for a newly registered tenant.
- Aggregate-only result: score, counts, severity, risk areas and impact band.
- No finding titles, issue codes, exact EUR values, root causes, detailed recommendations, record drilldowns or remediation worklists.
- Free Health Check is **not** sold as a paid Fiverr package.

### Quick Assessment

Quick Assessment is an entitlement/report layer, not a second scan mode.

Frozen scope:
- reuse the qualifying existing initial scan;
- no scan credit and no rescan;
- permanent Quick entitlement until explicitly revoked;
- reveal up to Top 5 prioritized findings;
- finding title, severity, affected count and risk area for the exposed subset;
- short management interpretation and limited recommended next actions;
- no complete root-cause catalogue;
- no complete finding list;
- no record-level drilldown;
- no full remediation worklist;
- no exact complete Estimated Loss / Potential Saving model; aggregate impact band remains available;
- dedicated Quick Assessment HTML/PDF report;
- Fiverr launch package name: **BASIC — Quick Assessment**.

### Full Assessment

- reuse the same qualifying existing scan;
- no rescan;
- full findings, exact modeled financial values, root-cause context, prioritization, recommendations and allowed detail/drilldown surfaces;
- professional Assessment Report;
- fixed 7-day full-detail access after activation;
- optional one-time +7-day extension remains technically available, but is not a separate Fiverr launch package;
- Fiverr launch package name: **ADVANCED — Full Assessment**.

### Validation

- separate follow-up Gig / offer, not bundled into ADVANCED;
- requires prior paid Full Assessment baseline;
- grants exactly one new validation scan credit;
- customer applies remediation first, then runs a new full Data Health Scan;
- before/after comparison: resolved, improved, remaining, regressed and new;
- fixed 7-day Validation result window anchored to validation scan consumption.

### Monitoring

- recurring full scans while subscription is active;
- later launch phase; not required for the first Fiverr controlled pilot unless scope changes.

## Canonical record-volume classes

Use one shared sizing taxonomy across Fiverr, direct sales, operator tooling, future Stripe/AppSource/partner pricing and reporting:

| Class | Analyzed records |
|---|---:|
| Micro | ≤100,000 |
| Small | 100,001–250,000 |
| Medium | 250,001–1,000,000 |
| Large | 1,000,001–5,000,000 |
| Enterprise | 5,000,001–20,000,000 |
| Custom | >20,000,000 |

The backend derives the class from authoritative analyzed `Scan.total_records` rather than customer self-estimation whenever possible.

## Frozen Fiverr launch pricing (USD)

These values include the commercial Fiverr margin/provision assumption and are the launch source of truth for operator recommendations and Fiverr copy.

| Record volume | BASIC — Quick Assessment | ADVANCED — Full Assessment | Validation follow-up |
|---|---:|---:|---:|
| ≤100k | **$149** | **$349** | **$179** |
| 100k–250k | **$199** | **$399** | **$219** |
| 250k–1m | **$279** | **$549** | **$289** |
| 1m–5m | **$429** | **$799** | **$429** |
| 5m–20m | **$649** | **$1,199** | **$649** |
| >20m | **Custom Offer** | **Custom Offer** | **Custom Offer** |

## Fiverr package freeze

Launch with exactly these commercial products:

1. **BASIC — Quick Assessment**
2. **ADVANCED — Full Assessment**
3. **Validation** as a separate follow-up Gig / Custom Offer after Full Assessment

There is no paid Fiverr Free Health Check package and no launch-time Assessment Plus/Premium package.

## Channel behavior

### Visitor from BCSentinel.com / LinkedIn / direct

Free Health Check → Quick Assessment or Full Assessment → Validation.

### Visitor arriving directly on Fiverr

The customer may buy Quick Assessment or Full Assessment directly. During fulfillment, the normal initial BCSentinel Free Health Scan is performed as the technical baseline and the purchased entitlement unlocks the corresponding result layer. The customer does not need to purchase a separate Free product on Fiverr.

Fiverr remains the commercial/payment channel for Fiverr-origin paid services. The free technical scan must not be used to redirect paid Fiverr-origin transactions off-platform.

## Frozen implementation principles

- No Quick Scan engine.
- No second scan between Free, Quick Assessment and Full Assessment.
- Progressive access over one stored full initial scan.
- Quick entitlement is permanent until explicit revoke.
- New scan only for Validation/remediation proof, then recurring scans for Monitoring.
- Validation requires a paid Full Assessment baseline.
- Record-volume pricing is centralized and channel-aware.
- Fiverr pricing is sales-channel metadata, not entitlement semantics.
- Direct/Stripe EUR pricing is independent and must not be overwritten by Fiverr pricing changes.
- `Scan.total_records` is authoritative for final Fiverr record class and recommendation.
