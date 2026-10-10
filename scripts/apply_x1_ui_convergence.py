#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landingpage"

# Remove external Google Fonts from every static public page. Inter remains the
# preferred CSS family with system fallbacks; external font delivery is not a
# prerequisite for the product experience.
for path in LANDING.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r'^\s*<link rel="preconnect" href="https://fonts\.googleapis\.com"\s*/?>\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*<link rel="preconnect" href="https://fonts\.gstatic\.com"[^>]*>\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*<link href="https://fonts\.googleapis\.com/[^\"]+" rel="stylesheet"\s*/?>\s*\n?', '', text, flags=re.MULTILINE)
    if text != original:
        path.write_text(text, encoding="utf-8")

styles = LANDING / "styles.css"
css = styles.read_text(encoding="utf-8")
replacements = {
    "--orange: #ff8f3d;": "--orange: #FF921F;",
    "--blue: #4a8dff;": "--blue: #246BFD;",
    "--green: #56d6a1;": "--green: #11A36A;",
    "color: #fff;\n  background: linear-gradient(135deg, var(--orange), #ff7618);": "color: #082138;\n  background: var(--orange);",
}
for old, new in replacements.items():
    if old not in css and new not in css:
        raise SystemExit(f"Expected X1 CSS source fragment is missing: {old}")
    css = css.replace(old, new)
styles.write_text(css, encoding="utf-8")

print("X1 UI convergence patch applied.")
