# Sprint 3A.2 finalization — work in progress

**Not complete. Do not release or claim verified comparability.**

The scan-start endpoint can accept a versioned declared expectation and seals it together with scan acceptance and credit consumption. The declaration includes tenant, scan, registered company, environment, currency, selected modules, methodology and catalog versions and the expected check entries; server-side canonicalization and a deterministic catalog fingerprint make order-independent retries possible. Contradictory retries, late backfills and contradictory final syncs are rejected. Revision `0039_scan_expectation_snapshot` adds guarded storage without modifying revision 0038 or historical scans. Its downgrade refuses to discard nonempty snapshots.

The 1.0.2.58 BC client captures and persists its start declaration before sending it, and refuses to run newly started scans without a server acknowledgement. Check enablement during the run uses the persisted declaration. The server checks its inventory against the pinned 199 code/module pairs from AL 1.0.2.57, but does not establish that the declared version describes all actual execution. Stored declarations are not trusted as proof and the shared Validation/Monitoring adapter still returns `MISSING_PROVENANCE`. Score and impact deltas are not proven by this work.

For authenticated legacy tenants lacking a registered company, scan sync now continues without storing execution observations; the response says `unavailable_company_binding`. It does not set a company or invent a snapshot or credit. The existing authenticated legacy registration path now serializes concurrent binding claims, rejects claims contradicting already recorded company, Entra tenant or BC environment details, and audits the winning claim without storing credentials. That path proves possession of the tenant credential, not independent BC company identity; secure, independently established future company binding is not implemented by this fallback.

The BC v2 start declaration also captures up to 2,000 active catalog-related record exceptions and the runner uses this frozen set. The backend retains v1 hash compatibility and stores the new scope tenant-bound. The source and tests compile locally; actual BC behavior and all possible scope inputs still need verification.

Remaining implementation gates: identify and persist all terminal check outcomes including grouped errors and abrupt aborts, authenticate and finalize complete execution evidence, establish stable per-record identity only where BC supplies it, and connect verified snapshots to the existing comparison service. The six explicit duplicate checks persist STARTED and can be marked FAILED by the controlled failure path; disabled checks are SKIPPED, and enabled checks in modules that provably never started are NOT_EXECUTED. Unobserved checks in a started group remain unknown. Partial failure evidence is persisted atomically with failure status and may be retried without losing the execution token. Aggregate findings remain noncomparable. Prove these flows in AL runtime and PostgreSQL including negative and positive end-to-end comparisons. Existing report export guards remain in force.

The current `DHDeepScanRunner.Codeunit.al` creates count findings with an aggregated affected count; the six duplicate-check paths create grouped findings based on a value marker. `InsertFinding` does not retain each affected BC record's SystemId. A per-record identity therefore requires changing the actual record-enumeration and persistence paths, not reusing the generated finding SystemId or falsely assigning one record to an aggregate.

Lifecycle ordering must preserve the existing backend semantics: `mark_scan_result_persisted` records the stored result before the run transitions to `completed` and receives `completed_at_utc`. A future provenance adapter must distinguish check completion, result persistence and lifecycle completion; requiring persistence to occur after the lifecycle's completion timestamp would incorrectly reject valid scans.

BC27 sandbox runtime and real in-place upgrade require separate approval and evidence; tests or CI must not be described as that acceptance.

## 2026-11-10 consolidation: AL source-routing inventory (NOT runtime acceptance)

Consolidated Draft PR #162 includes the WIP 1.0.2.58 checkpoint and replaces the two short-lived review PRs #160 and #161. The isolated source-contract test `backend/tests/test_scan_runtime_catalog_routing.py` verifies that all 199 declared AL catalog codes are covered by exactly one syntactic reporting route: 193 `AddCountFinding` calls and six individually instrumented duplicate-check starts. This check passed against the matching locally uploaded source snapshot and runs again in GitHub CI on the integrated branch.

**This is a static inventory only.** It does not prove that each check executed, that a group failure can be attributed to its constituent checks, or that an aggregate finding has per-record identity. Existing `MISSING_PROVENANCE` blocks and Validation/Monitoring export guards remain mandatory. The next engineering work is real per-check terminal evidence for interrupted/grouped execution and a demonstrably positive verified comparison for the subset with stable identities. No BC sandbox or real DEV runtime evidence has been obtained.

## Individual check lifecycle hardening (2026-11-10)

