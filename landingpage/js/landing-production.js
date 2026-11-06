(function () {
  const API_BASE = (() => {
    const host = (window.location.hostname || '').toLowerCase();
    return host.startsWith('dev.') ? 'https://dev-api.bcsentinel.com' : 'https://api.bcsentinel.com';
  })();

  function lang() {
    return (document.documentElement.lang || 'de').toLowerCase().startsWith('de') ? 'de' : 'en';
  }

  function applyCopy() {
    const selected = lang();
    document.querySelectorAll('[data-de][data-en]').forEach((node) => {
      const value = node.getAttribute(selected === 'de' ? 'data-de' : 'data-en');
      if (value !== null) node.textContent = value;
    });
  }

  function price(value, currency) {
    return new Intl.NumberFormat(lang() === 'de' ? 'de-DE' : 'en-US', {
      style: 'currency', currency: currency || 'EUR', maximumFractionDigits: 0,
    }).format(Number(value || 0));
  }

  function validPricing(payload) {
    return Boolean(payload && Array.isArray(payload.products) && payload.products.length);
  }

  function renderPricing(payload) {
    if (!validPricing(payload)) return;
    payload.products.forEach((product) => {
      const target = document.querySelector(`[data-product-price="${product.product_key}"]`);
      if (!target) return;
      const prefix = lang() === 'de' ? 'Ab ' : 'From ';
      target.textContent = `${prefix}${price(Number(product.price_cents) / 100, product.currency || payload.currency)}`;
    });
    document.querySelectorAll('[data-pricing-model-copy]').forEach((node) => {
      node.textContent = lang() === 'de'
        ? 'Preis abhängig vom analysierten Datensatzvolumen. Enterprise+ wird individuell angeboten.'
        : 'Price depends on analyzed record volume. Enterprise+ is quoted individually.';
    });
  }

  let pricing = window.__BCS_PRODUCT_PRICING__ || null;
  if (pricing) renderPricing(pricing);

  fetch(`${API_BASE}/pricing/public`, { headers: { Accept: 'application/json' } })
    .then((response) => {
      if (!response.ok) throw new Error('pricing unavailable');
      return response.json();
    })
    .then((payload) => {
      if (!validPricing(payload)) throw new Error('invalid pricing');
      pricing = payload;
      renderPricing(payload);
    })
    .catch(() => {
      if (pricing) renderPricing(pricing);
    });

  const languageObserver = new MutationObserver(() => {
    applyCopy();
    if (pricing) renderPricing(pricing);
  });
  languageObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  applyCopy();

  const form = document.getElementById('pilotInterestForm');
  if (!form) return;

  const status = document.getElementById('pilotFormStatus');
  const button = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const data = new FormData(form);
    const payload = {
      contact_name: String(data.get('contact_name') || ''),
      contact_email: String(data.get('contact_email') || ''),
      company_name: String(data.get('company_name') || ''),
      bc_context: String(data.get('bc_context') || ''),
      message: String(data.get('message') || ''),
      website: String(data.get('website') || ''),
      privacy_consent: data.get('privacy_consent') === 'on',
      preferred_language: lang(),
      source_page: 'controlled-pilot',
    };

    button.disabled = true;
    status.textContent = lang() === 'de' ? 'Anfrage wird übermittelt …' : 'Submitting request …';
    status.dataset.state = 'pending';

    try {
      const response = await fetch(`${API_BASE}/public/pilot-interest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('submission failed');
      const result = await response.json();
      form.reset();
      status.dataset.state = 'success';
      status.textContent = lang() === 'de'
        ? `Danke. Die Pilot-Anfrage wurde aufgenommen${result.reference ? ` (${result.reference})` : ''}.`
        : `Thank you. Your pilot request was recorded${result.reference ? ` (${result.reference})` : ''}.`;
    } catch (_) {
      status.dataset.state = 'error';
      status.textContent = lang() === 'de'
        ? 'Die Anfrage konnte gerade nicht übermittelt werden. Bitte später erneut versuchen.'
        : 'The request could not be submitted right now. Please try again later.';
    } finally {
      button.disabled = false;
    }
  });
})();
