# E1 Entitlement & Tenant Security Contract

Status: frozen for Controlled Pilot acceptance

## Authority order

Every protected tenant request is evaluated in this order:

1. **Credential authentication** — machine API token or short-lived dashboard session token.
2. **Tenant scope** — the authenticated credential resolves to exactly one tenant.
3. **Tenant lifecycle status** — `active`, `suspended`, or `deactivated`.
4. **Product entitlement** — Assessment, Validation Check or Monitoring remains server-authoritative.
5. **Resource ownership** — resource identifiers are always resolved inside the authenticated tenant scope.

Authentication never implies entitlement and entitlement never bypasses tenant suspension.

## Credentials

### Machine / Business Central integration

Business Central and trusted machine integrations may use:

- `X-Tenant-Id`
- `X-Api-Token`

The token is stored as a PBKDF2 hash. Legacy plaintext tenant tokens are upgraded after a successful authenticated request.

### Dashboard runtime

The preferred browser credential is a short-lived `tenant_dashboard_session` JWT issued by `POST /auth/session` after machine-credential authentication.

Properties:

- TTL: 15 minutes
- scope: `tenant:dashboard`
- runtime role: `dashboard_runtime`
- bound to the current tenant API credential hash
- API-key rotation invalidates already-issued dashboard sessions
- tenant suspension/deactivation invalidates effective access immediately
- browser requests use `Authorization: Bearer ...`

A legacy raw API token remains accepted by the dashboard client only as a transition path. It must not be persisted in local storage or treated as a product entitlement.

## Tenant lifecycle

`tenant_access_states.status` is independent from billing/license status:

- `active` — normal authenticated access
- `suspended` — authenticated access blocked
- `deactivated` — authenticated access blocked

Missing state rows are treated as `active` for backward compatibility; migration `0022_tenant_access_states` backfills existing tenants.

## Membership and role boundary

The Controlled Pilot backend does **not** invent a second Business Central user/role system.

- Tenant machine credentials establish tenant membership for the integration principal.
- Dashboard sessions carry only the scoped runtime role `dashboard_runtime`.
- Product access is derived from server-side entitlements, never from a browser role claim.
- Business Central operational roles and permission sets remain authoritative inside Business Central and receive real runtime acceptance in E3.
- The Web Dashboard remains read-only for Business-Central-owned remediation and notification operations.

## Resource isolation

Protected resources must be selected with the authenticated tenant identifier in the database predicate. Foreign resource IDs must not disclose whether a resource exists for another tenant.

For report resources, both a missing ID and a foreign-tenant ID return the same `404 Report not found` response.

## Shared report links

Shared Executive Report links are tenant- and scan-bound, time-limited, entitlement-checked and tenant-lifecycle-checked on every request. Suspension/deactivation therefore invalidates otherwise unexpired share links.

## E1 evidence

Automated E1 evidence covers:

- unknown tenant vs wrong token enumeration resistance
- machine token authentication
- short-lived dashboard session authentication
- API-key rotation invalidating dashboard sessions
- suspended/deactivated tenant blocking
- authentication != entitlement
- report cross-tenant existence masking
- remediation action isolation
- scan-status isolation
- payload/header tenant mismatch protection
- shared-link invalidation after tenant suspension

E3 remains the owner of manual Business Central Viewer / Setup / Scheduler / Admin runtime evidence. E4 remains the owner of real external billing/email-provider validation.
