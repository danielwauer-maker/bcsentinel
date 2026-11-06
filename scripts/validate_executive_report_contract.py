from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "backend" / "app" / "schemas" / "report.py"
SERVICE = ROOT / "backend" / "app" / "services" / "executive_report_service.py"
ROUTER = ROOT / "backend" / "app" / "routers" / "reports.py"
DASH_API = ROOT / "dashboard" / "src" / "api" / "corePages.ts"
DOC = ROOT / "docs" / "EXECUTIVE_REPORT_CONTRACT.md"

for path in [SCHEMA, SERVICE, ROUTER, DASH_API, DOC]:
    if not path.exists():
        raise SystemExit(f"D10 missing required file: {path.relative_to(ROOT)}")

schema = SCHEMA.read_text(encoding="utf-8")
service = SERVICE.read_text(encoding="utf-8")
router = ROUTER.read_text(encoding="utf-8")
dash_api = DASH_API.read_text(encoding="utf-8")
doc = DOC.read_text(encoding="utf-8")

for marker in [
    'REPORT_CONTRACT_VERSION = "executive-report-v1"',
    'FINANCIAL_METHODOLOGY_VERSION = "fin-v1"',
    'validated_improvement_eur',
    'realized_saving_eur',
    'report_variant',
]:
    if marker not in schema:
        raise SystemExit(f"D10 report schema marker missing: {marker}")

# Legacy commercial fields may remain in historical scan storage/service normalization,
# but must not be exposed through the D10 report schema.
for forbidden in ["roi_eur:", "estimated_premium_price_monthly:"]:
    if forbidden in schema:
        raise SystemExit(f"D10 legacy field leaked into report contract: {forbidden}")

if 'apiRequest<ExecutiveReport>(`/reports/executive/' not in dash_api:
    raise SystemExit("D10 dashboard does not consume the shared report API contract.")

for route in [
    '@router.get("/executive/{scan_id}", response_model=ExecutiveReport)',
    '@router.get("/monitoring/{scan_id}", response_model=ExecutiveReport)',
    '@router.get("/executive/{scan_id}/html"',
    '@router.get("/executive/{scan_id}/pdf")',
]:
    if route not in router:
        raise SystemExit(f"D10 report surface missing: {route}")

if 'report = _load_report(scan_id, tenant_auth)' not in router:
    raise SystemExit("D10 report surfaces lost the shared report loader.")
if 'build_executive_report' not in router or 'render_executive_report_pdf(report)' not in router:
    raise SystemExit("D10 HTML/PDF must remain derivatives of the shared report builder.")

for label in ["estimated_loss_eur", "potential_saving_eur"]:
    if label not in service:
        raise SystemExit(f"D10 service missing canonical financial field: {label}")

for forbidden_claim in ["guaranteed savings", "realized roi"]:
    if forbidden_claim in doc.lower():
        raise SystemExit(f"D10 contract documentation contains unsupported claim: {forbidden_claim}")

if "one backend report model and one report builder" not in doc:
    raise SystemExit("D10 contract does not freeze single-source renderer architecture.")

print("Executive Report Contract Quality Gate: PASS")
