# EXT-50-INTEGRATION – Pilot / Performance Release Candidate

Status: **INTEGRATION_CANDIDATE – CI AND REMAINING RUNTIME GATES REQUIRED**

## Basis

Integration branch `sprint/ext-50-integration-pilot-performance` starts from the runtime-verified EXT-50-12C.3 head (PR #41) and deliberately ports the still-relevant work from PR #37, #39 and #38 instead of merging their older shared infrastructure blindly.

Order:

1. EXT-50-04 permission/role contracts and evidence (#37)
2. EXT-50-12B copied-company recovery (#39)
3. EXT-50-12A performance generator (#38)

PR #40 is the base of #41 and is therefore already represented by the integration baseline.

## Conflict policy

The current #41 product/finding identity implementation remains authoritative.

Shared historical files from #38/#39 are **not** allowed to downgrade current behavior:

- `backend/tests/test_billing.py`: keep current lossless-findings branch fixture and assertions.
- product manifests: keep BCSentinel 1.0.2.22 and current BC27/runtime identity; do not restore older 1.0.2.20/1.0.2.21 manifests.
- current lossless finding schema/migration and BC finding identity implementation remain unchanged.
- `New-BCBuildWorkspace.ps1`: merge QA profiles. DiagnosticsQA/FindingTestsQA and PerformanceQA/PerformanceQABaseline must coexist.
- central BC compile workflow receives the performance QA fresh/upgrade gate without replacing the dedicated EXT-50-12C.3 gates.

## Integrated components

### EXT-50-04
Permission role matrix contracts, workflow, documentation and evidence are ported. Real non-SUPER SaaS evidence remains a release gate.

### EXT-50-12B
Copied-company recovery codeunit, setup action, admin permission extension, workflows/contracts and evidence are ported onto the current product baseline. Backend identity conflict protection is not weakened.

Known runtime result from the prior BC27 SaaS exercise: local copied registration reset succeeded with SUPER, generated business data was preserved and the copied company re-registered as a separate BCSentinel tenant. Non-SUPER permission evidence remains open and is covered by EXT-50-04.

### EXT-50-12A
The separate sandbox-only `BCSentinel Performance QA` extension 1.0.0.1 is ported with its deterministic DEV/LARGE/XL/STRESS profiles, ownership tracking and guarded cleanup design.

Historical runtime evidence retained:
- DEV: 6,000 customers + 2,000 vendors + 12,000 items = 20,000 business records.
- Seed 5001 / 10% error rate.
- generation completed with 0 failed batches in about 3m20s (~99.69 business records/s).
- subsequent BCSentinel DEV scan completed in ~8m22s.
- historical scan: 95 finding rows, 224,999 check occurrences, EUR 2,202,021.49 impact, EUR 1,541,415.04 potential saving.
- that historical run had 95 distinct check IDs, so the later same-check multi-group defect did not demonstrably lose rows in that run.

The historical DEV values are retained as historical evidence, not promoted to the new integrated release baseline.

## Required gates before LARGE

1. All integration CI green: backend regression, BC27 product fresh/upgrade, finding identity, recovery contracts, generator contracts and Performance QA fresh/upgrade/AL tests.
2. No regression of the real EXT-50-12C.3 multi-group evidence.
3. Complete non-SUPER permission/runtime matrix for the relevant pilot roles.
4. Exercise Performance QA cleanup/recovery guards and prove normal/pre-existing records remain unchanged.
5. Run a fresh integrated DEV20k generation + BCSentinel scan and record it as the new release baseline.
6. Only then authorize LARGE500k.

## Explicitly not authorized by this integration

- production deployment
- automatic LARGE/XL/STRESS execution
- weakening registration identity guards
- treating QA extensions as customer extensions
