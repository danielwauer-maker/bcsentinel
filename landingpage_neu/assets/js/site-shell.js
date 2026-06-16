(function () {
  function t(key, fallback) {
    return window.BCSentinelI18n ? window.BCSentinelI18n.t(key, fallback) : (fallback || key);
  }

  function pageVisible(page) {
    return !window.BCSentinelVisibility || window.BCSentinelVisibility.isVisible(page.key);
  }

  function brand() {
    return `
      <a class="brand" href="index.html" aria-label="BCSentinel Home">
        <span class="brand-mark">BC</span>
        <span class="brand-copy"><strong>BCSentinel</strong><span data-i18n="brand_claim">${t("brand_claim")}</span></span>
      </a>`;
  }

  function buildHeader() {
    const config = window.BCSentinelConfig || {};
    const navPages = (config.pages || []).filter(pageVisible);
    const mainPages = navPages.filter((page) => ["home", "pricing", "executive_reports", "why_bcsentinel", "trust"].includes(page.key));
    const supportAction = pageVisible({ key: "support" })
      ? `<a class="btn btn-secondary" href="support.html" data-page-link="support" data-i18n="nav_login">${t("nav_login")}</a>`
      : "";
    return `
      <header class="site-header">
        <div class="container nav">
          ${brand()}
          <nav class="desktop-nav" aria-label="Primary">
            ${mainPages.map((page) => `<a class="nav-item" href="${page.href}" data-i18n="${page.labelKey}">${t(page.labelKey)}</a>`).join("")}
          </nav>
          <div class="nav-actions">
            <select class="lang-select" data-lang-select aria-label="Language">
              <option value="de">DE</option>
              <option value="en">EN</option>
            </select>
            <button class="theme-toggle" type="button" data-theme-toggle aria-label="Theme"><span data-theme-icon>D</span></button>
            ${supportAction}
            <a class="btn btn-primary" href="contact.html?intent=full_analysis" data-checkout-product="full_analysis" data-product-code="full_analysis" data-i18n="cta_assessment">${t("cta_assessment")}</a>
            <button class="nav-toggle" type="button" data-nav-toggle aria-label="Menu">Menu</button>
          </div>
        </div>
        <div class="mobile-menu" data-mobile-menu>
          <div class="container">
            ${navPages.map((page) => `<a href="${page.href}" data-i18n="${page.labelKey}">${t(page.labelKey)}</a>`).join("")}
            <a href="contact.html?intent=full_analysis" data-checkout-product="full_analysis" data-product-code="full_analysis" data-i18n="cta_assessment">${t("cta_assessment")}</a>
          </div>
        </div>
      </header>`;
  }

  function footerColumn(titleKey, links) {
    const visibleLinks = links.filter((link) => !link.pageKey || !window.BCSentinelVisibility || window.BCSentinelVisibility.isVisible(link.pageKey));
    return `
      <div class="footer-col">
        <h3 data-i18n="${titleKey}">${t(titleKey)}</h3>
        ${visibleLinks.map((link) => `<a href="${link.href}" data-i18n="${link.labelKey}">${t(link.labelKey)}</a>`).join("")}
      </div>`;
  }

  function buildFooter() {
    return `
      <footer class="site-footer">
        <div class="container">
          <div class="footer-grid">
            <div class="footer-col">
              ${brand()}
              <p class="small" data-i18n="footer_claim">${t("footer_claim")}</p>
            </div>
            ${footerColumn("footer_product", [
              { href: "index.html", labelKey: "nav_home", pageKey: "home" },
              { href: "pricing.html", labelKey: "nav_pricing", pageKey: "pricing" },
              { href: "executive-reports.html", labelKey: "nav_executive_reports", pageKey: "executive_reports" },
              { href: "why-bcsentinel.html", labelKey: "nav_data_health", pageKey: "why_bcsentinel" },
            ])}
            ${footerColumn("footer_solutions", [
              { href: "why-bcsentinel.html#finance", labelKey: "target_finance_title", pageKey: "why_bcsentinel" },
              { href: "why-bcsentinel.html#operations", labelKey: "target_operations_title", pageKey: "why_bcsentinel" },
              { href: "why-bcsentinel.html#it", labelKey: "target_it_title", pageKey: "why_bcsentinel" },
            ])}
            ${footerColumn("footer_resources", [
              { href: "support.html", labelKey: "nav_support", pageKey: "support" },
              { href: "support.html#knowledge", labelKey: "support_knowledge_title", pageKey: "support" },
              { href: "executive-reports.html", labelKey: "reports_sample_cta", pageKey: "executive_reports" },
            ])}
            ${footerColumn("footer_company", [
              { href: "about.html", labelKey: "nav_about", pageKey: "about" },
              { href: "why-bcsentinel.html", labelKey: "nav_why", pageKey: "why_bcsentinel" },
              { href: "contact.html", labelKey: "nav_contact", pageKey: "contact" },
            ])}
            ${footerColumn("footer_trust", [
              { href: "trust.html", labelKey: "nav_trust", pageKey: "trust" },
              { href: "trust.html#security", labelKey: "trust_security_title", pageKey: "trust" },
              { href: "trust.html#compliance", labelKey: "trust_compliance_title", pageKey: "trust" },
              { href: "support.html#status", labelKey: "support_status_title", pageKey: "support" },
            ])}
            ${footerColumn("footer_legal", [
              { href: "../landingpage/privacy.html", labelKey: "footer_privacy" },
              { href: "../landingpage/terms.html", labelKey: "footer_dpa" },
              { href: "../landingpage/impressum.html", labelKey: "footer_imprint" },
              { href: "../landingpage/terms.html", labelKey: "footer_terms" },
            ])}
          </div>
          <div class="footer-bottom">
            <span data-i18n="footer_copyright">${t("footer_copyright")}</span>
            <span>DE / EN</span>
          </div>
        </div>
      </footer>`;
  }

  function guardCurrentPage() {
    const pageKey = document.body.dataset.pageKey || "home";
    if (pageKey !== "home" && window.BCSentinelVisibility && !window.BCSentinelVisibility.isVisible(pageKey)) {
      window.location.replace("index.html");
    }
  }

  function renderShell() {
    guardCurrentPage();
    document.body.insertAdjacentHTML("afterbegin", buildHeader());
    document.body.insertAdjacentHTML("beforeend", buildFooter());
    window.BCSentinelI18n.apply(window.BCSentinelI18n.lang());
    window.BCSentinelTheme.applyTheme(window.BCSentinelTheme.currentTheme());
  }

  function bind() {
    document.addEventListener("change", (event) => {
      const select = event.target.closest("[data-lang-select]");
      if (select) window.BCSentinelI18n.apply(select.value);
    });
    document.addEventListener("click", (event) => {
      if (event.target.closest("[data-theme-toggle]")) window.BCSentinelTheme.toggle();
      const toggle = event.target.closest("[data-nav-toggle]");
      if (toggle) {
        const menu = document.querySelector("[data-mobile-menu]");
        if (menu) menu.classList.toggle("open");
      }
      if (event.target.closest("[data-checkout-product]")) {
        const product = event.target.closest("[data-checkout-product]").dataset.checkoutProduct;
        try { sessionStorage.setItem("bcsentinel_checkout_product", product); } catch (_) {}
      }
    });
  }

  document.addEventListener("DOMContentLoaded", async () => {
    await window.BCSentinelI18n.load(window.BCSentinelI18n.initialLang());
    await window.BCSentinelPricing.load();
    await window.BCSentinelVisibility.load();
    renderShell();
    bind();
  });
})();
