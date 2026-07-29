/* LP-GL-06 / LP-GL-11D — Product Proof from centralized content. */
(function () {
  let current = null;

  function findingList(t) {
    const classes = ["critical", "high", "medium"];
    return t.findingRows.map((row, index) => `<div class="lp6-finding-item ${index === 0 ? "active" : ""}"><span class="lp6-dot ${classes[index] || "medium"}"></span><div><strong>${row.title}</strong><small>${row.records} · ${row.code}</small></div><span class="lp6-loss">${row.loss}</span></div>`).join("");
  }

  function previewCopy(kind) {
    const de = document.documentElement.lang !== "en";
    if (kind === "report") return de
      ? { badge: "Aktueller Designstand", alt: "Vorschau des aktuellen BCSentinel Free-Scan-Executive-Reports" }
      : { badge: "Current design state", alt: "Preview of the current BCSentinel Free Scan executive report" };
    return de
      ? { badge: "Dashboard-Konzept", alt: "Repräsentative Vorschau des aktuellen BCSentinel Dashboard-Konzepts" }
      : { badge: "Dashboard concept", alt: "Representative preview of the current BCSentinel dashboard concept" };
  }

  function markup(t) {
    const first = t.findingRows[0];
    const reportPreview = previewCopy("report");
    const dashboardPreview = previewCopy("dashboard");
    return `<div id="lp6-product-proof">
      <section class="lp6-section" id="findings"><div class="lp6-container"><div class="lp6-head"><p class="lp6-eyebrow">${t.findEyebrow}</p><h2>${t.findTitle}</h2><p>${t.findLead}</p></div><div class="lp6-findings-grid"><div class="lp6-findings-list">${findingList(t)}</div><article class="lp6-finding-detail"><div class="lp6-detail-top"><span class="lp6-badge">${first.severity}</span><span class="lp6-code">${first.code}</span></div><h3>${t.detailTitle}</h3><p>${t.detailText}</p><div class="lp6-detail-grid"><div class="lp6-detail-card"><span>${t.affected}</span><strong>12</strong></div><div class="lp6-detail-card"><span>${t.impact}</span><strong>${first.loss}</strong></div><div class="lp6-detail-card"><span>${t.status}</span><strong>${t.open}</strong></div></div><div class="lp6-recommendation"><strong>${t.recommend}</strong><p>${t.recommendText}</p></div><a class="lp6-method-link" href="loss-examples.html">${t.method}</a></article></div></div></section>
      <section class="lp6-section dark" id="report"><div class="lp6-container lp6-report-grid"><figure class="lp6-asset-frame lp6-report-asset"><span class="lp6-preview-badge">${reportPreview.badge}</span><img src="assets/report-free-preview.svg" alt="${reportPreview.alt}" width="794" height="1123" loading="lazy" decoding="async" /></figure><div class="lp6-report-copy"><div class="lp6-head lp6-dark-head"><p class="lp6-eyebrow">${t.reportEyebrow}</p><h2>${t.reportTitle}</h2><p>${t.reportLead}</p></div><div class="lp6-checks">${t.reportChecks.map((x) => `<span>${x}</span>`).join("")}</div></div></div></section>
      <section class="lp6-section alt" id="dashboard"><div class="lp6-container"><div class="lp6-head"><p class="lp6-eyebrow">${t.dashboardEyebrow}</p><h2>${t.dashboardTitle}</h2><p>${t.dashboardLead}</p></div><figure class="lp6-asset-frame lp6-dashboard-asset"><span class="lp6-preview-badge">${dashboardPreview.badge}</span><img src="assets/dashboard-concept-preview.svg" alt="${dashboardPreview.alt}" width="1440" height="900" loading="lazy" decoding="async" /></figure><p class="lp6-caption">${t.sample}</p></div></section>
    </div>`;
  }

  function loadStyles() {
    if (document.querySelector('link[data-lp6-proof]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "css/product-proof.css";
    link.dataset.lp6Proof = "true";
    document.head.appendChild(link);
  }

  function loadPricing() {
    if (document.querySelector('script[data-lp7-pricing]')) return;
    const script = document.createElement("script");
    script.src = "js/pricing-conversion-journey.js";
    script.defer = true;
    script.dataset.lp7Pricing = "true";
    document.body.appendChild(script);
  }

  function render() {
    if (!current || !/\/(?:index\.html)?$/.test(location.pathname)) return;
    const story = document.getElementById("lp5-product-story");
    const pricing = document.getElementById("pricing");
    if (!story || !pricing) return;
    document.getElementById("lp6-product-proof")?.remove();
    pricing.insertAdjacentHTML("beforebegin", markup(current));
  }

  function init() {
    loadStyles();
    const runtime = window.BCSentinelContent;
    if (!runtime) return;
    runtime.subscribe((content) => {
      current = content.product_proof;
      render();
    });
    loadPricing();
    window.setTimeout(render, 220);
    window.setTimeout(render, 800);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();