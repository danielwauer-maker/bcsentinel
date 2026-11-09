# Scan provenance: comparison contract, incomplete implementation

Status: **experimental, not wired into scan sync or reports; not a release gate**. Historical scans do not become verified by the presence of this code. No migration or backfill is included. The existing report/export restrictions must remain active.

## What was found

The AL runner has a check selection catalogue, but many checks execute in grouped procedures that increment counters and only persist findings; it does not persist a complete per-check outcome ledger. `DH Deep Scan Finding`.`Group Key` incorporates the run SystemId and the synced `finding_id` is the finding row SystemId. Neither proves a stable identity across runs. A missing finding therefore cannot establish that a check passed or that the original problem was fixed. Historical environment, method version, complete coverage and score/impact model versions are not reliably established.

## Provisional comparison primitives

`scan_comparability_service.py` defines `bcs-check-catalog-v1`: UTF-8 canonical compact JSON containing contract, explicit catalog and methodology versions and sorted normalized `(check code, module)` pairs, then SHA-256. Duplicate/empty check codes are rejected. Input ordering does not change the digest.

`bcs-finding-comparison-v1` hashes a compact JSON array of contract, tenant, canonical BC company GUID, check code, method version, module, finding type, criterion and the **affected record's** BC SystemId. Missing/invalid IDs return no identity. A deleted and recreated BC record has a new identity. Group or aggregate findings without a proven stable subject are not comparable; neither the scan's finding row SystemId nor its run-dependent group key is a substitute. Hashing is not anonymization, and identities must be handled as customer-related data.

The comparator accepts immutable in-memory evidence objects only from a future **trusted verification and persistence layer**. `source_verified` is an internal assertion, not an externally trustworthy API claim. It fails closed on missing data, mismatched tenant/company/environment/currency/scope/methodology/catalog, incomplete or failed scan/checks, unstable finding identities and invalid scan order. It can report per-check comparability. Health-score and impact comparability are always false because their own versioned inputs and model are not established.

## Work still required

1. Instrument each actual AL check, including passed/no-finding, failure, skip, and nonexecution; preserve transactional correctness if a grouped procedure fails or a scan retries. Define the full catalog/version at the true source.
2. Establish which checks are per-record, aggregate or grouped. Supply stable affected-record SystemIds only where actually present and safe; ambiguous groups must remain noncomparable.
3. Add a versioned authenticated BC sync contract; bind tenant, company, environment and currency to the scan. Establish how source evidence is authenticated, validated and finalized, including parallel/idempotent retries.
4. Design and test a non-destructive PostgreSQL migration, referential integrity and database-enforced immutable completed snapshots; preserve retention/deletion semantics. Do not set default evidence for old data.
5. Add a trusted adapter from persisted evidence to this comparator and integrate it in both Validation and Monitoring, including archive and security checks. Do not treat this experimental function as proof that any existing report is comparable.
6. Build BC27 and perform real sandbox upgrade and runtime verification only after the required operator approvals.
