let currentSelectedScanId = null;
let recentScansPage = 1;
const RECENT_SCANS_PAGE_SIZE = 12;
let currentDashboardState = null;

function byId(id) {
  return document.getElementById(id);
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-US').format(Number(value || 0));
}

function formatCurrency(value) {
  const number = Number(value || 0);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(number);
}

function formatDateTime(value) {
  const raw = String(value || '').trim();
  if (!raw || raw === '—') return '—';

  const isoLike = raw.includes('T') ? raw : raw.replace(/ UTC$/, 'Z').replace(', ', 'T');
  const parsed = new Date(isoLike);
  if (!Number.isNaN(parsed.getTime())) {
    const pad = (part) => String(part).padStart(2, '0');
    return `${pad(parsed.getDate())}.${pad(parsed.getMonth() + 1)}.${parsed.getFullYear()} ${pad(parsed.getHours())}:${pad(parsed.getMinutes())}:${pad(parsed.getSeconds())}`;
  }

  const match = raw.match(/^(\d{2})\.(\d{2})\.(\d{4})[,\s]+(\d{2}):(\d{2})(?::(\d{2}))?/);
  if (match) {
    return `${match[1]}.${match[2]}.${match[3]} ${match[4]}:${match[5]}:${match[6] || '00'}`;
  }

  return raw;
}

function escapeHtml(value) {
  return String(value || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "";
}

function setHtml(id, value) {
  const el = byId(id);
  if (el) el.innerHTML = value;
}

function scoreBand(score) {
  const safeScore = Math.max(0, Math.min(100, Number(score || 0)));
  if (safeScore <= 60) return 'critical';
  if (safeScore <= 75) return 'warning';
  if (safeScore <= 85) return 'moderate';
  if (safeScore <= 95) return 'good';
  return 'excellent';
}

function renderPricingBreakdown(data) {
  const breakdown = data?.pricing_breakdown || {};
  const subscription = data?.subscription || {};
  const subscriptionBreakdown = subscription?.pricing_breakdown || breakdown;
  const billingOptions = subscription?.billing_options || {};

  setText("preview-base-price", formatCurrency(breakdown.base_price_monthly));
  setText("preview-variable-price", formatCurrency(breakdown.variable_price_monthly));
  setText("preview-final-price", formatCurrency(breakdown.final_price_monthly));
  setText("preview-annual-fixed", formatCurrency(breakdown.annual_fixed_price));
  setText("preview-monthly-note", breakdown.monthly_note || "");
  setText("preview-annual-note", breakdown.annual_note || "");

  setText("subscription-base-price", formatCurrency(subscriptionBreakdown.base_price_monthly));
  setText("subscription-variable-price", formatCurrency(subscriptionBreakdown.variable_price_monthly));
  setText("subscription-final-price", formatCurrency(subscriptionBreakdown.final_price_monthly));
  setText("subscription-annual-fixed", formatCurrency(subscriptionBreakdown.annual_fixed_price));

  setText("subscription-monthly-label", billingOptions.monthly_label || "Monthly billing");
  setText("subscription-monthly-note", billingOptions.monthly_note || "");
  setText("subscription-annual-label", billingOptions.annual_label || "Annual fixed plan");
  setText("subscription-annual-note", billingOptions.annual_note || "");
}

function renderHeroPoints(items) {
  const host = byId('hero-points');
  if (!host) return;
  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = '';
    host.classList.add('hidden');
    return;
  }
  host.classList.remove('hidden');
  host.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
}

function renderProfileCards(moduleScores, fallbackItems) {
  const host = byId('profile-cards');
  if (!host) return;
  host.innerHTML = '';

  const scoreItems = Array.isArray(moduleScores) ? moduleScores.filter(Boolean) : [];
  const fallback = Array.isArray(fallbackItems) ? fallbackItems.filter(Boolean) : [];

  if (scoreItems.length > 0) {
    scoreItems.forEach((item) => {
      const score = Math.max(0, Math.min(100, Number(item?.score ?? item?.value ?? 0)));
      const variant = item?.variant || scoreBand(score);
      const label = item?.name || item?.label || '';
      const badgeText = variant.charAt(0).toUpperCase() + variant.slice(1);

      const card = document.createElement('div');
      card.className = `mini-card score-card score-${variant}`;
      card.innerHTML = `
        <div class="mini-card-top">
          <div class="mini-card-value">${formatNumber(score)}</div>
          <div class="mini-score-badge score-${variant}">${escapeHtml(badgeText)}</div>
        </div>
        <div class="mini-card-label">${escapeHtml(label)}</div>
      `;
      host.appendChild(card);
    });
    return;
  }

  if (fallback.length === 0) {
    host.innerHTML = '<div class="empty-state">No module scores are available yet.</div>';
    return;
  }

  fallback.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'mini-card';
    card.innerHTML = `
      <div class="mini-card-value">${formatNumber(item?.value)}</div>
      <div class="mini-card-label">${escapeHtml(item?.label)}</div>
    `;
    host.appendChild(card);
  });
}

