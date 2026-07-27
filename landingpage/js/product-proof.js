/* LP-GL-06 / LP-GL-11A — Product Proof from centralized content. */
(function () {
  let current = null;

  function findingList(t) {
    const classes = ["critical", "high", "medium"];
    return t.findingRows.map((row, index) => `<div class="lp6-finding-item ${index === 0 ? "active" : ""}"><span class="lp6-dot ${classes[index] || "medium"}"></span><div><strong>${row.title}</strong><small>${row.records} · ${row.code}</small></div><span class="lp6-loss">${row.loss}</span></div>`).join("");
  }

  function markup(t) {
    const ui = t.ui;
    const first = t.findingRows[0];
    return `<div id="lp6-product-proof">
      <section class="lp6-section" id="findings"><div class="lp6-container"><div class="lp6-head"><p class="lp6-eyebrow">${t.findEyebrow}</p><h2>${t.findTitle}</h2><p>${t.findLead}</p></div><div class="lp6-findings-grid"><div class="lp6-findings-list">${findingList(t)}</div><article class="lp6-finding-detail"><div class="lp6-detail-top"><span class="lp6-badge">${first.severity}</span><span class="lp6-code">${first.code}</span></div><h3>${t.detailTitle}</h3><p>${t.detailText}</p><div class="lp6-detail-grid"><div class="lp6-detail-card"><span>${t.affected}</span><strong>12</strong></div><div class="lp6-detail-card"><span>${t.impact}</span><strong>${first.loss}</strong></div><div class="lp6-detail-card"><span>${t.status}</span><strong>${t.open}</strong></div></div><div class="lp6-recommendation"><strong>${t.recommend}</strong><p>${t.recommendText}</p></div><a class="lp6-method-link" href="loss-examples.html">${t.method}</a></article></div></div></section>
      <section class="lp6-section dark" id="report"><div class="lp6-container lp6-report-grid"><div class="lp6-report-stage"><div class="lp6-page back"><span class="lp6-report-kicker">BCSENTINEL</span><h3 class="lp6-report-title">${t.reportBackTitle}</h3><div class="lp6-report-bars"><span></span><span></span><span></span></div></div><div class="lp6-page front"><span class="lp6-report-kicker">EXECUTIVE REPORT</span><h3 class="lp6-report-title">${t.reportPageTitle}</h3><div class="lp6-report-score">72</div><div class="lp6-report-kpis"><div><span>${ui.estimatedLoss}</span><strong>€48,300</strong></div><div><span>${ui.potentialSaving}</span><strong>€31,700</strong></div><div><span>${t.findingsLabel}</span><strong>37</strong></div><div><span>${t.criticalLabel}</span><strong>8</strong></div></div><div class="lp6-report-bars"><span></span><span></span><span></span></div></div></div><div class="lp6-report-copy"><div class="lp6-head lp6-dark-head"><p class="lp6-eyebrow">${t.reportEyebrow}</p><h2>${t.reportTitle}</h2><p>${t.reportLead}</p></div><div class="lp6-checks">${t.reportChecks.map((x) => `<span>${x}</span>`).join("")}</div></div></div></section>
      <section class="lp6-section alt" id="dashboard"><div class="lp6-container"><div class="lp6-head"><p class="lp6-eyebrow">${t.dashboardEyebrow}</p><h2>${t.dashboardTitle}</h2><p>${t.dashboardLead}</p></div><div class="lp6-dashboard-shell"><div class="lp6-dashboard-top"><strong>BCSentinel</strong><div class="lp6-dashboard-tabs"><span class="active">${ui.overview}</span><span>${ui.findings}</span><span>${ui.monitoring}</span></div></div><div class="lp6-dashboard-body"><aside class="lp6-sidebar"><strong>${ui.dataHealth}</strong><span class="active">${ui.overview}</span><span>${ui.findings}</span><span>${ui.actions}</span><span>${ui.monitoring}</span><span>${ui.reports}</span></aside><div class="lp6-dashboard-main"><div class="lp6-kpi-grid"><div class="lp6-kpi-card"><span>${ui.healthScore}</span><strong>72 / 100</strong></div><div class="lp6-kpi-card"><span>${ui.estimatedLoss}</span><strong>€48,300</strong></div><div class="lp6-kpi-card"><span>${ui.potentialSaving}</span><strong>€31,700</strong></div><div class="lp6-kpi-card"><span>${ui.openFindings}</span><strong>37</strong></div></div><div class="lp6-dashboard-lower"><div class="lp6-panel"><h3>${ui.moduleHealth}</h3><div class="lp6-mini-bars"><span></span><span></span><span></span><span></span></div></div><div class="lp6-panel"><h3>${ui.priorityFindings}</h3><div class="lp6-mini-list"><div><span>${ui.vendorBankAccounts}</span><strong>${ui.critical}</strong></div><div><span>${ui.paymentTerms}</span><strong>${ui.high}</strong></div><div><span>${ui.openDocuments}</span><strong>${ui.medium}</strong></div></div></div></div></div></div></div><p class="lp6-caption">${t.sample}</p></div></section>
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