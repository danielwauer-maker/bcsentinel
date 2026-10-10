# Sprint D8 — Dashboard Service Pages

Status: implementation candidate

## Scope

- Settings consumes the existing tenant-isolated notification read model and remains read-only.
- Subscription / Billing consumes server-authoritative subscription state and may open the provider billing portal through the existing backend endpoint.
- Support & Docs explains the product boundaries without introducing a second operational surface.
- Auth runtime stops before the application shell when no valid tenant session has been established.
- Locked / 403 / 404 / 500 states are explicit and never fabricate substitute data.
- Existing D6 shell and D7 core pages remain the regression baseline.

## Authority boundaries

Authentication does not imply product access. The runtime boundary remains:

`Authentication -> Tenant Membership -> Tenant Status -> Entitlements -> Product Access`

Business Central remains operative authority for scans, monitoring setup, notification configuration and remediation. The dashboard remains a management/read-model surface. Billing changes are delegated to the server-authorized payment-provider portal.

## Source-of-truth rules

- No product prices are hard-coded on D8 pages.
- Notification settings come from `/notifications/settings`.
- Subscription state comes from `/billing/subscription/status`.
- Billing portal sessions come from `/billing/portal`.
- Missing data is rendered as loading, empty, locked or error state instead of invented zeroes.

## Quality gate

`.github/workflows/dashboard-service-pages-quality.yml` runs:

1. D6 dashboard foundation regression validator.
2. D7 dashboard core pages regression validator.
3. D8 service-page contract validator.
4. TypeScript check.
5. Production dashboard build.

D8 may only be marked PASS after the pull-request checks pass. Target portfolio readiness after accepted D8 remains 94.5% according to the current sprint baseline.
