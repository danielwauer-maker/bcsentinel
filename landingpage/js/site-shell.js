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
      ["#partners", "nav_partners"],
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
    ["/partner-login.html", "footer_partner_login"],
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

  function buildHeader() {
    const key = pageKey();
    const nav = pageNav[key] || pageNav.index;
    const links = nav.map(([href, label]) => `<a href="${href}" data-i18n="${label}">${t(label)}</a>`).join("");
    return `
      <header class="site-header">
        <div class="container nav">
          <a class="brand" href="/index.html#top" aria-label="BCSentinel home">
            <span class="brand-mark"><img src="/logo-bcsentinel.png" alt="BCSentinel Logo" /></span>
            <span class="brand-copy"><strong>BCSentinel</strong><span data-i18n="brand_sub">${t("brand_sub")}</span></span>
          </a>
          <nav class="nav-links desktop-nav" aria-label="Primary navigation">${links}</nav>
          <div class="nav-actions">
            <div class="lang-switch" aria-label="Language switcher">
              <button class="lang-btn" data-lang="de" type="button" data-i18n-title="lang_de_title" data-i18n-aria-label="lang_de_label">DE</button>
              <button class="lang-btn" data-lang="en" type="button" data-i18n-title="lang_en_title" data-i18n-aria-label="lang_en_label">EN</button>
            </div>
            <button class="theme-toggle" id="themeToggle" type="button" data-i18n-aria-label="theme_toggle_aria">
              <span class="theme-toggle-icon" aria-hidden="true">Dark</span>
              <span class="theme-toggle-label sr-only" data-i18n="theme_toggle_dark">${t("theme_toggle_dark")}</span>
            </button>
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
            <span class="brand-copy"><strong>BCSentinel</strong><span data-i18n="brand_sub">${t("brand_sub")}</span></span>
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
      if (icon) icon.textContent = theme === "dark" ? "Dark" : "Light";
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
      }
    });
  }

  document.addEventListener("DOMContentLoaded", async () => {
    await loadTranslations();
    ensureShell();
    bindControls();
    applyTheme(currentTheme());
    applyTranslations(currentLang());
  });
})();
