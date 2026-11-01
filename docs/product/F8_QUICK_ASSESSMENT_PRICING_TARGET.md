# F8 Target Contract — Quick Assessment + Record-Volume Pricing

Status: product target frozen for implementation planning.

## Final customer journey

Free Health Check → Quick Assessment → Full Assessment → Validation → Monitoring.

## Scan architecture

There remains exactly one customer-facing scan engine/depth: the full BCSentinel Data Health / Deep Scan.

The initial customer scan is executed once and stored in full. Free Health Check, Quick Assessment and Full Assessment are progressive access layers over that same initial scan. A new scan is created only for Validation after remediation; Monitoring later adds recurring full scans.

### Free Health Check

- Price: free.
- Exactly one initial full Data Health Scan for a newly registered tenant.
- Aggregate-only result: score, counts, severity, risk areas and impact band.
- No finding titles, issue codes, exact EUR values, root causes, detailed recommendations, record drilldowns or remediation worklists.

### Quick Assessment

Quick Assessment is an entitlement/report layer, not a second scan mode.

Target scope:
- reuse the qualifying existing initial scan;
- no scan credit and no rescan;
- reveal a limited prioritized subset of findings (target: Top 5);
- finding title, severity, affected count and risk area for the exposed subset;
- short management interpretation and limited recommended next actions;
- no complete root-cause catalogue;
- no complete finding list;
- no record-level drilldown;
- no full remediation worklist;
- no exact complete Estimated Loss / Potential Saving model; aggregate impact band remains available;
- dedicated Quick Assessment HTML/PDF report;
- designed as the first paid entry product for Fiverr and direct channels.

### Full Assessment

- reuse the same qualifying existing scan;
- no rescan;
- full findings, exact modeled financial values, root-cause context, prioritization, recommendations and allowed detail/drilldown surfaces;
- professional Assessment Report;
- fixed 7-day full-detail access after activation;
- optional one-time +7-day extension remains possible.

### Validation

- requires prior paid Assessment baseline;
- grants exactly one new validation scan credit;
- customer applies remediation first, then runs a new full Data Health Scan;
- before/after comparison: resolved, improved, remaining, regressed and new;
- fixed 7-day Validation result window anchored to validation scan consumption.

### Monitoring

- recurring full scans while subscription is active;
- later polish, not required for the first controlled Fiverr pilot unless scope changes.

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

The backend should derive the class from authoritative analyzed `total_records` rather than customer self-estimation whenever possible.

## Fiverr pilot pricing target (USD)

These values are the current pilot pricing target and may be commercially tuned without changing the product architecture.

| Record volume | Quick Assessment | Full Assessment | Validation |
|---|---:|---:|---:|
| ≤100k | $129 | $299 | $149 |
| 100k–250k | $169 | $349 | $179 |
| 250k–1m | $229 | $449 | $229 |
| 1m–5m | $349 | $649 | $329 |
| 5m–20m | Custom Offer | Custom Offer | Custom Offer |
| >20m | Individual review | Individual review | Individual review |

## Channel behavior

### Visitor from BCSentinel.com / LinkedIn / direct

Free Health Check → Quick Assessment or Full Assessment → Validation.

### Visitor arriving directly on Fiverr

The customer may buy Quick Assessment or Full Assessment directly. During fulfillment, the normal initial BCSentinel Free Health Scan is performed as the technical baseline and the purchased entitlement unlocks the corresponding result layer. The customer does not need to purchase a separate Free product on Fiverr.

Fiverr remains the commercial/payment channel for Fiverr-origin paid services. The free technical scan must not be used to redirect paid Fiverr-origin transactions off-platform.

## Implementation target

F8 should add, without creating another scan engine:

1. `quick_assessment` entitlement/product code and capability flags.
2. Quick Assessment report contract, HTML/PDF and secure share links.
3. Server-side payload boundary for Top-Finding exposure; never CSS-only hiding.
4. Operator action to grant Quick Assessment with source/order metadata.
5. Lifecycle email events for Quick Assessment activation/expiry where appropriate.
6. Central record-volume class service based on `total_records`.
7. Channel-specific pricing recommendation/read model; Fiverr USD pricing remains sales-channel metadata, not entitlement semantics.
8. Update Fiverr launch kit and landing copy so Basic starts with Quick Assessment rather than selling the Free Health Report.
9. Regression tests proving Free < Quick < Full Assessment detail boundaries and ensuring Quick never creates a new scan credit.

## Frozen principles

- No Quick Scan engine.
- No second scan between Free, Quick Assessment and Full Assessment.
- Progressive access over one stored full initial scan.
- New scan only for Validation/remediation proof, then recurring scans for Monitoring.
- Record-volume pricing is centralized and channel-aware.
- Pricing values may be tuned; entitlement semantics and scan architecture should remain stable.
