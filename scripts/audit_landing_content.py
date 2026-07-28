#!/usr/bin/env python3
"""Audit public landing pages for LP-GL-11A content-management readiness."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landingpage"
LANG = LANDING / "lang"

MIGRATED_PAGES = {
    "index.html": "redesign",
    "loss-examples.html": "loss-examples",
    "security.html": "security",
    "docs.html": "docs",
    "contact.html": "contact",
    "privacy.html": "privacy",
    "terms.html": "terms",
    "impressum.html": "impressum",
    "help.html": "help",
    "support.html": "support",
    "partner-register.html": "partner-auth",
    "partner-login.html": "partner-auth",
    "partner-reset-password.html": "partner-auth",
    "partner-portal.html": "partner-portal",
    "billing-success.html": "billing",
    "billing-cancel.html": "billing",
}

EXCLUDED_PAGES = {"blueprint.html", "design-system.html"}
INLINE_CSS_WARNINGS = {"index.html"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_meta_description(html: str) -> bool:
    return bool(re.search(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*>', html, re.I))


def audit_page(path: Path, bundle: str) -> tuple[list[str], list[str]]:
    html = read(path)
    errors: list[str] = []
    warnings: list[str] = []
    if not re.search(r"<title(?:\s|>)", html, re.I):
        errors.append(f"{path.name}: missing <title>")
    if not has_meta_description(html):
        errors.append(f"{path.name}: missing meta description")
    if 'class="site-header"' not in html:
        errors.append(f"{path.name}: missing shared site header")
    if 'class="site-footer"' not in html:
        errors.append(f"{path.name}: missing shared site footer")
    if "js/site-shell.js" not in html:
        errors.append(f"{path.name}: missing site-shell.js")
    if "js/content-runtime.js" not in html and path.name != "index.html":
        errors.append(f"{path.name}: missing content-runtime.js")
    if re.search(r"<script(?![^>]*\bsrc=)[^>]*>\s*\S", html, re.I):
        errors.append(f"{path.name}: contains executable inline JavaScript")
    if re.search(r"<style[^>]*>\s*\S", html, re.I):
        message = f"{path.name}: contains inline CSS"
        if path.name in INLINE_CSS_WARNINGS:
            warnings.append(message + " (tracked for LP-GL-11B design consolidation)")
        else:
            errors.append(message)
    for locale in ("de", "en"):
        bundle_path = LANG / f"{bundle}.{locale}.json"
        if not bundle_path.exists():
            errors.append(f"{path.name}: missing bundle {bundle_path.name}")
            continue
        try:
            payload = json.loads(read(bundle_path))
        except json.JSONDecodeError as exc:
            errors.append(f"{bundle_path.name}: invalid JSON ({exc})")
            continue
        if payload.get("meta", {}).get("locale") != locale:
            errors.append(f"{bundle_path.name}: invalid meta.locale")
    return errors, warnings


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    html_files = sorted(LANDING.glob("*.html"))
    known = set(MIGRATED_PAGES) | EXCLUDED_PAGES
    for path in html_files:
        if path.name not in known:
            errors.append(f"Unclassified landing page: {path.name}")
    for name, bundle in MIGRATED_PAGES.items():
        path = LANDING / name
        if not path.exists():
            errors.append(f"Missing migrated page: {name}")
            continue
        page_errors, page_warnings = audit_page(path, bundle)
        errors.extend(page_errors)
        warnings.extend(page_warnings)

    if errors:
        print("Landing content audit FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Landing content audit PASS")
    print(f"- audited pages: {len(MIGRATED_PAGES)}")
    print(f"- excluded design/reference pages: {len(EXCLUDED_PAGES)}")
    for warning in warnings:
        print(f"- WARNING: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
