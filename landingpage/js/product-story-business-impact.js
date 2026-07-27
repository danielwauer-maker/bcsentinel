/* LP-GL-05 / LP-GL-11A — product story from centralized content. */
(function () {
  let current = null;

  function markup(t) {
    const problems = t.problems.map((x) => `<div class="lp5-problem-row"><strong>${x[0]}</strong><span>${x[1]}</span></div>`).join("");
    const impacts = t.impactRows.map((x) => `<div class="lp5-impact-line"><span>${x[0]}</span><strong>${x[1]}</strong></div>`).join("");
    const steps = t.steps.map((x, i) => `<article class="lp5-step"><span>${i + 1}</span><h3>${x[0]}</h3><p>${x[1]}</p></article>`).join("");
    const products = t.products.map((p, i) => `<article class="lp5-life-card ${i === 0 ? "recommended" : ""}"><span class="lp5-life-tag">${p.tag}</span><h3>${p.title}</h3><p>${p.text}</p><ul>${p.items.map((v) => `<li>${v}</li>`).join("")}</ul><span class="lp5-life-time">${p.time}</span></article>`).join("");
    return `<div id="lp5-product-story">
      <section class="lp5-section" id="problem"><div class="lp5-container"><div class="lp5-head"><p class="lp5-eyebrow">${t.problemEyebrow}</p><h2>${t.problemTitle}</h2><p>${t.problemLead}</p></div><div class="lp5-problem-grid"><div class="lp5-problem-list">${problems}</div><aside class="lp5-impact-panel"><h3>${t.impactTitle}</h3>${impacts}<div class="lp5-impact-total"><span>${t.impactTotal}</span><strong>${t.impactValue}</strong></div><p class="lp5-note">${t.impactNote}</p></aside></div></div></section>
      <section class="lp5-section alt" id="loss-methodology"><div class="lp5-container"><div class="lp5-loss-grid"><div class="lp5-loss-copy"><p class="lp5-eyebrow">${t.lossEyebrow}</p><h3>${t.lossTitle}</h3><p>${t.lossLead}</p><a href="loss-examples.html">${t.lossLink}</a></div><div class="lp5-formula"><h3>${t.formulaTitle}</h3><div class="lp5-data-row measured"><span>${t.records}<small>${t.measured}</small></span><strong>43</strong></div><div class="lp5-data-row assumption"><span>${t.frequency}<small>${t.assumption}</small></span><strong>3</strong></div><div class="lp5-data-row assumption"><span>${t.effort}<small>${t.assumption}</small></span><strong>15 min</strong></div><div class="lp5-data-row assumption"><span>${t.rate}<small>${t.assumption}</small></span><strong>€42/h</strong></div><div class="lp5-equation">${t.equation}</div><div class="lp5-result"><span>${t.resultLabel}</span><strong>${t.result}</strong></div><p class="lp5-disclaimer">${t.disclaimer}</p></div></div></div></section>
      <section class="lp5-section" id="how-it-works"><div class="lp5-container"><div class="lp5-head"><p class="lp5-eyebrow">${t.howEyebrow}</p><h2>${t.howTitle}</h2><p>${t.howLead}</p></div><div class="lp5-how-grid">${steps}</div></div></section>
      <section class="lp5-section dark" id="solution"><div class="lp5-container"><div class="lp5-head"><p class="lp5-eyebrow">${t.lifeEyebrow}</p><h2>${t.lifeTitle}</h2><p>${t.lifeLead}</p></div><div class="lp5-lifecycle">${products}</div></div></section>
    </div>`;
  }

  function loadStyles() {
    if (document.querySelector('link[data-lp5-story]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "css/product-story-business-impact.css";
    link.dataset.lp5Story = "true";
    document.head.appendChild(link);
  }

  function loadProductProof() {
    if (document.querySelector('script[data-lp6-proof]')) return;
    const script = document.createElement("script");
    script.src = "js/product-proof.js";
    script.defer = true;
    script.dataset.lp6Proof = "true";
    document.body.appendChild(script);
  }

  function removeLegacy(main) {
    const targets = [];
    let node = main.querySelector(".lp4-trust-strip")?.nextElementSibling;
    while (node && node.id !== "pricing") {
      const next = node.nextElementSibling;
      if (node.matches("section.section,section.section-split") || node.id === "problem" || node.id === "solution" || node.id === "how-it-works") targets.push(node);
      node = next;
    }
    targets.forEach((item) => item.remove());
  }

  function render() {
    if (!current || !/\/(?:index\.html)?$/.test(location.pathname)) return;
    const main = document.querySelector("main");
    const trust = main?.querySelector(".lp4-trust-strip");
    if (!main || !trust) return;
    removeLegacy(main);
    document.getElementById("lp5-product-story")?.remove();
    trust.insertAdjacentHTML("afterend", markup(current));
    loadProductProof();
  }

  function ensureContentRuntime() {
    if (window.BCSentinelContent) return Promise.resolve(window.BCSentinelContent);
    return new Promise((resolve, reject) => {
      const existing = document.querySelector('script[data-content-runtime]');
      if (existing) {
        window.addEventListener("bcsentinel:content-ready", () => resolve(window.BCSentinelContent), { once: true });
        return;
      }
      const script = document.createElement("script");
      script.src = "js/content-runtime.js";
      script.defer = true;
      script.dataset.contentRuntime = "true";
      script.onload = () => resolve(window.BCSentinelContent);
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function init() {
    if (!/\/(?:index\.html)?$/.test(location.pathname)) return;
    loadStyles();
    const runtime = await ensureContentRuntime();
    runtime.subscribe((content) => {
      current = content.product_story;
      render();
    });
    await runtime.refresh();
    window.setTimeout(render, 180);
    window.setTimeout(render, 700);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init().catch(() => {}), { once: true });
  else init().catch(() => {});
})();