(function () {
  const KEY = "bcsentinel-lang";
  const SUPPORTED = ["de", "en"];
  let translations = {};

  function initialLang() {
    const params = new URLSearchParams(window.location.search);
    const fromUrl = params.get("lang");
    if (SUPPORTED.includes(fromUrl)) return fromUrl;
    try {
      const saved = localStorage.getItem(KEY);
      if (SUPPORTED.includes(saved)) return saved;
    } catch (_) {}
    return (navigator.language || "").toLowerCase().startsWith("de") ? "de" : "en";
  }

  function t(key, fallback) {
    const lang = document.documentElement.lang || initialLang();
    return (translations[lang] && translations[lang][key]) || fallback || key;
  }

  async function load(lang) {
    const selected = SUPPORTED.includes(lang) ? lang : "de";
    const [de, en] = await Promise.all(
      SUPPORTED.map((code) =>
        fetch(`lang/${code}.json`, { cache: "no-cache" })
          .then((response) => response.ok ? response.json() : {})
          .catch((error) => {
            console.error("Could not load language file", code, error);
            return {};
          })
      )
    );
    translations = { de, en };
    apply(selected);
  }

  function apply(lang) {
    const selected = SUPPORTED.includes(lang) ? lang : "de";
    document.documentElement.lang = selected;
    try { localStorage.setItem(KEY, selected); } catch (_) {}
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.getAttribute("data-i18n");
      if (translations[selected] && translations[selected][key] !== undefined) {
        node.textContent = translations[selected][key];
      }
    });
    [
      ["data-i18n-placeholder", "placeholder"],
      ["data-i18n-title", "title"],
      ["data-i18n-aria-label", "aria-label"],
      ["data-i18n-alt", "alt"],
      ["data-i18n-content", "content"],
    ].forEach(([attr, target]) => {
      document.querySelectorAll(`[${attr}]`).forEach((node) => {
        const key = node.getAttribute(attr);
        if (translations[selected] && translations[selected][key] !== undefined) {
          node.setAttribute(target, translations[selected][key]);
        }
      });
    });
    document.querySelectorAll("[data-lang-select]").forEach((select) => {
      select.value = selected;
    });
    if (translations[selected] && translations[selected].meta_title) {
      const pageKey = document.body.dataset.pageKey || "home";
      const pageTitle = translations[selected][`meta_${pageKey}_title`];
      document.title = pageTitle || translations[selected].meta_title;
    }
    window.dispatchEvent(new CustomEvent("bcsentinel:language-change", { detail: { lang: selected } }));
  }

  window.BCSentinelI18n = {
    initialLang,
    load,
    apply,
    t,
    lang: () => document.documentElement.lang || initialLang(),
  };
})();
