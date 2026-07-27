/* AUTO-GENERATED - do not edit. Source: scripts/generate_landing_pricing.py */
/* Runtime source: GET /pricing/public */
window.__BCS_MARKETING_STRINGS__ = {};
window.__BCS_CANONICAL_BASE_EUR__ = 149;
window.__BCS_PRODUCT_PRICING__ = {
  "source": "fallback",
  "currency": "EUR",
  "products": [
    {"product_key":"data_health_score","display_name":"Data Health Score","price_cents":0,"currency":"EUR","billing_interval":"one_time","is_active":true},
    {"product_key":"full_analysis","display_name":"Assessment","price_cents":7900,"currency":"EUR","billing_interval":"one_time","is_active":true},
    {"product_key":"validation_check","display_name":"Validation","price_cents":4900,"currency":"EUR","billing_interval":"one_time","is_active":true},
    {"product_key":"monitoring","display_name":"Monitoring","price_cents":14900,"currency":"EUR","billing_interval":"month","is_active":true},
    {"product_key":"monitoring_monthly","display_name":"Monitoring Monthly","price_cents":14900,"currency":"EUR","billing_interval":"month","is_active":true},
    {"product_key":"monitoring_annual","display_name":"Monitoring Annual","price_cents":149000,"currency":"EUR","billing_interval":"year","is_active":true}
  ]
};

(function bootstrapLandingModules() {
  if (!/\/(?:index\.html)?$/.test(window.location.pathname)) return;
  [
    ["js/hero-conversion-core.js", "lp4Hero"],
    ["js/pricing-runtime-sync.js", "lp7PricingSync"]
  ].forEach(([src, key]) => {
    const script = document.createElement("script");
    script.src = src;
    script.defer = true;
    script.dataset[key] = "true";
    document.head.appendChild(script);
  });
})();