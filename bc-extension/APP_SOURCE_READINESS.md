# BCSentinel AppSource Readiness

## Analyzer Baseline

- `app.ruleset.json` is the release baseline ruleset.
- `.vscode/settings.json` enables CodeCop, AppSourceCop and PerTenantExtensionCop for AL workspaces that have the analyzers available.
- Analyzer execution uses `app.ruleset.json` through VS Code settings or the AL compiler `/ruleset` parameter.
- P2.13 P0 intentionally enables analyzers without suppressing the expected warning backlog.

## Marketplace Metadata

Current manifest metadata:

- Product URL: `https://bcsentinel.com`
- Privacy statement: `https://bcsentinel.com/privacy.html`
- Help URL: `https://bcsentinel.com`

Required before AppSource submission:

- Final app id check for `8c7f0f9c-0c1a-4a4e-9c6f-111111111111`.
- Final publisher confirmation for `BCSentinel Analytics - Daniel Wauer`.
- Final EULA or terms URL.
- Final support URL if it differs from the product/help URL.
- Final app logo file referenced by `app.json`.
- Final privacy URL confirmation.
- Final help URL confirmation.
- AppSource screenshots for setup, scan run, findings, dashboard/report flow, and license/credit status.
- Final short and long AppSource listing text review.

## Current Listing Text Draft

Short description:

BCSentinel monitors and improves data quality in Microsoft Dynamics 365 Business Central.

Long description draft:

BCSentinel helps Business Central administrators and process owners assess data quality, identify critical master-data and transaction-data findings, track a Data Health Score, and open dashboards or executive reports for follow-up. The app connects Business Central to the BCSentinel backend after explicit data processing consent and tenant registration.

## Onboarding Status

- The Assisted Setup entry `Set up BCSentinel` opens the existing `DH Setup` page so marketplace customers can find setup after installation.
- The current backend still requires a pilot invite code for registration.
- The BC setup page explains that the invite code is required until backend self-service signup is available.
- Backend follow-up block: implement AppSource self-service tenant registration or a verified signup/access request flow.

## Security Notes

- Normal marketplace pages must not show build markers, diagnostics groups, status endpoints or tenant identifiers.
- Backend response bodies must not be shown directly to end users because they can contain internal URLs, headers, tokens or stack traces.
- Dashboard embed tokens must not be displayed in labels, loading states, errors or logs.
- Current state: the dashboard launch flow uses a dedicated `analytics_embed` token, not the tenant API token.
- The embed token is tenant/company/scope-bound, short-lived, and exchanged by the backend into an HttpOnly analytics cookie before rendering the tokenless `/analytics/embed` page.
- The token is not displayed in the ControlAddIn loading state or written to JavaScript logs.
- Remaining risk: the first browser navigation still carries `embed_token` in the query string because current BC pages open the dashboard with `Hyperlink(...)`.
- Mid-term target: POST-init, one-time token exchange, or same-site backend session so no tokens are carried in URLs at all.

## Release Hygiene

The following existing files/directories are ignored but still present in the source tree and should be cleaned manually before release packaging:

- `bc-extension/.alpackages/`
- `bc-extension/.snapshots/`
- `bc-extension/.vscode/launch.json`
- `bc-extension/BCSentinel Analytics - Daniel Wauer_BCSentinel_*.app`

Do not delete these during automated P0 fixes without an explicit release-cleanup task.
