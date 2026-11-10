# Scan provenance: comparison contract, incomplete implementation

Status: **partial and not a release gate**. A versioned partial check-observation payload is emitted by the AL `AddCountFinding` path and may be persisted through authenticated leased scan sync. Historical scans do not become verified by the presence of this code. Migration `0038_scan_execution_evidence` creates a new table without backfill. The existing report/export restrictions must remain active.

## What was found

The AL runner has a check selection catalogue, but many checks execute in grouped procedures that increment counters and only persist findings; it does not persist a complete per-check outcome ledger. `DH Deep Scan Finding`.`Group Key` incorporates the run SystemId and the synced `finding_id` is the finding row SystemId. Neither proves a stable identity across runs. A missing finding therefore cannot establish that a check passed or that the original problem was fixed. Historical environment, method version, complete coverage and score/impact model versions are not reliably established.

## Provisional comparison primitives

`scan_comparability_service.py` defines `bcs-check-catalog-v1`: UTF-8 canonical compact JSON containing contract, explicit catalog and methodology versions and sorted normalized `(check code, module)` pairs, then SHA-256. Duplicate/empty check codes are rejected. Input ordering does not change the digest.

`bcs-finding-comparison-v1` hashes a compact JSON array of contract, tenant, canonical BC company GUID, check code, method version, module, finding type, criterion and the **affected record's** BC SystemId. Missing/invalid IDs return no identity. A deleted and recreated BC record has a new identity. Group or aggregate findings without a proven stable subject are not comparable; neither the scan's finding row SystemId nor its run-dependent group key is a substitute. Hashing is not anonymization, and identities must be handled as customer-related data.

The comparator accepts immutable in-memory evidence objects only from a future **trusted verification and persistence layer**. `source_verified` is an internal assertion, not an externally trustworthy API claim. It fails closed on missing data, mismatched tenant/company/environment/currency/scope/methodology/catalog, incomplete or failed scan/checks, unstable finding identities and invalid scan order. It can report per-check comparability. Health-score and impact comparability are always false because their own versioned inputs and model are not established.

## Partial execution observations

### Declared start expectations (`0039`)

`POST /scan/start` optionally accepts `bc-scan-expectation-v1`. The authenticated tenant must already have the same registered company and environment. The payload contains a methodology and catalog version, company, environment, LCY, selected modules, and unique check/module/enabled entries. The backend adds tenant and scan identity, sorts both sets, computes a catalog fingerprint and binds the canonical payload hash into the existing start idempotency hash. The expectation row, accepted scan, free slot or paid credit and lifecycle are committed in one transaction. Identical reordered retries replay; modified or omitted expectations conflict. An existing orphan or historic scan cannot acquire a new expectation. `created_at_utc` is the server-side acceptance time. Migration 0039 adds immutable-row guards and does not edit migration 0038 or backfill prior scans.

If such an expectation exists, final sync checks its hash, tenant, company, environment, currency and module set. Execution observations must refer to declared checks, follow the server acceptance time and agree with their enabled/disabled state; submitted findings must have an observation. This prevents accepting contradictory final evidence, but missing observations remain partial and do not prove successful completion.

The backend pins the 199 code/module pairs from the 1.0.2.57 AL default catalog and rejects incomplete, altered or unsupported catalog/version declarations. A source-contract test checks that inventory against the AL source. This confirms only the declared inventory, not execution of the checks or the trustworthiness of client version claims.

This remains a **source declaration, not verified complete methodology**: the AL client does not yet create or persist the snapshot, and the server has not established that the runtime actually uses the declared settings. Its presence must never set `source_verified` or enable a comparison. Missing scope/version details, execution lifecycle, actual frozen client selection and stable record identities remain open.

For an authenticated legacy tenant with no registered company, `/scan/sync` preserves the legacy scan flow but declines to persist partial check observations and returns `execution_evidence_status: unavailable_company_binding`. It does not bind a submitted company, invent evidence, grant a credit or make the scan comparable. Already-persisted evidence cannot be dropped via this fallback. A trustworthy future company-binding proof remains necessary.

`bc-check-execution-partial-v1` contains only check code, PASS/FINDINGS/SKIPPED, count of emitted finding rows and observation time. The AL runner records those when `AddCountFinding` or one of six explicitly instrumented duplicate-check procedures actually reaches its individual outcome; it does not infer a missing check passed. This covers a subset of checks, not the full catalog, and does not establish FAILED, NOT_EXECUTED, per-check start times, complete scope, methodology or stable record identities. Group failure can leave partial or no durable observations; failure telemetry is not finalized by this path.

The optional sync accepts at most 1,500 unique check codes and a bounded payload, requires authenticated tenant, matching registered company and original scan execution lease, and rejects backfilling completed historical scans. It canonicalizes check order and full sync identity without storing lease secrets. Exact retries return persisted results; changed or evidence-omitting retries are rejected. Database migration 0038 binds scan/tenant/company on insert, rejects direct update/delete, and permits parent-scan retention deletion. Downgrade refuses to remove a nonempty evidence table. PostgreSQL administrators can override database controls; these triggers are not a cryptographic attestation.

Validation and Monitoring call the same persisted-evidence adapter in v2. For historical or `partial-v1` evidence it returns `MISSING_PROVENANCE` and all comparison flags false. This adapter intentionally has no path that elevates partial evidence to `source_verified`. Existing legacy report values are not made comparable by this metadata, and export guards remain unchanged.
Existing immutable report archives created before this metadata are not rewritten; their missing metadata must not be interpreted as verified evidence.

## Work still required

1. Instrument the remaining actual AL checks, including technical failure and nonexecution; preserve transactional correctness if a grouped procedure fails or a scan retries. Define and capture the full catalog/version and immutable scope at the true source.
2. Establish which checks are per-record, aggregate or grouped. Supply stable affected-record SystemIds only where actually present and safe; ambiguous groups must remain noncomparable.
3. Extend the existing partial authenticated BC sync contract with verifiable environment, catalog/methodology, expected check coverage, scope and stable identities; establish full-source finalization and partial/aborted-run semantics.
4. Prove the full evidence schema and database-enforced immutability across retries, restore, concurrent requests and actual BC runtime. Never set default evidence for old data.
5. Extend the currently fail-closed shared adapter for a future fully verified schema and integrate verified comparisons in Validation and Monitoring, including archive and security checks. Do not treat partial evidence as proof that any existing report is comparable.
6. Build BC27 and perform real sandbox upgrade and runtime verification only after the required operator approvals.
**Compatibility gate:** A new client that sends a start expectation requires an already registered company. For an unbound legacy tenant the existing sync path continues without storing execution evidence, as described above. A safe company-binding procedure remains required before such a tenant can produce verified provenance. Legacy payloads without optional evidence retain their existing behavior.