The six explicit duplicate-check routes still call `RecordCheckStarted` before their individual work. `RecordCompletedCheck` now requires a persisted `DH Check Execution` row in `STARTED` state before it can derive `PASS` or `FINDINGS` from the finding count. Missing or already terminal observations fail closed with `CHECK_EVIDENCE_CONFLICT`. This prevents a future call path from treating absence of findings as evidence of successful execution.

The focused source-contract test passed against the corresponding local 1.0.2.58 source copy (5 passed). The exact GitHub commit passed the BC Extension AL Build CI gate; real BC27 execution and complete grouped-check provenance remain unverified. In particular, the 193 aggregated output routes do **not** have a separately proven `STARTED` boundary. This is a narrow defensive correction, not a positive comparison or report release.

## 2026-11-10 AL pre-finalization terminal coverage guard

Before score and result persistence, the scan runner now invokes `DH Scan Check Mgt.AssertCompletedCheckEvidenceForRun` on scans with a persisted start declaration. The check iterates enabled entries of the frozen catalog snapshot and requires each to have local `DH Check Execution` with a terminal `PASS` or `FINDINGS` observation. Missing, `STARTED`, `FAILED`, `SKIPPED`, or `NOT_EXECUTED` enabled checks fail closed with `SCAN_CHECK_EVIDENCE_INCOMPLETE`. Historical runs without a declaration retain their existing legacy flow.

This is a **defensive finalization gate**, not proof that grouped work is independently instrumented, not a per-record identity migration, and not authorization to enable Validation/Monitoring exports. Real BC27 runtime and positive comparison evidence remain mandatory. Focused source-contract tests added; CI and sandbox results must be verified against the exact final SHA.

## 2026-11-10 narrow persisted clean-scan comparison (experimental)

The shared `compare_persisted_scans` adapter now has a deliberately narrow positive route for **two completed and independently persisted clean scans**: tenant/company binding; valid sealed start expectations (migration 0039); valid immutable execution evidence (0038); pinned full 199-check catalog/fingerprint; identical active modules, enabled checks, methodology and exception scope; final run lifecycle and time ordering; no stored finding rows; a `PASS` observation for every enabled check. Legacy/missing/tampered snapshots, mismatched scope and scans with findings stay fail-closed.

This establishes **check-level presence and zero-finding comparability only**. No resolved/new/regressed finding identities, no Health Score delta, no Impact delta, no Validation or Monitoring HTML/PDF and **no report export unlock** follow from it. A direct SQLAlchemy/SQLite persistence test with two source-like snapshots was added under `backend/tests/test_persisted_clean_scan_comparison.py`; the code and test must pass GitHub CI at a matched SHA and subsequently be verified with actual BC27-generated scans. This is not yet Sprint 3A.2 or Fiverr acceptance.

## 2026-11-10 persisted comparison CI remediation and consistency guard

The first full-regression attempt on `a8360f9041d058165534e678ec160098aaa1f0fb` produced **908 passed, 1 failed, 16 skipped, 2 xfailed**. The single failure was an overly narrow test expectation: comparing the same scan correctly returns both `SAME_SCAN` and `INVALID_SCAN_ORDER`. The assertion was corrected without changing comparison policy.

The verified clean-scan adapter now additionally demands `Scan.checks_count == len(enabled snapshot checks)`. An ORM negative case deliberately stores a mismatched scan count and asserts fail-closed `MISSING_PROVENANCE`. Full CI for the final SHA and actual BC27-generated scan pairs must still be checked. All finding transition / score / impact comparisons and Validation/Monitoring PDF unlocks remain explicitly blocked.

## Finding transitions prototype — 2026-11-10

A new pure helper compares preverified canonical SHA-256 finding identities for one check and returns resolved, persistent and new identities. Invalid statuses, duplicate IDs, missing IDs, legacy IDs and unmatched checks fail closed. Tests include positive, empty-result and negative cases.

This is not yet a source-verified BC data flow. The AL finding-row SystemId is not the affected business-record SystemId; its current Group Key is tied to the run SystemId. Aggregate findings cannot be interpreted as per-record identities. Report export guards must remain in place until versioned source-bound record identity evidence is implemented and verified in a real BC27 environment.

The full regression on bf764184 failed during Python test collection because a literal newline escape entered a test assertion. The syntax error was fixed in commit 0ad8430; final CI results remain to be checked.

