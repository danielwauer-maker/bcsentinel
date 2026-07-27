/* LP-GL-07 — keep dynamically inserted price fields synchronized. */
(function () {
  let payload = window.__BCS_PRODUCT_PRICING__ || null;
  let fetchStarted = false;
  let applyScheduled = false;

  function language() {
    return document.documentElement.lang === "en" ? "en" : "de";
  }

  function format(value, currency) {
    return new Intl.NumberFormat(language() === "de" ? "de-DE" : "en-US", {
      style: "currency",
      currency: currency || "EUR",
      maximumFractionDigits: Number.isInteger(value) ? 0 : 2,
    }).format(value);
  }

  function apply() {
    applyScheduled = false;
    if (!payload || !Array.isArray(payload.products)) return;

    payload.products.forEach((product) => {
      const keys = [product.product_key];
      if (product.product_key === "full_analysis") keys.push("assessment");
      if (product.product_key === "monitoring") keys.push("monitoring_monthly");

      const formatted = format(
        Number(product.price_cents || 0) / 100,
        product.currency || payload.currency
      );

      keys.forEach((key) => {
        document.querySelectorAll(`[data-product-price="${key}"]`).forEach((node) => {
          if (node.textContent !== formatted) node.textContent = formatted;
        });
      });
    });
  }

  function scheduleApply() {
    if (applyScheduled) return;
    applyScheduled = true;
    window.requestAnimationFrame(apply);
  }

  async function fetchPricing() {
    if (fetchStarted) return;
    fetchStarted = true;
    try {
      const host = location.hostname.toLowerCase().startsWith("dev.")
        ? "https://dev-api.bcsentinel.com"
        : "https://api.bcsentinel.com";
      const response = await fetch(`${host}/pricing/public`, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) return;
      const next = await response.json();
      if (next && Array.isArray(next.products)) payload = next;
      scheduleApply();
    } catch (_) {
      scheduleApply();
    }
  }

  function init() {
    scheduleApply();
    fetchPricing();

    const bodyObserver = new MutationObserver((mutations) => {
      const relevant = mutations.some((mutation) =>
        Array.from(mutation.addedNodes).some((node) => {
          if (!(node instanceof Element)) return false;
          return node.matches?.("[data-product-price]") || node.querySelector?.("[data-product-price]");
        })
      );
      if (relevant) scheduleApply();
    });
    bodyObserver.observe(document.body, { childList: true, subtree: true });

    new MutationObserver(scheduleApply).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["lang"],
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
