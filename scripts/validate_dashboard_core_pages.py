from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard" / "src"

required = [
    DASHBOARD / "App.tsx",
    DASHBOARD / "foundation" / "AppShell.tsx",
    DASHBOARD / "api" / "corePages.ts",
    DASHBOARD / "core" / "types.ts",
    DASHBOARD / "core" / "hooks.ts",
    DASHBOARD / "core" / "CorePages.tsx",
    DASHBOARD / "components" / "ui.tsx",
    DASHBOARD / "styles.css",
]
for path in required:
    if not path.exists():
        raise SystemExit(f"D7 missing required file: {path.relative_to(ROOT)}")

app = (DASHBOARD / "App.tsx").read_text(encoding="utf-8")
core_pages = (DASHBOARD / "core" / "CorePages.tsx").read_text(encoding="utf-8")
api = (DASHBOARD / "api" / "corePages.ts").read_text(encoding="utf-8")
shell = (DASHBOARD / "foundation" / "AppShell.tsx").read_text(encoding="utf-8")
styles = (DASHBOARD / "styles.css").read_text(encoding="utf-8")

for route in ["overview", "findings", "actions", "financial", "reports", "scans", "monitoring"]:
    if f"case '{route}'" not in app:
        raise SystemExit(f"D7 route not wired: {route}")

for component in [
    "OverviewPage",
    "FindingsPage",
    "ActionsPage",
    "FinancialImpactPage",
    "ReportsPage",
    "ScansPage",
    "MonitoringPage",
]:
    if f"export function {component}" not in core_pages:
        raise SystemExit(f"D7 page missing: {component}")

# Dashboard core pages are read-only. No mutation verb may be introduced in their API adapter.
for mutation in ["method: 'POST'", 'method: "POST"', "method: 'PUT'", "method: 'PATCH'", "method: 'DELETE'"]:
    if mutation in api:
        raise SystemExit(f"D7 read-only violation in dashboard API adapter: {mutation}")

for forbidden_endpoint in ["/scan/start", "/scan/sync", "/remediation/sync"]:
    if forbidden_endpoint in api:
        raise SystemExit(f"D7 web write endpoint referenced: {forbidden_endpoint}")

# Financial truth is consumed from the backend; the legacy roi_eur payload must never be rendered as ROI.
if "roi_eur" in core_pages:
    raise SystemExit("D7 UI must not render legacy roi_eur as ROI.")
if "Potential Saving" not in core_pages or "Estimated Loss" not in core_pages:
    raise SystemExit("D7 financial semantics are missing canonical labels.")
if "fin-v1" not in core_pages:
    raise SystemExit("D7 financial methodology disclosure is missing.")

# C5 shell invariants.
if "grid-template-columns: var(--sidebar-width) minmax(0, 1fr)" not in styles:
    raise SystemExit("D7 desktop shell lost the dedicated sidebar column.")
if "100vw" in styles:
    raise SystemExit("D7 app shell must not use browser-width sections inside the main column.")
if "grid-column: 2" not in styles or "app-footer" not in styles:
    raise SystemExit("D7 main/footer shell invariants are missing.")
if "data-active" not in shell:
    raise SystemExit("D7 navigation does not expose active-page state.")

# Frozen brand tokens remain unchanged.
for token in ["#FF921F", "#082138", "#14213D", "#246BFD"]:
    if token not in styles:
        raise SystemExit(f"D7 missing frozen design token {token}")

# Global product-state truth: missing backend values are not silently presented as numeric zero.
if "Critical severity not supplied" in core_pages:
    raise SystemExit("Use the German partial-data copy used by the product surface, not a validator-only placeholder.")
if "High wird nicht stillschweigend als Critical" not in core_pages:
    raise SystemExit("D7 must explicitly avoid mapping High to Critical.")

print("Dashboard Core Pages Quality Gate: PASS")
