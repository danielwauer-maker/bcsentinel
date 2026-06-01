# BCSentinel Processing Overview

Status: Phase 1 pilot operation for 1-3 hand-guided customers.

## Processing purpose

BCSentinel processes Business Central metadata, counters, scan findings, commercial impact estimates, tenant licensing state, and support-relevant status data to provide data health analysis, dashboard reporting, billing, and pilot support.

## Business Central data read by the extension

- Customer, vendor, item, ledger, sales, purchasing, inventory, CRM, manufacturing, service, jobs, and HR-related records are read locally in Business Central for checks.
- Quick Scan sends aggregated counters and data profile counts.
- Deep Scan sends finding codes, categories, severities, affected counts, recommendation previews, module scores, data profile counts, and calculated commercial impact data.
- Duplicate checks may create local Business Central findings that include values such as e-mail addresses, VAT registration numbers, names, post codes, and cities. These values should be treated as personal or business-sensitive data.

## Data stored in the BCSentinel backend

- Tenant id, environment name, app version, creation and last-seen timestamps.
- API token hash only for new tenants. The plaintext API token is returned once at registration and must not be stored in backend tables for new tenants.
- Scan headers, scan issue records, scan run status, module status, and recent event messages.
- Billing subscription and invoice metadata from Stripe.
- Partner applications, partner users, referral and commission metadata when partner flows are used.
- Admin audit events for operational traceability.

## Data minimization rules for Phase 1

- Do not send record-level customer/vendor/item master data to the backend unless required for a premium drilldown flow explicitly agreed with the pilot customer.
- Do not log API tokens, registration invite codes, Stripe secrets, reset tokens, or passwords.
- Keep registration invite codes outside Git and provide them manually to pilot customers.
- Keep pilot tenants manually approved and limited to named customers.

## Processing roles

- Customer: controller for Business Central data.
- BCSentinel operator: processor for SaaS scan processing and support.
- Stripe: independent provider/processor depending on billing setup.
- Hosting provider: infrastructure processor.

This document is operational guidance and not legal advice. A customer-facing DPA/AVV must confirm final roles, subprocessors, retention periods, and technical-organizational measures.
