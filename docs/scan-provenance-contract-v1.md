# Scan provenance: comparison contract, incomplete implementation

Status: **partial and not a release gate**. A versioned partial check-observation payload is emitted by the AL `AddCountFinding` path and may be persisted through authenticated leased scan sync. Historical scans do not become verified by the presence of this code. Migration `0038_scan_execution_evidence` creates a new table without backfill. The existing report/export restrictions must remain active.

## What was found

The AL runner has a check selection catalogue, but many checks execute in grouped procedures that increment counters and only persist findings; it does not persist a complete per-check outcome ledger. `DH Deep Scan Finding`.`Group Key` incorporates the run SystemId and the synced `finding_id` is the finding row SystemId. Neither proves a stable identity across runs. A missing finding therefore cannot establish that a check passed or that the original problem was fixed. Historical environment, method version, complete coverage and score/impact model versions are not reliably established.

## Provisional comparison primitives

`scan_comparability_service.py` defines `bcs-check-catalog-v1`: UTF-8 canonical compact JSON containing contract, explicit catalog and methodology versions and sorted normalized `(check code, module)` pairs, then SHA-256. Duplicate/empty check codes are rejected. Input ordering does not change the digest.

`bcs-finding-comparison-v1` hashes a compact JSON array of contract, tenant, canonical BC company GUID, check code, method version, module, finding type, criterion and the **affected record's** BC SystemId. Missing/invalid IDs return no identity. A deleted and recreated BC record has a new identity. Group or aggregate findings without a proven stable subject are not comparable; neither the scan's finding row SystemId nor its run-dependent group key is a substitute. Hashing is not anonymization, and identities must be handled as customer-related data.

The comparator accepts immutable in-memory evidence objects only from a future **trusted verification and persistence layer**. `source_verified` is an internal assertion, not an externally trustworthy API claim. It fails closed on missing data, mismatched tenant/company/environment/currency/scope/methodology/catalog, incomplete or failed scan/checks, unstable finding identities and invalid scan order. It can report per-check comparability. Health-score and impact comparability are always false because their own versioned inputs and model are not established.

## Partial execution observations

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
**Compatibility gate:** A new client that sends partial execution evidence requires an already registered tenant company and an active execution lease. Older tenants without that company binding can have their sync rejected; compatibility and a verified binding or an explicitly reported safe fallback must be resolved before rollout. Legacy payloads without the optional evidence retain their existing behavior.
