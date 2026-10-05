# BCSentinel Go-Live Design Source of Truth

This directory contains the consolidated visual design reference for BCSentinel public pages and product UI.

## Final design areas
1. Landingpage
2. Pilotpage
3. Overview
4. Findings
5. Actions / Measures
6. Financial Impact
7. Executive Summary Report
8. Scans
9. Monitoring
10. Settings / Tenant / Security
11. Subscription / Billing
12. Auth flows
13. Documentation / Support

## Executive Summary Report pack
`07-executive-report/` contains:
- `concepts/01-...svg` through `concepts/10-...svg`: ten explored report directions.
- `final/free.svg`: final Free report design, maximum two A4 pages and no paid finding detail.
- `final/assessment.svg`: final full Assessment executive report.
- `final/monitoring.svg`: final Monitoring report with trend, re-validation and realised impact.
- `final/print-variants.svg`: print/PDF design reference for all three subscriptions.
- `REPORT_DESIGN_SPEC.md`: canonical HTML and print rules.

## Design rules
- GitHub is the technical source of truth.
- Same BCSentinel design DNA across Landingpage, Pilotpage, Dashboard and reports.
- Free shows aggregate value without exposing paid detail.
- Assessment unlocks complete single-analysis depth and actionable recommendations.
- Monitoring adds history, automation, deltas, re-validation and outcome tracking.
- Backend entitlements are authoritative; visual locks are presentation only.
- Product facts, pricing and entitlements must not be duplicated manually when they can be generated from structured source data.

## Status
These files are design/reference material. Runtime behaviour changes require separate implementation PRs and the normal quality gates.
