(function () {
  const API_HOSTS = {
    production: "https://api.bcsentinel.com",
    development: "https://dev-api.bcsentinel.com",
    local: "",
  };

  function apiBase() {
    const host = (window.location.hostname || "").toLowerCase();
    if (!host || host === "localhost" || host === "127.0.0.1") return API_HOSTS.local;
    if (host.startsWith("dev.")) return API_HOSTS.development;
    return API_HOSTS.production;
  }

  window.BCSentinelConfig = {
    apiBase: apiBase(),
    productCodes: ["assessment", "validation_check", "monitoring_monthly", "monitoring_annual"],
    fallbackPricing: {
      source: "fallback",
      currency: "EUR",
      products: [
        { product_key: "assessment", display_name: "Assessment", price_cents: 7900, currency: "EUR", billing_interval: "one_time", is_active: true },
        { product_key: "validation_check", display_name: "Validation Check", price_cents: 4900, currency: "EUR", billing_interval: "one_time", is_active: true },
        { product_key: "monitoring_monthly", display_name: "Monitoring Monthly", price_cents: 9900, currency: "EUR", billing_interval: "month", is_active: true },
        { product_key: "monitoring_annual", display_name: "Monitoring Annual", price_cents: 99000, currency: "EUR", billing_interval: "year", is_active: true },
      ],
    },
    pages: [
      { key: "home", href: "index.html", labelKey: "nav_home", footerGroup: "product" },
      { key: "pricing", href: "pricing.html", labelKey: "nav_pricing", footerGroup: "product" },
      { key: "executive_reports", href: "executive-reports.html", labelKey: "nav_executive_reports", footerGroup: "product" },
      { key: "why_bcsentinel", href: "why-bcsentinel.html", labelKey: "nav_why", footerGroup: "company" },
      { key: "trust", href: "trust.html", labelKey: "nav_trust", footerGroup: "trust" },
      { key: "support", href: "support.html", labelKey: "nav_support", footerGroup: "resources" },
      { key: "about", href: "about.html", labelKey: "nav_about", footerGroup: "company" },
      { key: "contact", href: "contact.html", labelKey: "nav_contact", footerGroup: "company" },
    ],
  };
})();
