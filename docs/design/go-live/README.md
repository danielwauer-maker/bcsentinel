# BCSentinel Go-Live Design Mockups

This directory is the design source-of-truth for the BCSentinel Core user experience.

## Status

- Public landing page: final target mockup
- Pilot landing page: final target mockup
- Dashboard Overview: final Free / Assessment / Monitoring target mockups
- Findings: final Free / Assessment / Monitoring target mockup
- Actions: final Free / Assessment / Monitoring target mockup
- Remaining product surfaces: 10 explored concepts + selected final Free / Assessment / Monitoring target mockup + implementation spec

## Product experience rules

1. GitHub remains the technical source of truth.
2. Backend entitlements are authoritative; frontend locks are only presentation.
3. Free shows clear business value without exposing paid detail.
4. Assessment unlocks full single-analysis depth, recommendations, actions and Executive Report.
5. Monitoring adds history, automation, deltas, alerts, re-validation and outcome tracking.
6. No production plan switching via localStorage.
7. Design language stays consistent across landing page, pilot page, dashboard and reports.
8. Security/hosting claims must stay evidence-based and legally reviewable.

## Structure

- `01-landingpage/` — final public product landing page
- `02-pilotpage/` — final controlled-pilot acquisition page
- `03-overview/` — dashboard overview, Free / Assessment / Monitoring
- `04-findings/` — findings workspace
- `05-actions/` — recommendations/actions workspace
- `06-financial-impact/` — 10 concepts + final
- `07-executive-report/` — 10 concepts + final
- `08-scans/` — 10 concepts + final
- `09-monitoring/` — 10 concepts + final
- `10-settings-security/` — 10 concepts + final
- `11-subscription-billing/` — 10 concepts + final
- `12-auth/` — 10 concepts + final
- `13-docs-support/` — 10 concepts + final

Final SVGs are self-contained and reviewable directly in GitHub.