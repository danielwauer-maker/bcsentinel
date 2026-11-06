# D10 — Executive Report Contract

Status: Implemented technical contract

## Purpose

Web JSON, HTML, PDF and Monitoring report projections must consume one backend report model and one report builder. Renderers may change presentation only; they must not recalculate financial or data-health KPIs.

## Contract identity

- Contract version: `executive-report-v1`
- Financial methodology: `fin-v1`
- Backend schema: `backend/app/schemas/report.py::ExecutiveReport`
- Backend builder: `backend/app/services/executive_report_service.py::build_executive_report`

## Canonical financial semantics

- `estimated_loss_eur`: modeled annualized economic risk / estimated loss; not an accounting-confirmed loss.
- `potential_saving_eur`: modeled avoidable potential; not guaranteed or realized saving.
- `validated_improvement_eur`: only populated when validation evidence supports the value.
- `realized_saving_eur`: only populated when an approved attribution methodology supports realization; otherwise `null`.
- Legacy `roi_eur` and `estimated_premium_price_monthly` are not part of the D10 public report contract.

## Surfaces

- Web/API: `GET /reports/executive/{scan_id}`
- Monitoring projection: `GET /reports/monitoring/{scan_id}`
- HTML: `GET /reports/executive/{scan_id}/html`
- PDF: `GET /reports/executive/{scan_id}/pdf`
- Shared HTML/PDF links use the same report builder after tenant/access verification.

The Monitoring endpoint uses the exact same schema and builder; only `report_variant` changes from `executive` to `monitoring`.

## Authority rule

The report is a derivative of server-side scan/findings/impact truth. HTML, PDF, dashboard and monitoring renderers must never own KPI formulas, price formulas or financial outcome calculations.

## Security

Tenant isolation and product entitlement checks run before report rendering. Share links are time-limited, bound to tenant/scan/type and do not contain API tokens.
