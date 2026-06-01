# Pilot Runbook

Status: Phase 1 pilot operation.

## Onboarding

1. Create a unique pilot registration invite code and set it in backend environment as `TENANT_REGISTRATION_INVITE_CODE`.
2. Confirm backend `/health` and `/health/ready`.
3. Confirm Alembic revision is current.
4. Provide the pilot invite code and API URL to the customer.
5. Customer enables Data Processing Consent in Business Central setup.
6. Customer registers tenant and runs first scan.
7. Verify scan appears in Admin UI and Analytics dashboard.

## Support workflow

- Capture tenant id, run id, timestamp, and `X-Request-Id` from API responses or logs.
- Never request passwords or API tokens in plain chat/email.
- If a token is suspected exposed, reset registration manually and invalidate the old tenant token.
- For scan failures, check local BC run status first, then backend scan status events.

## Incident workflow

1. Triage severity: data exposure, authentication issue, billing issue, scan failure, performance.
2. Preserve logs with request ids.
3. Notify the customer contact if customer data or availability is impacted.
4. Apply containment: block tenant, rotate invite/API token, disable billing action, or pause scan.
5. Document root cause and follow-up fix.

## Pilot boundaries

- 1-3 hand-guided customers.
- Manual provisioning and support.
- No public self-service registration.
- No SLA beyond pilot agreement.
- No automatic data correction promise.
