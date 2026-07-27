/* LP-GL-10 / LP-GL-11A — Estimated Loss Examples */
(function () {
  function locale() { return document.documentElement.lang === "en" ? "en" : "de"; }
  function money(value) {
    return new Intl.NumberFormat(locale() === "de" ? "de-DE" : "en-US", {
      style: "currency", currency: "EUR", maximumFractionDigits: 0
    }).format(value);
  }
  function examplesMarkup(section) {
    const labels = section.labels;
    return section.items.map((item) => `
      <article class="lx-example">
        <div class="lx-example-head"><div><h3>${item.title}</h3><span class="lx-code">${item.code}</span></div><div class="lx-amount">${money(item.loss)}</div></div>
        <div class="lx-example-body">
          <div class="lx-copy"><h4>${labels.why}</h4><p>${item.why}</p><div class="lx-action"><strong>${labels.action}</strong>${item.action}</div></div>
          <div class="lx-calc"><div class="lx-calc-grid">
            <div class="lx-data"><small>${labels.records} · ${labels.measured}</small><strong>${item.count}</strong></div>
            <div class="lx-data"><small>${labels.prob} · ${labels.assumption}</small><strong>${item.prob}%</strong></div>
            <div class="lx-data"><small>${labels.effort} · ${labels.assumption}</small><strong>${item.minutes}</strong></div>
            <div class="lx-data"><small>${labels.rate} · ${labels.assumption}</small><strong>${money(item.rate)}/h</strong></div>
            <div class="lx-data"><small>${labels.freq} · ${labels.assumption}</small><strong>${item.frequency}</strong></div>
            <div class="lx-data"><small>${labels.annual} · ${labels.derived}</small><strong>${money(item.loss)}</strong></div>
          </div><div class="lx-equation">${item.count} × ${item.prob}% × ${item.minutes}/60 × ${money(item.rate)} × ${item.frequency} = ${money(item.loss)}</div></div>
        </div>
      </article>`).join("");
  }
  function markup(content) {
    const h = content.hero, s = content.summary, m = content.method, e = content.examples, c = content.catalog, d = content.disclaimer, f = content.final;
    return `
      <section class="lx-hero"><div class="lx-container lx-hero-grid"><div class="lx-head"><p class="lx-eyebrow">${h.eyebrow}</p><h1>${h.title}</h1><p>${h.lead}</p><div class="lx-actions"><a class="lx-btn primary" href="index.html#pricing">${h.primary}</a><a class="lx-btn secondary" href="#examples">${h.secondary}</a></div><div class="lx-trust">${h.trust.map((x) => `<span>${x}</span>`).join("")}</div></div><aside class="lx-hero-card" aria-label="${content.accessibility.workedExample}"><div class="lx-formula"><span>${h.exampleTitle}</span>48 × 30 % × 10/60 × 75 € × 12</div><div class="lx-result"><div><small>${h.estimatedAnnual}</small><br><strong>2.160 €</strong></div><div><small>${h.directlyMeasured}</small><br><b>${h.recordsValue}</b></div></div></aside></div></section>
      <section class="lx-section" id="summary"><div class="lx-container"><div class="lx-head"><p class="lx-eyebrow">${s.eyebrow}</p><h2>${s.title}</h2><p>${s.lead}</p></div><div class="lx-kpis">${s.kpis.map((x) => `<article class="lx-kpi"><span>${x[0]}</span><strong>${x[1]}</strong><small>${x[2]}</small></article>`).join("")}</div></div></section>
      <section class="lx-section alt" id="formula"><div class="lx-container"><div class="lx-head"><p class="lx-eyebrow">${m.eyebrow}</p><h2>${m.title}</h2><p>${m.lead}</p></div><div class="lx-method">${m.factors.map((x, i) => `<article><b>${i + 1}</b><h3>${x[0]}</h3><p>${x[1]}</p></article>`).join("")}</div><div class="lx-legend"><span class="lx-pill measured">${m.measured}</span><span class="lx-pill assumption">${m.assumption}</span><span class="lx-pill derived">${m.derived}</span></div></div></section>
      <section class="lx-section" id="examples"><div class="lx-container"><div class="lx-head"><p class="lx-eyebrow">${e.eyebrow}</p><h2>${e.title}</h2><p>${e.lead}</p></div><div class="lx-examples">${examplesMarkup(e)}</div></div></section>
      <section class="lx-section alt" id="catalog"><div class="lx-container"><div class="lx-head"><p class="lx-eyebrow">${c.eyebrow}</p><h2>${c.title}</h2></div><div class="lx-catalog">${c.groups.map((group) => `<article><h3>${group[0]}</h3><ul>${group[1].map((x) => `<li>${x}</li>`).join("")}</ul></article>`).join("")}</div></div></section>
      <section class="lx-section"><div class="lx-container"><div class="lx-disclaimer"><strong>${d.title}</strong> ${d.text}</div></div></section>
      <section class="lx-section dark"><div class="lx-container lx-final"><div class="lx-head"><p class="lx-eyebrow">${f.eyebrow}</p><h2>${f.title}</h2><p>${f.lead}</p></div><div class="lx-actions" style="justify-content:center"><a class="lx-btn primary" href="index.html#pricing">${f.primary}</a><a class="lx-btn secondary" href="index.html#findings">${f.secondary}</a></div></div></section>`;
  }
  async function render() {
    const main = document.querySelector("main.lx-main");
    if (!main || !window.BCSentinelContent) return;
    const content = await window.BCSentinelContent.loadBundle("loss-examples", locale());
    document.title = content.meta.title;
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content = content.meta.description;
    main.innerHTML = markup(content);
  }
  function init() {
    render().catch(() => {});
    new MutationObserver((mutations) => {
      if (mutations.some((item) => item.attributeName === "lang")) render().catch(() => {});
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();