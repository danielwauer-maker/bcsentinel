## BC extension build profiles

This repository now uses a release-safe default manifest for cloud packaging:

- `app.json`
  - default cloud manifest
  - intended for production/release packaging
  - `resourceExposurePolicy` is hardened for release:
    - `allowDebugging=false`
    - `allowDownloadingSource=false`
    - `includeSourceInSymbolFile=false`

Additional manifests are kept for explicit non-default scenarios:

- `app.cloud.json`
  - cloud development companion manifest
  - currently keeps the same hardened source/debug exposure policy as the release manifest
- `app.onprem.bc19.json`
  - legacy on-prem BC19 companion manifest
  - hardened, not the default cloud release path

## Build path

### DEV cloud

- Use `.vscode/launch.json` (`Microsoft cloud sandbox (DEV)`) for local debugging.
- If a cloud sandbox build with debug/source exposure is explicitly needed, use `app.cloud.json` intentionally as the manifest source for that build.
- The repository default `app.json` is no longer the DEV profile.
- To prepare an isolated DEV build workspace without mutating the repo manifest, run:
  - `powershell -ExecutionPolicy Bypass -File .\bc-extension\scripts\New-BCBuildWorkspace.ps1 -Profile DevCloud`
- Use the generated workspace at `.build\bc-extension\DevCloud\` in the repository root.

### PROD / release cloud

- Use `app.json` as the only default packaging manifest for customer-facing cloud releases.
- Do not replace it with `app.cloud.json` during release packaging.
- To prepare an isolated release build workspace, run:
  - `powershell -ExecutionPolicy Bypass -File .\bc-extension\scripts\New-BCBuildWorkspace.ps1 -Profile ReleaseCloud`
- Use the generated workspace at `.build\bc-extension\ReleaseCloud\` in the repository root.

### OnPrem BC19

- Use `app.onprem.bc19.json` only for explicit BC19 on-prem builds.
- To prepare an isolated BC19 OnPrem workspace, run:
  - `powershell -ExecutionPolicy Bypass -File .\bc-extension\scripts\New-BCBuildWorkspace.ps1 -Profile OnPremBc19`
- Use the generated workspace at `.build\bc-extension\OnPremBc19\` in the repository root.

## What The Script Does

- copies `app/` into a generated build workspace
- copies the selected manifest into that workspace as `app.json`
- copies `app.ruleset.json` into that workspace
- copies `AppSourceCop.json` into that workspace
- copies the project `Translations/` directory when present
- copies `.vscode/settings.json` so CodeCop, AppSourceCop and PerTenantExtensionCop are enabled when available
- copies `.alpackages/` when present
- copies `.vscode/launch.json` for the DEV cloud profile

The script rejects every output path that is the AL project, lies below it, or contains it. This keeps generated `.al` files and manifests outside the active AL source root while preserving `bc-extension/app.json` as the release-safe default.

## AppSource readiness baseline

- Analyzer activation is configured in `.vscode/settings.json`.
- Analyzer execution uses `app.ruleset.json` through VS Code settings or the AL compiler `/ruleset` parameter.
- `app.json` includes the current public product, privacy and help URLs.
- Final AppSource submission still needs verified EULA/terms and logo assets before packaging.
- The app id `8c7f0f9c-0c1a-4a4e-9c6f-111111111111` must be verified before marketplace submission because it looks placeholder-like.
- Dashboard embed URLs currently use a short-lived dashboard token in the iframe URL. The token is no longer displayed in the ControlAddIn loading state; a tokenless/session-cookie embed flow remains the preferred follow-up.

## Release hygiene

The repo still contains dev/build artifacts that should not be treated as release sources:

- `.alpackages/`
- `.snapshots/`
- `.vscode/launch.json` with sandbox tenant metadata
- packaged `.app` files in the repo root

They are already ignored in the root `.gitignore`, but existing tracked artifacts should be cleaned up separately to reduce the risk of shipping the wrong output.

See `APP_SOURCE_READINESS.md` for the current P2.13 P0 baseline and remaining AppSource items.

## EXT-04 scan history

The scan history page now uses customer-facing display columns for go-live:

- Run ID, Scan Date, Scan Type, Rating, Score, Modules, Checks, Issues Count, Impact, Result
- Scan Type is derived from the existing scan type and deep scan mode where available.
- Result and Rating are displayed with localized English/German values on the page.
- The former Headline column is hidden from the standard list view.
- Delete actions require confirmation and show clear completion messages.

## EXT-05 currency and amount formatting

Customer-facing financial values are displayed with two decimals and the tenant local currency code from Business Central `General Ledger Setup`.`LCY Code` when available.

- Visible amount captions avoid hard-coded EUR terminology.
- Scan history and issue lists show formatted impact values, for example `21.908,42 EUR`.
- Setup shows the last scan amount as Estimated Impact.
- Internal legacy field names that still contain `EUR` are kept for upgrade safety.

See `docs/EXT-05_CURRENCY_AMOUNT_FORMATTING.md` for the implementation notes and manual verification checklist.
