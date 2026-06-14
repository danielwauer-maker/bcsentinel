(function () {
  let state = null;

  function defaultState() {
    const config = window.BCSentinelConfig || {};
    return {
      source: "fallback",
      pages: (config.pages || []).map((page) => ({ page_key: page.key, is_visible: true })),
    };
  }

  function normalize(payload) {
    if (!payload || !Array.isArray(payload.pages)) return defaultState();
    const config = window.BCSentinelConfig || {};
    const known = new Set((config.pages || []).map((page) => page.key));
    const pages = payload.pages
      .filter((page) => page && known.has(page.page_key))
      .map((page) => ({ page_key: page.page_key, is_visible: Boolean(page.is_visible) }));
    return { source: payload.source || "database", pages };
  }

  function isVisible(pageKey) {
    const data = state || defaultState();
    const row = data.pages.find((page) => page.page_key === pageKey);
    return row ? row.is_visible : true;
  }

  async function load() {
    const config = window.BCSentinelConfig || {};
    try {
      const response = await fetch(`${config.apiBase || ""}/landingpage/pages/visibility`, {
        headers: { Accept: "application/json" },
        cache: "no-cache",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state = normalize(await response.json());
    } catch (error) {
      console.error("Visibility API unavailable, showing all pages.", error);
      state = defaultState();
    }
    window.dispatchEvent(new CustomEvent("bcsentinel:visibility-change", { detail: state }));
    return state;
  }

  window.BCSentinelVisibility = { load, isVisible, current: () => state || defaultState() };
})();