## 2026-11-10 scan-bound finding transition guard

The standalone transition helper is now wrapped by `compare_verified_scan_finding_sets`. It requires a fully comparable pair of source-verified scan evidences, consistent tenant/company/environment/currency/methodology/catalog and complete terminal check coverage before calculating `resolved`, `persistent` and `new` for a named check. Regression cases cover positive transitions, unverified source, cross-company scope, module mismatch, untrusted finding identities and unknown checks.

**This is an internal verified-evidence API, not production Finding-Evidence ingestion.** Present BC AL `DH Deep Scan Finding.SystemId` is a finding-row identity, and `Group Key` incorporates the run SystemId. No proven record-level Business Central SystemId is yet submitted with the six duplicate groups or 193 aggregate routes. These routes must not be marked row-comparable.

Next: define versioned, source-originating, bounded per-record evidence only for check types that actually enumerate business records, with explicit table ID, affected record SystemId, check code, origin scan, and a mandatory completeness contract. Compare only after persistence, company binding, lifecycle checks and a real BC27 two-scan test. Existing export guards remain unchanged. Deployment remains NO-GO.

## 2026-11-10 first BC source-record evidence producer (local only)

Additive AL table `53198 DH Scan Record Evidence` holds (run entry number, check code, source table ID, affected BC **business record** SystemId) with a composite primary key, rejecting empty identities and duplicate observations. Scan/Admin/Scheduler permission sets can write; Viewer has no direct table access. The first producing path is `CUSTOMERS_DUPLICATE_VAT`: when a non-excluded VAT group actually contains more than one customer, the existing customer-record iterator stores each affected `Customer.SystemId` (table `Database::Customer`). This is neither the finding row's SystemId nor the run-scoped Group Key.

**P0 / NOT READY:** Only one named check is instrumented, and the local records are not yet packaged in an authenticated, immutable, bounded backend contract. The producer has no attested per-check *completeness* envelope, and a failed run can have partial local records. Multi-record group memberships are not individual issue resolutions; existing aggregated and other grouped checks remain unsupported for row-level change assertions. No Validation/Monitoring report gates are modified. AL compile, upgrade compatibility, non-SUPER runtime and two real BC sandbox scans remain required. Do not expose this table directly in the customer UI.

## 2026-11-10 backend record evidence contract (schema-only)

New `backend/app/services/source_record_evidence_contract.py` defines the strict `bc-record-evidence-v1` envelope for the **single initially supported** `CUSTOMERS_DUPLICATE_VAT` check. It carries tenant, scan and BC company GUID, UTC source observation time, mandatory `completed=true`, declared affected-record count, and a bounded set of source Customer table 18 SystemIds. Input validation rejects empty GUIDs, duplicates, unsupported tables/checks, partial flags, mismatched counts and oversized memberships. Canonical JSON ordering and SHA-256 aid integrity verification; a separate binder requires exact trusted scope and check status / group count / affected-row count. Automated tests cover clean PASS, duplicate-member FINDINGS and negative bindings.

**Important:** This module is deliberately not wired into `/scan/sync`, persisted as immutable evidence, or used to unlock comparisons/reports. A SHA-256 of client-declared data is not proof of Business Central provenance. Before ingestion, an authenticated leased scan, sealed expectation, source-side completion, bounded record payload, immutable storage, idempotent retry and non-SUPER BC27 runtime tests must be tied together. Existing group-member count equality alone cannot establish member-set stability under concurrent BC data changes. Other 198 checks remain without this record-evidence producer.

## 2026-11-10 migration 0040 — immutable record identity storage (NOT SYNCED)

New Alembic migration `0040_scan_record_identity_evidence` and ORM model `ScanRecordIdentityEvidence` define an additive, per-(scan,check) identity envelope. Columns: authenticated-scope identifiers (scan, tenant, BC company), supported check and schema version, canonical JSON, SHA-256, creation timestamp. PostgreSQL and SQLite insert triggers require a finalized scan with matching tenant and registered company plus existing sealed start snapshot and scan execution evidence. Update/delete triggers protect historical integrity; downgrades reject a populated evidence table.

