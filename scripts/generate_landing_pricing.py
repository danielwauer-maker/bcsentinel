#!/usr/bin/env python3
"""
Generate landingpage/pricing-snapshot.js with static product-pricing fallbacks.

Runtime pricing is loaded from GET /pricing/public. The snapshot is only the
no-API fallback for static landingpage rendering.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_PATHS = [
    REPO / "landingpage" / "pricing-snapshot.js",
]
PRODUCTS = [
    {
        "product_key": "assessment",
        "display_name": "Assessment",
        "price_cents": 7900,
        "currency": "EUR",
        "billing_interval": "one_time",
        "is_active": True,
    },
    {
        "product_key": "validation_check",
        "display_name": "Validation Check",
        "price_cents": 4900,
        "currency": "EUR",
        "billing_interval": "one_time",
        "is_active": True,
    },
    {
        "product_key": "monitoring_monthly",
        "display_name": "Monitoring Monthly",
        "price_cents": 9900,
        "currency": "EUR",
        "billing_interval": "month",
        "is_active": True,
    },
    {
        "product_key": "monitoring_annual",
        "display_name": "Monitoring Annual",
        "price_cents": 99000,
        "currency": "EUR",
        "billing_interval": "year",
        "is_active": True,
    },
]


def main() -> int:
    payload = {
        "source": "fallback",
        "currency": "EUR",
        "products": PRODUCTS,
    }
    js_lines = [
        "/* AUTO-GENERATED - do not edit. Source: scripts/generate_landing_pricing.py */",
        "/* Runtime source: GET /pricing/public */",
        "window.__BCS_MARKETING_STRINGS__ = {};",
        "window.__BCS_CANONICAL_BASE_EUR__ = 99;",
        "window.__BCS_PRODUCT_PRICING__ = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";",
        "",
    ]
    body = "\n".join(js_lines)

    for out in OUT_PATHS:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        print(f"Wrote {out.relative_to(REPO)}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