function renderIssueGroups(items, emptyMessage = 'No module data is available for this scan.') {
  const host = byId('issue-groups');
  if (!host) return;
  host.innerHTML = '';

  const normalizedItems = Array.isArray(items)
    ? items.filter(Boolean).map((item) => ({
        name: item?.name || item?.label || '',
        count: Number(item?.count ?? item?.value ?? 0),
      }))
    : [];

  if (normalizedItems.length === 0) {
    host.innerHTML = `<div class="empty-state">${escapeHtml(emptyMessage)}</div>`;
    return;
  }

  const maxValue = Math.max(...normalizedItems.map((item) => Number(item?.count || 0)), 1);

  normalizedItems.forEach((item) => {
    const width = Math.max((Number(item?.count || 0) / maxValue) * 100, 2);
    const row = document.createElement('div');
    row.className = 'progress-row';
    row.innerHTML = `
      <div class="progress-meta">
        <span>${escapeHtml(item?.name)}</span>
        <span>${formatNumber(item?.count)}</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:${width}%"></div></div>
    `;
    host.appendChild(row);
  });
}

function renderModuleVolume(data) {
  const issueGroups = Array.isArray(data?.issue_groups) ? data.issue_groups : [];

  renderIssueGroups(issueGroups, 'No module issue counts are available for this scan.');
}
function renderTrend(containerId, items, asCurrency = false) {
  const host = byId(containerId);
  if (!host) return;
  host.innerHTML = '';

  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = '<div class="empty-state">No trend data available yet.</div>';
    return;
  }

  const safeItems = items.map((item) => ({
    label: item?.label || '',
    value: Number(item?.value || 0),
    is_selected: Boolean(item?.is_selected),
  }));

  const width = 560;
  const height = 220;
  const paddingX = 34;
  const paddingTop = 24;
  const paddingBottom = 39;
  const usableWidth = width - paddingX * 2;
  const usableHeight = height - paddingTop - paddingBottom;
  const maxValue = Math.max(...safeItems.map((item) => item.value), 1);
  const stepX = safeItems.length > 1 ? usableWidth / (safeItems.length - 1) : 0;

  const points = safeItems.map((item, index) => {
    const x = paddingX + stepX * index;
    const ratio = item.value / maxValue;
    const y = paddingTop + (usableHeight - usableHeight * ratio);
    return { ...item, x, y };
  });

  const polylinePoints = points.map((point) => `${point.x},${point.y}`).join(' ');
  const areaPoints = `${paddingX},${height - paddingBottom} ${polylinePoints} ${width - paddingX},${height - paddingBottom}`;

  const gridLines = [0, 0.5, 1].map((ratio) => {
    const y = paddingTop + usableHeight - usableHeight * ratio;
    const labelValue = maxValue * ratio;
    const label = asCurrency ? formatCurrency(labelValue).replace(',00', '') : formatNumber(Math.round(labelValue));
    return `
      <line x1="${paddingX}" y1="${y}" x2="${width - paddingX}" y2="${y}" class="trend-grid-line"></line>
      <text x="${paddingX - 10}" y="${y + 4}" text-anchor="end" class="trend-axis-label">${escapeHtml(label)}</text>
    `;
  }).join('');

  const pointCircles = points.map((point) => `
    <circle cx="${point.x}" cy="${point.y}" r="${point.is_selected ? 6 : 4}" class="trend-point${point.is_selected ? ' is-selected' : ''}"></circle>
  `).join('');

  const xLabels = points.map((point) => `
    <text x="${point.x}" y="${height - 14}" text-anchor="middle" class="trend-axis-label">${escapeHtml(point.label)}</text>
  `).join('');

  host.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" class="trend-svg" role="img">
      ${gridLines}
      <polygon points="${areaPoints}" class="trend-area"></polygon>
      <polyline points="${polylinePoints}" class="trend-line"></polyline>
      ${pointCircles}
      ${xLabels}
    </svg>
  `;
}

function renderRecentScans(items) {
  const host = byId('recent-scans-body');
  if (!host) return;

  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = '<tr><td colspan="5" class="table-empty">No scans available yet.</td></tr>';
    return;
  }

  host.innerHTML = items.map((item) => `
    <tr class="scan-row${item?.is_selected ? ' is-selected' : ''}" data-scan-id="${escapeHtml(item?.scan_id)}" tabindex="0">
      <td>${escapeHtml(formatDateTime(item?.generated_at))}</td>
      <td>${escapeHtml(item?.scan_type)}</td>
      <td>${formatNumber(item?.data_score)}</td>
      <td>${formatNumber(item?.issues_count)}</td>
      <td>${escapeHtml(item?.headline || '')}</td>
    </tr>
  `).join('');
}

function renderRecentScansPagination(pagination) {
  const prevButton = byId('recent-scans-prev');
  const nextButton = byId('recent-scans-next');
  const pageInfo = byId('recent-scans-page-info');
  const container = byId('recent-scans-pagination');
  if (!prevButton || !nextButton || !pageInfo || !container) return;

  const page = Math.max(1, Number(pagination?.page || 1));
  const totalPages = Math.max(1, Number(pagination?.total_pages || 1));
  const hasPrev = Boolean(pagination?.has_prev);
  const hasNext = Boolean(pagination?.has_next);
  const totalItems = Math.max(0, Number(pagination?.total_items || 0));

  recentScansPage = page;
  prevButton.disabled = !hasPrev;
  nextButton.disabled = !hasNext;
  pageInfo.textContent = `Page ${page} / ${totalPages}`;
  container.classList.toggle('hidden', totalItems <= RECENT_SCANS_PAGE_SIZE);
}

function renderFindings(items, isPremium) {
  const host = byId('findings-body');
  if (!host) return;

  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = '<tr><td colspan="6" class="table-empty">No findings are available for this scan.</td></tr>';
    return;
  }

  host.innerHTML = items.map((item) => {
    const accessClass = isPremium ? 'unlocked' : 'locked';
    const accessLabel = isPremium ? 'Open in BC' : 'Paid Access';
    const openInBcUrl = String(item?.open_in_bc_url || '');
    warnOnInvalidBcCompanyFormat(openInBcUrl);
    const accessMarkup = isPremium && openInBcUrl
      ? `<a href="${escapeHtml(openInBcUrl)}" class="access-chip ${accessClass}" target="_blank" rel="noopener noreferrer">${accessLabel}</a>`
      : `<span class="access-chip ${accessClass}">${accessLabel}</span>`;
    return `
      <tr>
        <td><strong>${escapeHtml(item?.title)}</strong></td>
        <td>${escapeHtml(item?.group)}</td>
        <td><span class="severity severity-${escapeHtml(item?.severity)}">${escapeHtml(String(item?.severity || '').toUpperCase())}</span></td>
        <td>${formatNumber(item?.count)}</td>
        <td>${formatCurrency(item?.impact_eur)}</td>
        <td>${accessMarkup}</td>
      </tr>
    `;
  }).join('');
}

function warnOnInvalidBcCompanyFormat(url) {
  const match = String(url || '').match(/[?&]company=([^&#]+)/i);
  if (!match) return;

  const companyValue = match[1];
  if (companyValue.includes('+')) {
    console.warn('Invalid company format detected:', companyValue);
  }
}

function renderPremiumPreview(items) {
  const host = byId('access-preview-findings');
  if (!host) return;
  host.innerHTML = '';

  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = '<div class="empty-state">The paid scan preview will appear after the next scan.</div>';
    return;
  }

  host.innerHTML = items.map((item) => `
    <article class="preview-card">
      <div class="preview-card-top">
        <div>
          <h4>${escapeHtml(item?.title)}</h4>
          <div class="muted">${escapeHtml(item?.group)}</div>
        </div>
        <div class="preview-impact">${formatCurrency(item?.impact_eur)}</div>
      </div>
      <div class="preview-metrics">
        <span>${formatNumber(item?.count)} affected</span>
        <span>Recommendations available</span>
      </div>
      <p class="muted">${escapeHtml(item?.recommendation_preview || '')}</p>
    </article>
  `).join('');
}

function renderUnlockPanel(data) {
  setText('unlock-headline', data?.premium_unlock?.headline || 'Paid scan access unlocks record-level details and direct action.');
  setText('unlock-body', data?.premium_unlock?.body || 'Upgrade to see exact affected records and recommendations.');
  setText('upgrade-button', data?.premium_unlock?.button_label || 'Buy Assessment');

  const host = byId('unlock-highlights');
  if (host) {
    host.innerHTML = (data?.premium_unlock?.highlights || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  }

  renderPremiumPreview(data?.premium_preview_findings || []);
}

function applyPlanState(data) {
  const visibility = data?.visibility || {};
  const productAccess = data?.product_access || {};
  const hasPaidAccess = Boolean(visibility?.is_premium);
  const monitoringActive = Boolean(productAccess?.monitoring_active);
  const planBadge = byId('current-plan-badge');
  const subBadge = byId('subscription-plan-badge');
  const accessUnlock = byId('access-unlock-panel');
  const monitoringPanels = byId('monitoring-overview-panels');
  const findingsPanel = byId('access-findings-panel');
  const accessLabel = monitoringActive
    ? 'Monitoring active'
    : (hasPaidAccess ? 'Assessment / Validation active' : 'Credits needed');

  if (planBadge) {
    planBadge.textContent = accessLabel;
    planBadge.classList.toggle('is-locked', !hasPaidAccess);
  }
  if (subBadge) {
    subBadge.textContent = accessLabel;
    subBadge.classList.toggle('is-locked', !hasPaidAccess);
  }

  if (accessUnlock) accessUnlock.classList.toggle('hidden', hasPaidAccess);
  if (monitoringPanels) monitoringPanels.classList.toggle('hidden', !monitoringActive);
  if (findingsPanel) findingsPanel.classList.toggle('hidden', !hasPaidAccess);
}

function renderSubscription(data) {
  const monitoringActive = Boolean(data?.product_access?.monitoring_active);
  const hasPaidAccess = Boolean(data?.visibility?.is_premium);
  const priceCard = byId('subscription-price-card');
  const annualCard = byId('subscription-annual-card');
  const buyMoreButton = byId('buy-more-credits-cta');

  setText('subscription-plan', data?.subscription?.plan_label || 'Assessment needed');
  setText('subscription-note', data?.subscription?.plan_note || '');
  setText('subscription-cta', data?.subscription?.cta_label || 'Buy Assessment');
  setText('subscription-scan-credits', formatNumber(data?.product_access?.scan_credits_available));
  setText('subscription-dashboard-until', formatDateTime(data?.product_access?.dashboard_access_until));
  setText('subscription-issue-until', formatDateTime(data?.product_access?.issue_access_until));

  if (priceCard) priceCard.classList.toggle('hidden', !monitoringActive);
  if (annualCard) annualCard.classList.toggle('hidden', !monitoringActive);
  if (buyMoreButton) buyMoreButton.classList.toggle('hidden', monitoringActive || !hasPaidAccess);

  if (monitoringActive) {
    setText('subscription-price', formatCurrency(data?.subscription?.price_monthly));
    setText('subscription-annual', formatCurrency(data?.subscription?.annual_cost));
  } else {
    setText('subscription-price', '');
    setText('subscription-annual', '');
  }
}

async function triggerBillingAction(action, productCode = null) {
  const baseEndpoint = action === 'portal'
    ? '/analytics/billing/portal'
    : '/analytics/billing/checkout';
  const endpoint = new URL(baseEndpoint, window.location.origin);
  if (productCode) endpoint.searchParams.set('product_code', productCode);

  try {
    const response = await fetch(endpoint.toString(), {
      method: 'POST',
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      console.error('Billing action failed:', response.status);
      return;
    }

    const payload = await response.json();
    const targetUrl = payload?.portal_url || payload?.checkout_url || '';
    if (!targetUrl) {
      console.error('Billing action did not return a target URL.');
      return;
    }

    window.location.href = targetUrl;
  } catch (error) {
    console.error('Billing action failed:', error);
  }
}

function switchTab(tab) {
  document.querySelectorAll('.topnav-link').forEach((btn) => {
    btn.classList.toggle('is-active', btn.dataset.tab === tab);
  });
  document.querySelectorAll('.tab-panel').forEach((panel) => {
    panel.classList.toggle('hidden', panel.id !== `${tab}-tab`);
    panel.classList.toggle('is-active', panel.id === `${tab}-tab`);
  });
}

async function loadDashboard(scanId = null) {
  const url = new URL('/analytics/embed/data', window.location.origin);
  if (scanId) url.searchParams.set('scan_id', scanId);
  url.searchParams.set('recent_scans_page', String(recentScansPage));
  url.searchParams.set('recent_scans_page_size', String(RECENT_SCANS_PAGE_SIZE));

  try {
    const response = await fetch(url.toString());
    if (!response.ok) {
      setText('page-subtitle', 'The dashboard could not be loaded.');
      return;
    }

    const data = await response.json();
    currentDashboardState = data;
    currentSelectedScanId = data?.selected_scan_id || null;

    setText('page-title', data?.title || 'BCSentinel Analytics');
    setText('page-subtitle', data?.subtitle || '');
    setText('last-updated', `Last updated: ${formatDateTime(data?.last_updated)}`);
    setText('hero-eyebrow', data?.hero?.eyebrow || 'Assessment first. Monitoring when data quality needs control.');
    setText('hero-prefix', data?.hero?.headline_prefix || 'Your data health is');
    setText('hero-highlight', data?.hero?.headline_highlight || 'critical');
    setText('hero-suffix', data?.hero?.headline_suffix || '');
    renderHeroPoints(data?.hero?.points || []);
    const heroHighlight = byId('hero-highlight');
    if (heroHighlight) {
      heroHighlight.className = `hero-highlight ${scoreBand(data?.kpis?.health_score)}`;
    }

    setText('kpi-records', formatNumber(data?.kpis?.total_records));
    setText('kpi-affected-records', formatNumber(data?.kpis?.affected_records));
    setText('kpi-checks', formatNumber(data?.kpis?.checks_run));
    setText('kpi-issues', formatNumber(data?.kpis?.issues_count));
    setText('kpi-loss', formatCurrency(data?.kpis?.estimated_loss_eur));
    setText('kpi-roi', formatCurrency(data?.kpis?.roi_eur));

    renderProfileCards(data?.module_scores || [], data?.profile_cards || []);
    renderModuleVolume(data);
    renderRecentScans(data?.recent_scans || []);
    renderRecentScansPagination(data?.recent_scans_pagination || {});
    renderTrend('trend-chart', data?.score_trend || []);
    renderTrend('loss-chart', data?.loss_trend || [], true);
    renderFindings(data?.top_findings || [], Boolean(data?.visibility?.is_premium));
    renderUnlockPanel(data);
    renderSubscription(data);
    renderPricingBreakdown(data);
    applyPlanState(data);
  } catch (error) {
    console.error('loadDashboard failed:', error);
    setText('page-subtitle', 'The dashboard could not be loaded.');
  }
}

function registerEvents() {
  const scansBody = byId('recent-scans-body');
  if (scansBody) {
    scansBody.addEventListener('click', async (event) => {
      const row = event.target.closest('.scan-row');
      if (!row) return;
      const scanId = row.dataset.scanId;
      if (!scanId || scanId === currentSelectedScanId) return;
      await loadDashboard(scanId);
    });

    scansBody.addEventListener('keydown', async (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      const row = event.target.closest('.scan-row');
      if (!row) return;
      event.preventDefault();
      const scanId = row.dataset.scanId;
      if (!scanId || scanId === currentSelectedScanId) return;
      await loadDashboard(scanId);
    });
  }

  const prevButton = byId('recent-scans-prev');
  if (prevButton) {
    prevButton.addEventListener('click', async () => {
      if (recentScansPage <= 1) return;
      recentScansPage -= 1;
      await loadDashboard(currentSelectedScanId);
    });
  }

  const nextButton = byId('recent-scans-next');
  if (nextButton) {
    nextButton.addEventListener('click', async () => {
      recentScansPage += 1;
      await loadDashboard(currentSelectedScanId);
    });
  }

  document.querySelectorAll('.topnav-link').forEach((btn) => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab || 'overview'));
  });

  const upgradeButton = byId('upgrade-button');
  if (upgradeButton) {
    upgradeButton.addEventListener('click', async () => {
      await triggerBillingAction(currentDashboardState?.premium_unlock?.button_action || 'checkout');
    });
  }

  const subscriptionButton = byId('subscription-cta');
  if (subscriptionButton) {
    subscriptionButton.addEventListener('click', async () => {
      await triggerBillingAction(
        currentDashboardState?.subscription?.cta_action || 'checkout',
        currentDashboardState?.subscription?.cta_product_code || null,
      );
    });
  }

  const buyMoreButton = byId('buy-more-credits-cta');
  if (buyMoreButton) {
    buyMoreButton.addEventListener('click', async () => {
      await triggerBillingAction('checkout', 'assessment');
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  registerEvents();
  switchTab('overview');
  recentScansPage = 1;
  loadDashboard();
});
