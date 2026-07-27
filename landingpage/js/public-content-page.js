/* LP-GL-11A — shared renderer for translated public content pages. */
(function () {
  function currentPage() {
    return document.body.dataset.publicPage || "";
  }

  function locale() {
    return document.documentElement.lang === "en" ? "en" : "de";
  }

  function applyMeta(content) {
    if (content.metaTitle) document.title = content.metaTitle;
    const meta = document.querySelector('meta[name="description"]');
    if (meta && content.metaDescription) meta.setAttribute("content", content.metaDescription);
  }

  function cardGrid(cards) {
    return `<div class="public-card-grid">${cards.map((card) => `<article class="public-card"><h3>${card.title}</h3><p>${card.text}</p></article>`).join("")}</div>`;
  }

  function markup(content) {
    const aside = (content.heroAside || []).map((item) => `<div class="public-aside-item"><strong>${item.title}</strong><p>${item.text}</p></div>`).join("");
    const sections = (content.sections || []).map((section) => `<section class="public-section" id="${section.id}"><div class="public-section-head"><p class="public-eyebrow">${section.eyebrow || ""}</p><h2>${section.title}</h2><p>${section.lead || ""}</p></div>${cardGrid(section.cards || [])}${section.note ? `<div class="public-note">${section.note}</div>` : ""}</section>`).join("");
    const actions = (content.actions || []).map((action, index) => `<a class="public-btn ${index === 0 ? "primary" : "secondary"}" href="${action.href}">${action.label}</a>`).join("");
    return `<div class="public-page"><div class="public-container"><section class="public-hero"><div class="public-hero-copy"><p class="public-eyebrow">${content.eyebrow}</p><h1>${content.title}</h1><p class="public-lead">${content.lead}</p>${actions ? `<div class="public-actions">${actions}</div>` : ""}</div><aside class="public-hero-aside" aria-label="${content.asideAria}">${aside}</aside></section><div class="public-sections">${sections}</div></div></div>`;
  }

  function render(content) {
    const root = document.getElementById("publicPageRoot");
    if (!root || !content) return;
    applyMeta(content);
    root.innerHTML = markup(content);
  }

  async function refresh() {
    const page = currentPage();
    if (!page || !window.BCSentinelContent) return;
    try {
      const payload = await window.BCSentinelContent.loadBundle(page, locale());
      render(payload?.page);
    } catch (error) {
      console.error(`Unable to load ${page} content`, error);
    }
  }

  function init() {
    refresh();
    new MutationObserver((mutations) => {
      if (mutations.some((item) => item.attributeName === "lang")) refresh();
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
