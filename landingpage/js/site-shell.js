(function () {
  const LANG_KEY = "bcsentinel-lang";
  const THEME_KEY = "bcsentinel-theme";
  const SUPPORTED_LANGS = ["de", "en"];
  const ROOT = "/";

  const pageNav = {
    index: [["#problem", "nav_problem"], ["#solution", "nav_solution"], ["#pricing", "nav_pricing"], ["#security", "nav_security"], ["/partner-register.html", "nav_partners"], ["#faq", "nav_faq"]],
    "loss-examples": [["#summary", "nav_summary"], ["#formula", "nav_formula"], ["#top5", "nav_top5"], ["#all-checks", "nav_all"], ["#loss-cta", "nav_cta_short"]],
    docs: [["#getting-started", "nav_getting_started"], ["#setup", "nav_setup"], ["#screenshots", "nav_screenshots"], ["#videos", "nav_videos"], ["#troubleshooting", "nav_troubleshooting"], ["#docs-faq", "nav_faq"]],
    security: [["#privacy-principles", "nav_privacy_principles"], ["#tokens-access", "nav_tokens_access"], ["#tenant-isolation", "nav_tenant_isolation"], ["#audit-monitoring", "nav_audit_monitoring"], ["#responsible-disclosure", "nav_responsible_disclosure"]],
    terms: [["#usage", "nav_usage"], ["#licenses", "nav_licenses"], ["#payments", "nav_payments"], ["#customer-data", "nav_customer_data"], ["#liability", "nav_liability"], ["#termination", "nav_termination"]],
    privacy: [], contact: [], impressum: [], help: [], support: [],
    "partner-login": [["#partner-login", "partner_login_nav"], ["/partner-register.html", "partner_register_nav"]],
    "partner-register": [["#partner-register", "partner_register_nav"], ["/partner-login.html", "partner_login_nav"]],
    "partner-reset-password": [["#partner-reset", "partner_reset_nav"], ["/partner-login.html", "partner_login_nav"]],
    "partner-portal": [["#overview", "menu_overview"], ["#profile", "menu_profile"]],
  };

  let translations = {};

  function pageKey() {
    return ((location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "")) || "index";
  }

  function currentLang() {
    try {
      const saved = localStorage.getItem(LANG_KEY);
      if (SUPPORTED_LANGS.includes(saved)) return saved;
    } catch (_) {}
    return (navigator.language || "").toLowerCase().startsWith("de") ? "de" : "en";
  }

  function currentTheme() {
    try {
      const saved = localStorage.getItem(THEME_KEY);
      if (saved === "light" || saved === "dark") return saved;
    } catch (_) {}
    return "light";
  }

  function t(key) {
    const lang = document.documentElement.lang || currentLang();
    return translations[lang]?.[key] ?? key;
  }

  function footerCopy() {
    const de = (document.documentElement.lang || currentLang()) === "de";
    return de ? {
      claim: "Data Quality & Business Impact für Microsoft Dynamics 365 Business Central.",
      note: "Datenprobleme erkennen, finanzielle Auswirkungen verstehen und Verbesserungen dauerhaft sichtbar machen.",
      product: "Produkt", resources: "Ressourcen", company: "Unternehmen",
      home: "Startseite", pricing: "Produkte & Preise", loss: "Estimated Loss", docs: "Dokumentation", security: "Sicherheit",
      privacy: "Datenschutz", contact: "Kontakt", legal: "Impressum", terms: "Nutzungsbedingungen", partner: "Partner werden", login: "Partner-Login",
      rights: "Alle Rechte vorbehalten.", lifecycle: "Assessment · Validation · Monitoring"
    } : {
      claim: "Data Quality & Business Impact for Microsoft Dynamics 365 Business Central.",
      note: "Detect data issues, understand financial impact, and keep improvements visible over time.",
      product: "Product", resources: "Resources", company: "Company",
      home: "Home", pricing: "Products & pricing", loss: "Estimated Loss", docs: "Documentation", security: "Security",
      privacy: "Privacy", contact: "Contact", legal: "Legal notice", terms: "Terms", partner: "Become a partner", login: "Partner login",
      rights: "All rights reserved.", lifecycle: "Assessment · Validation · Monitoring"
    };
  }

  function exposeI18n() {
    window.BCSentinelI18n = { lang: () => document.documentElement.lang || currentLang(), t, translations };
  }

  function injectShellStyles() {
    if (document.getElementById("site-shell-styles")) return;
    const style = document.createElement("style");
    style.id = "site-shell-styles";
    style.textContent = `
      .sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
      .site-header{position:sticky!important;top:0!important;z-index:1000!important;backdrop-filter:blur(18px)!important;-webkit-backdrop-filter:blur(18px)!important;background:rgba(7,14,26,.76)!important;border-bottom:1px solid rgba(255,255,255,.07)!important;box-shadow:0 12px 34px rgba(0,0,0,.16)!important}
      html[data-theme="light"] .site-header{background:rgba(255,255,255,.94)!important;border-bottom-color:rgba(19,35,63,.08)!important;box-shadow:0 8px 24px rgba(16,38,74,.045)!important}
      .site-header .nav{width:min(calc(100% - 32px),1180px)!important;margin:auto!important;min-height:64px!important;display:grid!important;grid-template-columns:auto 1fr auto!important;align-items:center!important;gap:22px!important}
      .site-header .brand,.site-footer .footer-brand{display:inline-flex!important;align-items:center!important;gap:10px!important;text-decoration:none!important;color:inherit!important}
      .site-header .brand-mark,.site-footer .brand-mark{width:42px!important;height:42px!important;display:grid!important;place-items:center!important;flex:0 0 auto!important}
      .site-header .brand-mark img,.site-footer .brand-mark img{width:42px!important;height:42px!important;object-fit:contain!important}
      .site-header .brand-copy,.site-footer .brand-copy{display:flex!important;flex-direction:column!important;line-height:1.1!important}
      .site-header .brand-copy strong,.site-footer .brand-copy strong{font-size:1rem!important;font-weight:800!important;color:var(--text,#eff4ff)!important}
      .site-header .brand-copy span,.site-footer .brand-copy span{margin-top:3px!important;color:var(--muted-2,#7f91b3)!important;font-size:.78rem!important}
      html[data-theme="light"] .site-header .brand-copy strong{color:#10213d!important}html[data-theme="light"] .site-header .brand-copy span{color:#55709f!important}
      .site-header .desktop-nav,.site-header .nav-actions{display:flex!important;align-items:center!important}.site-header .desktop-nav{justify-content:flex-end!important;gap:20px!important}.site-header .nav-actions{gap:12px!important}
      .site-header .desktop-nav a{color:var(--muted,#aebbd7)!important;font-size:.92rem!important;font-weight:600!important;text-decoration:none!important;white-space:nowrap!important}html[data-theme="light"] .site-header .desktop-nav a{color:#31486f!important}
      .site-header .lang-switch{display:inline-flex!important;gap:12px!important}.site-header .lang-btn{display:inline-flex!important;align-items:center!important;gap:6px!important;border:0!important;background:transparent!important;color:var(--muted,#aebbd7)!important;font-weight:700!important;cursor:pointer!important}.site-header .lang-btn.active{opacity:.62!important}
      .site-header .lang-flag{width:20px!important;height:20px!important;border-radius:50%!important;border:1px solid rgba(12,33,66,.12)!important;overflow:hidden!important}.site-header .flag-de{background:linear-gradient(180deg,#111 0 33%,#d00 33% 66%,#ffce00 66% 100%)!important}.site-header .flag-en{background:#012169!important}
      .site-header .theme-toggle,.site-header .nav-toggle{width:44px!important;height:44px!important;border-radius:999px!important;border:1px solid rgba(255,255,255,.12)!important;background:rgba(255,255,255,.05)!important;color:inherit!important;cursor:pointer!important}.site-header .theme-toggle-icon{font-size:15px!important}.site-header .nav-toggle{display:none!important}.site-header .nav-toggle span{display:block!important;width:18px!important;height:2px!important;margin:4px auto!important;background:currentColor!important}
      html[data-theme="light"] .site-header .theme-toggle,html[data-theme="light"] .site-header .nav-toggle{background:#fff!important;border-color:rgba(49,72,115,.16)!important;color:#18284a!important}
      .site-header .mobile-menu{display:none!important;border-top:1px solid rgba(255,255,255,.06)!important}.site-header .mobile-menu.open{display:block!important}.site-header .mobile-menu-inner{width:min(calc(100% - 32px),1180px)!important;margin:auto!important;display:grid!important;gap:14px!important;padding:16px 0 22px!important}.site-header .mobile-menu a{color:var(--muted,#aebbd7)!important;text-decoration:none!important;font-weight:650!important}
      .site-footer{padding:64px 0 24px!important;background:#071426!important;color:#eef4ff!important;border-top:1px solid rgba(255,255,255,.08)!important}.site-footer .footer-container{width:min(calc(100% - 40px),1180px)!important;margin:auto!important}.site-footer .footer-grid{display:grid!important;grid-template-columns:minmax(240px,1.45fr) repeat(3,minmax(150px,1fr))!important;gap:42px!important}.site-footer .footer-brand-block p{max-width:360px!important;margin:14px 0 0!important;color:#aebbd0!important;line-height:1.65!important}.site-footer .footer-brand-block .footer-note{font-size:.9rem!important;color:#8191ad!important}.site-footer h2{margin:0 0 16px!important;font-size:.82rem!important;letter-spacing:.1em!important;text-transform:uppercase!important;color:#fff!important}.site-footer nav{display:grid!important;gap:11px!important}.site-footer nav a{color:#aebbd0!important;text-decoration:none!important;font-size:.94rem!important}.site-footer nav a:hover{color:#fff!important}.site-footer .footer-bottom{display:flex!important;justify-content:space-between!important;gap:20px!important;margin-top:44px!important;padding-top:20px!important;border-top:1px solid rgba(255,255,255,.09)!important;color:#8191ad!important;font-size:.86rem!important}
      .site-header a:focus-visible,.site-header button:focus-visible,.site-footer a:focus-visible{outline:3px solid rgba(242,122,43,.45)!important;outline-offset:4px!important}
      @media(max-width:1160px){.site-header .desktop-nav{display:none!important}.site-header .nav-toggle{display:inline-block!important}.site-header .nav-actions{margin-left:auto!important}.site-footer .footer-grid{grid-template-columns:1.4fr repeat(2,1fr)!important}.site-footer .footer-grid>div:last-child{grid-column:2/4!important}}
      @media(max-width:760px){.site-header .brand-copy span{display:none!important}.site-footer{padding-top:48px!important}.site-footer .footer-container{width:min(calc(100% - 28px),1180px)!important}.site-footer .footer-grid{grid-template-columns:1fr 1fr!important;gap:32px 22px!important}.site-footer .footer-brand-block{grid-column:1/-1!important}.site-footer .footer-grid>div:last-child{grid-column:auto!important}.site-footer .footer-bottom{flex-direction:column!important}}
      @media(max-width:480px){.site-footer .footer-grid{grid-template-columns:1fr!important}.site-footer .footer-brand-block,.site-footer .footer-grid>div:last-child{grid-column:auto!important}}
    `;
    document.head.appendChild(style);
  }

  function buildHeader() {
    const nav = pageNav[pageKey()] || pageNav.index;
    const links = nav.map(([href, label]) => `<a href="${href}" data-i18n="${label}">${t(label)}</a>`).join("");
    return `<header class="site-header"><div class="nav"><a class="brand" href="/index.html#top" aria-label="BCSentinel home"><span class="brand-mark"><img src="/logo-bcsentinel.png" alt="BCSentinel Logo"></span><span class="brand-copy"><strong>BCSentinel</strong><span data-i18n="brand_header_claim">${t("brand_header_claim")}</span></span></a><nav class="desktop-nav" aria-label="Primary navigation">${links}</nav><div class="nav-actions"><div class="lang-switch" aria-label="Language switcher"><button class="lang-btn" data-lang="de" type="button"><span class="lang-flag flag-de" aria-hidden="true"></span><span>DE</span></button><button class="lang-btn" data-lang="en" type="button"><span class="lang-flag flag-en" aria-hidden="true"></span><span>EN</span></button></div><button class="theme-toggle" id="themeToggle" type="button"><span class="theme-toggle-icon" aria-hidden="true">☾</span><span class="theme-toggle-label sr-only">${t("theme_toggle_dark")}</span></button><button aria-controls="mobileMenu" aria-expanded="false" aria-label="Open menu" class="nav-toggle" id="navToggle" type="button"><span></span><span></span><span></span></button></div></div><div class="mobile-menu" id="mobileMenu"><div class="mobile-menu-inner">${links}</div></div></header>`;
  }

  function buildFooter() {
    const c = footerCopy();
    return `<footer class="site-footer"><div class="footer-container"><div class="footer-grid"><div class="footer-brand-block"><a class="footer-brand" href="/index.html#top" aria-label="BCSentinel home"><span class="brand-mark"><img src="/logo-bcsentinel.png" alt="BCSentinel Logo"></span><span class="brand-copy"><strong>BCSentinel</strong></span></a><p>${c.claim}</p><p class="footer-note">${c.note}</p></div><div><h2>${c.product}</h2><nav><a href="/index.html">${c.home}</a><a href="/index.html#pricing">${c.pricing}</a><a href="/loss-examples.html">${c.loss}</a></nav></div><div><h2>${c.resources}</h2><nav><a href="/docs.html">${c.docs}</a><a href="/help.html">Help</a><a href="/support.html">Support</a><a href="/security.html">${c.security}</a><a href="/privacy.html">${c.privacy}</a></nav></div><div><h2>${c.company}</h2><nav><a href="/contact.html">${c.contact}</a><a href="/impressum.html">${c.legal}</a><a href="/terms.html">${c.terms}</a><a href="/partner-register.html">${c.partner}</a><a href="/partner-login.html">${c.login}</a></nav></div></div><div class="footer-bottom"><span>© ${new Date().getFullYear()} BCSentinel. ${c.rights}</span><span>${c.lifecycle}</span></div></div></footer>`;
  }

  function ensureShell() {
    document.querySelectorAll("header.site-header").forEach((el, i) => { if (i) el.remove(); });
    const header = document.querySelector("header.site-header");
    if (header) header.outerHTML = buildHeader(); else document.body.insertAdjacentHTML("afterbegin", buildHeader());
    document.querySelectorAll("footer.site-footer, footer.lp9-footer").forEach((el) => el.remove());
    document.body.insertAdjacentHTML("beforeend", buildFooter());
  }

  function applyTranslations(lang) {
    const selected = SUPPORTED_LANGS.includes(lang) ? lang : "en";
    document.documentElement.lang = selected;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const key = el.dataset.i18n; if (translations[selected]?.[key] !== undefined) el.textContent = translations[selected][key]; });
    document.querySelectorAll(".lang-btn").forEach((btn) => { const active = btn.dataset.lang === selected; btn.classList.toggle("active", active); btn.setAttribute("aria-pressed", active ? "true" : "false"); });
    try { localStorage.setItem(LANG_KEY, selected); } catch (_) {}
    exposeI18n();
    const footer = document.querySelector("footer.site-footer");
    if (footer) footer.outerHTML = buildFooter();
    updateThemeToggle();
  }

  function applyTheme(theme) {
    const selected = theme === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = selected;
    try { localStorage.setItem(THEME_KEY, selected); } catch (_) {}
    updateThemeToggle();
  }

  function updateThemeToggle() {
    const dark = (document.documentElement.dataset.theme || currentTheme()) === "dark";
    document.querySelectorAll(".theme-toggle").forEach((btn) => { const icon = btn.querySelector(".theme-toggle-icon"); const label = btn.querySelector(".theme-toggle-label"); if (icon) icon.textContent = dark ? "☀" : "☾"; if (label) label.textContent = t(dark ? "theme_toggle_light" : "theme_toggle_dark"); });
  }

  async function loadTranslations() {
    const [de, en] = await Promise.all(SUPPORTED_LANGS.map((lang) => fetch(`${ROOT}lang/${lang}.json`, { cache: "no-cache" }).then((r) => r.ok ? r.json() : {}).catch(() => ({}))));
    translations = { de, en };
    exposeI18n();
  }

  function bindControls() {
    document.addEventListener("click", (event) => {
      const langButton = event.target.closest(".lang-btn");
      if (langButton) return applyTranslations(langButton.dataset.lang);
      if (event.target.closest(".theme-toggle")) return applyTheme((document.documentElement.dataset.theme || currentTheme()) === "light" ? "dark" : "light");
      const navToggle = event.target.closest(".nav-toggle");
      if (navToggle) { const menu = document.getElementById("mobileMenu"); const open = menu?.classList.toggle("open") || false; navToggle.setAttribute("aria-expanded", open ? "true" : "false"); return; }
      if (event.target.closest(".mobile-menu a")) { document.getElementById("mobileMenu")?.classList.remove("open"); document.getElementById("navToggle")?.setAttribute("aria-expanded", "false"); }
    });
  }

  document.addEventListener("DOMContentLoaded", async () => {
    await loadTranslations();
    injectShellStyles();
    ensureShell();
    bindControls();
    applyTheme(currentTheme());
    applyTranslations(currentLang());
  });
})();