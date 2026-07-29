#!/usr/bin/env python3
"""Audit landing-page design consolidation rules for LP-GL-11B."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landingpage"
EXCLUDED = {"blueprint.html", "design-system.html"}
CONTENT_LEGAL_LAYER = "css/content-legal-visual-consistency.css"
FORM_AUTH_LAYER = "css/form-auth-visual-consistency.css"
ACCOUNT_TRANSACTION_LAYER = "css/account-transaction-visual-consistency.css"

REQUIRED_SHARED_ASSETS = {
    "index.html": ("styles.css", "css/home-layout-consolidation.css", "css/primary-pages-visual-consistency.css", "js/site-shell.js"),
    "loss-examples.html": ("styles.css", "css/loss-examples-redesign.css", "css/primary-pages-visual-consistency.css", "js/site-shell.js"),
    "security.html": ("css/public-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "docs.html": ("css/public-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "help.html": ("css/public-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "support.html": ("css/public-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "contact.html": ("css/public-content-pages.css", "css/contact-page.css", FORM_AUTH_LAYER, "js/site-shell.js"),
    "privacy.html": ("css/legal-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "terms.html": ("css/legal-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "impressum.html": ("css/legal-content-pages.css", CONTENT_LEGAL_LAYER, "js/site-shell.js"),
    "partner-register.html": ("css/partner-auth-pages.css", FORM_AUTH_LAYER, "js/site-shell.js"),
    "partner-login.html": ("css/partner-auth-pages.css", FORM_AUTH_LAYER, "js/site-shell.js"),
    "partner-reset-password.html": ("css/partner-auth-pages.css", FORM_AUTH_LAYER, "js/site-shell.js"),
    "partner-portal.html": ("css/partner-portal.css", ACCOUNT_TRANSACTION_LAYER, "js/site-shell.js"),
    "billing-success.html": ("css/billing-result-pages.css", ACCOUNT_TRANSACTION_LAYER, "js/site-shell.js"),
    "billing-cancel.html": ("css/billing-result-pages.css", ACCOUNT_TRANSACTION_LAYER, "js/site-shell.js"),
}


def audit(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if re.search(r"<style[^>]*>\s*\S", html, re.I):
        errors.append(f"{path.name}: inline <style> block")
    if re.search(r"<script(?![^>]*\bsrc=)[^>]*>\s*\S", html, re.I):
        errors.append(f"{path.name}: executable inline <script>")
    inline_styles = len(re.findall(r"\sstyle=[\"']", html, re.I))
    if inline_styles:
        errors.append(f"{path.name}: {inline_styles} inline style attribute(s)")
    if "</link>" in html.lower():
        errors.append(f"{path.name}: invalid </link> closing tag")
    if "<!--" in "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.I | re.S)):
        errors.append(f"{path.name}: HTML comment inside CSS")
    for asset in REQUIRED_SHARED_ASSETS.get(path.name, ()):
        if asset not in html:
            errors.append(f"{path.name}: missing shared asset {asset}")
    return errors


def audit_footer_ownership() -> list[str]:
    errors: list[str] = []
    shell = (LANDING / "js" / "site-shell.js").read_text(encoding="utf-8")
    audience = (LANDING / "js" / "audience-faq-footer.js").read_text(encoding="utf-8")
    if "function buildFooter()" not in shell or 'class="site-footer"' not in shell:
        errors.append("site-shell.js: global footer component missing")
    if "footerMarkup" in audience or "lp9-footer" in audience:
        errors.append("audience-faq-footer.js: duplicate homepage footer renderer detected")
    return errors


def main() -> int:
    errors: list[str] = []
    pages = [p for p in sorted(LANDING.glob("*.html")) if p.name not in EXCLUDED]
    for page in pages:
        errors.extend(audit(page))
    errors.extend(audit_footer_ownership())
    if errors:
        print("Landing design audit FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Landing design audit PASS")
    print(f"- audited public pages: {len(pages)}")
    print("- no inline CSS blocks, executable inline scripts, or inline style attributes")
    print("- homepage and Estimated Loss share the primary visual-consistency layer")
    print("- Security, Docs, Help, Support and Legal pages share the content/legal visual layer")
    print("- Contact and partner authentication share the form/auth visual layer")
    print("- Partner Portal and Billing pages share the account/transaction visual layer")
    print("- one global marketing footer is owned by site-shell.js across all public pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
