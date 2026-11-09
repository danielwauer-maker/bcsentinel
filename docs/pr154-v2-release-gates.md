# PR #154 – V2 Release Gate and DEV Acceptance

**Status: DRAFT / NOT PRODUCTION READY** (2026-11-09). Do not merge or install until the gates below have passed. This document is intentionally explicit about external dependencies and evidence that cannot be manufactured by unit tests.

## Implemented in PR #154

- One Free Deep Scan, original Free Report permanently accessible; original completed Free scan may be confirmed as the Full baseline after paid activation.
- Full Assessment v2: 14 days Premium, no extra scan.
- Access Renewal: +14 days Premium, no new scan.
- Renewal + Validation: +14 days Premium, exactly one scan credit. Scan credit consumption does not extend access.
- Monitoring continues as recurring access. Archive and link delivery are tenant/company/scan scoped, and expire with entitlements.
- Five new v2 data classes: <=250,000 / <=1,000,000 / <=5,000,000 / <=20,000,000 / Custom above 20m.
- New product rows are disabled and unpriced until explicitly approved.
- Immutable scope confirmation requires original persisted Free scan, verified BC company and EUR LCY; a previously confirmed baseline is not re-confirmed with changed decisions.
- New v2 scan sync transaction captures an **automatic**, unconfirmed scope after successful persistence. Confirming scope remains an explicit, separate user action.
- Validation compares the latest comparable completed scan and separately references the first confirmed baseline.
- BC Scan Monitor actions for Full scope review, Validation and Monitoring; legacy Executive buttons hidden.
- A new authenticated preflight endpoint exposes missing evidence without generating baseline, scan or report access.

## Must-pass gates before enabling V2

| Gate | Expected evidence | Status |
| --- | --- | --- |
| G1 backend regression | All new + legacy tests green on PR head | Check GitHub Actions on current HEAD |
| G2 BC AL build | AL build green; exact installed DEV .app schema diff (all fields/tables); successful non-destructive upgrade of a backed-up sandbox | **SOURCE COMPATIBILITY VERIFIED against uploaded installed 1.0.2.52 .app (21/21 identical table/tableextension AL files); real non-destructive BC SaaS upgrade still pending** |
| G3 prices & checkout | Approved amounts for every v2 SKU and data class, correctly mapped Stripe Price IDs; finance/currency checked | **BLOCKED: final prices not approved** |
| G4 webhook lifecycle | Paid, failed, replay, refund, dispute, chargeback, concurrency, out-of-order and delayed webhook events; no overgrant | Core refund/dispute revocation, unknown reversal retry and idempotency implemented; full real Stripe payment E2E pending |
| G5 Free→Full real scan | Real Free scan has company GUID, EUR LCY, completed+persisted status; scope auto-created, explicit user confirmation and Full v6 report opens | **BLOCKED: end-to-end DEV real evidence not yet verified** |
| G6 Validation history | Verified comparable initial and previous scan, immutable baseline, failed/incomplete/mixed-currency excluded, Monitoring trend | Unit regression exists; real DEV acceptance missing |
| G7 browser live renderer | /report/live deployed, live flag and API URL intentionally configured, Full v6 renders; Validation & Monitoring live adapters use only verified source data | Validation/Monitoring factual limited-evidence browser views now exist and passed project tests; DEV deployment and real BC-token/API E2E still unverified |
| G8 data isolation | Two tenants, two BC companies, cross-user attempts, guessed links, expired links, non-SUPER permissions, token expiry, browser caching | Unit coverage partial; full DEV acceptance missing |
| G9 deployment | Database backup, migration dry-run, extension upgrade compatibility and rollback plan, DEV approval, then PROD promotion | Not started |

## 2026-11-09 preflight hardening — verification required

The read-only `GET /scans/{scan_id}/report-preflight` now includes `original_free_scan` when v2 is enabled. This is verified server-side against the **first Free scan**, completed/with-warnings status and a persisted scan result; failed verification adds `original_completed_free_scan_missing` to `missing_prerequisites`. The CLI now fails closed if this field is missing (older DEV deployment), false, or if any backend prerequisite other than expected `confirmed_scope_missing` is present before first confirmation.

The authenticated preflight now also returns a validated, canonical `company_id` GUID (or `null` when missing/invalid). `--expected-company-id` compares exact UUID identity, including safe handling of GUID casing and braces. An older DEV backend omitting `company_id` **fails closed**, even if `company_bound=true`. Preflight access remains tenant-authenticated and scan-owner scoped; it does not issue any report credential.

Regression tests: `backend/tests/test_report_preflight_v2.py` and `backend/tests/test_dev_bc_acceptance_script.py`. **No CI result, DEV deployment, schema migration, real scan or BC acceptance is claimed by these commits.**

## Installed version 1.0.2.52 source compatibility — evidence 2026-11-09

The sandbox operator supplied the **actual installed BCSentinel 1.0.2.52 .app** (also shown in the BC Extension Management screen). It was inspected read-only as a ZIP/AL package.

