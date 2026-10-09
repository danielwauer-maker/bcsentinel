#!/usr/bin/env python3
"""Generate the no-API landing pricing fallback for BCSentinel ARV tiers.

Runtime pricing is loaded from GET /pricing/public. This generated snapshot is
only a static fallback and must mirror the approved default tier model.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_PATHS = [REPO / "landingpage" / "pricing-snapshot.js"]

TIERS = [
    {
        "code": "small",
        "display_name": "Small",
        "min_records": 0,
        "max_records": 250000,
        "custom_quote": False,
        "prices": {
            "assessment": 24900,
            "validation_check": 12900,
            "monitoring_monthly": 19900,
            "monitoring_annual": 199000,
        },
    },
    {
        "code": "medium",
        "display_name": "Medium",
        "min_records": 250001,
        "max_records": 1000000,
        "custom_quote": False,
        "prices": {
            "assessment": 39900,
            "validation_check": 19900,
            "monitoring_monthly": 29900,
            "monitoring_annual": 299000,
        },
    },
    {
        "code": "large",
        "display_name": "Large",
        "min_records": 1000001,
        "max_records": 5000000,
        "custom_quote": False,
        "prices": {
            "assessment": 69900,
            "validation_check": 34900,
            "monitoring_monthly": 49900,
            "monitoring_annual": 499000,
        },
    },
    {
        "code": "enterprise",
        "display_name": "Enterprise",
        "min_records": 5000001,
        "max_records": 20000000,
        "custom_quote": False,
        "prices": {
            "assessment": 119000,
            "validation_check": 59000,
            "monitoring_monthly": 79900,
            "monitoring_annual": 799000,
        },
    },
    {
        "code": "enterprise_plus",
        "display_name": "Enterprise+",
        "min_records": 20000001,
        "max_records": None,
        "custom_quote": True,
        "prices": {},
    },
]

PRODUCT_META = {
    "assessment": ("Assessment", "one_time"),
    "validation_check": ("Validation Check", "one_time"),
    "monitoring_monthly": ("Monitoring Monthly", "month"),
    "monitoring_annual": ("Monitoring Annual", "year"),
}

FROM_PRICE_RENDERER = r'''(function () {
  function prefixForLanguage() {
    return (document.documentElement.lang || "de").toLowerCase().startsWith("de") ? "Ab " : "From ";
  }

  function applyFromPriceLabels() {
    const prefix = prefixForLanguage();
    document.querySelectorAll("[data-product-price]").forEach((node) => {
      const current = (node.textContent || "").trim().replace(/^(Ab |From )/, "");
      if (current) node.textContent = prefix + current;
    });
  }

  function startObserver() {
    applyFromPriceLabels();
    const observer = new MutationObserver(() => {
      observer.disconnect();
      applyFromPriceLabels();
      observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startObserver, { once: true });
  } else {
    startObserver();
  }
})();'''


def product_payload(product_key: str, price_cents: int) -> dict:
    display_name, interval = PRODUCT_META[product_key]
    return {
        "product_key": product_key,
        "display_name": display_name,
        "price_cents": price_cents,
        "price_eur": round(price_cents / 100, 2),
        "currency": "EUR",
        "billing_interval": interval,
        "is_active": True,
        "is_from_price": True,
    }


def main() -> int:
    products = [product_payload(key, TIERS[0]["prices"][key]) for key in PRODUCT_META]
    payload = {
        "source": "fallback",
        "currency": "EUR",
        "pricing_model": "record_volume_tiers",
        "pricing_metric": "bcsentinel_analyzed_record_volume",
        "price_dependency_copy": "Price depends on analyzed record volume.",
        "products": products,
        "tiers": TIERS,
        "custom_quote_above_records": 20000000,
    }
    js_lines = [
        "/* AUTO-GENERATED - do not edit. Source: scripts/generate_landing_pricing.py */",
        "/* Runtime source: GET /pricing/public */",
        "window.__BCS_MARKETING_STRINGS__ = {};",
        "window.__BCS_CANONICAL_BASE_EUR__ = 199;",
        "window.__BCS_PRODUCT_PRICING__ = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";",
        "",
        "/* Public ARV prices are minimum/from prices; keep labels explicit even after runtime re-render. */",
        FROM_PRICE_RENDERER,
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
