/* LP-GL-11A — centralized landing page content runtime. */
(function () {
  const cache = new Map();
  const listeners = new Set();
  let activeLocale = document.documentElement.lang === "en" ? "en" : "de";
  let activeContent = null;

  function locale() {
    return document.documentElement.lang === "en" ? "en" : "de";
  }

  function deepMerge(base, override) {
    if (!override || typeof override !== "object" || Array.isArray(override)) return base;
    const result = { ...(base || {}) };
    Object.keys(override).forEach((key) => {
      const value = override[key];
      result[key] = value && typeof value === "object" && !Array.isArray(value)
        ? deepMerge(result[key], value)
        : value;
    });
    return result;
  }

  async function loadStatic(targetLocale) {
    const response = await fetch(`lang/redesign.${targetLocale}.json`, { cache: "no-cache" });
    if (!response.ok) throw new Error(`Landing content fallback unavailable: ${response.status}`);
    return response.json();
  }

  async function loadPublished(targetLocale) {
    const endpoint = window.BCSENTINEL_LANDING_CONTENT_ENDPOINT
      || document.querySelector('meta[name="bcsentinel-landing-content-endpoint"]')?.content;
    if (!endpoint) return null;
    const url = new URL(endpoint, window.location.origin);
    url.searchParams.set("locale", targetLocale);
    const response = await fetch(url.toString(), { headers: { Accept: "application/json" }, cache: "no-cache" });
    if (!response.ok) return null;
    const payload = await response.json();
    return payload && typeof payload === "object" ? payload : null;
  }

  async function load(targetLocale = locale()) {
    if (cache.has(targetLocale)) return cache.get(targetLocale);
    const fallback = await loadStatic(targetLocale);
    let published = null;
    try { published = await loadPublished(targetLocale); } catch (_) { published = null; }
    const merged = deepMerge(fallback, published);
    cache.set(targetLocale, merged);
    return merged;
  }

  async function refresh() {
    activeLocale = locale();
    activeContent = await load(activeLocale);
    listeners.forEach((listener) => {
      try { listener(activeContent, activeLocale); } catch (_) {}
    });
    window.dispatchEvent(new CustomEvent("bcsentinel:content-ready", { detail: { locale: activeLocale } }));
    return activeContent;
  }

  function section(name) {
    return activeContent?.[name] || null;
  }

  function subscribe(listener) {
    listeners.add(listener);
    if (activeContent) listener(activeContent, activeLocale);
    return () => listeners.delete(listener);
  }

  window.BCSentinelContent = { load, refresh, section, subscribe, locale: () => activeLocale };

  const observer = new MutationObserver((mutations) => {
    if (mutations.some((item) => item.attributeName === "lang")) {
      const nextLocale = locale();
      if (nextLocale !== activeLocale) {
        activeLocale = nextLocale;
        activeContent = null;
        refresh().catch(() => {});
      }
    }
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => refresh().catch(() => {}), { once: true });
  } else {
    refresh().catch(() => {});
  }
})();