- SHA-256 of supplied package: `50a85c0462a7a52d3dc141b827d5f4db977df7ac296be0a33bca332e76ffdfee`
- `NavxManifest.xml`: App ID `8c7f0f9c-0c1a-4a4e-9c6f-111111111111`, publisher `BCSentinel Analytics - Daniel Wauer`, version `1.0.2.52`, BC 27 Cloud.
- `SymbolReference.json` includes **20 Tables** and **1 TableExtension**. Original source contains exactly those 21 table/tableextension AL files.
- All **21 of 21** installed package AL source files under `src/app/src/tables/` and `src/app/src/tableextensions/` were compared with matching paths under `bc-extension/app/src/` on the PR #154 branch using exact Git blob SHA-1 of original bytes; **all 21 SHA-1 values match**.
- Previously suspected missing fields are in **tableextension 53201 `DH Setup Lifecycle Ext`** (not in the base `DH Setup` table): field **53136 `Report Notification Email` = `Text[250]`**, field **53137 `Preferred Report Language` = `Code[2]`**. Current PR branch contains this exact source file unmodified, Git blob SHA `5101f1104d34ddaf00ef12231310cd30906394a4`.
- The previously alleged missing notification tables **53170–53176** also appear in the installed package and match the PR source byte-for-byte.
- The branch release manifest `bc-extension/app.json` was bumped from `1.0.2.51` to **`1.0.2.53`** to be greater than the actual installed version.

**G2 interpretation:** persisted AL table and tableextension source compatibility is established for the supplied installed v1.0.2.52 artifact. This is substantially stronger than comparing against an unrelated Git branch. **Do not claim actual BC SaaS upgrade success yet.** An installed sandbox backup, a successful non-destructive SaaS upgrade to the exact new .app, non-SUPER permissions and existing record integrity checks remain mandatory. Verify the artifact really is the package installed in the test tenant. Never ForceSync/recreate/uninstall to bypass errors.

## CRITICAL: BC SaaS extension upgrade schema must be compared to the *installed* DEV app

**Do not install the current CI-produced .app yet without backup and version verification.** The supplied installed 1.0.2.52 artifact matches all 21 persisted AL sources in PR #154, but AL compilation and source comparison still do not prove a successful upgrade in the populated sandbox.

The historical BC upgrade error reported for `BCSentinel 1.0.2.51` named removed fields **DH Setup / Report Notification Email** and **DH Setup / Preferred Report Language** and omitted notification tables `DH Notification Event` (53170), `DH Notification Rule` (53171) and `DH Notification Recipient` (53172). The newly verified installed **1.0.2.52** package contains all of these. The two fields are declared in `bc-extension/app/src/tableextensions/DHSetupLifecycle.TableExt.al`, not in the base table. The corresponding PR sources match the package exactly. This supersedes the earlier assumption that the current PR is missing those fields.

**Required before DEV BC extension upgrade:**

1. **DONE for operator-supplied 1.0.2.52 package:** actual `.app`, `SymbolReference.json` and source files inspected; verify this is the exact installed sandbox artifact before deploying.
2. **DONE for persisted table/tableextension source files:** all 21 exact Git blob SHAs match. Recheck keys/enums and any packaging differences when building the upgrade artifact; do not silently delete objects.
3. Notification tables are confirmed present and identical; verify existing enum and other object compatibility in the final build.
4. Run an automated schema-diff gate against this *installed* baseline. Compile an app with a version greater than the DEV-installed version, then run a true **BC SaaS DEV upgrade test on a backed-up sandbox**, with a non-SUPER user and existing records. Only an actual successful upgrade authorizes installing for the business acceptance.
5. Under no circumstances use destructive Recreate/ForceSync, uninstall, or schema deletion to make the upgrade appear successful; historical customer data must survive.

Microsoft's AL schema synchronization does not permit deleting persisted fields/tables in normal synchronize mode. See https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-retaining-data-after-publishing .

## Installed AL schema audit tool (2026-11-09)

The read-only `scripts/check_bc_installed_schema.py` now checks persisted table/field IDs, names, and AL types, including fields declared in tableextensions. It **requires** a verified, non-empty JSON baseline extracted and reviewed from the exact previously installed BC app (not from current GitHub main or staging). Command after obtaining that evidence:

```bash
python scripts/check_bc_installed_schema.py \
  --installed-baseline /secure/reviewed-installed-dev-schema.json \
  --source bc-extension/app/src
```

Baseline format: `{"tables":[{"id":53100,"name":"DH Setup","fields":[{"id":1,"name":"Primary Key","type":"Code[10]"}]}]}`. This is a format example **only**, not an asserted installed baseline. Include **all** persisted tables/fields from the installed app, not only DH Setup.

