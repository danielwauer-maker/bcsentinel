/* AUTO-GENERATED - do not edit. Source: scripts/generate_landing_pricing.py */
/* Runtime source: GET /pricing/public */
window.__BCS_MARKETING_STRINGS__ = {};
window.__BCS_CANONICAL_BASE_EUR__ = 199;
window.__BCS_PRODUCT_PRICING__ = {
  "source": "fallback",
  "currency": "EUR",
  "pricing_model": "record_volume_tiers",
  "pricing_metric": "bcsentinel_analyzed_record_volume",
  "price_dependency_copy": "Price depends on analyzed record volume.",
  "products": [
    {
      "product_key": "assessment",
      "display_name": "Assessment",
      "price_cents": 24900,
      "price_eur": 249.0,
      "currency": "EUR",
      "billing_interval": "one_time",
      "is_active": true,
      "is_from_price": true
    },
    {
      "product_key": "validation_check",
      "display_name": "Validation Check",
      "price_cents": 12900,
      "price_eur": 129.0,
      "currency": "EUR",
      "billing_interval": "one_time",
      "is_active": true,
      "is_from_price": true
    },
    {
      "product_key": "monitoring_monthly",
      "display_name": "Monitoring Monthly",
      "price_cents": 19900,
      "price_eur": 199.0,
      "currency": "EUR",
      "billing_interval": "month",
      "is_active": true,
      "is_from_price": true
    },
    {
      "product_key": "monitoring_annual",
      "display_name": "Monitoring Annual",
      "price_cents": 199000,
      "price_eur": 1990.0,
      "currency": "EUR",
      "billing_interval": "year",
      "is_active": true,
      "is_from_price": true
    }
  ],
  "tiers": [
    {
      "code": "small",
      "display_name": "Small",
      "min_records": 0,
      "max_records": 250000,
      "custom_quote": false,
      "prices": {
        "assessment": 24900,
        "validation_check": 12900,
        "monitoring_monthly": 19900,
        "monitoring_annual": 199000
      }
    },
    {
      "code": "medium",
      "display_name": "Medium",
      "min_records": 250001,
      "max_records": 1000000,
      "custom_quote": false,
      "prices": {
        "assessment": 39900,
        "validation_check": 19900,
        "monitoring_monthly": 29900,
        "monitoring_annual": 299000
      }
    },
    {
      "code": "large",
      "display_name": "Large",
      "min_records": 1000001,
      "max_records": 5000000,
      "custom_quote": false,
      "prices": {
        "assessment": 69900,
        "validation_check": 34900,
        "monitoring_monthly": 49900,
        "monitoring_annual": 499000
      }
    },
    {
      "code": "enterprise",
      "display_name": "Enterprise",
      "min_records": 5000001,
      "max_records": 20000000,
      "custom_quote": false,
      "prices": {
        "assessment": 119000,
        "validation_check": 59000,
        "monitoring_monthly": 79900,
        "monitoring_annual": 799000
      }
    },
    {
      "code": "enterprise_plus",
      "display_name": "Enterprise+",
      "min_records": 20000001,
      "max_records": null,
      "custom_quote": true,
      "prices": {}
    }
  ],
  "custom_quote_above_records": 20000000
};
