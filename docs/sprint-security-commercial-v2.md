# Sprint security and commercial v2

The registration changes were checked on 9 November 2026 with 12 HTTP and
service tests on an isolated PostgreSQL 15 container. A separate PostgreSQL
test ran two concurrent first registrations of the same identity and observed
one successful creation and one rejection. The existing Business Central
client supplies the tenant ID and API token as headers on re-registration.
These tests do not replace a real Business Central runtime acceptance.

The current paid v2 grant is `grant_v2_access_purchase`. It locks the tenant,
requires an existing verified positive EUR purchase, records a source-scoped
entitlement and grants a Validation credit in the same transaction. The
legacy `grant_product_entitlement` overwrites one-time expiry using the
seven-day legacy path and cannot issue v2 operator access safely.

## Operator API

Authenticated operators submit form-encoded requests with the existing admin
HTTP Basic credentials and CSRF token. The operator verifies the external
payment and tenant mapping before submitting the amount actually paid in EUR.

- `POST /admin/operator/{tenant_id}/v2/grant` accepts `product_code`,
  `order_reference`, `order_position` and `amount_eur`. Supported products are
  `full_assessment_v2`, `access_renewal`, and
  `access_renewal_validation`. A completed original Free scan bound to the
  registered company, EUR and a confirmed scope is mandatory. Renewal products
  additionally require a paid Full v2 purchase for the tenant.
- `POST /admin/operator/{tenant_id}/v2/monitoring` accepts the same order and
  payment fields, a monthly or annual monitoring SKU, and timezone-aware
  `period_start` and `period_end`. Each confirmed paid period has its own order
  position and subscription record. It does not automatically renew.
- `POST /admin/operator/{tenant_id}/v2/monitoring/cancel` accepts the order
  and position and records cancellation at the end of that paid period.
- `POST /admin/operator/{tenant_id}/v2/revoke` accepts the order, position and
  refund `reason`. The purchase and its entitlement are revoked. Unused
  Validation credits are revoked, while consumed credits and scans remain.
  A confirmed reversal received before its grant records a refunded,
  zero-amount placeholder with an unknown SKU to prevent later replay. The
  amount is unknown rather than an inferred payment.

The order and position produce a deterministic key in the existing unique
`provider_checkout_session_id` column. A tenant row lock serializes grants for
that tenant. A duplicate matching request returns the existing action, while
a conflicting tenant, SKU, amount or revoked purchase fails closed. Existing
purchase, entitlement, credit ledger, subscription and operator audit tables
are reused, so no schema migration is required by these changes.

V2 entitlements use the same locked purchase grant as checkout. Refunds affect
the associated purchase and credit. Later stacked purchase windows are
recalculated to preserve their purchased 14 days. The diagnostic payment
reversal flag is separate from tenant suspension. The existing tenant status
checks continue to enforce security suspension. Legacy grants continue to use
their existing policy. These paths still require BC, DEV and production runtime
acceptance, including real provider, operator and scheduler workflows.

The operator flow currently accepts confirmed EUR payments and scan baselines
with verified EUR LCY. The monitoring dates are explicit confirmed dates in UTC
or with a timezone offset. Renewals require a new confirmed order position;
neither cancellation nor expiry creates a payment or a new period. A period
can be cancelled at its end or revoked immediately by a confirmed refund.
