from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard" / "src"

required = [
    DASHBOARD / "App.tsx",
    DASHBOARD / "foundation" / "AppShell.tsx",
    DASHBOARD / "foundation" / "contexts.tsx",
    DASHBOARD / "api" / "servicePages.ts",
    DASHBOARD / "service" / "ServicePages.tsx",
    DASHBOARD / "service" / "LockedStatePage.tsx",
    DASHBOARD / "service" / "service.css",
]
for path in required:
    if not path.exists():
        raise SystemExit(f"D8 missing required file: {path.relative_to(ROOT)}")

app = (DASHBOARD / "App.tsx").read_text(encoding="utf-8")
shell = (DASHBOARD / "foundation" / "AppShell.tsx").read_text(encoding="utf-8")
contexts = (DASHBOARD / "foundation" / "contexts.tsx").read_text(encoding="utf-8")
api = (DASHBOARD / "api" / "servicePages.ts").read_text(encoding="utf-8")
pages = (DASHBOARD / "service" / "ServicePages.tsx").read_text(encoding="utf-8")
locked = (DASHBOARD / "service" / "LockedStatePage.tsx").read_text(encoding="utf-8")

for route in ["settings", "subscription", "support"]:
    if f"case '{route}'" not in app:
        raise SystemExit(f"D8 route not wired: {route}")
    if f"route: '{route}'" not in shell:
        raise SystemExit(f"D8 navigation item missing: {route}")

if "case 'locked'" not in app or "Funktion nicht freigeschaltet" not in locked:
    raise SystemExit("D8 explicit locked state is missing.")

for component in ["AuthRuntimePage", "SettingsPage", "SubscriptionPage", "SupportPage", "ProductStatePage"]:
    if f"export function {component}" not in pages:
        raise SystemExit(f"D8 page missing: {component}")

# Runtime security remains layered. Authentication alone may not grant entitlements.
for marker in ["AuthContext", "TenantContext", "EntitlementContext"]:
    if marker not in contexts:
        raise SystemExit(f"D8 lost runtime security context: {marker}")
if "Authentication → Tenant Membership → Tenant Status → Entitlements → Product Access." not in pages:
    raise SystemExit("D8 runtime boundary disclosure is missing.")

# Settings must remain read-only and notification configuration authoritative in Business Central.
if "/notifications/settings" not in api:
    raise SystemExit("D8 notification settings read model is not consumed.")
if "Änderungen an Regeln, Empfängern, Vorlagen und Events erfolgen ausschließlich in Business Central." not in pages:
    raise SystemExit("D8 settings page lost BC write-authority disclosure.")
for forbidden in ["/notifications/read-model/sync", "/scan/start", "/remediation/sync"]:
    if forbidden in api or forbidden in pages:
        raise SystemExit(f"D8 web write boundary violation: {forbidden}")

# Billing may open the server-authorized provider portal, but prices must never be duplicated in the UI.
if "/billing/subscription/status" not in api or "/billing/portal" not in api:
    raise SystemExit("D8 billing runtime endpoints are incomplete.")
for price_literal in ["249 €", "129 €", "199 €", "1.990 €", "399 €", "699 €", "1.190 €"]:
    if price_literal in pages or price_literal in locked:
        raise SystemExit(f"D8 hard-coded price detected: {price_literal}")

# Global product states must be explicit and may not fabricate fallback data.
for code in ["403", "404", "500"]:
    if f"'{code}'" not in pages:
        raise SystemExit(f"D8 product state missing: {code}")
if "Es werden keine Ersatzwerte erzeugt." not in pages:
    raise SystemExit("D8 error state must not fabricate data.")
if "keine Premium-Daten als Vorschau" not in locked:
    raise SystemExit("D8 locked state must not leak premium detail content.")

print("Dashboard Service Pages Quality Gate: PASS")
