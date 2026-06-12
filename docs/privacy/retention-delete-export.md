# Retention, Delete, and Export

Status: Phase 1 manual process.

## Retention defaults

- Tenant metadata: retained while the pilot or contract is active.
- Scan data and findings: retained during pilot unless the customer requests deletion earlier.
- Scan run events: retained for support and troubleshooting during pilot.
- Billing data: retained according to accounting and Stripe requirements.
- Admin audit events: retained for security and operational traceability.
- Partner applications: retained only while needed for review and partner onboarding.

## Manual export process

1. Identify the tenant by `tenant_id` in the Admin UI.
2. Export tenant metadata, scan headers, scan issues, scan run statuses, subscriptions, invoices, and relevant audit events from the database.
3. Provide exports as CSV or JSON through a controlled support channel.
4. Record who requested the export, when it was created, and when it was delivered.
5. Delete temporary export files after delivery confirmation.

## Manual delete process

1. Confirm requester authorization with the customer contact.
2. Confirm whether billing/accounting records must be retained.
3. Delete or anonymize scan data, scan issue records, scan run status/events/modules, partner referrals where applicable, and tenant metadata.
4. Keep legally required billing records if deletion is not permitted.
5. Record the deletion in an internal support note.

## Phase 1 limitation

There is no self-service data export or deletion endpoint yet. Pilot contracts must state that export and deletion are handled manually by BCSentinel support within the agreed response time.
