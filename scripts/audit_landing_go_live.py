#!/usr/bin/env python3
"""Static go-live readiness audit for the BCSentinel public landing pages."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landingpage"
LANG = LANDING / "lang"
EXCLUDED = {"blueprint.html", "design-system.html"}

REQUIRED_PRODUCT_TERMS = {
    "de": ("Kostenlos", "Assessment", "Validation", "Monitoring"),
    "en": ("free", "Assessment", "Validation", "Monitoring"),
}
FORBIDDEN_PUBLIC_TERMS = (
    re.compile(r"\bPremium(?:zugriff| access)?\b", re.I),
    re.compile(r"\bFull Analysis\b", re.I),
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def audit_html(path: Path) -> list[str]:
    html = read(path)
    errors: list[str] = []
    if not re.search(r'<meta\s+name=["\']viewport["\'][^>]*width=device-width', html, re.I):
        errors.append(f"{path.name}: responsive viewport missing")
    if 'class="site-header"' not in html or 'class="site-footer"' not in html:
        errors.append(f"{path.name}: shared shell incomplete")
    if "js/site-shell.js" not in html:
        errors.append(f"{path.name}: site shell missing")
    if not re.search(r'<html\b[^>]*\blang=["\'](?:de|en)["\']', html, re.I):
        errors.append(f"{path.name}: supported initial language missing")
    return errors


def audit_css() -> list[str]:
    css = "\n".join(read(path) for path in sorted((LANDING / "css").glob("*.css")))
    errors: list[str] = []
    checks = {
        "mobile breakpoint": r"@media\s*\([^)]*max-width",
        "keyboard focus": r":focus-visible",
        "reduced motion": r"prefers-reduced-motion",
        "dark mode": r'data-theme\s*=\s*["\']?dark',
        "minimum touch target": r"min-height\s*:\s*(?:4[4-9]|[5-9]\d)px",
    }
    for label, pattern in checks.items():
        if not re.search(pattern, css, re.I):
            errors.append(f"shared CSS: missing {label} coverage")
    return errors


def audit_product_journey() -> list[str]:
    errors: list[str] = []
    runtime = read(LANDING / "js" / "content-runtime.js")
    if "normalizePublicCopy" not in runtime:
        errors.append("content-runtime.js: public copy normalization missing")
    for locale in ("de", "en"):
        path = LANG / f"redesign.{locale}.json"
        payload = json.loads(read(path))
        serialized = json.dumps(payload, ensure_ascii=False)
        for term in REQUIRED_PRODUCT_TERMS[locale]:
            if term.lower() not in serialized.lower():
                errors.append(f"{path.name}: product journey term missing ({term})")
    return errors


def audit_preview_assets() -> list[str]:
    errors: list[str] = []
    required = (
        LANDING / "assets" / "dashboard-concept-preview.svg",
        LANDING / "assets" / "report-free-preview.svg",
        LANDING / "css" / "product-preview-assets.css",
    )
    for path in required:
        if not path.exists() or path.stat().st_size < 100:
            errors.append(f"missing or empty preview asset: {path.relative_to(ROOT)}")
    renderer = read(LANDING / "js" / "product-proof.js")
    if "Dashboard concept preview" not in renderer or "Current design state" not in renderer:
        errors.append("product-proof.js: explicit preview labels missing")
    return errors


def main() -> int:
    errors: list[str] = []
    pages = [p for p in sorted(LANDING.glob("*.html")) if p.name not in EXCLUDED]
    for page in pages:
        errors.extend(audit_html(page))
    errors.extend(audit_css())
    errors.extend(audit_product_journey())
    errors.extend(audit_preview_assets())

    if errors:
        print("Landing go-live audit FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Landing go-live audit PASS")
    print(f"- audited public pages: {len(pages)}")
    print("- responsive viewport and shared shell present on all public pages")
    print("- mobile breakpoints, keyboard focus, reduced motion and dark mode are covered")
    print("- Free Scan, Assessment, Validation and Monitoring journey is represented")
    print("- dashboard and report previews remain explicitly labelled")
    print("- manual cross-browser visual acceptance is still required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