Exit 0 means source matches the supplied declared baseline for table and field definitions; 2 means missing or altered persisted objects; 3 means input missing/invalid. This is a **precheck, not** a replacement for BC tenant in-place upgrade and full field/key/enum compatibility review. The exact old field IDs for `Report Notification Email` and `Preferred Report Language` remain unverified, so **do not install** on the customer sandbox yet.

## DEV acceptance – no new paid scan required for first Full test

1. Keep `ACCESS_MODEL_V2_ENABLED=False` and `ACCESS_V2_PAID_CHECKOUT_ENABLED=False` until the designated DEV cutover. The latter stays disabled even during initial v2 DEV access testing; it must be enabled only after Stripe price, refund, dispute and concurrency acceptance. Verify last deployed DEV backend and original BC extension remain healthy.
2. Backup DEV DB. Check existing original Free scan `Scan`, `ScanStartRequest`/`TenantScanCredit`, `ScanRunStatus`, company GUID and LCY.
   Supply the known BC Company GUID through `--expected-company-id` to require exact company verification; the preflight never invents or changes scan bindings.
3. After approved DEV branch deployment, explicitly enable v2 on DEV only; never flip PROD by copying DEV env.
4. Retrieve `GET /scans/{scan_id}/report-preflight` with authorized tenant headers. It MUST NOT write scope or grant any access. Optional read-only helper: `BCSENTINEL_API_TOKEN=... python scripts/check_dev_bc_acceptance.py --base-url https://dev-api.bcsentinel.com --tenant-id YOUR_TENANT --scan-id YOUR_FREE_SCAN`. It returns exit 0 only if core report prerequisites are present, exit 2 for blockers, exit 3 for network/auth failures; it does not disclose tokens.
5. Open BC Deep Scan Monitor > **Review Scope / Full Assessment** on the original Free scan with a verified test Full Access entitlement. Inspect actual detected modules; explicitly confirm.
6. Confirm scope version remains immutable across repeated requests and that paid report can be opened with a single-use code. Check `GET /account/reports/full/{scan_id}?company_id=...` with report-scoped bearer. Verify no raw BC API token in browser, URL or PDF.
7. Expire Premium and verify Full link issuance/exchange, report reader, history and exports fail closed. Reactivate via renewal with no additional scan.
8. Use a separate paid Validation credit and a new scan only when entitlement and test approval are explicit. Compare with original baseline and last compatible scan. Verify mixed-company/currency and incomplete scans rejected.
9. Test Monitoring, scheduler, non-SUPER roles, two tenants, DE/EN and PDFs. Only then review PR for merge.

## External dependency: Lovable Report System

Lovable project ID: `2efa722e-a036-4e3e-a695-6cda46f88541`. The route `src/routes/report.live.tsx` already exists in project source, but live rendering is gated by build-time `VITE_BCSENTINEL_LIVE_REPORTS` and `VITE_BCSENTINEL_REPORT_API_BASE_URL`. Do **not** enable until verified backend and frontend are deployed.

Lovable now implements evidence-limited read-only Validation and Monitoring screens from strictly validated raw backend fields. These **do not** claim confirmed comparability, missing baseline metrics or financial improvement. The frozen full ValidationGoldenVM / MonitoringVM remains dependent on stronger signed evidence. Lovable project validation on Nov 9: **345 frontend tests passed, typecheck clean**, without a production deployment. For ongoing credit-free editing, connect Lovable Settings → Git to the owner's GitHub account; Lovable creates a *new private repository* (suggest `bcsentinel-report-viewer`) and cannot automatically push into the backend repository. Optionally add that repository as a Git submodule under `report-viewer/`. The first GitHub authorization requires the user's account action; it cannot be silently granted from this PR.


## Checkout safety at DEV acceptance

Both `ACCESS_MODEL_V2_ENABLED` and `ACCESS_V2_PAID_CHECKOUT_ENABLED` default to `False`. For the first BC Full report acceptance test, **only** `ACCESS_MODEL_V2_ENABLED=True` may be enabled on backed-up DEV after updating its backend and verifying non-SUPER access; keep `ACCESS_V2_PAID_CHECKOUT_ENABLED=False` throughout. All active Full rights for the acceptance scan must come from an explicitly documented **test/operator entitlement** or pre-existing paid grants, not an actual Stripe charge. V2 Stripe checkout uses card-only methods until async settlement is separately supported and verified. Real refunds/chargebacks must be tested against Stripe test mode before changing the paid-checkout switch.

## Commercial/Stripe signoff

Do not silently treat the earlier **EUR 79** access-only Renewal suggestion as final or copy the historical 7-day product prices. Full Assessment starts from EUR 249, Renewal+Validation from EUR 129, Monitoring from EUR 199/mo in the agreed product plan; actual amounts must be set per approved data class before Stripe Price creation. The remaining new SKU price rows should stay inactive.

## Production invariant

The PR is not "complete", approved or deployable merely because backend regression and AL compilation are green. Real scan scope, signed viewer presentation, money/currency integrity, refund safety, live rendering and customer acceptance require independent evidence.