The new SQLite Alembic integration test uses a dedicated temporary database to exercise binding rejection, insert immutability and refusal to drop populated evidence. **No backfill and no live ingestion**: `/scan/sync` is unchanged and no report/validation comparison consumes this new table. Canonical hash checking, source lease authentication, snapshot-enabled-check verification, exception-scope/methodology checks, source-to-finding membership proof, explicit retry handling and BC27 runtime tests must precede enabling ingestion. Direct database insertion bypassing these application-level validations must never be considered trustworthy provenance.

## 2026-11-10 gated record evidence ingestion path

`/scan/sync` now optionally accepts a `source_record_evidence` envelope for `CUSTOMERS_DUPLICATE_VAT` only. It requires the original tenant authentication, registered BC Company, frozen start expectation with the check enabled, matching check execution observation, original scan lease and source observation time between accepted start and terminal check observation. Affected-record membership count is reconciled against the sum of the submitted group findings, not just the number of groups. Canonical record evidence is inserted in the same transaction as the terminal scan run and frozen execution observations.

Retries must present matching original lease, worker and identical canonical record evidence; omission, altered IDs and retrofitting finalized scans fail closed. The existing public reports remain blocked. New HTTP integration tests cover successful atomic storage, out-of-order row retry, changed/omitted evidence, invalid membership/scope and an incorrect lease.

**Runtime status:** The AL extension currently creates local `DH Scan Record Evidence` rows, but does not yet serialize or transmit the new `source_record_evidence` field. Thus this backend endpoint capability is ready for isolated tests but is not yet an end-to-end BC27-tested flow. No server deployment has been performed. DB immutability guards are not by themselves cryptographic proof of BC origin, and the group-member counting method does not prove stable membership across concurrent BC source edits. Keep Validation/Monitoring comparisons and exports gated until actual BC sender + sandbox/runtime verification.

## 2026-11-10 BC27 record-evidence sender wired (not yet sandbox accepted)

`DH Deep Scan Runner.BuildSyncPayload` now conditionally attaches `source_record_evidence` for **only** `CUSTOMERS_DUPLICATE_VAT` when the run has an original frozen expectation, a lease token and a real terminal `PASS` or `FINDINGS` check observation. It packages only stored `DH Scan Record Evidence` Customer table 18 SystemIds, the original tenant/scan/company binding and the terminal check timestamp. Before serialization it rechecks that the number of stored distinct customer IDs matches the sum of affected members in this check's grouped findings; `PASS` requires zero members; `FINDINGS` requires at least two. With >2000 members the optional payload is omitted rather than blocking a valid aggregate scan. No business names, emails or VAT values are transmitted in the new field.

AL source-contract tests verify the schema, source ID origin, terminal-status guard, frozen start requirement and explicit limit. The AL compiler ran successfully on the sender code commit. Backend migration 0040 and gated lease-bound persistence were developed earlier. The new sender is **not yet verified** in an installed BC27 sandbox against the backend. Legacy scan sync remains supported, and no Validation / Monitoring comparison or report gating has been relaxed.

CI remediation: The complete backend suite on `fe26f3c408ba61d8b47424232180d98ca5c2b4a1` reported 949 passed / 1 failed / 16 skipped / 2 xfailed because the metadata-contract test asserted 52 mapped tables rather than the correct 53 after migration 0040. This stale assertion has been updated, alongside explicit columns verification. A full clean run at the current final SHA remains required. **NO-GO** until that, BC upgrade/non-SUPER and two real source scans.

## 2026-11-10 verified persisted source record membership reader (internal only)

The full backend and AL workflows for the previous sender SHA `0f412dc31b95fb950c0d3fcbf17af3dfb01f2417` are confirmed **PASS**. A new read-only `read_verified_record_membership` service now reconstructs the persisted `bc-record-evidence-v1` membership for `CUSTOMERS_DUPLICATE_VAT` only after checking its canonical JSON, SHA-256, original tenant/company, sealed v2 expectation, enabled check, terminal execution observation, stored finding-row and affected-member counts, and ordering of lifecycle timestamps. It refuses absent, inconsistent, foreign or malformed provenance. HTTP integration tests verify reading after successful leased sync plus rejection of manipulated payload or changed stored finding membership.

This reader intentionally returns **reported source-record membership**, not per-record issue resolution, cross-scan group matching or proof against concurrent Business Central data changes. The six duplicate checks represent groups, not individual issue identities. No customer-facing report/validation/monitoring unlock is authorized. Current code is committed only to the isolated Draft PR branch; BC27 sandbox runtime, upgrade and non-SUPER role checks remain open.
