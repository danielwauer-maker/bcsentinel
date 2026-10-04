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
