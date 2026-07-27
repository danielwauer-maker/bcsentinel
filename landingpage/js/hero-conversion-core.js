/* LP-GL-04 — start page hero and conversion core */
(function () {
  const copy = {
    de: {
      eyebrow: "Für Microsoft Dynamics 365 Business Central",
      title: "Machen Sie Datenqualität messbar und steuerbar.",
      lead: "BCSentinel erkennt Datenqualitätsrisiken, bewertet ihre operativen und finanziellen Auswirkungen und zeigt, welche Maßnahmen zuerst den größten Nutzen bringen.",
      primary: "Assessment starten",
      secondary: "Estimated Loss verstehen",
      proof1: "Keine Kreditkarte erforderlich",
      proof2: "Für Business Central entwickelt",
      proof3: "Managementtaugliche Ergebnisse",
      appTitle: "Data Health Overview",
      lastScan: "Assessment abgeschlossen",
      score: "Health Score",
      loss: "Estimated Loss",
      saving: "Potential Saving",
      reportLabel: "EXECUTIVE REPORT",
      reportTitle: "Data Health Assessment",
      findingLabel: "Kritisch",
      findingTitle: "Doppelte Kreditoren-Bankverbindungen",
      findingText: "12 betroffene Datensätze mit erhöhtem Kontroll- und Zahlungsrisiko.",
      impact: "Geschätzter Impact",
      trust1: "Assessment, Validation und Monitoring",
      trust2: "Priorisierte Findings mit Handlungsempfehlungen",
      trust3: "Transparente Estimated-Loss-Methodik",
      trust4: "Executive PDF Reporting",
      headerCta: "Assessment starten"
    },
    en: {
      eyebrow: "Built for Microsoft Dynamics 365 Business Central",
      title: "Turn data quality into measurable business control.",
      lead: "BCSentinel detects data-quality risks, evaluates their operational and financial impact, and shows which actions should be addressed first.",
      primary: "Start assessment",
      secondary: "Understand Estimated Loss",
      proof1: "No credit card required",
      proof2: "Built for Business Central",
      proof3: "Executive-ready results",
      appTitle: "Data Health Overview",
      lastScan: "Assessment completed",
      score: "Health Score",
      loss: "Estimated Loss",
      saving: "Potential Saving",
      reportLabel: "EXECUTIVE REPORT",
      reportTitle: "Data Health Assessment",
      findingLabel: "Critical",
      findingTitle: "Duplicate vendor bank accounts",
      findingText: "12 affected records with increased control and payment risk.",
      impact: "Estimated impact",
      trust1: "Assessment, Validation and Monitoring",
      trust2: "Prioritized findings with recommendations",
      trust3: "Transparent Estimated Loss methodology",
      trust4: "Executive PDF reporting",
      headerCta: "Start assessment"
    }
  };

  function language() {
    return document.documentElement.lang === "en" ? "en" : "de";
  }

  function heroMarkup(t) {
    return `
      <section class="lp4-hero" id="top" aria-labelledby="lp4-title">
        <div class="lp4-container lp4-grid">
          <div>
            <p class="lp4-eyebrow">${t.eyebrow}</p>
            <h1 class="lp4-title" id="lp4-title">${t.title}</h1>
            <p class="lp4-lead">${t.lead}</p>
            <div class="lp4-actions">
              <a class="lp4-btn lp4-btn-primary" href="#pricing">${t.primary}</a>
              <a class="lp4-btn lp4-btn-secondary" href="loss-examples.html">${t.secondary}</a>
            </div>
            <div class="lp4-proof" aria-label="Product assurances">
              <span>${t.proof1}</span><span>${t.proof2}</span><span>${t.proof3}</span>
            </div>
          </div>
          <div class="lp4-stage" aria-label="BCSentinel product preview">
            <div class="lp4-report" aria-hidden="true">
              <small>${t.reportLabel}</small><h3>${t.reportTitle}</h3><div class="lp4-report-score">72</div><div class="lp4-report-lines"></div>
            </div>
            <div class="lp4-dashboard">
              <div class="lp4-appbar"><strong>${t.appTitle}</strong><span>${t.lastScan}</span></div>
              <div class="lp4-dashboard-body">
                <div class="lp4-kpis">
                  <div class="lp4-kpi"><small>${t.score}</small><strong>72 / 100</strong></div>
                  <div class="lp4-kpi loss"><small>${t.loss}</small><strong>€48,300</strong></div>
                  <div class="lp4-kpi saving"><small>${t.saving}</small><strong>€31,700</strong></div>
                </div>
                <div class="lp4-chart" aria-label="Module health distribution"><span style="height:44%"></span><span></span><span></span><span></span><span></span></div>
                <div class="lp4-findings">
                  <div class="lp4-finding-row"><span class="lp4-severity"></span><strong>Duplicate vendor bank accounts</strong><span>12 records</span></div>
                  <div class="lp4-finding-row"><span class="lp4-severity"></span><strong>Customers without payment terms</strong><span>43 records</span></div>
                  <div class="lp4-finding-row"><span class="lp4-severity"></span><strong>Inactive items in open documents</strong><span>28 records</span></div>
                </div>
              </div>
            </div>
            <div class="lp4-finding-card">
              <div class="lp4-finding-head"><span>${t.findingLabel}</span><small>FIN-014</small></div>
              <h3>${t.findingTitle}</h3><p>${t.findingText}</p>
              <div class="lp4-impact"><span>${t.impact}</span><strong>€18,400</strong></div>
            </div>
          </div>
        </div>
      </section>
      <section class="lp4-trust-strip" aria-label="BCSentinel capabilities">
        <div class="lp4-container lp4-trust-inner"><span>${t.trust1}</span><span>${t.trust2}</span><span>${t.trust3}</span><span>${t.trust4}</span></div>
      </section>`;
  }

  function loadStyles() {
    if (document.querySelector('link[data-lp4-hero]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "css/hero-conversion-core.css";
    link.dataset.lp4Hero = "true";
    document.head.appendChild(link);
  }

  function render() {
    if (!/\/(?:index\.html)?$/.test(location.pathname)) return;
    const main = document.querySelector("main#top, main");
    if (!main) return;
    const oldHero = main.querySelector("section.hero") || main.querySelector("section.lp4-hero");
    const existingTrust = main.querySelector("section.lp4-trust-strip");
    if (existingTrust) existingTrust.remove();
    const wrapper = document.createElement("div");
    wrapper.innerHTML = heroMarkup(copy[language()]).trim();
    const hero = wrapper.firstElementChild;
    const trust = wrapper.lastElementChild;
    if (oldHero) oldHero.replaceWith(hero); else main.prepend(hero);
    hero.insertAdjacentElement("afterend", trust);
    main.id = "main";

    const navActions = document.querySelector(".site-header .nav-actions");
    if (navActions && !navActions.querySelector(".lp4-header-cta")) {
      const cta = document.createElement("a");
      cta.className = "lp4-header-cta";
      cta.href = "#pricing";
      cta.textContent = copy[language()].headerCta;
      navActions.prepend(cta);
    } else if (navActions) {
      navActions.querySelector(".lp4-header-cta").textContent = copy[language()].headerCta;
    }
  }

  function init() {
    if (!/\/(?:index\.html)?$/.test(location.pathname)) return;
    loadStyles();
    render();
    window.setTimeout(render, 120);
    window.setTimeout(render, 600);
    const languageObserver = new MutationObserver((mutations) => {
      if (mutations.some((item) => item.attributeName === "lang")) render();
    });
    languageObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
