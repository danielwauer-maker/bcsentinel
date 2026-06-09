(function () {
  const LANG_KEY = "bcsentinel-lang";
  const THEME_KEY = "bcsentinel-theme";
  const SUPPORTED_LANGS = ["de", "en"];
  const ROOT = "/";

  const pageNav = {
    "index": [
      ["#problem", "nav_problem"],
      ["#solution", "nav_solution"],
      ["#pricing", "nav_free_vs_premium"],
      ["#security", "nav_security"],
      ["#faq", "nav_faq"],
    ],
    "loss-examples": [
      ["#summary", "nav_summary"],
      ["#formula", "nav_formula"],
      ["#top5", "nav_top5"],
      ["#all-checks", "nav_all"],
      ["#loss-cta", "nav_cta_short"],
    ],
    "docs": [
      ["#overview", "nav_overview"],
      ["#getting-started", "nav_getting_started"],
      ["#setup", "nav_setup"],
      ["#screenshots", "nav_screenshots"],
      ["#videos", "nav_videos"],
      ["#troubleshooting", "nav_troubleshooting"],
      ["#docs-faq", "nav_faq"],
    ],
    "security": [
      ["#overview", "nav_overview"],
      ["#privacy-principles", "nav_privacy_principles"],
      ["#tokens-access", "nav_tokens_access"],
      ["#tenant-isolation", "nav_tenant_isolation"],
      ["#audit-monitoring", "nav_audit_monitoring"],
      ["#responsible-disclosure", "nav_responsible_disclosure"],
    ],
    "terms": [
      ["#overview", "nav_overview"],
      ["#usage", "nav_usage"],
      ["#licenses", "nav_licenses"],
      ["#payments", "nav_payments"],
      ["#customer-data", "nav_customer_data"],
      ["#liability", "nav_liability"],
      ["#termination", "nav_termination"],
    ],
    "privacy": [
      ["#overview", "nav_overview"],
      ["#processed-data", "nav_processed_data"],
      ["#purposes", "nav_purposes"],
      ["#legal-basis", "nav_legal_basis"],
      ["#retention", "nav_retention"],
      ["#rights", "nav_rights"],
      ["#contact", "nav_contact"],
    ],
    "contact": [
      ["#contact-form", "nav_contact_form"],
      ["#direct-contact", "nav_direct_contact"],
      ["#topics", "nav_topics"],
      ["#response-times", "nav_response_times"],
    ],
    "impressum": [
      ["#provider", "nav_provider"],
      ["#contact", "nav_contact"],
      ["#legal-info", "nav_legal_info"],
    ],
    "help": [
      ["#overview", "nav_overview"],
      ["#docs-link", "footer_docs"],
      ["#support-link", "footer_contact"],
    ],
    "support": [
      ["#overview", "nav_overview"],
      ["#contact-link", "footer_contact"],
      ["#docs-link", "footer_docs"],
    ],
    "partner-login": [
      ["#partner-login", "partner_login_nav"],
      ["/partner-register.html", "partner_register_nav"],
    ],
    "partner-register": [
      ["#partner-register", "partner_register_nav"],
      ["/partner-login.html", "partner_login_nav"],
    ],
    "partner-reset-password": [
      ["#partner-reset", "partner_reset_nav"],
      ["/partner-login.html", "partner_login_nav"],
    ],
    "partner-portal": [
      ["#overview", "menu_overview"],
      ["#profile", "menu_profile"],
    ],
  };

  const footerLinks = [
    ["/index.html", "footer_home"],
    ["/docs.html", "footer_docs"],
    ["/security.html", "footer_security"],
    ["/privacy.html", "footer_privacy"],
    ["/terms.html", "footer_terms"],
    ["/contact.html", "footer_contact"],
    ["/impressum.html", "footer_legal"],
    ["/loss-examples.html", "footer_loss_examples"],
  ];

  let translations = {};

  function pageKey() {
    const name = (window.location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "");
    return name || "index";
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
    return "dark";
  }

  function t(key) {
    const lang = document.documentElement.lang || currentLang();
    return (translations[lang] && translations[lang][key]) || key;
  }

  function injectShellStyles() {
    if (document.getElementById("site-shell-styles")) return;
    const style = document.createElement("style");
    style.id = "site-shell-styles";
    style.textContent = `
      .site-header{position:sticky!important;top:0!important;z-index:100!important;backdrop-filter:blur(16px)!important;background:linear-gradient(180deg,rgba(6,13,24,.9),rgba(6,13,24,.5))!important;border-bottom:1px solid rgba(255,255,255,.05)!important}
      html[data-theme="light"] .site-header{background:linear-gradient(180deg,rgba(255,255,255,.9),rgba(255,255,255,.72))!important;border-bottom-color:rgba(19,35,63,.08)!important}
      .site-header .nav{min-height:82px!important;display:grid!important;grid-template-columns:minmax(230px,1fr) auto minmax(190px,1fr)!important;align-items:center!important;gap:22px!important}
      .site-header .brand,.site-footer .brand{display:flex!important;align-items:center!important;gap:14px!important;min-width:0!important;text-decoration:none!important;color:inherit!important}
      .site-header .brand-mark,.site-footer .brand-mark{width:48px!important;height:48px!important;display:grid!important;place-items:center!important;border-radius:16px!important;overflow:hidden!important;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02))!important;border:1px solid rgba(255,255,255,.08)!important;box-shadow:0 12px 34px rgba(0,0,0,.22)!important;flex:0 0 auto!important}
      .site-header .brand-mark img,.site-footer .brand-mark img{width:82%!important;height:82%!important;object-fit:contain!important}
      .site-header .brand-copy,.site-footer .brand-copy{display:flex!important;flex-direction:column!important;min-width:0!important}
      .site-header .brand-copy strong,.site-footer .brand-copy strong{font-size:1.04rem!important;font-weight:800!important;color:var(--text,#eff4ff)!important;line-height:1.2!important}
      .site-header .brand-copy span,.site-footer .brand-copy span{color:var(--muted-2,#7f91b3)!important;font-size:.84rem!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
      .site-header .desktop-nav,.site-header .nav-actions{display:flex!important;align-items:center!important;gap:16px!important}
      .site-header .desktop-nav{justify-content:center!important;flex-wrap:wrap!important}
      .site-header .nav-actions{justify-content:flex-end!important}
      .site-header .desktop-nav a{color:var(--muted,#aebbd7)!important;font-size:.95rem!important;line-height:1!important;white-space:nowrap!important;text-decoration:none!important}
      .site-header .desktop-nav a:hover,.site-footer .footer-links a:hover{color:var(--text,#eff4ff)!important;text-decoration:none!important}
      .site-header .lang-switch{display:inline-flex!important;align-items:center!important;gap:4px!important;padding:4px!important;border-radius:999px!important;background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.08)!important;min-width:0!important;min-height:0!important;overflow:visible!important}
      .site-header .lang-btn{display:inline-flex!important;align-items:center!important;gap:6px!important;min-width:58px!important;min-height:36px!important;padding:8px 10px!important;border:0!important;border-radius:999px!important;background:transparent!important;color:var(--muted,#aebbd7)!important;cursor:pointer!important;font-weight:700!important;font-size:.88rem!important;line-height:1!important}
      .site-header .lang-btn.active{display:inline-flex!important;color:#fff!important;background:linear-gradient(135deg,rgba(74,141,255,.22),rgba(255,143,61,.18))!important}
      .site-header .lang-flag{display:inline-grid!important;place-items:center!important;width:20px!important;height:20px!important;border-radius:50%!important;border:1px solid rgba(255,255,255,.12)!important;overflow:hidden!important;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)!important}
      .site-header .flag-de{background:linear-gradient(180deg,#111 0 33%,#d00 33% 66%,#ffce00 66% 100%)!important}
      .site-header .flag-en{background:linear-gradient(90deg,transparent 42%,#fff 42% 58%,transparent 58%),linear-gradient(0deg,transparent 42%,#fff 42% 58%,transparent 58%),linear-gradient(90deg,transparent 46%,#c8102e 46% 54%,transparent 54%),linear-gradient(0deg,transparent 46%,#c8102e 46% 54%,transparent 54%),linear-gradient(135deg,transparent 0 42%,#fff 42% 49%,#c8102e 49% 53%,#fff 53% 60%,transparent 60%),linear-gradient(45deg,transparent 0 42%,#fff 42% 49%,#c8102e 49% 53%,#fff 53% 60%,transparent 60%),#012169!important}
      .site-header .theme-toggle{display:inline-flex!important;align-items:center!important;justify-content:center!important;min-width:46px!important;min-height:46px!important;padding:10px!important;border-radius:999px!important;border:1px solid var(--line-strong,rgba(255,255,255,.14))!important;background:rgba(255,255,255,.03)!important;color:var(--text,#eff4ff)!important;cursor:pointer!important}
      .site-header .theme-toggle-icon{display:inline-grid!important;place-items:center!important;width:24px!important;height:24px!important;border-radius:50%!important;background:linear-gradient(135deg,rgba(74,141,255,.18),rgba(255,143,61,.18))!important;font-size:.88rem!important}
      .site-header .nav-toggle{display:none!important;width:48px!important;height:48px!important;border-radius:14px!important;border:1px solid rgba(255,255,255,.08)!important;background:rgba(255,255,255,.04)!important;cursor:pointer!important}
      .site-header .nav-toggle span{display:block!important;width:18px!important;height:2px!important;margin:4px auto!important;background:var(--text,#eff4ff)!important;border-radius:999px!important}
      .site-header .mobile-menu{display:none!important;border-top:1px solid rgba(255,255,255,.05)!important}
      .site-header .mobile-menu.open{display:block!important}
      .site-header .mobile-menu-inner{display:grid!important;gap:14px!important;padding:18px 0 22px!important}
      .site-header .mobile-menu a{color:var(--muted,#aebbd7)!important;text-decoration:none!important}
      .site-footer{padding:28px 0!important;border-top:1px solid rgba(255,255,255,.05)!important}
      .site-footer .footer-inner{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:18px!important;flex-wrap:wrap!important}
      .site-footer .footer-links{display:flex!important;gap:18px!important;flex-wrap:wrap!important}
      .site-footer .footer-links a{color:var(--muted-2,#7f91b3)!important;font-size:.94rem!important;text-decoration:none!important;white-space:nowrap!important}
      @media(max-width:1160px){.site-header .nav{grid-template-columns:minmax(0,1fr) auto!important}.site-header .desktop-nav{display:none!important}.site-header .nav-toggle{display:inline-block!important}.site-header .nav-actions{margin-left:auto!important}}
      @media(max-width:680px){.site-header .brand-copy span{display:none!important}.site-header .lang-btn{min-width:48px!important;padding:8px!important}.site-footer .footer-inner{align-items:flex-start!important;flex-direction:column!important}}
    `;
    document.head.appendChild(style);
  }

  function buildHeader() {
    const key = pageKey();
    const nav = pageNav[key] || pageNav.index;
    const links = nav.map(([href, label]) => `<a href="${href}" data-i18n="${label}">${t(label)}</a>`).join("");
    const mobileLinks = nav.map(([href, label]) => `<a href="${href}" data-i18n="${label}">${t(label)}</a>`).join("");
    return `
      <header class="site-header">
        <div class="container nav">
          <a class="brand" href="/index.html#top" aria-label="BCSentinel home">
            <span class="brand-mark"><img src="/logo-bcsentinel.png" alt="BCSentinel Logo" /></span>
            <span class="brand-copy"><strong>BCSentinel</strong><span data-i18n="brand_header_claim">${t("brand_header_claim")}</span></span>
          </a>
          <nav class="nav-links desktop-nav" aria-label="Primary navigation">${links}</nav>
          <div class="nav-actions">
            <div class="lang-switch" aria-label="Language switcher">
              <button class="lang-btn" data-lang="de" type="button" data-i18n-title="lang_de_title" data-i18n-aria-label="lang_de_label"><span class="lang-flag flag-de" aria-hidden="true"></span><span>DE</span></button>
              <button class="lang-btn" data-lang="en" type="button" data-i18n-title="lang_en_title" data-i18n-aria-label="lang_en_label"><span class="lang-flag flag-en" aria-hidden="true"></span><span>EN</span></button>
            </div>
            <button class="theme-toggle" id="themeToggle" type="button" data-i18n-aria-label="theme_toggle_aria">
              <span class="theme-toggle-icon" aria-hidden="true">◐</span>
              <span class="theme-toggle-label sr-only" data-i18n="theme_toggle_dark">${t("theme_toggle_dark")}</span>
            </button>
            <button aria-controls="mobileMenu" aria-expanded="false" aria-label="Open menu" class="nav-toggle" id="navToggle" type="button">
              <span></span><span></span><span></span>
            </button>
          </div>
        </div>
        <div class="mobile-menu" id="mobileMenu">
          <div class="container mobile-menu-inner">
            ${mobileLinks}
          </div>
        </div>
      </header>`;
  }

  function buildFooter() {
    const links = footerLinks.map(([href, label]) => `<a href="${href}" data-i18n="${label}">${t(label)}</a>`).join("");
    return `
      <footer class="site-footer">
        <div class="container footer-inner">
          <a class="brand footer-brand" href="/index.html#top" aria-label="BCSentinel home">
            <span class="brand-mark"><img src="/logo-bcsentinel.png" alt="BCSentinel Logo" /></span>
            <span class="brand-copy"><strong>BCSentinel</strong><span data-i18n="footer_claim">${t("footer_claim")}</span></span>
          </a>
          <div class="footer-links">${links}</div>
        </div>
      </footer>`;
  }

  function ensureShell() {
    const header = document.querySelector("header.site-header");
    if (header) header.outerHTML = buildHeader();
    else document.body.insertAdjacentHTML("afterbegin", buildHeader());

    const footer = document.querySelector("footer.site-footer");
    if (footer) footer.outerHTML = buildFooter();
    else document.body.insertAdjacentHTML("beforeend", buildFooter());
  }

  function applyTranslations(lang) {
    const selected = SUPPORTED_LANGS.includes(lang) ? lang : "en";
    document.documentElement.lang = selected;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (translations[selected] && translations[selected][key] !== undefined) {
        el.textContent = translations[selected][key];
      }
    });
    [
      ["data-i18n-placeholder", "placeholder"],
      ["data-i18n-title", "title"],
      ["data-i18n-aria-label", "aria-label"],
      ["data-i18n-content", "content"],
    ].forEach(([attr, target]) => {
      document.querySelectorAll(`[${attr}]`).forEach((el) => {
        const key = el.getAttribute(attr);
        if (translations[selected] && translations[selected][key] !== undefined) {
          el.setAttribute(target, translations[selected][key]);
        }
      });
    });
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      const active = btn.dataset.lang === selected;
      btn.classList.toggle("active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
    try { localStorage.setItem(LANG_KEY, selected); } catch (_) {}
    updateThemeToggle();
  }

  function applyTheme(theme) {
    const selected = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", selected);
    try { localStorage.setItem(THEME_KEY, selected); } catch (_) {}
    updateThemeToggle();
  }

  function updateThemeToggle() {
    const theme = document.documentElement.getAttribute("data-theme") || currentTheme();
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
      const icon = btn.querySelector(".theme-toggle-icon");
      const label = btn.querySelector(".theme-toggle-label");
      if (icon) icon.textContent = theme === "dark" ? "◐" : "○";
      if (label) label.textContent = theme === "dark" ? t("theme_toggle_light") : t("theme_toggle_dark");
    });
  }

  async function loadTranslations() {
    const [de, en] = await Promise.all(
      SUPPORTED_LANGS.map((lang) =>
        fetch(`${ROOT}lang/${lang}.json`, { cache: "no-cache" })
          .then((response) => response.ok ? response.json() : {})
          .catch(() => ({}))
      )
    );
    translations = { de, en };
  }

  function bindControls() {
    document.addEventListener("click", (event) => {
      const langButton = event.target.closest(".lang-btn");
      if (langButton) {
        applyTranslations(langButton.dataset.lang);
        return;
      }
      const themeButton = event.target.closest(".theme-toggle");
      if (themeButton) {
        applyTheme((document.documentElement.getAttribute("data-theme") || currentTheme()) === "light" ? "dark" : "light");
        return;
      }
      const navToggle = event.target.closest(".nav-toggle");
      if (navToggle) {
        const menu = document.getElementById("mobileMenu");
        const isOpen = menu ? menu.classList.toggle("open") : false;
        navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        return;
      }
      if (event.target.closest(".mobile-menu a")) {
        const menu = document.getElementById("mobileMenu");
        const navToggle = document.getElementById("navToggle");
        if (menu) menu.classList.remove("open");
        if (navToggle) navToggle.setAttribute("aria-expanded", "false");
      }
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
