# BCSentinel Assessment Scope Contract v1

## Product invariant

BCSentinel has one full initial Data Health / Deep Scan. Free Health Check, Quick Assessment and Full Assessment are disclosure/scoping layers over that same stored scan. A new technical scan is created only for Validation (or later Monitoring).

## Supported scope

BCSentinel v1 scores only explicitly supported Microsoft Dynamics 365 Business Central standard areas:

- System / Setup
- Finance
- Sales
- Purchasing
- Inventory
- CRM
- Manufacturing
- Service
- Jobs / Projects
- HR

Third-party extensions, ISV applications and customer-specific customizations are outside the scoring scope unless BCSentinel explicitly adds support for them. Their presence may be disclosed as assessment-coverage metadata, but they must not increase or decrease the BCSentinel Health Score.

Standard tables/processes remain assessable even when a custom extension adds fields or behavior to them; only the extension-specific business logic is outside scope.

## Automatic usage detection

The initial scan always executes the complete supported check set. Customers cannot select modules or checks in Free or Quick.

After the scan, the backend creates an automatic scope snapshot. Each supported standard module receives one of:

- `active` — reliable scan evidence indicates that the standard area is used;
- `not_detected` — reliable scan evidence indicates no usage in the available profile;
- `unknown` — the current scan contract lacks sufficient evidence to make a safe determination.

Absence of evidence must never be treated as `not_detected` when the scan payload does not contain a reliable usage signal.

## Score semantics

### Free Health Check / Quick Assessment

Display a **Preliminary Health Score** based only on automatically detected active standard modules. `not_detected` and `unknown` modules do not penalize the preliminary score. The report must communicate that scope applicability has not yet been confirmed.

Free and Quick may not edit the scope.

### Full Assessment

An active Full Assessment may confirm the business-relevant standard scope. The customer confirms or corrects the automatic module suggestions. No new scan is required: the stored findings are re-evaluated against the confirmed scope.

The resulting score is the **Confirmed Baseline Score**. A score change caused solely by scope confirmation is a scope adjustment, not remediation/improvement.

The core `System` area cannot be excluded.

Full Assessment JSON/HTML/PDF and dashboard projections must use the confirmed scope once it exists: score, findings, affected records and modeled impact must not silently include excluded standard areas.

### Check-level exceptions

v1 does not expose a global list of all checks as a score-optimization control. Existing finding/exception workflows remain the mechanism for individual exceptions. `Not applicable` and `Accepted risk` must remain auditable and must not be confused with a corrected issue.

## Validation

Validation creates the next real full scan after remediation and compares it with the confirmed Full Assessment baseline using the same supported standard scope. Only the delta between the confirmed baseline and Validation is a remediation improvement.

When a scope-aware Validation report is created, BCSentinel persists an immutable binding between the Validation scan, the baseline scan and the exact confirmed scope snapshot/version. Subsequent report rendering must reuse that binding rather than silently switching to a newer scope version. Historical Validation runs that predate Assessment Scope v1 retain legacy whole-scan semantics.

Example:

- Preliminary Quick score: 68
- Confirmed Full baseline after scope confirmation: 76
- Validation score after remediation: 89

`68 -> 76` is a scope adjustment. `76 -> 89` is a real measured improvement.

## Customer-facing coverage statement

Recommended wording:

> BCSentinel assesses supported Microsoft Dynamics 365 Business Central standard data and process areas. Third-party extensions and custom business logic are outside the scoring scope unless explicitly supported.

Full Assessment exposes an Assessment Coverage section with supported/included/unknown module counts and, when available, detected unsupported extension metadata.
