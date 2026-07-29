/* LP-GL-11C / LP-LEGAL-01 — centralized landing-page content runtime and public terminology. */
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
      [/Alle Preise sind B2B-Listenpreise in EUR\. Gesetzliche Steuern können abhängig von Kunde und Abrechnungsland hinzukommen\. Maßgeblich sind die im Checkout beziehungsweise Vertrag ausgewiesenen Konditionen\./g, "Alle Preise sind B2B-Endpreise in EUR. Daniel Wauer wendet derzeit die Kleinunternehmerregelung gemäß § 19 UStG an; deutsche Umsatzsteuer wird nicht ausgewiesen. Maßgeblich sind die im Checkout beziehungsweise Vertrag ausgewiesenen Konditionen."],
      [/Für den produktiven Go-Live werden keine extern von Google geladenen Schriftarten benötigt\. Die Website verwendet lokal verfügbare beziehungsweise systemseitige Schriftarten, sodass beim reinen Seitenaufruf keine Schriftanfrage an Google erforderlich ist\./g, "Die Website lädt derzeit die Schriftart Inter über Google Fonts. Dabei wird technisch eine Verbindung zu Google-Servern hergestellt und insbesondere die IP-Adresse übertragen. Diese externe Einbindung wird vor dem öffentlichen Go-Live entfernt und durch lokal verfügbare beziehungsweise systemseitige Schriftarten ersetzt."],
    ],
    en: [
      [/Full Analysis/g, "complete analysis"],
      [/premium access/gi, "full access"],
      [/premium/gi, "full"],
      [/Start Assessment/g, "Start free scan"],
      [/Issues and Actions/g, "Findings and actions"],
      [/Issues/g, "Findings"],
      [/All prices are B2B list prices in EUR\. Statutory taxes may be added depending on the customer and billing country\. The terms shown in checkout or the contract apply\./g, "All prices are B2B final prices in EUR. Daniel Wauer currently applies the German small-business VAT exemption under section 19 UStG; German VAT is not shown. The terms shown in checkout or the contract apply."],
      [/The production go-live does not require fonts loaded from Google\. The website uses locally available or system fonts so that a normal page view does not require a font request to Google\./g, "The website currently loads Inter through Google Fonts. This technically creates a connection to Google servers and transfers data including the IP address. The external integration will be removed before public go-live and replaced with locally available or system fonts."],
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