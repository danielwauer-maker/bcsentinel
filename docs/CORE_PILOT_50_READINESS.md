# BCSentinel Core — Pilot Readiness for up to 50 Tenants

Status: **AUTOMATED CLOSURE IN PROGRESS / MANUAL GATES EXPLICIT**

## Pilot boundary

BCSentinel Core is prepared for a controlled pilot program capped at 50 tenants. Admission is staged rather than opened as unrestricted self-service.

Planned waves:

1. 1 tenant
2. up to 5 tenants
3. up to 10 tenants
4. up to 25 tenants
5. up to 50 tenants

Each expansion requires review of the previous wave. A P0 incident stops further admission until the affected gate is repeated.

## Automated evidence

The Core closure gate verifies:

- compatibility-safe legacy product mapping;
- no Monitoring rights from the historic `premium` plan name alone;
- bounded transient SMTP retries and permanent-failure classification;
- public pilot/claims truthfulness;
- 50 isolated tenant admissions through the real scan-start API;
- existing atomic scan/idempotency regression;
- existing multi-tenant dashboard isolation;
- full backend regression;
- real PostgreSQL concurrency/transaction regression;
- AL compile + CodeCop/PTECop through the existing BC gate;
- RC build manifest and SHA-256 generated in CI.

## What this does not prove

The 50-tenant automated test is an isolation/admission preflight. It does not claim that a specific production-sized host has already completed a 24-hour 50-tenant throughput/soak test.

That operational evidence remains a staged pilot gate.


## Public pilot platform closure

The automated Core closure additionally verifies or provides:

- API-backed contact intake with privacy acknowledgement, rate limiting and durable storage;
- operator-visible Contact Inbox independent of SMTP delivery;
- DE/EN invite, password reset and welcome-mail templates;
- bounded transient SMTP retry and safe permanent-failure classification;
- Pilot Page routed through the persistent contact flow;
- current Legal Notice, Privacy, Pilot Terms and DPA/AVV working-template surfaces;
- a current documentation page with explicit screenshot/video capture requirements;
- an explicit deferred high-end design audit roadmap with a >=9.5/10 target after technical closure.

Legal working texts are not considered legally approved by automation. The final operator identity, address, tax/legal wording, support policy and contractual terms remain a manual business/legal sign-off.
