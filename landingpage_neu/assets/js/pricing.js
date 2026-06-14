(function () {
  let currentPayload = null;

  function isValid(payload) {
    return Boolean(
      payload &&
      Array.isArray(payload.products) &&
      payload.products.every((product) =>
        product &&
        typeof product.product_key === "string" &&
        Number.isFinite(Number(product.price_cents))
      )
    );
  }

  function format(product) {
    const lang = window.BCSentinelI18n ? window.BCSentinelI18n.lang() : "de";
    const value = Number(product.price_cents || 0) / 100;
    return new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-US", {
      style: "currency",
      currency: product.currency || "EUR",
      minimumFractionDigits: Number.isInteger(value) ? 0 : 2,
      maximumFractionDigits: Number.isInteger(value) ? 0 : 2,
    }).format(value);
  }

  function render(payload) {
    if (!isValid(payload)) return;
    currentPayload = payload;
    const byKey = Object.fromEntries(payload.products.map((product) => [product.product_key, product]));
    document.querySelectorAll("[data-product-price]").forEach((node) => {
      const product = byKey[node.dataset.productPrice];
      if (product) node.textContent = format(product);
    });
  }

  async function load() {
    const config = window.BCSentinelConfig || {};
    try {
      const response = await fetch(`${config.apiBase || ""}/pricing/public`, {
        headers: { Accept: "application/json" },
        cache: "no-cache",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      if (!isValid(payload)) throw new Error("Invalid pricing payload");
      render(payload);
      return payload;
    } catch (error) {
      console.error("Pricing API unavailable, using fallback prices.", error);
      render(config.fallbackPricing);
      return config.fallbackPricing;
    }
  }

  window.addEventListener("bcsentinel:language-change", () => {
    if (currentPayload) render(currentPayload);
  });

  window.BCSentinelPricing = { load, render, current: () => currentPayload };
})();
