# S03 Pilot Onboarding — Pre-Runtime Hardening

Status: **IMPLEMENTED / AUTOMATED EVIDENCE PENDING**

## Objective

Prepare a controlled pilot onboarding and dashboard-access lifecycle before the real Business Central / customer journey acceptance.

## Existing foundation

- tenant registration and identity binding;
- multi-tenant dashboard memberships;
- cryptographically random dashboard invite tokens;
- invite token hashes stored instead of raw tokens;
- seven-day invite expiry;
- invite token invalidated after activation;
- generic login failure responses;
- localized SMTP invitation contract;
- onboarding/offboarding operator checklist.

## Added in S03 pre-work

### Persistent login throttling

Dashboard users now persist:

- failed-login count;
- temporary lock expiry.

Repeated invalid passwords cause a temporary lock. A valid login after the lock window clears the security counters.

### Password reset

Public reset request:

- always returns the same accepted response;
- does not reveal whether an email address exists;
- issues a cryptographically random token only for active users;
- stores only the token hash;
- expires automatically;
- can only be used once;
- clears login lock state after successful reset.

DE/EN password-reset email templates are versioned through the existing email-template system.

### Operator lifecycle

Authenticated admin operations can:

- suspend dashboard access for a tenant;
- reactivate tenant membership;
- revoke outstanding invite tokens.

Every action is written to Admin Audit.

For multi-tenant users, tenant suspension disables only the selected membership. The whole user is disabled only when no active memberships remain.

### Evidence

`backend/tests/test_dashboard_security_lifecycle.py` covers:

- persistent lockout;
- recovery after lock window;
- non-enumerating reset request;
- one-time reset token;
- login with new password;
- audited suspend/reactivate/invite revoke.

`PILOT-AUTH-001` binds this lifecycle to the pilot E2E evidence matrix.

## Deliberately open

The following cannot be claimed from repository tests alone:

1. real Gmail/Outlook SMTP delivery;
2. SPF/DKIM/DMARC validation for the production sending domain;
3. bounce/unsubscribe/provider feedback handling;
4. real invitation -> activation -> BC connection -> dashboard journey;
5. customer/operator acceptance.

These remain explicit S03 runtime/operational gates.

## Safety

- no existing dashboard passwords are rewritten;
- no tenant membership is automatically re-enabled by registration;
- password-reset responses do not enumerate accounts;
- raw invite/reset tokens are never persisted;
- suspended tenant access invalidates outstanding invite/reset state.


## Mail transport hardening for Core pilot

The dashboard invite/password-reset SMTP transport now retries bounded transient failures up to three attempts.

- SMTP 4xx responses are treated as transient.
- connection/disconnect/timeout failures are treated as transient.
- SMTP 5xx responses are treated as permanent and are not retried.
- stored/operator-visible errors are classified without copying arbitrary provider response bodies.
- retry logic is covered by `backend/tests/test_s03_mail_resilience.py`.

Still external/manual: real provider delivery, SPF/DKIM/DMARC, mailbox reception and provider bounce/feedback behavior.


## Core closure additions

- transient SMTP transport failures use a bounded retry policy;
- permanent SMTP failures are classified without leaking provider response content;
- dashboard invite and password-reset flows are backed by DE/EN templates;
- successful first dashboard activation triggers a best-effort DE/EN welcome message;
- activation remains successful even when the external mail provider is temporarily unavailable;
- real provider delivery, SPF/DKIM/DMARC and bounce/feedback-loop validation remain manual pilot gates.
