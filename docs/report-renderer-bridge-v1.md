# BCSentinel v6 Report Data Bridge — implementation handoff

Status: **development pull request; not deployed.** The design-locked Lovable reports still use Contoso examples. No real tenant may be shown as validated until the steps below are completed.

## Architecture
- Source of truth: existing FastAPI Free, Quick, Full, Validation and Monitoring builders. No financial estimates recomputed in React.
- New route: `GET /account/reports/{free|quick|full|validation|monitoring}/{scan_id}?company_id=<BC COMPANY GUID>`
- Authorization: `Authorization: Bearer <tenant_user_session>`; the server verifies the active user-tenant membership and role binding, tenant status, scan tenant ownership, **immutable BC company binding** and current product entitlement. BC X-Api-Token must NEVER be passed to a browser or Lovable.
- `Cache-Control: no-store, private`. No share URL, no report token in query parameters.
- The response envelope has `contract_version = "bcsentinel-render-bridge-v1"`, `variant`, `source="live"`, `tenant_id`, `company_id`, `scan_id`, `language`, `currency`, `report`. The `report` member contains the **existing Pydantic report schema**, NOT a Lovable UI view model. A strict field-level adapter must be used in the dashboard. No demo fallback.
- Free is aggregate only. Quick is at most five findings and contains no exact impact amounts or issue codes. Full requires active Assessment access; Validation and Monitoring require their own product entitlements.

## Company and currency ingestion
Schema migration `0035_scan_company_lcy` adds nullable `scans.bc_company_id` and `scans.lcy_code`. New BC AL scan syncs send `bc_company_id` from `CompanyProperty.ID()` and `lcy_code` from the current company's General Ledger Setup. Both fields must be supplied as a pair; existing scan bindings cannot be changed by resync. Tenant-only legacy scans remain readable via legacy endpoints but are **blocked from the new live web route** (409). Each requested company ID must match the scan binding; 404 otherwise.

Current core model stores computed modeled impact as EUR. Therefore **only EUR LCY financial reports are currently eligible** for the new live bridge. Non-EUR Full/Validation/Monitoring fail closed (409) until a verified immutable FX conversion snapshot exists. Free/Quick may be rendered without any currency conversion. Never replace EUR with USD/SEK via locale or browser query. All scope/exception values and historical comparisons must be read from scan-time snapshots; never fabricate missing items.

## Gaps before production activation
1. BC AL compilation against the target BC symbols and extension acceptance test for company GUID/LCY ingestion. A missing LCY setup leaves a scan unbound rather than inferring it from country/language.
2. Run Alembic migration on DEV only, run backend integration suite and a full tenant-isolation matrix; then review migration before PROD.
3. Map existing Pydantic report payloads to Lovable's typed Free/Quick/Full/Validation/Monitoring view models. The current templates may require report information not yet in the backend (especially finding rationales, metadata, localized check definitions, scope exceptions and monitoring historic values); **block absent fields** instead of copying Contoso data.
4. Mount the live renderer only inside the authenticated BCSentinel dashboard using the 15-minute user-tenant session. Align the exact route and snake_case envelope with the Lovable live client; remove the redundant X-BCSentinel headers if not explicitly CORS-allowed.
5. Implement verified and persisted rate source (e.g. ECB supported-currency reference data), EUR model-to-LCY conversion with per-scan source/provenance, history rebasing to a pinned comparison snapshot, safe unsupported-currency behavior. No manual rate management.
6. Finish single-source HTML-to-PDF generation after privileged server-side authorization, ensuring DE/EN text and A4 layout. Never expose raw customer data from the public Lovable preview.
7. Verify real BC pilot scan, Quick/Full upgrades, exceptions, Validation baseline binding, Monitoring history, PDF in DE and EN, no company/tenant data leaks; only then activate PROD.

## Hard gates
- No live render for unbound company, different company, absent tenant session, revoked membership, missing entitlement, unverifiable FX, or missing evidence.
- A non-EUR scan must never be rendered with an unchanged EUR-derived model value but a different currency symbol.
- Existing v6 DE/EN 36-page Contoso demo remains the visual reference and must not be mutated by backend contract work.
