(function () {
  const LANG_KEY = "bcsentinel-lang";
  const THEME_KEY = "bcsentinel-theme";
  const SUPPORTED_LANGS = ["de", "en"];
  const ROOT = "/";

  const pageNav = {
    "index": [
      ["#problem", "nav_problem"],
      ["#solution", "nav_solution"],
      ["#pricing", "nav_pricing"],
      ["#security", "nav_security"],
      ["/partner-register.html", "nav_partners"],
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
      ["#getting-started", "nav_getting_started"],
      ["#setup", "nav_setup"],
      ["#screenshots", "nav_screenshots"],
      ["#videos", "nav_videos"],
      ["#troubleshooting", "nav_troubleshooting"],
      ["#docs-faq", "nav_faq"],
    ],
    "security": [
      ["#privacy-principles", "nav_privacy_principles"],
      ["#tokens-access", "nav_tokens_access"],
      ["#tenant-isolation", "nav_tenant_isolation"],
      ["#audit-monitoring", "nav_audit_monitoring"],
      ["#responsible-disclosure", "nav_responsible_disclosure"],
    ],
    "terms": [
      ["#usage", "nav_usage"],
      ["#licenses", "nav_licenses"],
      ["#payments", "nav_payments"],
      ["#customer-data", "nav_customer_data"],
      ["#liability", "nav_liability"],
      ["#termination", "nav_termination"],
    ],
    "privacy": [
    ],
    "contact": [
    ],
    "impressum": [
    ],
    "help": [
    ],
    "support": [
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
    return "light";
  }

  function t(key) {
    const lang = document.documentElement.lang || currentLang();
    return (translations[lang] && translations[lang][key]) || key;
  }

  function exposeI18n() {
    window.BCSentinelI18n = {
      lang: () => document.documentElement.lang || currentLang(),
      t: (key) => t(key),
      translations,
    };
  }

  function injectShellStyles() {
    if (document.getElementById("site-shell-styles")) return;
    const style = document.createElement("style");
    style.id = "site-shell-styles";
    style.textContent = `
      .sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
      .site-header{position:sticky!important;top:0!important;z-index:1000!important;backdrop-filter:blur(18px)!important;-webkit-backdrop-filter:blur(18px)!important;background:rgba(7,14,26,.76)!important;border-bottom:1px solid rgba(255,255,255,.07)!important;box-shadow:0 12px 34px rgba(0,0,0,.16)!important}
      html[data-theme="light"] .site-header{background:rgba(255,255,255,.94)!important;border-bottom:1px solid rgba(19,35,63,.08)!important;box-shadow:0 8px 24px rgba(16,38,74,.045)!important}
      .site-header .nav{width:min(calc(100% - 32px),1180px)!important;margin:0 auto!important;min-height:64px!important;padding:0!important;display:grid!important;grid-template-columns:auto 1fr auto!important;align-items:center!important;gap:22px!important}
      .site-header .brand,.site-footer .brand{display:inline-flex!important;align-items:center!important;gap:10px!important;min-width:0!important;text-decoration:none!important;color:inherit!important}
      .site-header .brand-mark{width:42px!important;height:42px!important;display:grid!important;place-items:center!important;border-radius:0!important;overflow:visible!important;background:transparent!important;border:0!important;box-shadow:none!important;flex:0 0 auto!important}
      .site-header .brand-mark img{width:42px!important;height:42px!important;object-fit:contain!important;filter:drop-shadow(0 6px 12px rgba(18,40,76,.10))!important}
      .site-footer .brand-mark{width:42px!important;height:42px!important;display:grid!important;place-items:center!important;border-radius:0!important;overflow:visible!important;background:transparent!important;border:0!important;box-shadow:none!important;flex:0 0 auto!important}
      .site-footer .brand-mark img{width:42px!important;height:42px!important;object-fit:contain!important}
      .site-header .brand-copy,.site-footer .brand-copy{display:flex!important;flex-direction:column!important;min-width:0!important;line-height:1.1!important}
      .site-header .brand-copy strong,.site-footer .brand-copy strong{font-size:1rem!important;font-weight:800!important;letter-spacing:-.02em!important;color:var(--text,#eff4ff)!important;line-height:1.1!important}
      .site-header .brand-copy span,.site-footer .brand-copy span{margin-top:3px!important;color:var(--muted-2,#7f91b3)!important;font-size:.78rem!important;font-weight:500!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;max-width:340px!important}
      html[data-theme="light"] .site-header .brand-copy strong{color:#10213d!important}
      html[data-theme="light"] .site-header .brand-copy span{color:#55709f!important}
      .site-header .desktop-nav,.site-header .nav-actions{display:flex!important;align-items:center!important}
      .site-header .desktop-nav{justify-content:flex-end!important;gap:20px!important;flex-wrap:nowrap!important}
      .site-header .nav-actions{justify-content:flex-end!important;gap:12px!important}
      .site-header .desktop-nav a{color:var(--muted,#aebbd7)!important;font-size:.92rem!important;font-weight:600!important;line-height:1!important;white-space:nowrap!important;text-decoration:none!important;transition:color .18s ease!important}
      html[data-theme="light"] .site-header .desktop-nav a{color:#31486f!important}
      .site-header .desktop-nav a:hover{color:var(--text,#eff4ff)!important;text-decoration:none!important}
      html[data-theme="light"] .site-header .desktop-nav a:hover{color:#102a5c!important}
      .site-header .lang-switch{display:inline-flex!important;align-items:center!important;gap:12px!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;min-width:0!important;min-height:0!important;overflow:visible!important}
      .site-header .lang-btn{display:inline-flex!important;align-items:center!important;gap:6px!important;min-width:auto!important;min-height:auto!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;color:var(--muted,#aebbd7)!important;cursor:pointer!important;font-weight:700!important;font-size:.84rem!important;line-height:1!important;opacity:1!important}
      html[data-theme="light"] .site-header .lang-btn{color:#36527f!important}
      .site-header .lang-btn.active{display:inline-flex!important;background:transparent!important;color:var(--text,#eff4ff)!important;opacity:.65!important}
      html[data-theme="light"] .site-header .lang-btn.active{color:#36527f!important;opacity:.65!important}
      .site-header .lang-flag{display:inline-grid!important;place-items:center!important;width:20px!important;height:20px!important;border-radius:50%!important;border:1px solid rgba(12,33,66,.12)!important;overflow:hidden!important;box-shadow:0 1px 4px rgba(14,35,72,.12)!important;flex:0 0 auto!important}
      .site-header .flag-de{background:linear-gradient(180deg,#111 0 33%,#d00 33% 66%,#ffce00 66% 100%)!important}
      .site-header .flag-en{background:linear-gradient(90deg,transparent 42%,#fff 42% 58%,transparent 58%),linear-gradient(0deg,transparent 42%,#fff 42% 58%,transparent 58%),linear-gradient(90deg,transparent 46%,#c8102e 46% 54%,transparent 54%),linear-gradient(0deg,transparent 46%,#c8102e 46% 54%,transparent 54%),linear-gradient(135deg,transparent 0 42%,#fff 42% 49%,#c8102e 49% 53%,#fff 53% 60%,transparent 60%),linear-gradient(45deg,transparent 0 42%,#fff 42% 49%,#c8102e 49% 53%,#fff 53% 60%,transparent 60%),#012169!important}
      .site-header .theme-toggle{display:inline-grid!important;place-items:center!important;width:44px!important;height:44px!important;min-width:44px!important;min-height:44px!important;padding:0!important;border-radius:999px!important;border:1px solid rgba(255,255,255,.12)!important;background:rgba(255,255,255,.05)!important;color:var(--text,#eff4ff)!important;box-shadow:0 8px 22px rgba(0,0,0,.14)!important;cursor:pointer!important}
      html[data-theme="light"] .site-header .theme-toggle{background:#fff!important;border:1px solid rgba(49,72,115,.16)!important;box-shadow:0 8px 22px rgba(16,38,74,.08)!important;color:#18284a!important}
      .site-header .theme-toggle-icon{display:inline-grid!important;place-items:center!important;width:26px!important;height:26px!important;border-radius:50%!important;background:rgba(255,255,255,.08)!important;font-size:15px!important;line-height:1!important}
      html[data-theme="light"] .site-header .theme-toggle-icon{background:#eef4ff!important;color:#18284a!important}
      .site-header .nav-toggle{display:none!important;width:44px!important;height:44px!important;border-radius:999px!important;border:1px solid rgba(255,255,255,.12)!important;background:rgba(255,255,255,.05)!important;cursor:pointer!important;padding:0!important}
      .site-header .nav-toggle span{display:block!important;width:18px!important;height:2px!important;margin:4px auto!important;background:var(--text,#eff4ff)!important;border-radius:999px!important}
      html[data-theme="light"] .site-header .nav-toggle{background:#fff!important;border-color:rgba(49,72,115,.16)!important;box-shadow:0 8px 22px rgba(16,38,74,.08)!important}
      html[data-theme="light"] .site-header .nav-toggle span{background:#18284a!important}
      .site-header .mobile-menu{display:none!important;border-top:1px solid rgba(255,255,255,.06)!important;background:inherit!important}
      .site-header .mobile-menu.open{display:block!important}
      .site-header .mobile-menu-inner{width:min(calc(100% - 32px),1180px)!important;margin:0 auto!important;display:grid!important;gap:14px!important;padding:16px 0 22px!important}
      .site-header .mobile-menu a{color:var(--muted,#aebbd7)!important;text-decoration:none!important;font-weight:650!important}
      html[data-theme="light"] .site-header .mobile-menu a{color:#31486f!important}
      .site-footer{padding:28px 0!important;border-top:1px solid rgba(255,255,255,.05)!important}
      html[data-theme="light"] .site-footer{border-top-color:rgba(12,33,66,.08)!important}
      .site-footer .footer-inner{width:min(calc(100% - 32px),1180px)!important;margin:0 auto!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:18px!important;flex-wrap:wrap!important}
      .site-footer .footer-links{display:flex!important;gap:18px!important;flex-wrap:wrap!important}
      .site-footer .footer-links a{color:var(--muted-2,#7f91b3)!important;font-size:.94rem!important;text-decoration:none!important;white-space:nowrap!important}
      .site-footer .footer-links a:hover{color:var(--text,#eff4ff)!important;text-decoration:none!important}
      @media(max-width:1160px){.site-header .nav{grid-template-columns:auto 1fr auto !important}.site-header .desktop-nav{display:none!important}.site-header .nav-toggle{display:inline-block!important}.site-header .nav-actions{margin-left:auto!important}}
      @media(max-width:680px){.site-header .nav{min-height:62px!important}.site-header .brand-copy span{display:none!important}.site-header .lang-switch{gap:9px!important}.site-header .lang-btn{font-size:.8rem!important}.site-header .theme-toggle,.site-header .nav-toggle{width:42px!important;height:42px!important;min-width:42px!important;min-height:42px!important}.site-footer .footer-inner{align-items:flex-start!important;flex-direction:column!important}}
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
        <div class="nav">
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
              <span class="theme-toggle-icon" aria-hidden="true">☾</span>
              <span class="theme-toggle-label sr-only" data-i18n="theme_toggle_dark">${t("theme_toggle_dark")}</span>
            </button>
            <button aria-controls="mobileMenu" aria-expanded="false" aria-label="Open menu" class="nav-toggle" id="navToggle" type="button">
              <span></span><span></span><span></span>
            </button>
          </div>
        </div>
        <div class="mobile-menu" id="mobileMenu">
          <div class="mobile-menu-inner">
            ${mobileLinks}
          </div>
        </div>
      </header>`;
  }

  function buildFooter() {
    const links = footerLinks.map(([href, label]) => `<a href="${href}" data-i18n="${label}">${t(label)}</a>`).join("");
    return `
      <footer class="site-footer">
        <div class="footer-inner">
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
    exposeI18n();
    updateThemeToggle();
  }

  function applyTheme(theme) {
    const selected = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", selected);
    try { localStorage.setItem(THEME_KEY, selected); } catch (_) {}
    updateThemeToggle();
  }

  function updateThemeToggle() {
    const theme = document.documentElement.getAttribute("data-theme") || currentTheme();
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
      const icon = btn.querySelector(".theme-toggle-icon");
      const label = btn.querySelector(".theme-toggle-label");
      if (icon) icon.textContent = theme === "dark" ? "☀" : "☾";
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
    exposeI18n();
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
