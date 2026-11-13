# Pilot enrollment #182 — Operator safety and rollout contract

Status: **DRAFT / NO DEPLOY / DO NOT ENABLE**. This document does not authorize a staging merge, BC Sandbox acceptance, pilot credentials, or a customer invitation.

## API protection

The feature is disabled unless `PILOT_ENROLLMENT_ENABLED=true`. All `/internal/pilot/enrollments` routes require both existing HTTP Basic operator credentials and an independently configured `PILOT_ENROLLMENT_ADMIN_KEY` (minimum 32 characters). Requests containing `Origin` or `Sec-Fetch-Site` are rejected. The key is not a replacement for an ingress ACL or network boundary; request headers are not trustworthy network identity.

**Mandatory before enabling:** configure and verify an ingress/reverse-proxy **deny-by-default** rule for `/internal/pilot/enrollments` (including subpaths). Permit only explicitly trusted admin source IPs/VPN or authenticated internal route; deny Internet and public dashboard origins. Verify the *deployed* Nginx/Caddy route, any other proxy entry points, IPv4 and IPv6, and actual external requests. Use the real peer or a trusted load balancer configuration, never arbitrary `X-Forwarded-For` input. Confirm secrets are never logged. No ingress configuration is changed by this PR.

Dedicated key and operator Basic authentication must be provided only from a trusted server-side operator client, via HTTPS. Do not put secrets in browser JavaScript, query parameters, links, shell history, screenshots, issue comments, or ordinary mail. Prevent response caching and access logs capturing request bodies/headers or token response. Rotate the dedicated key after accidental exposure.

## Pilot customer enrollment verification

Before creating/approving an enrollment:
1. Operator independently verifies the customer's authorized contact and BC company/environment identity using a previously established channel; an email string alone is **not** ownership proof.
2. Operator records explicit customer approval and authorized email/identity in approved internal records, without the token.
3. Issue an individual short-lived, one-use code only after verification; deliver it privately over an authenticated channel to the verified contact. The source code intentionally does not implement verified email delivery; do not claim automated delivery.
4. Customer enters the code in BC Setup. Confirm the correct company and environment before first registration. Never paste code into log tickets.
5. Operator checks audit event, enrolled tenant identity, number of Free credits (exactly one), and whether subsequent replay is denied. If a code was leaked, revoke it and reissue a new one before redemption.
6. For failure or timeout, verify the existing enrollment state before reissuing. Registered codes cannot be reissued by the normal API. Do not automatically re-activate a tenant when another admin/security suspension exists.

## Required gate evidence

- Real PostgreSQL two-request concurrent redemption: exactly one success, one rejection, one tenant, one Free credit, one membership, one registered audit event.
- Independent API negative tests for missing/wrong operator key and browser-Origin requests. Network ACL must be independently tested on the actual DEV ingress; unit tests do not prove this.
- Explicit deny with `PILOT_ENROLLMENT_ENABLED=false` in DEV and PROD until approved.
- Final commit SHA: backend suite, migration 0041, PostgreSQL concurrency, BC27 fresh/upgrade and non-SUPER manual BC sandbox in-place upgrade, registration/history preservation.
- Keep global Fiverr release state `NO_GO`; record evidence in AI-PM only after observable gates.

## Rollback and migration caution

Do not delete the enrollment database or undo migration 0041 with populated customer evidence. Revocation/suspension must preserve audit history. Database backup and verified restore path are required before any DEV rollout. Record deployed SHA and use the explicit manual DEV release controller. No automatic promotion to `main`.
