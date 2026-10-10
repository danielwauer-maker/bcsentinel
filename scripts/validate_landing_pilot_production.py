from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landingpage"
BACKEND = ROOT / "backend"

required = [
    LANDING / "index.html",
    LANDING / "pilot.html",
    LANDING / "privacy.html",
    LANDING / "terms.html",
    LANDING / "impressum.html",
    LANDING / "robots.txt",
    LANDING / "sitemap.xml",
    LANDING / "pricing-snapshot.js",
    LANDING / "js" / "landing-production.js",
    BACKEND / "app" / "routers" / "public.py",
    BACKEND / "app" / "public_lead_models.py",
    BACKEND / "alembic" / "versions" / "0021_pilot_interests.py",
    BACKEND / "tests" / "test_public_pilot_interest.py",
]
for path in required:
    if not path.exists():
        raise SystemExit(f"D9 missing required file: {path.relative_to(ROOT)}")

index = (LANDING / "index.html").read_text(encoding="utf-8")
pilot = (LANDING / "pilot.html").read_text(encoding="utf-8")
runtime = (LANDING / "js" / "landing-production.js").read_text(encoding="utf-8")
public_router = (BACKEND / "app" / "routers" / "public.py").read_text(encoding="utf-8")
model = (BACKEND / "app" / "public_lead_models.py").read_text(encoding="utf-8")
migration = (BACKEND / "alembic" / "versions" / "0021_pilot_interests.py").read_text(encoding="utf-8")
robots = (LANDING / "robots.txt").read_text(encoding="utf-8")
sitemap = (LANDING / "sitemap.xml").read_text(encoding="utf-8")

# Pricing: landing has no independent numeric truth. Runtime API + generated snapshot only.
for product in ["assessment", "validation_check", "monitoring_monthly", "monitoring_annual"]:
    if f'data-product-price="{product}"' not in index:
        raise SystemExit(f"D9 pricing surface missing product: {product}")
if "/pricing/public" not in runtime or "__BCS_PRODUCT_PRICING__" not in runtime:
    raise SystemExit("D9 pricing must use runtime public pricing with generated snapshot fallback.")
for forbidden_price in ["EUR 79", "EUR 49", "EUR 99", "EUR 990", "€ 79", "€ 49", "€ 99", "€ 990"]:
    if forbidden_price in index:
        raise SystemExit(f"D9 stale hard-coded price on landing page: {forbidden_price}")

# Public claims stay inside approved product truth.
combined = (index + "\n" + pilot).lower()
for forbidden_claim in [
    "your business central data is costing you money",
    "guaranteed savings",
    "realized roi",
    "production ready",
    "appsource available",
    "guaranteed uptime",
]:
    if forbidden_claim in combined:
        raise SystemExit(f"D9 unsupported public claim: {forbidden_claim}")
if "controlled pilot" not in combined:
    raise SystemExit("D9 pilot availability must be described as controlled pilot.")
if "modeled" not in combined and "modelliert" not in combined:
    raise SystemExit("D9 financial claims must disclose modeled outcomes.")
if "read-only" not in combined:
    raise SystemExit("D9 must disclose the read-only web boundary.")

# Pilot intake: first-party persistence, privacy consent and spam honeypot.
for marker in ["/public/pilot-interest", "privacy_consent", "website"]:
    if marker not in public_router and marker not in runtime and marker not in pilot:
        raise SystemExit(f"D9 pilot intake marker missing: {marker}")
if "PilotInterest" not in public_router or "PilotInterest" not in model:
    raise SystemExit("D9 pilot interest is not persisted by the first-party backend.")
if "formsubmit.co" in pilot.lower():
    raise SystemExit("D9 pilot form must not depend on FormSubmit.")
if "privacy.html" not in pilot:
    raise SystemExit("D9 pilot form must link to the privacy policy.")
if 'aria-live="polite"' not in pilot:
    raise SystemExit("D9 pilot form needs an accessible live submission status.")
if "skip-link" not in index or "skip-link" not in pilot:
    raise SystemExit("D9 public pages need skip links for keyboard navigation.")

# Migration chain must remain linear.
if 'down_revision = "0020_product_migration_metadata"' not in migration:
    raise SystemExit("D9 migration does not extend the current migration head.")

# SEO / public discovery.
for page_name, page in [("landing", index), ("pilot", pilot)]:
    for marker in ['rel="canonical"', 'name="description"', 'name="robots"', 'property="og:title"']:
        if marker not in page:
            raise SystemExit(f"D9 {page_name} SEO marker missing: {marker}")
if "Sitemap: https://www.bcsentinel.com/sitemap.xml" not in robots:
    raise SystemExit("D9 robots.txt does not advertise the sitemap.")
for url in ["https://www.bcsentinel.com/", "https://www.bcsentinel.com/pilot.html", "https://www.bcsentinel.com/privacy.html", "https://www.bcsentinel.com/impressum.html"]:
    if url not in sitemap:
        raise SystemExit(f"D9 sitemap missing public URL: {url}")

print("Landing + Pilot Production Quality Gate: PASS")
