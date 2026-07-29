/* LP-GL-11C — centralized landing-page content runtime and public terminology. */
(function () {
  const cache = new Map();
  const listeners = new Set();
  let activeLocale = document.documentElement.lang === "en" ? "en" : "de";
  let activeContent = null;

  const COPY_REPLACEMENTS = {
    de: [
      [/Full Analysis/g, "vollständige Analyse"],
      [/Premiumzugriff/g, "Vollzugriff"],
      [/Premium-Zugriff/g, "Vollzugriff"],
      [/Premium/g, "vollständig"],
      [/Starten Sie das Assessment/g, "Starten Sie den kostenlosen Scan"],
      [/Assessment starten/g, "Kostenlosen Scan starten"],
      [/Issues und Actions/g, "Findings und Maßnahmen"],
      [/Issues/g, "Findings"],
      [/Actions/g, "Maßnahmen"],
    ],
    en: [
      [/Full Analysis/g, "complete analysis"],
      [/premium access/gi, "full access"],
      [/premium/gi, "full"],
      [/Start Assessment/g, "Start free scan"],
      [/Issues and Actions/g, "Findings and actions"],
      [/Issues/g, "Findings"],
    ],
  };

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

  function normalizeString(value, targetLocale) {
    return (COPY_REPLACEMENTS[targetLocale] || []).reduce(
      (result, [pattern, replacement]) => result.replace(pattern, replacement),
      value
    );
  }

  function normalizeCopy(value, targetLocale) {
    if (typeof value === "string") return normalizeString(value, targetLocale);
    if (Array.isArray(value)) return value.map((item) => normalizeCopy(item, targetLocale));
    if (value && typeof value === "object") {
      return Object.fromEntries(
        Object.entries(value).map(([key, item]) => [key, normalizeCopy(item, targetLocale)])
      );
    }
    return value;
  }

  async function loadStatic(targetLocale, bundle = "redesign") {
    const response = await fetch(`lang/${bundle}.${targetLocale}.json`, { cache: "no-cache" });
    if (!response.ok) throw new Error(`Landing content fallback unavailable: ${response.status}`);
    return response.json();
  }

  async function loadPublished(targetLocale, bundle = "redesign") {
    const endpoint = window.BCSENTINEL_LANDING_CONTENT_ENDPOINT
      || document.querySelector('meta[name="bcsentinel-landing-content-endpoint"]')?.content;
    if (!endpoint) return null;
    const url = new URL(endpoint, window.location.origin);
    url.searchParams.set("locale", targetLocale);
    url.searchParams.set("bundle", bundle);
    const response = await fetch(url.toString(), { headers: { Accept: "application/json" }, cache: "no-cache" });
    if (!response.ok) return null;
    const payload = await response.json();
    return payload && typeof payload === "object" ? payload : null;
  }

  async function loadBundle(bundle = "redesign", targetLocale = locale(), options = {}) {
    const cacheKey = `${bundle}:${targetLocale}`;
    if (!options.force && cache.has(cacheKey)) return cache.get(cacheKey);
    const fallback = await loadStatic(targetLocale, bundle);
    let published = null;
    try { published = await loadPublished(targetLocale, bundle); } catch (_) { published = null; }
    const merged = normalizeCopy(deepMerge(fallback, published), targetLocale);
    cache.set(cacheKey, merged);
    return merged;
  }

  async function load(targetLocale = locale()) {
    return loadBundle("redesign", targetLocale);
  }

  async function refresh() {
    activeLocale = locale();
    activeContent = await load(activeLocale);
    listeners.forEach((listener) => {
      try { listener(activeContent, activeLocale); } catch (_) {}
    });
    window.dispatchEvent(new CustomEvent("bcsentinel:content-ready", { detail: { locale: activeLocale, bundle: "redesign" } }));
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

  function invalidate(bundle, targetLocale) {
    if (bundle && targetLocale) cache.delete(`${bundle}:${targetLocale}`);
    else if (bundle) [...cache.keys()].filter((key) => key.startsWith(`${bundle}:`)).forEach((key) => cache.delete(key));
    else cache.clear();
  }

  window.BCSentinelContent = { load, loadBundle, refresh, section, subscribe, invalidate, locale: () => activeLocale };

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