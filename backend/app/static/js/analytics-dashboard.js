let currentSelectedScanId = null;
let currentSelectedIssueIndex = null;
let recentScansPage = 1;
const RECENT_SCANS_PAGE_SIZE = 12;
let currentDashboardState = null;
let currentDashboardLanguage = 'en';
let currentDashboardUi = {};

function byId(id) {
  return document.getElementById(id);
}

function formatNumber(value) {
  const number = Number(value);
  const safeNumber = Number.isFinite(number) ? number : 0;
  return new Intl.NumberFormat(currentDashboardLanguage === 'de' ? 'de-DE' : 'en-US').format(safeNumber);
}

function formatCurrency(value) {
  const number = Number(value);
  const safeNumber = Number.isFinite(number) ? number : 0;
  return new Intl.NumberFormat(currentDashboardLanguage === 'de' ? 'de-DE' : 'en-US', {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(safeNumber);
}

function formatKpiCurrency(value) {
  const number = Number(value);
  const safeNumber = Number.isFinite(number) ? number : 0;
  return new Intl.NumberFormat(currentDashboardLanguage === 'de' ? 'de-DE' : 'en-US', {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(safeNumber);
}

function safeNumber(value, defaultValue = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : defaultValue;
}

function formatPercent(value) {
  const number = safeNumber(value);
  return `${formatNumber(Math.round(number))}%`;
}

function firstFiniteNumber(values) {
  for (const value of values) {
    const number = Number(value);
    if (Number.isFinite(number)) return number;
  }
  return null;
}

function trendFromFields(source, keys) {
  if (!source || !Array.isArray(keys)) return null;
  return firstFiniteNumber(keys.map((key) => source?.[key]));
}

function trendFromSeries(items) {
  const values = Array.isArray(items)
    ? items.map((item) => Number(item?.value ?? item?.score ?? item?.amount)).filter(Number.isFinite)
    : [];
  if (values.length < 2) return null;
  const previous = values[values.length - 2];
  const latest = values[values.length - 1];
  if (!Number.isFinite(previous) || previous === 0 || !Number.isFinite(latest)) return null;
  return ((latest - previous) / Math.abs(previous)) * 100;
}

function renderKpiTrend(targetId, trendValue, options = {}) {
  const el = byId(targetId);
  if (!el) return;

  const emptyLabel = options.emptyLabel || 'No trend data yet';
  if (trendValue === null || trendValue === undefined || !Number.isFinite(Number(trendValue))) {
    el.className = 'stat-helper kpi-trend-line is-empty';
    el.textContent = emptyLabel;
    return;
  }

  const value = Number(trendValue);
  const isDown = value < 0;
  const variant = options.variant || (isDown ? 'negative' : 'positive');
  const arrow = isDown ? 'down' : 'up';
  el.className = `stat-helper kpi-trend-line kpi-trend-${variant}`;
  el.innerHTML = `
    <span class="kpi-trend-arrow kpi-trend-arrow-${arrow}" aria-hidden="true">${isDown ? '↓' : '↑'}</span>
    <strong>${escapeHtml(formatPercent(Math.abs(value)))}</strong>
    <span>vs. last month</span>
  `;
}

function t(key, fallback) {
  return currentDashboardUi?.[key] || fallback || key;
}

function setTextContent(selector, value) {
  const el = document.querySelector(selector);
  if (el) el.textContent = value;
}

function applyDashboardUi(ui, language) {
  currentDashboardLanguage = language === 'de' ? 'de' : 'en';
  currentDashboardUi = ui || {};
  document.documentElement.lang = currentDashboardLanguage;

  setTextContent('[data-tab="overview"] .nav-label', t('overview', 'Overview'));
  setTextContent('[data-tab="analytics"] .nav-label', t('analytics', 'Analytics'));
  setTextContent('[data-tab="scans"] .nav-label', t('scans', 'Scans'));
  setTextContent('[data-tab="issues"] .nav-label', t('issues', 'Issues'));
  setTextContent('[data-tab="actions"] .nav-label', t('actions', 'Actions'));
  setTextContent('[data-tab="reports"] .nav-label', t('reports', 'Reports'));
  setTextContent('[data-tab="subscription"] .nav-label', t('subscription', 'Subscription'));
  setTextContent('[data-tab="settings"] .nav-label', t('settings', 'Settings'));
  setTextContent('#current-plan-badge', t('credits_needed', 'Credits needed'));
  setTextContent('#subscription-plan-badge', t('credits_needed', 'Credits needed'));
  setTextContent('#page-subtitle', t('loading', 'Loading...'));

  const statLabels = document.querySelectorAll('.stats-grid .stat-label');
  const statHelpers = document.querySelectorAll('.stats-grid .stat-helper');
  const statLabelKeys = ['health_score', 'estimated_annual_loss', 'potential_savings', 'scanned_records', 'checks_run', 'issues_found'];
  const statHelperKeys = ['health_score_helper', 'estimated_annual_loss_helper', 'potential_savings_helper', 'scanned_records_helper', 'checks_run_helper', 'issues_found_helper'];
  statLabels.forEach((el, index) => { if (statLabelKeys[index]) el.textContent = t(statLabelKeys[index], el.textContent); });
  statHelpers.forEach((el, index) => { if (statHelperKeys[index]) el.textContent = t(statHelperKeys[index], el.textContent); });

  setTextContent('#profile-grid h3', t('module_scores', 'Data Scores by BC module'));
  setTextContent('#profile-grid .muted', t('module_scores_helper', 'Score per module - 0 to 100'));
  setTextContent('#module-volume-title', t('issues_by_module', 'Issues by BC module'));
  setTextContent('#module-volume-subtitle', t('issues_by_module_helper', 'Affected findings per module'));
  setTextContent('#scan-table-panel h3', t('recent_scans', 'Recent Scans'));
  setTextContent('#scan-table-panel .muted', t('recent_scans_helper', 'Click a scan to load it'));
  setTextContent('#recent-scans-prev', t('previous', 'Previous'));
  setTextContent('#recent-scans-next', t('next', 'Next'));
  setTextContent('#score-trend-panel h3', t('score_trend', 'Score Trend'));
  setTextContent('#score-trend-panel .muted', t('score_trend_helper', 'History of selected scans'));
  setTextContent('#loss-trend-panel h3', t('loss_trend', 'Loss Trend'));
  setTextContent('#loss-trend-panel .muted', t('loss_trend_helper', 'Estimated annual impact'));
  setTextContent('#access-unlock-panel h3', t('paid_scan_access', 'Paid scan access'));
  setTextContent('.preview-title', t('scan_preview', 'Scan preview'));
  setTextContent('.preview-title-row .muted', t('scan_preview_helper', 'Record details, recommendations, actions'));
  setTextContent('.pricing-breakdown-title', t('estimated_monitoring_pricing', 'Estimated monitoring pricing'));
  setTextContent('#access-findings-panel h3', t('findings', 'Findings'));
  setTextContent('#access-findings-panel .muted', t('findings_helper', 'Visible with paid scan access, actionable in Business Central'));
  setTextContent('#subscription-tab .subscription-page-intro h2', 'Subscription & Access');
}

function updatePageHeader(tab) {
  const data = currentDashboardState || {};
  const companyName = getDashboardCompanyName(data);
  const pageCopy = {
    overview: ['Overview', 'Executive overview of your data quality and business impact'],
    analytics: ['Analytics', 'Score, loss and distribution analysis for the selected scan'],
    scans: ['Scans', 'Available scan runs and dashboard context'],
    issues: ['Issues', 'Review detected data quality issues, business impact and affected records.'],
    'issue-detail': ['Issue detail', 'Detailed issue context, impact and recommendation'],
    actions: ['Actions', 'Prioritized actions to reduce data quality risk and business impact.'],
    reports: ['Reports', 'Generate and review executive, operational and impact reports.'],
    subscription: ['Subscription & Access', 'Manage your product access, monitoring status and available scan credits.'],
    settings: ['Settings', 'Configure your account and preferences'],
  };
  const [title, fallbackSubtitle] = pageCopy[tab] || pageCopy.overview;
  setText('page-title', title);
  setText('page-subtitle', fallbackSubtitle);

  const companyEl = byId('overview-company-name');
  if (companyEl) {
    companyEl.textContent = tab === 'overview' ? companyName : '';
    companyEl.classList.toggle('hidden', tab !== 'overview' || !companyName);
  }
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
    host.innerHTML = `<div class="empty-state">${escapeHtml(t('no_module_scores', 'No module scores are available yet.'))}</div>`;
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

function renderIssueGroups(items, emptyMessage = t('no_module_data', 'No module data is available for this scan.')) {
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

  renderIssueGroups(issueGroups, t('no_module_data', 'No module issue counts are available for this scan.'));
}
function renderTrend(containerId, items, asCurrency = false, emptyMessage = t('no_trend_data', 'No trend data available yet.')) {
  const host = byId(containerId);
  if (!host) return;
  host.innerHTML = '';

  if (!Array.isArray(items) || items.length < 2) {
    host.innerHTML = `<div class="empty-state executive-empty">${escapeHtml(emptyMessage)}</div>`;
    return;
  }

  const safeItems = items.map((item) => ({
    label: item?.label || '',
    value: safeNumber(item?.value),
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

function scoreLabel(score) {
  const band = scoreBand(score);
  const labels = {
    critical: 'Critical',
    warning: 'Needs attention',
    moderate: 'Moderate',
    good: 'Good',
    excellent: 'Excellent',
  };
  return labels[band] || 'Not calculated yet';
}

function getDashboardCompanyName(data) {
  const settings = data?.settings || data?.tenant_settings || {};
  const profile = data?.tenant_profile || data?.profile || {};
  const subtitleParts = String(data?.subtitle || '').split(' - ');
  return firstPresent(
    settings.company,
    settings.company_name,
    data?.company,
    data?.company_name,
    profile.company,
    profile.company_name,
    subtitleParts[0],
  );
}

function renderOverviewContext(data) {
  const host = byId('overview-context');
  if (!host) return;
  host.innerHTML = '';
  host.classList.add('hidden');
}

function renderOverviewKpis(data) {
  const kpis = data?.kpis || {};
  const healthScore = Math.max(0, Math.min(100, safeNumber(kpis.health_score)));
  const totalRecords = safeNumber(kpis.total_records);
  const checksRun = safeNumber(kpis.checks_run);
  const estimatedLoss = safeNumber(kpis.estimated_loss_eur);
  const potentialSaving = safeNumber(kpis.potential_saving_eur);
  const hasScan = Boolean(data?.selected_scan_id);
  const healthTrend = trendFromFields(kpis, ['health_score_change_percent', 'health_score_trend_percent', 'health_score_delta_percent', 'score_change_percent']) ?? trendFromSeries(data?.score_trend);
  const lossTrend = trendFromFields(kpis, ['estimated_loss_change_percent', 'estimated_loss_trend_percent', 'estimated_loss_delta_percent', 'loss_change_percent']) ?? trendFromSeries(data?.loss_trend);
  const savingsTrend = trendFromFields(kpis, ['potential_saving_change_percent', 'potential_savings_change_percent', 'potential_saving_trend_percent', 'potential_savings_trend_percent']);
  const recordsTrend = trendFromFields(kpis, ['total_records_change_percent', 'records_change_percent', 'scanned_records_change_percent']);
  const checksTrend = trendFromFields(kpis, ['checks_run_change_percent', 'validation_checks_change_percent', 'checks_change_percent']);

  setText('kpi-health-label-title', 'Health Score');
  setText('kpi-loss-label-title', 'Estimated Loss');
  setText('kpi-savings-label-title', 'Potential Savings');
  setText('kpi-records-label-title', 'Total Records');
  setText('kpi-checks-label-title', 'Validation Checks');
  setText('kpi-health-score', formatNumber(healthScore));
  setText('kpi-health-label', hasScan ? scoreLabel(healthScore) : 'Not calculated yet');
  const healthLabelEl = byId('kpi-health-label');
  if (healthLabelEl) healthLabelEl.className = `kpi-status ${hasScan ? scoreBand(healthScore) : 'is-empty'}`;
  renderKpiTrend('kpi-health-helper', hasScan ? healthTrend : null, { emptyLabel: hasScan ? 'No trend data yet' : 'Run a validation check to unlock this KPI' });
  const healthGauge = byId('kpi-health-gauge');
  if (healthGauge) {
    healthGauge.style.setProperty('--score', String(healthScore));
    healthGauge.className = `health-gauge ${scoreBand(healthScore)}`;
  }
  const healthScoreEl = byId('kpi-health-score');
  if (healthScoreEl) healthScoreEl.className = `stat-value score-value ${scoreBand(healthScore)}`;

  setText('kpi-loss', hasScan ? formatKpiCurrency(estimatedLoss) : 'Not calculated yet');
  renderKpiTrend('kpi-loss-helper', hasScan && estimatedLoss > 0 ? lossTrend : null, {
    emptyLabel: hasScan ? 'No trend data yet' : 'Available after full analysis',
    variant: Number(lossTrend) < 0 ? 'positive' : 'negative',
  });
  setText('kpi-savings', hasScan ? formatKpiCurrency(potentialSaving) : 'Not calculated yet');
  renderKpiTrend('kpi-savings-helper', hasScan && potentialSaving > 0 ? savingsTrend : null, { emptyLabel: hasScan ? 'No trend data yet' : 'Run a validation check to unlock this KPI' });
  setText('kpi-records', hasScan ? formatNumber(totalRecords) : 'Not calculated yet');
  renderKpiTrend('kpi-records-helper', hasScan && totalRecords > 0 ? recordsTrend : null, { emptyLabel: hasScan ? 'No trend data yet' : 'Available after scan sync' });
  setText('kpi-checks', hasScan ? formatNumber(checksRun) : 'Not calculated yet');
  renderKpiTrend('kpi-checks-helper', hasScan && checksRun > 0 ? checksTrend : null, { emptyLabel: hasScan ? 'No trend data yet' : 'Run a validation check to unlock this KPI' });
}

function renderIssueDistribution(data) {
  const host = byId('overview-issue-distribution');
  if (!host) return;
  const summary = data?.free_insights?.active_issues_summary || {};
  const rows = [
    ['critical', 'Critical', safeNumber(summary.critical)],
    ['high', 'High', safeNumber(summary.high)],
    ['medium', 'Medium', safeNumber(summary.medium)],
    ['low', 'Low', safeNumber(summary.low)],
  ];
  const total = rows.reduce((sum, row) => sum + row[2], 0);

  if (total <= 0) {
    host.innerHTML = `<div class="empty-state executive-empty">No issue distribution is available for this scan yet.</div>`;
    return;
  }

  host.innerHTML = rows.map(([key, label, count]) => {
    const percent = total > 0 ? (count / total) * 100 : 0;
    return `
      <div class="severity-row">
        <div><span class="severity-dot severity-dot-${key}"></span><span>${escapeHtml(label)}</span></div>
        <strong>${formatNumber(count)}</strong>
        <div class="distribution-track"><div class="distribution-fill severity-fill-${key}" style="width:${Math.max(percent, count > 0 ? 4 : 0)}%"></div></div>
        <span class="muted">${formatPercent(percent)}</span>
      </div>
    `;
  }).join('');
}

function normalizeDistributionItems(items) {
  return Array.isArray(items)
    ? items.filter(Boolean).map((item) => ({
        name: item?.name || item?.label || '',
        count: safeNumber(item?.count ?? item?.value),
        percent: safeNumber(item?.percent),
      })).filter((item) => item.name)
    : [];
}

function formatCompactRecords(value) {
  const number = safeNumber(value);
  if (number >= 1000000) {
    const compact = number / 1000000;
    return `${new Intl.NumberFormat(currentDashboardLanguage === 'de' ? 'de-DE' : 'en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(compact)} Mio.`;
  }
  return formatNumber(number);
}

function normalizePercentDistribution(items) {
  const totalCount = items.reduce((sum, item) => sum + safeNumber(item.count), 0);
  const rawPercentTotal = items.reduce((sum, item) => sum + safeNumber(item.percent), 0);
  return items.map((item) => {
    const percent = item.percent > 0
      ? item.percent
      : (totalCount > 0 ? (item.count / totalCount) * 100 : 0);
    return {
      ...item,
      percent: rawPercentTotal > 100.5 && item.percent > 0 ? (item.percent / rawPercentTotal) * 100 : percent,
    };
  });
}

function renderModuleDistribution(data) {
  const host = byId('overview-module-distribution');
  if (!host) return;
  const issueItems = normalizeDistributionItems(data?.free_insights?.module_distribution);
  const recordItems = normalizeDistributionItems(data?.free_insights?.records_by_module);
  const moduleItems = issueItems.length > 0 ? issueItems : normalizeDistributionItems(data?.issue_groups);

  if (moduleItems.length === 0 && recordItems.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">Module distribution will appear after scan results are available.</div>`;
    return;
  }

  const maxRecords = Math.max(...recordItems.map((item) => item.count), 1);
  const colors = ['#003c9e', '#2d56e8', '#2f7bff', '#5968f4', '#6da0ff'];
  const issueDistribution = normalizePercentDistribution(moduleItems.slice(0, 5));
  let start = 0;
  const donutSegments = issueDistribution.map((item, index) => {
    const end = start + Math.max(safeNumber(item.percent), 0);
    const segment = `${colors[index % colors.length]} ${start}% ${end}%`;
    start = end;
    return segment;
  });
  if (start < 100) donutSegments.push(`#edf2f8 ${start}% 100%`);
  const donutBackground = donutSegments.join(', ') || '#edf2f8 0% 100%';
  const issueMarkup = issueDistribution.length > 0 ? `
    <div class="module-donut-wrap">
      <div class="module-donut" style="--module-donut:${escapeHtml(donutBackground)}">
        <div><strong>100%</strong><span>Issues</span></div>
      </div>
      <div class="module-legend">
        ${issueDistribution.map((item, index) => `
          <div class="module-legend-row">
            <span class="module-legend-dot" style="background:${colors[index % colors.length]}"></span>
            <span>${escapeHtml(item.name)}</span>
            <strong>${formatPercent(item.percent)}</strong>
          </div>
        `).join('')}
      </div>
    </div>
  ` : `<div class="empty-state executive-empty compact-empty">No issue module data yet.</div>`;
  const recordMarkup = recordItems.slice(0, 5).map((item) => `
    <div class="module-record-row">
      <span>${escapeHtml(item.name)}</span>
      <div>
        <div class="distribution-track"><div class="distribution-fill record-fill" style="width:${Math.max((item.count / maxRecords) * 100, 3)}%"></div></div>
      </div>
      <strong>${formatCompactRecords(item.count)}</strong>
    </div>
  `).join('') || `<div class="empty-state executive-empty compact-empty">No record module data yet.</div>`;

  host.innerHTML = `
    <div class="module-distribution-column module-issues-column">
      <h4>Issue Distribution (by %)</h4>
      ${issueMarkup}
    </div>
    <div class="module-distribution-column module-records-column">
      <h4>Records by Module</h4>
      ${recordMarkup}
      <button type="button" class="module-view-button" data-jump-tab="analytics">View all modules <span aria-hidden="true">&rarr;</span></button>
    </div>
  `;
  const viewButton = host.querySelector('.module-view-button');
  if (viewButton) viewButton.addEventListener('click', () => switchTab('analytics'));
}

function renderOverviewRecentIssues(data) {
  const host = byId('overview-recent-issues');
  if (!host) return;
  const isPremium = Boolean(data?.visibility?.is_premium);
  const premiumItems = Array.isArray(data?.top_findings) ? data.top_findings : [];
  const freeItems = Array.isArray(data?.free_insights?.top_findings) ? data.free_insights.top_findings : [];
  const severityRank = { critical: 0, high: 1, medium: 2, low: 3 };
  const sourceItems = (isPremium ? premiumItems : freeItems)
    .filter(Boolean)
    .sort((a, b) => {
      const severityA = severityRank[String(a?.severity || '').toLowerCase()] ?? 9;
      const severityB = severityRank[String(b?.severity || '').toLowerCase()] ?? 9;
      return severityA - severityB || safeNumber(b?.impact_eur) - safeNumber(a?.impact_eur);
    });
  const criticalItems = sourceItems.filter((item) => ['critical', 'high'].includes(String(item?.severity || '').toLowerCase()));
  const items = (criticalItems.length > 0 ? criticalItems : sourceItems).slice(0, 5);

  if (items.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">Recent critical issues will appear after the next scan.</div>`;
    return;
  }

  host.innerHTML = items.map((item, index) => {
    const title = item?.title || `Issue ${index + 1}`;
    const moduleName = item?.group || item?.module || 'Module pending';
    const severity = String(item?.severity || 'low').toLowerCase();
    const impact = safeNumber(item?.impact_eur);
    const count = safeNumber(item?.count);
    return `
      <div class="overview-list-row">
        <div>
          <strong>${escapeHtml(title)}</strong>
          <span>${escapeHtml(moduleName)} - ${formatNumber(count)} affected</span>
        </div>
        <div class="overview-row-meta">
          <span class="severity severity-${escapeHtml(severity)}">${escapeHtml(item?.severity_label || severity.toUpperCase())}</span>
          <strong>${impact > 0 ? formatCurrency(impact) : 'Impact pending'}</strong>
        </div>
      </div>
    `;
  }).join('') + (!isPremium ? `<div class="placeholder-note">Full Analysis unlocks record-level issue details and recommended actions.</div>` : '');
}

function businessImpactIcon(name) {
  const key = String(name || '').toLowerCase();
  if (key.includes('finance') || key.includes('finanz')) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h16"/><path d="M6 18V9"/><path d="M10 18V9"/><path d="M14 18V9"/><path d="M18 18V9"/><path d="M3.5 9h17L12 4z"/></svg>';
  }
  if (key.includes('master') || key.includes('data') || key.includes('stamm')) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/></svg>';
  }
  if (key.includes('sales') || key.includes('verkauf')) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16"/><path d="M6 16l3-3 3 2 5-7"/><path d="M6 9v7"/><path d="M12 11v5"/><path d="M18 7v9"/></svg>';
  }
  if (key.includes('purchas') || key.includes('einkauf')) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 6h2l1.4 8.2a1.5 1.5 0 0 0 1.5 1.3h6.8a1.5 1.5 0 0 0 1.4-1l1.4-4.5H8.2"/><circle cx="10" cy="20" r="1"/><circle cx="17" cy="20" r="1"/></svg>';
  }
  if (key.includes('inventory') || key.includes('lager')) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5"/><path d="M12 12v9"/></svg>';
  }
  return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16"/><path d="M7 16V9"/><path d="M12 16V5"/><path d="M17 16v-4"/></svg>';
}

function businessImpactRows(data) {
  const freeImpactItems = Array.isArray(data?.free_insights?.business_impacts) ? data.free_insights.business_impacts : [];
  const sourceItems = freeImpactItems.length > 0
    ? freeImpactItems
    : (Array.isArray(data?.top_findings) ? data.top_findings : []);
  const grouped = new Map();

  sourceItems.forEach((item) => {
    const name = item?.group || item?.module || item?.module_name || item?.category || item?.title || '';
    const impact = safeNumber(item?.impact_eur ?? item?.estimated_loss_eur ?? item?.estimated_impact_eur);
    if (!name || impact <= 0) return;
    const current = grouped.get(name) || { name, impact: 0 };
    current.impact += impact;
    grouped.set(name, current);
  });

  if (grouped.size === 0) {
    const estimatedLoss = safeNumber(data?.kpis?.estimated_loss_eur);
    const modules = normalizeDistributionItems(data?.free_insights?.module_distribution);
    const total = modules.reduce((sum, item) => sum + safeNumber(item.count), 0);
    if (estimatedLoss > 0 && total > 0) {
      modules.forEach((item) => {
        grouped.set(item.name, {
          name: item.name,
          impact: estimatedLoss * (safeNumber(item.count) / total),
        });
      });
    }
  }

  return Array.from(grouped.values())
    .sort((a, b) => b.impact - a.impact)
    .slice(0, 5);
}

function renderBusinessImpact(data) {
  const host = byId('overview-business-impact');
  if (!host) return;
  const rows = businessImpactRows(data);

  if (!data?.selected_scan_id || rows.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">Business impact will be calculated after scan results are available.</div>`;
    return;
  }

  const maxImpact = Math.max(...rows.map((item) => item.impact), 1);

  host.innerHTML = `
    <div class="business-impact-breakdown">
      ${rows.map((item) => `
        <div class="business-impact-row">
          <span class="business-impact-icon">${businessImpactIcon(item.name)}</span>
          <span class="business-impact-name">${escapeHtml(item.name)}</span>
          <div class="distribution-track"><div class="distribution-fill" style="width:${Math.max((item.impact / maxImpact) * 100, 5)}%"></div></div>
          <strong>${formatKpiCurrency(item.impact)}</strong>
        </div>
      `).join('')}
    </div>
    <button type="button" class="business-impact-report-button">View full impact report <span aria-hidden="true">&rarr;</span></button>
  `;
  const reportButton = host.querySelector('.business-impact-report-button');
  if (reportButton) reportButton.addEventListener('click', () => switchTab('reports'));
}

function renderRecentScans(items) {
  const host = byId('recent-scans-body');
  if (!host) return;

  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = `<tr><td colspan="5" class="table-empty">${escapeHtml(t('no_scans', 'No scans available yet.'))}</td></tr>`;
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

function renderScansPage(data) {
  const host = byId('scans-page-body');
  if (!host) return;

  const items = Array.isArray(data?.recent_scans) ? data.recent_scans : [];
  if (items.length === 0) {
    host.innerHTML = `<tr><td colspan="6" class="table-empty">${escapeHtml(t('no_scans', 'No scans available yet.'))}</td></tr>`;
    return;
  }

  host.innerHTML = items.map((item) => {
    const statusLabel = item?.is_selected ? 'Loaded' : (item?.is_valid === false ? 'Incomplete' : 'Available');
    return `
      <tr class="scan-row${item?.is_selected ? ' is-selected' : ''}" data-scan-id="${escapeHtml(item?.scan_id)}" tabindex="0">
        <td>${escapeHtml(formatDateTime(item?.generated_at))}</td>
        <td>${escapeHtml(item?.scan_type)}</td>
        <td>${formatNumber(item?.data_score)}</td>
        <td>${formatNumber(item?.issues_count)}</td>
        <td><span class="access-chip ${item?.is_selected ? 'unlocked' : 'locked'}">${escapeHtml(statusLabel)}</span></td>
        <td>${escapeHtml(item?.headline || '')}</td>
      </tr>
    `;
  }).join('');
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
  pageInfo.textContent = `${t('page', 'Page')} ${page} / ${totalPages}`;
  container.classList.toggle('hidden', totalItems <= RECENT_SCANS_PAGE_SIZE);
}

function renderFindings(items, isPremium) {
  const host = byId('findings-body');
  if (!host) return;

  if (!Array.isArray(items) || items.length === 0) {
    host.innerHTML = `<tr><td colspan="6" class="table-empty">${escapeHtml(t('no_findings', 'No findings are available for this scan.'))}</td></tr>`;
    return;
  }

  host.innerHTML = items.map((item) => {
    const accessClass = isPremium ? 'unlocked' : 'locked';
    const accessLabel = isPremium ? t('open_in_bc', 'Open in BC') : t('paid_access', 'Paid Access');
    const openInBcUrl = String(item?.open_in_bc_url || '');
    warnOnInvalidBcCompanyFormat(openInBcUrl);
    const accessMarkup = isPremium && openInBcUrl
      ? `<a href="${escapeHtml(openInBcUrl)}" class="access-chip ${accessClass}" target="_blank" rel="noopener noreferrer">${accessLabel}</a>`
      : `<span class="access-chip ${accessClass}">${accessLabel}</span>`;
    return `
      <tr>
        <td><strong>${escapeHtml(item?.title)}</strong></td>
        <td>${escapeHtml(item?.group)}</td>
        <td><span class="severity severity-${escapeHtml(item?.severity)}">${escapeHtml(item?.severity_label || String(item?.severity || '').toUpperCase())}</span></td>
        <td>${formatNumber(item?.count)}</td>
        <td>${formatCurrency(item?.impact_eur)}</td>
        <td>${accessMarkup}</td>
      </tr>
    `;
  }).join('');
}

function normalizeIssueSeverity(value) {
  const severity = String(value || '').trim().toLowerCase();
  if (['critical', 'high', 'medium', 'low'].includes(severity)) return severity;
  return severity ? 'unknown' : 'low';
}

function issueSeverityLabel(value, fallback) {
  const normalized = normalizeIssueSeverity(value);
  if (fallback) return String(fallback);
  const labels = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    unknown: 'Unknown',
  };
  return labels[normalized] || 'Unknown';
}

function normalizeIssueItem(item, index, isLocked, data) {
  const severity = normalizeIssueSeverity(item?.severity ?? item?.priority);
  const title = item?.title || item?.issue || item?.name || '';
  const group = item?.group || item?.module || item?.area || 'Module pending';
  const count = safeNumber(item?.count ?? item?.affected_records ?? item?.affected_count);
  const impact = safeNumber(item?.impact_eur ?? item?.estimated_loss_eur ?? item?.estimated_impact_eur ?? item?.potential_saving_eur);
  const potentialSaving = safeNumber(item?.potential_saving_eur ?? item?.potential_savings_eur);
  const status = String(item?.status || 'Open').trim() || 'Open';
  const recommendation = item?.recommendation || item?.recommendation_preview || item?.action || item?.suggested_action || '';
  const description = item?.description || item?.details || item?.summary || '';
  const openInBcUrl = String(item?.open_in_bc_url || item?.open_in_business_central_url || item?.bc_url || '');
  warnOnInvalidBcCompanyFormat(openInBcUrl);

  return {
    id: item?.code || item?.id || `issue-${index + 1}`,
    rawTitle: title || 'Issue detail',
    title: isLocked ? 'Premium issue details' : (title || 'Issue'),
    group: group || 'General',
    severity,
    severityLabel: issueSeverityLabel(severity, item?.severity_label),
    count,
    impact,
    potentialSaving,
    status,
    detectedOn: item?.detected_on || item?.detected_at || data?.last_updated || '',
    description,
    recommendation,
    scoreImpact: item?.score_impact || item?.score_impact_points || item?.health_score_impact || '',
    openInBcUrl,
    locked: isLocked,
  };
}

function collectIssueCandidates(data, isLocked) {
  const pageItems = Array.isArray(data?.issues_page?.items) ? data.issues_page.items : [];
  const premiumItems = Array.isArray(data?.top_findings) ? data.top_findings : [];
  const freeItems = Array.isArray(data?.free_insights?.top_findings) ? data.free_insights.top_findings : [];
  const previewItems = Array.isArray(data?.premium_preview_findings) ? data.premium_preview_findings : [];

  if (!isLocked && pageItems.length > 0) return pageItems;
  if (!isLocked && premiumItems.length > 0) return premiumItems;
  if (freeItems.length > 0) return freeItems;
  if (previewItems.length > 0) return previewItems;
  return pageItems.length > 0 ? pageItems : [];
}

function normalizeIssuesForPage(data) {
  const page = data?.issues_page || {};
  const isLocked = Boolean(page.locked || data?.pages?.issues?.locked || !data?.visibility?.is_premium);
  return collectIssueCandidates(data, isLocked)
    .filter(Boolean)
    .map((item, index) => normalizeIssueItem(item, index, isLocked, data));
}

function severityCountsForIssues(data, normalizedItems) {
  const summary = data?.free_insights?.active_issues_summary || {};
  const counts = {
    critical: safeNumber(summary.critical),
    high: safeNumber(summary.high),
    medium: safeNumber(summary.medium),
    low: safeNumber(summary.low),
  };
  const hasSummary = Object.values(counts).some((value) => value > 0);
  if (hasSummary) return counts;

  normalizedItems.forEach((item) => {
    const severity = normalizeIssueSeverity(item?.severity);
    if (severity in counts) counts[severity] += 1;
  });
  return counts;
}

function renderIssuesMeta(data, normalizedItems, isLocked) {
  const host = byId('issues-page-meta');
  if (!host) return;
  const counts = severityCountsForIssues(data, normalizedItems);
  const totalFromSummary = Object.values(counts).reduce((sum, value) => sum + value, 0);
  const totalIssues = safeNumber(data?.kpis?.issues_count, totalFromSummary || normalizedItems.length);
  const accessLabel = isLocked ? 'Locked access' : 'Full issue access';
  const scanLabel = data?.last_updated ? `Last scan ${formatDateTime(data.last_updated)}` : 'No scan timestamp';

  host.innerHTML = `
    <span class="placeholder-status">${formatNumber(totalIssues)} Issues</span>
    <span class="placeholder-status">${escapeHtml(scanLabel)}</span>
    <span class="placeholder-status">${escapeHtml(accessLabel)}</span>
  `;
}

function renderIssueSeverityCards(data, normalizedItems) {
  const host = byId('issues-severity-cards');
  if (!host) return;
  const counts = severityCountsForIssues(data, normalizedItems);
  const cards = [
    ['critical', 'Critical', counts.critical],
    ['high', 'High', counts.high],
    ['medium', 'Medium', counts.medium],
    ['low', 'Low', counts.low],
  ];

  host.innerHTML = cards.map(([key, label, count]) => `
    <article class="stat-card panel issue-severity-card issue-severity-${key}">
      <div class="stat-label">${escapeHtml(label)}</div>
      <div class="stat-value">${formatNumber(count)}</div>
      <div class="stat-helper">Detected ${escapeHtml(label.toLowerCase())} issues</div>
    </article>
  `).join('');
}

function issueInfoRows(issue) {
  return [
    ['Issue Code', issue.id],
    ['Module / Category', issue.group || 'General'],
    ['Severity', issue.severityLabel],
    ['Status', issue.status || 'Open'],
    ['Affected Records', issue.locked ? 'Locked' : formatNumber(issue.count)],
    ['Estimated Impact / Loss', issue.locked ? 'Locked' : (issue.impact > 0 ? formatCurrency(issue.impact) : 'Not calculated yet')],
    ['Last Scan / Last Updated', issue.detectedOn ? formatDateTime(issue.detectedOn) : 'Not available'],
  ];
}

function detailSection(title, body, extraClass = '') {
  return `
    <article class="panel issue-detail-card ${escapeHtml(extraClass)}">
      <h3>${escapeHtml(title)}</h3>
      ${body}
    </article>
  `;
}

function renderIssueDetail(issue) {
  const host = byId('issue-detail-content');
  if (!host) return;

  if (!issue) {
    host.innerHTML = `<div class="empty-state executive-empty">Issue detail is available from the Issues page.</div>`;
    return;
  }

  const title = issue.locked ? 'Premium issue details' : (issue.title || issue.rawTitle || 'Issue detail');
  const affectedLabel = issue.locked ? 'Locked' : formatNumber(issue.count);
  const lossLabel = issue.locked ? 'Locked' : (issue.impact > 0 ? formatCurrency(issue.impact) : 'Not calculated yet');
  const description = issue.locked
    ? 'Detailed description is available after the full analysis.'
    : (issue.description || 'Detailed description is available after the full analysis.');
  const recommendation = issue.locked
    ? 'Recommendation will be generated after the full analysis.'
    : (issue.recommendation || 'Recommendation will be generated after the full analysis.');
  const scoreImpact = issue.locked
    ? 'Score impact details will appear when available.'
    : (issue.scoreImpact ? String(issue.scoreImpact) : 'Score impact details will appear when available.');
  const businessImpactBody = issue.locked
    ? `<div class="locked-detail-state">Business impact details are protected for the current access level.</div>`
    : `
      <div class="business-impact-grid">
        <div><span>Estimated Loss</span><strong>${escapeHtml(lossLabel)}</strong></div>
        <div><span>Affected Records</span><strong>${escapeHtml(affectedLabel)}</strong></div>
        <div><span>Severity</span><strong>${escapeHtml(issue.severityLabel)}</strong></div>
        <div><span>Potential Savings</span><strong>${issue.potentialSaving > 0 ? formatCurrency(issue.potentialSaving) : 'Not calculated yet'}</strong></div>
      </div>
    `;
  const openInBcMarkup = issue.openInBcUrl && !issue.locked
    ? `<a href="${escapeHtml(issue.openInBcUrl)}" class="primary-button issue-detail-bc-link" target="_blank" rel="noopener noreferrer">Open in Business Central</a>`
    : `<button type="button" class="pager-button issue-detail-bc-link" disabled>Business Central link not available</button>`;
  const unlockMarkup = issue.locked
    ? `<div class="issues-locked-note issue-detail-lock">
        <strong>Unlock full issue details</strong>
        <span>Full Analysis, Validation Check or Monitoring unlocks protected issue details and recommendations.</span>
        <button type="button" class="pager-button issue-detail-unlock-button">Unlock full issue details</button>
      </div>`
    : '';

  const informationRows = issueInfoRows(issue).map(([label, value]) => `
    <div class="issue-detail-info-row">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value || 'Not available')}</strong>
    </div>
  `).join('');

  host.innerHTML = `
    <section class="panel issue-detail-hero ${issue.locked ? 'is-locked-detail' : ''}">
      <div>
        <span class="section-kicker">Issue detail</span>
        <h2>${escapeHtml(title)}</h2>
        <div class="issue-detail-meta">
          <span>${escapeHtml(issue.group || 'General')}</span>
          <span class="severity severity-${escapeHtml(issue.severity)}">${escapeHtml(issue.severityLabel)}</span>
          <span class="status-badge status-open">${escapeHtml(issue.status || 'Open')}</span>
        </div>
      </div>
      <div class="issue-detail-summary">
        <div><span>Affected Records</span><strong>${escapeHtml(affectedLabel)}</strong></div>
        <div><span>Estimated Loss</span><strong>${escapeHtml(lossLabel)}</strong></div>
      </div>
    </section>
    ${unlockMarkup}
    <section class="issue-detail-grid">
      ${detailSection('Issue Information', `<div class="issue-detail-info">${informationRows}</div>`)}
      ${detailSection('Description', `<p>${escapeHtml(description)}</p>`)}
      ${detailSection('Business Impact', businessImpactBody)}
      ${detailSection('Score Impact', `<p>${escapeHtml(scoreImpact)}</p>`)}
      ${detailSection('Recommendation', `<p>${escapeHtml(recommendation)}</p>${openInBcMarkup}`, 'issue-detail-recommendation')}
    </section>
  `;
}

function openIssueDetail(index) {
  const items = normalizeIssuesForPage(currentDashboardState || {});
  const issue = items[index] || null;
  currentSelectedIssueIndex = issue ? index : null;
  renderIssueDetail(issue);
  switchTab('issue-detail');
}

function renderIssuesPage(data) {
  const host = byId('issues-page-body');
  if (!host) return;
  const page = data?.issues_page || {};
  const isLocked = Boolean(page.locked || data?.pages?.issues?.locked || !data?.visibility?.is_premium);
  const items = normalizeIssuesForPage(data);
  const lockedNote = byId('issues-locked-note');
  const unlockButton = byId('issues-unlock-button');

  renderIssuesMeta(data, items, isLocked);
  renderIssueSeverityCards(data, items);

  if (lockedNote) lockedNote.classList.toggle('hidden', !isLocked);
  if (unlockButton) unlockButton.classList.toggle('hidden', !isLocked);

  if (items.length === 0) {
    host.innerHTML = `<tr><td colspan="7" class="table-empty">No issues detected in the latest scan.</td></tr>`;
    return;
  }

  host.innerHTML = items.map((item, index) => `
    <tr class="${item.locked ? 'issue-row-locked' : ''}">
      <td>
        <strong>${escapeHtml(item.title)}</strong>
        <div class="muted">${item.locked ? 'Details protected by current access level' : `Issue ID ${escapeHtml(item.id)}`}</div>
      </td>
      <td>${escapeHtml(item.group)}</td>
      <td><span class="severity severity-${escapeHtml(item.severity)}">${escapeHtml(item.severityLabel)}</span></td>
      <td>${item.locked ? '<span class="locked-value">Locked</span>' : formatNumber(item.count)}</td>
      <td>${item.locked ? '<span class="locked-value">Locked</span>' : formatCurrency(item.impact)}</td>
      <td><span class="status-badge status-open">${escapeHtml(item.status)}</span></td>
      <td>
        <button type="button" class="pager-button issue-detail-button" data-issue-index="${index}">
          ${escapeHtml(item.locked ? 'View locked details' : 'View Details')}
        </button>
      </td>
    </tr>
  `).join('');

  if (currentSelectedIssueIndex !== null) {
    renderIssueDetail(items[currentSelectedIssueIndex] || null);
  }
}

function deriveActionText(item, issue) {
  const explicitAction = item?.action || item?.suggested_action || item?.recommendation || item?.recommendation_preview || issue?.recommendation;
  if (explicitAction) return String(explicitAction);
  const title = issue?.rawTitle || issue?.title || item?.issue || item?.title || '';
  if (title) return `Review and resolve ${title}`;
  return 'Review affected records and resolve the underlying setup issue in Business Central.';
}

function deriveActionEffort(item, issue) {
  const explicitEffort = item?.effort || item?.estimated_effort;
  if (explicitEffort) return String(explicitEffort);
  const severity = normalizeIssueSeverity(item?.priority || issue?.severity);
  const affected = safeNumber(issue?.count ?? item?.count ?? item?.affected_records);
  if (severity === 'critical' || severity === 'high' || affected >= 1000) return 'Medium';
  if (severity === 'medium') return 'Low / Medium';
  if (severity === 'low') return 'Low';
  return 'Not estimated';
}

function actionStatusLabel(item) {
  return String(item?.status || 'Open').trim() || 'Open';
}

function collectActionCandidates(data, isLocked) {
  const pageItems = Array.isArray(data?.actions_page?.items) ? data.actions_page.items : [];
  if (!isLocked && pageItems.length > 0) return pageItems;
  return normalizeIssuesForPage(data);
}

function normalizeActionsForPage(data) {
  const actionsPage = data?.actions_page || {};
  const isLocked = Boolean(actionsPage.locked || data?.pages?.actions?.locked || !data?.visibility?.is_premium);
  const issues = normalizeIssuesForPage(data);
  const issueByTitle = new Map(issues.map((issue) => [String(issue.rawTitle || issue.title || '').toLowerCase(), issue]));
  const candidates = collectActionCandidates(data, isLocked);

  return candidates.filter(Boolean).map((item, index) => {
    const explicitIssueTitle = item?.issue || item?.related_issue || item?.title || item?.name || '';
    const issue = item?.rawTitle || item?.openInBcUrl || item?.severityLabel
      ? item
      : (issueByTitle.get(String(explicitIssueTitle).toLowerCase()) || issues[index] || {});
    const priority = normalizeIssueSeverity(item?.priority || item?.severity || issue?.severity || 'medium');
    const saving = safeNumber(item?.potential_saving_eur ?? item?.potential_savings_eur ?? item?.impact_eur ?? issue?.potentialSaving ?? issue?.impact);
    const openInBcUrl = String(item?.open_in_bc_url || item?.open_in_business_central_url || item?.bc_url || issue?.openInBcUrl || '');
    warnOnInvalidBcCompanyFormat(openInBcUrl);

    return {
      action: isLocked ? 'Unlock to view exact action' : deriveActionText(item, issue),
      relatedIssue: isLocked ? 'Premium issue' : (explicitIssueTitle || issue?.rawTitle || issue?.title || 'Issue'),
      module: issue?.group || item?.module || item?.group || 'General',
      priority,
      priorityLabel: issueSeverityLabel(priority, item?.priority_label || item?.severity_label),
      effort: isLocked ? 'Locked' : deriveActionEffort(item, issue),
      potentialSaving: saving,
      status: actionStatusLabel(item),
      openInBcUrl,
      locked: isLocked,
    };
  });
}

function renderActionsMeta(data, actions, isLocked) {
  const host = byId('actions-page-meta');
  if (!host) return;
  const potentialSaving = safeNumber(data?.kpis?.potential_saving_eur) || actions.reduce((sum, item) => sum + safeNumber(item.potentialSaving), 0);
  const accessLabel = isLocked ? 'Locked access' : 'Full action access';
  host.innerHTML = `
    <span class="placeholder-status">${formatNumber(actions.length)} Actions</span>
    <span class="placeholder-status">${escapeHtml(potentialSaving > 0 ? formatCurrency(potentialSaving) : 'Saving pending')}</span>
    <span class="placeholder-status">${escapeHtml(accessLabel)}</span>
  `;
}

function renderActionsSummary(data, actions) {
  const host = byId('actions-summary-cards');
  if (!host) return;
  const recommended = actions.length;
  const highPriority = actions.filter((item) => ['critical', 'high'].includes(normalizeIssueSeverity(item.priority))).length;
  const potentialSaving = safeNumber(data?.kpis?.potential_saving_eur) || actions.reduce((sum, item) => sum + safeNumber(item.potentialSaving), 0);
  const openItems = actions.filter((item) => String(item.status || '').toLowerCase() === 'open').length;
  const cards = [
    ['Recommended Actions', formatNumber(recommended), 'Prioritized recommendations'],
    ['High Priority', formatNumber(highPriority), 'Critical and high priority'],
    ['Potential Saving', potentialSaving > 0 ? formatCurrency(potentialSaving) : 'Not calculated yet', 'Existing scan economics'],
    ['Open Items', formatNumber(openItems), 'Default open status'],
  ];

  host.innerHTML = cards.map(([label, value, helper]) => `
    <article class="stat-card panel action-summary-card">
      <div class="stat-label">${escapeHtml(label)}</div>
      <div class="stat-value">${escapeHtml(value)}</div>
      <div class="stat-helper">${escapeHtml(helper)}</div>
    </article>
  `).join('');
}

function renderActionsPage(data) {
  const host = byId('actions-page-body');
  if (!host) return;
  const page = data?.actions_page || {};
  const isLocked = Boolean(page.locked || data?.pages?.actions?.locked || !data?.visibility?.is_premium);
  const items = normalizeActionsForPage(data);
  const lockedNote = byId('actions-locked-note');
  const unlockButton = byId('actions-unlock-button');

  renderActionsMeta(data, items, isLocked);
  renderActionsSummary(data, items);

  if (lockedNote) lockedNote.classList.toggle('hidden', !isLocked);
  if (unlockButton) unlockButton.classList.toggle('hidden', !isLocked);

  if (items.length === 0) {
    host.innerHTML = `<tr><td colspan="8" class="table-empty">No recommended actions are available for the latest scan.</td></tr>`;
    return;
  }

  host.innerHTML = items.map((item) => {
    const savingLabel = item.locked ? '<span class="locked-value">Locked</span>' : (item.potentialSaving > 0 ? formatCurrency(item.potentialSaving) : 'Not calculated yet');
    const bcAction = item.openInBcUrl && !item.locked
      ? `<a href="${escapeHtml(item.openInBcUrl)}" class="pager-button action-bc-link" target="_blank" rel="noopener noreferrer">Open in BC</a>`
      : `<button type="button" class="pager-button action-bc-link" disabled>${escapeHtml(item.locked ? 'Unlock actions' : 'BC link unavailable')}</button>`;
    return `
    <tr class="${item.locked ? 'issue-row-locked' : ''}">
      <td><strong>${escapeHtml(item.action)}</strong></td>
      <td>${escapeHtml(item.relatedIssue)}</td>
      <td>${escapeHtml(item.module)}</td>
      <td><span class="severity severity-${escapeHtml(item.priority)}">${escapeHtml(item.priorityLabel)}</span></td>
      <td>${escapeHtml(item.effort)}</td>
      <td>${savingLabel}</td>
      <td><span class="status-badge status-open">${escapeHtml(item.status)}</span></td>
      <td>${bcAction}</td>
    </tr>
  `;
  }).join('');
}

function reportDefinitions() {
  return [
    {
      key: 'executive_summary',
      title: 'Executive Summary',
      description: 'Management-ready summary of health score, risks and business impact.',
      icon: 'ES',
    },
    {
      key: 'data_quality_report',
      title: 'Data Quality Report',
      description: 'Detailed overview of data quality KPIs, modules and distributions.',
      icon: 'DQ',
    },
    {
      key: 'issue_detail_report',
      title: 'Issue Detail Report',
      description: 'Detailed list of detected issues and affected records.',
      icon: 'ID',
    },
    {
      key: 'business_impact_report',
      title: 'Business Impact Report',
      description: 'Commercial impact, estimated loss and potential savings.',
      icon: 'BI',
    },
    {
      key: 'action_plan_report',
      title: 'Action Plan Report',
      description: 'Prioritized action plan for remediation.',
      icon: 'AP',
    },
    {
      key: 'trend_report',
      title: 'Trend Report',
      description: 'Monitoring trends for score, loss and issue development.',
      icon: 'TR',
      monitoringOnly: true,
    },
  ];
}

function firstPresent(...values) {
  return values.find((value) => String(value || '').trim());
}

function reportLinkFrom(item, links, key, type) {
  const linkSet = links?.[key] || links?.[item?.key] || {};
  if (type === 'pdf') {
    return firstPresent(item?.pdf_url, item?.pdf_report_url, linkSet.pdf_url, linkSet.pdf, linkSet.pdf_report_url);
  }
  return firstPresent(item?.html_url, item?.open_url, item?.url, item?.report_url, linkSet.html_url, linkSet.open_url, linkSet.url, linkSet.report_url);
}

function reportShareLinkCount(data) {
  const page = data?.reports_page || {};
  const links = data?.report_links || page.links || {};
  const candidates = [
    data?.share_url,
    data?.executive_share_url,
    page.share_url,
    links.share_url,
    links.executive_share_url,
    links.executive_summary?.share_url,
  ];
  return candidates.filter((value) => String(value || '').trim()).length;
}

function normalizeReportsForPage(data) {
  const page = data?.reports_page || {};
  const rawItems = Array.isArray(page.items) ? page.items : [];
  const byKey = new Map(rawItems.map((item) => [item?.key || String(item?.title || '').toLowerCase().replaceAll(' ', '_'), item]));
  const reportLinks = data?.report_links || page.links || {};
  const selectedScanId = firstPresent(data?.selected_scan_id, currentSelectedScanId, data?.latest_scan_id, data?.scan_id);
  const isLocked = Boolean(page.locked || data?.pages?.reports?.locked);
  const monitoringActive = Boolean(data?.product_access?.monitoring_active || data?.product_access?.can_use_monitoring);
  const historyCount = Math.max(
    Array.isArray(data?.recent_scans) ? data.recent_scans.length : 0,
    Array.isArray(data?.score_trend) ? data.score_trend.length : 0,
    Array.isArray(data?.loss_trend) ? data.loss_trend.length : 0,
  );
  const hasMonitoringHistory = monitoringActive && historyCount > 1;

  return {
    isLocked,
    selectedScanId,
    monitoringActive,
    hasMonitoringHistory,
    items: reportDefinitions().map((definition) => {
      const item = byKey.get(definition.key) || {};
      const accessAllowed = !isLocked && Boolean(item.available);
      let openUrl = reportLinkFrom(item, reportLinks, definition.key, 'open');
      let pdfUrl = reportLinkFrom(item, reportLinks, definition.key, 'pdf');

      if (definition.key === 'executive_summary' && accessAllowed && selectedScanId) {
        const safeScanId = encodeURIComponent(selectedScanId);
        openUrl = openUrl || `/reports/executive/${safeScanId}/html`;
        pdfUrl = pdfUrl || `/reports/executive/${safeScanId}/pdf`;
      }

      const hasLink = Boolean(openUrl || pdfUrl);
      let status = 'After scan';
      let statusClass = 'after-scan';
      let disabledLabel = 'Available after scan';
      let helper = selectedScanId ? 'Report link is not available in the current dashboard payload.' : 'Available after scan';

      if (isLocked) {
        status = 'Locked';
        statusClass = 'locked';
        disabledLabel = 'Unlock reports';
        helper = 'Protected report access is available on a paid product.';
      } else if (definition.monitoringOnly && !hasMonitoringHistory) {
        status = 'Monitoring only';
        statusClass = 'monitoring';
        disabledLabel = 'Available with monitoring history';
        helper = 'Available with monitoring history';
      } else if (accessAllowed && hasLink) {
        status = 'Available';
        statusClass = 'available';
        disabledLabel = '';
        helper = definition.key === 'executive_summary'
          ? 'Existing Executive Report endpoints are linked for this scan.'
          : 'Existing report link is available.';
      } else if (!selectedScanId) {
        helper = 'Available after scan';
      }

      return {
        ...definition,
        available: accessAllowed && hasLink && !(definition.monitoringOnly && !hasMonitoringHistory),
        openUrl: accessAllowed ? openUrl : '',
        pdfUrl: accessAllowed ? pdfUrl : '',
        status,
        statusClass,
        disabledLabel,
        helper,
      };
    }),
  };
}

function renderReportsMeta(data, normalized) {
  const host = byId('reports-page-meta');
  if (!host) return;
  const page = data?.reports_page || {};
  const accessLabel = normalized.isLocked ? 'Report Access: Locked' : 'Report Access: Active';
  const latestReport = firstPresent(page.latest_report_at, data?.latest_report_at, data?.last_report_at);
  host.innerHTML = [
    `<span class="placeholder-status">Latest Scan: ${escapeHtml(formatDateTime(data?.last_updated))}</span>`,
    `<span class="placeholder-status">${escapeHtml(accessLabel)}</span>`,
    `<span class="placeholder-status">Last Report: ${escapeHtml(latestReport ? formatDateTime(latestReport) : 'Not available')}</span>`,
  ].join('');
}

function renderReportsSummary(data, normalized) {
  const host = byId('reports-summary-cards');
  if (!host) return;
  const availableReports = normalized.items.filter((item) => item.available).length;
  const summaries = [
    ['Available Reports', `${availableReports} / ${normalized.items.length}`, normalized.isLocked ? 'Unlock reports to open protected outputs.' : 'Reports with existing usable links.'],
    ['Latest Scan', data?.last_updated ? formatDateTime(data.last_updated) : 'Available after scan', normalized.selectedScanId ? `Scan ${normalized.selectedScanId}` : 'No scan context available yet.'],
    ['Report Access', normalized.isLocked ? 'Locked' : 'Active', normalized.isLocked ? 'Open and PDF links stay protected.' : 'Existing report links can be opened.'],
    ['Share Links', formatNumber(reportShareLinkCount(data)), 'Only existing share links are counted. No share link is created here.'],
  ];

  host.innerHTML = summaries.map(([label, value, helper]) => `
    <article class="stat-card report-summary-card">
      <div class="stat-label">${escapeHtml(label)}</div>
      <div class="stat-value stat-value-small">${escapeHtml(value)}</div>
      <div class="stat-helper">${escapeHtml(helper)}</div>
    </article>
  `).join('');
}

function renderReportsPage(data) {
  const host = byId('reports-page-grid');
  if (!host) return;
  const normalized = normalizeReportsForPage(data);
  const lockedNote = byId('reports-locked-note');
  const unlockButton = byId('reports-unlock-button');

  renderReportsMeta(data, normalized);
  renderReportsSummary(data, normalized);

  if (lockedNote) lockedNote.classList.toggle('hidden', !normalized.isLocked);
  if (unlockButton) unlockButton.classList.toggle('hidden', !normalized.isLocked);

  host.innerHTML = normalized.items.map((item) => {
    const openButton = item.openUrl && item.available
      ? `<a href="${escapeHtml(item.openUrl)}" class="pager-button report-action-button" target="_blank" rel="noopener noreferrer">Open</a>`
      : `<button type="button" class="pager-button report-action-button" disabled>${escapeHtml(item.disabledLabel || 'Available after scan')}</button>`;
    const pdfButton = item.pdfUrl && item.available
      ? `<a href="${escapeHtml(item.pdfUrl)}" class="pager-button report-action-button" target="_blank" rel="noopener noreferrer">PDF</a>`
      : '';
    return `
      <article class="report-card report-center-card">
        <div class="report-card-header">
          <span class="report-card-icon">${escapeHtml(item.icon)}</span>
          <span class="report-status-badge report-status-${escapeHtml(item.statusClass)}">${escapeHtml(item.status)}</span>
        </div>
        <h4>${escapeHtml(item.title)}</h4>
        <p>${escapeHtml(item.description)}</p>
        <div class="report-card-helper">${escapeHtml(item.helper)}</div>
        <div class="report-card-actions">
          ${openButton}
          ${pdfButton}
        </div>
      </article>
    `;
  }).join('') || `<div class="empty-state executive-empty">${escapeHtml(t('no_findings', 'No reports are available for this scan.'))}</div>`;
}

function renderSettingsPageLegacy(data) {
  const host = byId('settings-grid');
  if (!host) return;
  const settings = data?.settings_page || {};
  const rows = [
    ['Tenant ID', settings.tenant_id || ''],
    ['Company', settings.company || ''],
    ['Language', settings.language || ''],
    ['Last Scan', formatDateTime(settings.last_scan)],
    ['Connection Status', settings.connection_status || ''],
  ];
  host.innerHTML = rows.map(([label, value]) => `
    <div class="subscription-card">
      <div class="stat-label">${escapeHtml(label)}</div>
      <div class="subscription-value stat-value-small">${escapeHtml(value || '—')}</div>
    </div>
  `).join('');
}

function maskIdentifier(value) {
  const raw = String(value || '').trim();
  if (!raw) return 'Not available';
  if (raw.length <= 8) return `${raw.slice(0, 2)}...${raw.slice(-2)}`;
  return `${raw.slice(0, 4)}...${raw.slice(-4)}`;
}

function renderSettingsPage(data) {
  const host = byId('settings-grid');
  if (!host) return;
  const settings = data?.settings_page || {};
  const access = data?.product_access || {};
  const profile = data?.profile || {};
  const subscription = data?.subscription || {};
  const subtitleParts = String(data?.subtitle || '').split(' - ');
  const company = firstPresent(settings.company, settings.company_name, data?.company, data?.company_name, profile.company, profile.company_name, subtitleParts[0]);
  const environment = firstPresent(settings.environment, data?.environment, profile.environment, subtitleParts[1]);
  const bcEnvironment = firstPresent(settings.bc_environment, data?.bc_environment, profile.bc_environment, environment);
  const language = firstPresent(settings.language, data?.language, profile.language, currentDashboardLanguage);
  const preferredLanguage = firstPresent(settings.preferred_language, data?.preferred_language, profile.preferred_language, language);
  const dateFormat = firstPresent(settings.date_format, data?.date_format, profile.date_format, subscription.date_format, 'Managed by Business Central / Tenant settings');
  const currency = firstPresent(settings.currency, data?.currency, profile.currency, subscription.currency, 'Managed by Business Central / Tenant settings');
  const theme = firstPresent(settings.theme, data?.theme, profile.theme, 'System default');
  const contactEmail = firstPresent(settings.contact_email, settings.tenant_contact_email, data?.contact_email, data?.tenant_contact_email, profile.contact_email, profile.tenant_contact_email, 'Not configured');
  const monitoringActive = Boolean(access.monitoring_active || access.can_use_monitoring || data?.monitoring_status === 'active');
  const notificationSettings = settings.notification_settings || data?.notification_settings || {};
  const pages = data?.pages || {};
  const dashboardAccess = Boolean(access.can_view_dashboard || !pages?.overview?.locked);
  const issueAccess = Boolean(access.can_view_issue_details || access.can_view_issues || !pages?.issues?.locked);
  const recordAccess = Boolean(access.can_view_record_details || access.can_view_records);

  const renderRows = (rows) => rows.map(([label, value, badge]) => `
    <div class="settings-row">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value || 'Not available')}</strong>
      ${badge ? `<em class="subscription-status-badge status-${escapeHtml(badge.className)}">${escapeHtml(badge.label)}</em>` : ''}
    </div>
  `).join('');

  const renderSection = (title, helper, rows, extra = '') => `
    <article class="panel settings-section ${escapeHtml(extra)}">
      <div class="panel-header">
        <div>
          <span class="section-kicker">${escapeHtml(title)}</span>
          <h3>${escapeHtml(title)}</h3>
        </div>
        <span class="muted">${escapeHtml(helper)}</span>
      </div>
      <div class="settings-row-list">${renderRows(rows)}</div>
    </article>
  `;

  const notificationRows = Object.keys(notificationSettings).length
    ? [
        ['Scan completed', notificationSettings.scan_completed ? 'Enabled' : 'Disabled'],
        ['Monitoring alerts', notificationSettings.monitoring_alerts ? 'Enabled' : 'Disabled'],
        ['Report available', notificationSettings.report_available ? 'Enabled' : 'Disabled'],
      ]
    : [
        ['Scan completed', 'Notification settings are not configured yet'],
        ['Monitoring alerts', 'Notification settings are not configured yet'],
        ['Report available', 'Notification settings are not configured yet'],
      ];

  host.innerHTML = [
    renderSection('Company & Tenant', 'Read-only tenant context', [
      ['Company', company || 'Not available'],
      ['Tenant ID', maskIdentifier(settings.tenant_id || data?.tenant_id)],
      ['Environment', environment || 'Not available'],
      ['Business Central Environment', bcEnvironment || 'Not available'],
      ['Last Updated', formatDateTime(firstPresent(settings.last_scan, data?.last_updated))],
    ], 'settings-section-wide'),
    renderSection('Language & Localization', 'Managed by existing tenant settings', [
      ['Language', language || 'Not available'],
      ['Preferred Language', preferredLanguage || 'Not available'],
      ['Date Format', dateFormat],
      ['Currency', currency],
    ]),
    renderSection('Dashboard Preferences', 'Access follows current product state', [
      ['Theme', theme],
      ['Dashboard Access', dashboardAccess ? 'Available' : 'Locked', accessStatus({ active: dashboardAccess, until: access.dashboard_access_until })],
      ['Issue Access', issueAccess ? 'Available' : 'Locked', accessStatus({ active: issueAccess, until: access.issue_access_until })],
      ['Record Details Access', recordAccess ? 'Available' : 'Locked', accessStatus({ active: recordAccess })],
      ['Monitoring Status', monitoringActive ? 'Active' : 'Inactive', accessStatus({ active: monitoringActive })],
    ]),
    renderSection('Contact', 'Existing support and documentation links', [
      ['Contact Email', contactEmail],
      ['Support Contact', 'support@bcsentinel.com'],
      ['Documentation', '/docs'],
    ]),
    renderSection('Notification Settings', 'Read-only readiness state', notificationRows),
  ].join('');
}

function accessStatus({ active = false, until = null, trial = false } = {}) {
  const rawUntil = String(until || '').trim();
  if (trial) return { label: 'Trial', className: 'trial' };
  if (active) return { label: 'Active', className: 'active' };
  if (rawUntil && rawUntil !== 'â€”') {
    const parsed = new Date(rawUntil.includes('T') ? rawUntil : rawUntil.replace(/ UTC$/, 'Z').replace(', ', 'T'));
    if (!Number.isNaN(parsed.getTime()) && parsed.getTime() < Date.now()) {
      return { label: 'Expired', className: 'expired' };
    }
  }
  return { label: 'Locked', className: 'locked' };
}

function renderSubscriptionStatusBadge(status) {
  return `<span class="subscription-status-badge status-${escapeHtml(status.className)}">${escapeHtml(status.label)}</span>`;
}

function subscriptionPriceFor(data, key) {
  const tenantPrice = data?.tenant_pricing?.prices?.[key] || {};
  const productPrice = data?.product_pricing?.prices?.[key] || data?.product_pricing?.[key] || {};
  const price = Object.keys(tenantPrice).length ? tenantPrice : productPrice;
  if (price.contact_sales) return { label: 'Contact Sales', disabled: true };
  if (price.amount_eur === null) return { label: 'Contact Sales', disabled: true };
  if (price.amount_eur !== undefined) return { label: formatCurrency(price.amount_eur), disabled: false };
  if (price.price_eur !== undefined) return { label: formatCurrency(price.price_eur), disabled: false };
  return { label: 'Price available in checkout', disabled: false };
}

function currentPlanLabel(data) {
  const raw = String(data?.current_plan || '').trim();
  if (data?.product_access?.monitoring_active) return 'Monitoring';
  if (raw && raw !== 'free') return raw.replaceAll('_', ' ').replace(/\b\w/g, (char) => char.toUpperCase());
  return data?.subscription?.plan_label || 'Free';
}

function renderSubscriptionAccess(data) {
  const host = byId('subscription-access-grid');
  if (!host) return;
  const access = data?.product_access || {};
  const trial = String(data?.license_status || '').toLowerCase() === 'trial' || String(data?.current_plan || '').toLowerCase() === 'trial';
  const rows = [
    {
      label: 'Current Plan',
      value: currentPlanLabel(data),
      helper: data?.subscription?.plan_note || 'Current billing-safe dashboard state.',
      status: accessStatus({ active: Boolean(data?.visibility?.is_premium || access.monitoring_active), trial }),
    },
    {
      label: 'Product Access',
      value: access.can_view_issues || access.can_view_actions || access.can_view_reports ? 'Premium access' : 'Free access',
      helper: 'Issues, actions, reports and records follow existing product access.',
      status: accessStatus({ active: Boolean(access.can_view_issues || access.can_view_actions || access.can_view_reports), trial }),
    },
    {
      label: 'Dashboard Access',
      value: formatDateTime(access.dashboard_access_until),
      helper: access.can_view_dashboard ? 'Dashboard access is available.' : 'Dashboard access is limited.',
      status: accessStatus({ active: Boolean(access.can_view_dashboard), until: access.dashboard_access_until, trial }),
    },
    {
      label: 'Issue Access',
      value: formatDateTime(access.issue_access_until),
      helper: access.can_view_issues || access.can_view_record_details ? 'Issue details are available.' : 'Issue details are locked.',
      status: accessStatus({ active: Boolean(access.can_view_issues || access.can_view_record_details || access.can_view_issue_details), until: access.issue_access_until, trial }),
    },
  ];

  host.innerHTML = rows.map((row) => `
    <article class="subscription-access-card">
      <div class="subscription-access-top">
        <span class="stat-label">${escapeHtml(row.label)}</span>
        ${renderSubscriptionStatusBadge(row.status)}
      </div>
      <div class="subscription-value stat-value-small">${escapeHtml(row.value || 'Not available')}</div>
      <div class="stat-helper">${escapeHtml(row.helper)}</div>
    </article>
  `).join('');
}

function renderSubscriptionMonitoring(data) {
  const host = byId('subscription-monitoring-card');
  const badge = byId('subscription-monitoring-badge');
  if (!host) return;
  const access = data?.product_access || {};
  const monitoringActive = Boolean(access.monitoring_active || access.can_use_monitoring || data?.monitoring_status === 'active');
  const status = accessStatus({ active: monitoringActive });
  if (badge) {
    badge.textContent = monitoringActive ? 'Active' : 'Inactive';
    badge.className = `subscription-status-badge status-${status.className}`;
  }

  const renewal = firstPresent(access.monitoring_renewal_date, data?.monitoring_renewal_date, data?.subscription?.renewal_date);
  const periodEnd = firstPresent(access.monitoring_period_end, data?.monitoring_period_end, data?.subscription?.period_end, access.dashboard_access_until);
  host.innerHTML = `
    <div class="subscription-status-value">${escapeHtml(monitoringActive ? 'Active' : 'Inactive')}</div>
    <div class="subscription-status-details">
      <div><span>Renewal Date</span><strong>${escapeHtml(renewal ? formatDateTime(renewal) : 'Not available')}</strong></div>
      <div><span>Period End</span><strong>${escapeHtml(periodEnd ? formatDateTime(periodEnd) : 'Not available')}</strong></div>
    </div>
  `;
}

function renderSubscriptionScanCredits(data) {
  const host = byId('subscription-scan-credit-card');
  const buyButton = byId('buy-more-credits-cta');
  if (!host) return;
  const access = data?.product_access || {};
  const credits = safeNumber(firstPresent(access.scan_credits_available, access.scan_credits, data?.scan_credits), 0);
  const canRunDeepScan = Boolean(access.can_run_deep_scan);
  const validationAvailable = Boolean(access.validation_access_active || data?.validation_access_active || access.can_run_validation_check);
  const needsCredits = credits <= 0;
  if (buyButton) buyButton.classList.toggle('hidden', !needsCredits);

  host.innerHTML = `
    <div class="subscription-credit-main">
      <span>Available Scan Credits</span>
      <strong>${escapeHtml(formatNumber(credits))}</strong>
    </div>
    <div class="subscription-status-details">
      <div><span>Deep Scan available?</span><strong>${escapeHtml(canRunDeepScan ? 'Yes' : 'No')}</strong></div>
      <div><span>Validation available?</span><strong>${escapeHtml(validationAvailable ? 'Yes' : 'No')}</strong></div>
    </div>
    ${needsCredits ? '<div class="subscription-credit-warning">No paid scan credits are currently available.</div>' : ''}
  `;
}

function renderSubscriptionProducts(data) {
  const host = byId('subscription-product-grid');
  if (!host) return;
  const access = data?.product_access || {};
  const activeAssessment = Boolean(access.assessment_access_active || data?.assessment_access_active || access.can_view_issues);
  const activeValidation = Boolean(access.validation_access_active || data?.validation_access_active);
  const monitoringActive = Boolean(access.monitoring_active || data?.monitoring_status === 'active');
  const items = [
    ['full_analysis', 'Full Analysis', 'Complete Data Health Assessment', 'Buy Now', activeAssessment, 'Most Popular'],
    ['validation_check', 'Validation Check', 'Validate improvements after remediation', 'Buy Now', activeValidation, ''],
    ['monitoring_monthly', 'Monitoring Monthly', 'Continuous monitoring with trends and alerts', 'Start Monitoring', monitoringActive, 'Current Plan'],
    ['monitoring_annual', 'Monitoring Annual', 'Best value annual monitoring plan', 'Start Annual Monitoring', monitoringActive, 'Best Value'],
  ];
  host.innerHTML = items.map(([key, title, description, cta, active, badge]) => {
    const price = subscriptionPriceFor(data, key);
    const isMonitoring = key.startsWith('monitoring');
    const cardBadge = active ? 'Active' : badge;
    return `
      <article class="subscription-product-card ${active ? 'is-active-product' : ''} ${isMonitoring ? 'is-monitoring-product' : ''}">
        <div class="subscription-product-top">
          <h4>${escapeHtml(title)}</h4>
          ${cardBadge ? `<span class="subscription-product-badge">${escapeHtml(cardBadge)}</span>` : ''}
        </div>
        <p>${escapeHtml(description)}</p>
        <div class="subscription-product-price">${escapeHtml(price.label)}</div>
        <button type="button" class="primary-button subscription-product-action" data-product-code="${escapeHtml(key)}" ${price.disabled ? 'disabled' : ''}>${escapeHtml(price.disabled ? 'Contact Sales' : cta)}</button>
      </article>
    `;
  }).join('');
}

function renderOverviewProducts(data) {
  const host = byId('overview-product-grid');
  if (!host) return;
  const access = data?.product_access || {};
  const activeAssessment = Boolean(access.assessment_access_active || data?.assessment_access_active || access.can_view_issues);
  const activeValidation = Boolean(access.validation_access_active || data?.validation_access_active);
  const monitoringActive = Boolean(access.monitoring_active || data?.monitoring_status === 'active');
  const items = [
    ['full_analysis', 'Full Analysis', 'Complete insights for 7 days: issue details, affected records, recommendations, actions and reports.', 'Buy Full Analysis', activeAssessment, 'Most Popular'],
    ['validation_check', 'Validation Check', 'New scan comparison for 7 days: validate fixes after remediation and update your score.', 'Buy Validation Check', activeValidation, 'After Fixes'],
    ['monitoring_monthly', 'Monitoring', 'One full month of recurring monitoring: trends, scan history, alerts, prioritized actions and executive reporting.', 'Start Monitoring', monitoringActive, 'Best for ongoing control'],
  ];
  host.innerHTML = items.map(([key, title, description, cta, active, badge]) => {
    const price = subscriptionPriceFor(data, key);
    const isMonitoring = key.startsWith('monitoring');
    const cardBadge = active ? 'Active' : badge;
    return `
      <article class="subscription-product-card overview-product-card ${active ? 'is-active-product' : ''} ${isMonitoring ? 'is-monitoring-product' : ''}">
        <div class="subscription-product-top">
          <h4>${escapeHtml(title)}</h4>
          ${cardBadge ? `<span class="subscription-product-badge">${escapeHtml(cardBadge)}</span>` : ''}
        </div>
        <p>${escapeHtml(description)}</p>
        <div class="subscription-product-price">${escapeHtml(price.label)}</div>
        <button type="button" class="primary-button subscription-product-action" data-product-code="${escapeHtml(key)}" ${price.disabled ? 'disabled' : ''}>${escapeHtml(price.disabled ? 'Contact Sales' : cta)}</button>
      </article>
    `;
  }).join('');
}

function renderFeatureComparisonBody(host, data) {
  if (!host) return;
  const rows = [
    ['Free Health Score Dashboard', true, true, true, true],
    ['Active Issues Summary', true, true, true, true],
    ['Issue Details', false, true, true, true],
    ['Affected Records', false, true, true, true],
    ['Actions & Recommendations', false, true, true, true],
    ['Open in Business Central', false, true, true, true],
    ['Reports', false, true, true, true],
    ['Validation Scan Comparison', false, false, true, true],
    ['Score Trends', false, false, false, true],
    ['Loss Trends', false, false, false, true],
    ['Monitoring History & Alerts', false, false, false, true],
  ];
  const access = data?.product_access || {};
  const validationActive = Boolean(access.validation_access_active || data?.validation_access_active);
  const currentColumn = access.monitoring_active ? 3 : (validationActive ? 2 : (data?.visibility?.is_premium ? 1 : 0));
  host.innerHTML = rows.map(([feature, free, assessment, validation, monitoring]) => {
    const cells = [free, assessment, validation, monitoring].map((enabled, index) => `
      <td class="${index === currentColumn ? 'is-current-plan-cell' : ''}">
        <span class="feature-mark ${enabled ? 'is-included' : 'is-locked'}">${enabled ? 'Included' : 'Locked'}</span>
      </td>
    `).join('');
    return `<tr><td><strong>${escapeHtml(feature)}</strong></td>${cells}</tr>`;
  }).join('');
}

function renderFeatureComparison(data) {
  renderFeatureComparisonBody(byId('subscription-feature-comparison-body'), data);
  renderFeatureComparisonBody(byId('overview-feature-comparison-body'), data);
}

function updateOverviewTrendVisibility(data) {
  const section = byId('overview-trend-section');
  if (!section) return;
  const access = data?.product_access || {};
  const premiumActive = Boolean(data?.visibility?.is_premium || access.monitoring_active || access.can_use_monitoring);
  const scorePoints = Array.isArray(data?.score_trend) ? data.score_trend.length : 0;
  const lossPoints = Array.isArray(data?.loss_trend) ? data.loss_trend.length : 0;
  const hasMultipleScans = scorePoints > 1 || lossPoints > 1 || (Array.isArray(data?.recent_scans) && data.recent_scans.length > 1);
  section.classList.toggle('hidden', !(premiumActive && hasMultipleScans));
}

function applyLockStates(data) {
  const pages = data?.pages || {};
  document.querySelectorAll('[data-lock-section]').forEach((region) => {
    const section = region.dataset.lockSection;
    const locked = Boolean(pages?.[section]?.locked);
    region.classList.toggle('is-locked', locked);
    let overlay = region.querySelector('.lock-overlay');
    if (locked && !overlay) {
      overlay = document.createElement('div');
      overlay.className = 'lock-overlay';
      overlay.innerHTML = `<strong>${escapeHtml(t('paid_access', 'Paid Access'))}</strong><span>${escapeHtml(pages?.[section]?.lock_reason || 'Unlock premium access to use this section.')}</span>`;
      region.appendChild(overlay);
    }
    if (!locked && overlay) overlay.remove();
  });
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
    host.innerHTML = `<div class="empty-state">${escapeHtml(t('preview_after_scan', 'The paid scan preview will appear after the next scan.'))}</div>`;
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
        <span>${formatNumber(item?.count)} ${escapeHtml(t('affected', 'affected'))}</span>
        <span>${escapeHtml(t('recommendations_available', 'Recommendations available'))}</span>
      </div>
      <p class="muted">${escapeHtml(item?.recommendation_preview || '')}</p>
    </article>
  `).join('');
}

function renderUnlockPanel(data) {
  setText('unlock-headline', data?.premium_unlock?.headline || 'Paid scan access unlocks record-level details and direct action.');
  setText('unlock-body', data?.premium_unlock?.body || 'Upgrade to see exact affected records and recommendations.');
  setText('upgrade-button', data?.premium_unlock?.button_label || 'Buy Full Analysis');

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
    ? 'Full Premium Analysis'
    : (hasPaidAccess ? 'Full Premium Analysis' : 'Free Data Score');

  if (planBadge) {
    planBadge.textContent = accessLabel;
    planBadge.classList.toggle('is-locked', !hasPaidAccess);
  }
  if (subBadge) {
    subBadge.textContent = monitoringActive ? 'Current Plan: Monitoring' : (hasPaidAccess ? 'Current Plan: Assessment' : 'Current Plan: Free');
    subBadge.classList.toggle('is-locked', !hasPaidAccess && !monitoringActive);
  }

  if (accessUnlock) accessUnlock.classList.add('hidden');
  if (monitoringPanels) monitoringPanels.classList.toggle('hidden', !monitoringActive);
  if (findingsPanel) findingsPanel.classList.toggle('hidden', !hasPaidAccess);
}

function renderSubscription(data) {
  const monitoringActive = Boolean(data?.product_access?.monitoring_active);
  const hasPaidAccess = Boolean(data?.visibility?.is_premium);
  const scanCreditButton = byId('buy-more-credits-cta');
  const planBadge = byId('subscription-plan-badge');

  if (planBadge) {
    planBadge.textContent = monitoringActive ? 'Current Plan: Monitoring' : (hasPaidAccess ? 'Current Plan: Assessment' : 'Current Plan: Free');
    planBadge.classList.toggle('is-locked', !hasPaidAccess && !monitoringActive);
  }

  setText('subscription-cta', data?.subscription?.cta_label || t('buy_assessment', 'Buy Full Analysis'));
  if (scanCreditButton) scanCreditButton.textContent = 'Buy Credits';

  renderSubscriptionAccess(data);
  renderSubscriptionMonitoring(data);
  renderSubscriptionScanCredits(data);
  renderFeatureComparison(data);
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
  const activeNavTab = tab === 'issue-detail' ? 'issues' : tab;
  document.querySelectorAll('.topnav-link').forEach((btn) => {
    const isActive = btn.dataset.tab === activeNavTab;
    btn.classList.toggle('is-active', isActive);
    btn.setAttribute('aria-current', isActive ? 'page' : 'false');
  });
  document.querySelectorAll('.tab-panel').forEach((panel) => {
    panel.classList.toggle('hidden', panel.id !== `${tab}-tab`);
    panel.classList.toggle('is-active', panel.id === `${tab}-tab`);
  });
  updatePageHeader(tab);
}

async function loadDashboard(scanId = null) {
  const url = new URL('/analytics/embed/data', window.location.origin);
  if (scanId) url.searchParams.set('scan_id', scanId);
  url.searchParams.set('recent_scans_page', String(recentScansPage));
  url.searchParams.set('recent_scans_page_size', String(RECENT_SCANS_PAGE_SIZE));

  try {
    const response = await fetch(url.toString());
    if (!response.ok) {
      setText('page-subtitle', t('dashboard_load_error', 'The dashboard could not be loaded.'));
      return;
    }

    const data = await response.json();
    currentDashboardState = data;
    applyDashboardUi(data?.ui || {}, data?.language || 'en');
    currentSelectedScanId = data?.selected_scan_id || null;

    const activeTab = document.querySelector('.topnav-link.is-active')?.dataset?.tab || 'overview';
    updatePageHeader(activeTab);
    setText('last-updated', `${t('last_updated', 'Last updated')}: ${formatDateTime(data?.last_updated)}`);
    setText('hero-eyebrow', 'Your Data Health Assessment');
    setText('hero-prefix', data?.hero?.headline_prefix || 'Your data health is');
    setText('hero-highlight', data?.hero?.headline_highlight || 'critical');
    setText('hero-suffix', data?.hero?.headline_suffix || '');
    setText('overview-summary', '');
    renderOverviewContext(data);
    renderHeroPoints(data?.hero?.points || []);
    const heroHighlight = byId('hero-highlight');
    if (heroHighlight) {
      heroHighlight.className = `hero-highlight ${scoreBand(data?.kpis?.health_score)}`;
    }

    renderOverviewKpis(data);
    renderProfileCards(data?.module_scores || [], data?.profile_cards || []);
    renderModuleVolume(data);
    renderRecentScans(data?.recent_scans || []);
    renderRecentScansPagination(data?.recent_scans_pagination || {});
    renderScansPage(data);
    updateOverviewTrendVisibility(data);
    renderTrend('trend-chart', data?.score_trend || [], false, 'Score history appears after at least two scans. Monitoring keeps this trend useful over time.');
    renderTrend('loss-chart', data?.loss_trend || [], true, 'Loss history appears after at least two scans. Monitoring adds the historical business context.');
    renderTrend('analytics-score-trend', data?.score_trend || [], false, 'Score history appears after at least two scans.');
    renderTrend('analytics-loss-trend', data?.loss_trend || [], true, 'Loss history appears after at least two scans.');
    renderIssueDistribution(data);
    renderModuleDistribution(data);
    renderOverviewRecentIssues(data);
    renderBusinessImpact(data);
    renderFindings(data?.top_findings || [], Boolean(data?.visibility?.is_premium));
    renderUnlockPanel(data);
    renderSubscription(data);
    renderSubscriptionProducts(data);
    renderOverviewProducts(data);
    renderIssuesPage(data);
    renderActionsPage(data);
    renderReportsPage(data);
    renderSettingsPage(data);
    applyLockStates(data);
    renderPricingBreakdown(data);
    applyPlanState(data);
  } catch (error) {
    console.error('loadDashboard failed:', error);
    setText('page-subtitle', t('dashboard_load_error', 'The dashboard could not be loaded.'));
  }
}

function registerEvents() {
  const bindScanTable = (host) => {
    if (!host) return;
    host.addEventListener('click', async (event) => {
      const row = event.target.closest('.scan-row');
      if (!row) return;
      const scanId = row.dataset.scanId;
      if (!scanId || scanId === currentSelectedScanId) return;
      await loadDashboard(scanId);
    });

    host.addEventListener('keydown', async (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      const row = event.target.closest('.scan-row');
      if (!row) return;
      event.preventDefault();
      const scanId = row.dataset.scanId;
      if (!scanId || scanId === currentSelectedScanId) return;
      await loadDashboard(scanId);
    });
  };

  bindScanTable(byId('recent-scans-body'));
  bindScanTable(byId('scans-page-body'));

  const issuesBody = byId('issues-page-body');
  if (issuesBody) {
    issuesBody.addEventListener('click', (event) => {
      const button = event.target.closest('.issue-detail-button');
      if (!button) return;
      openIssueDetail(safeNumber(button.dataset.issueIndex, -1));
    });
  }

  const detailBackButton = byId('issue-detail-back-button');
  if (detailBackButton) {
    detailBackButton.addEventListener('click', () => switchTab('issues'));
  }

  const detailContent = byId('issue-detail-content');
  if (detailContent) {
    detailContent.addEventListener('click', (event) => {
      const unlockButton = event.target.closest('.issue-detail-unlock-button');
      if (!unlockButton) return;
      switchTab('subscription');
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

  document.querySelectorAll('[data-jump-tab]').forEach((btn) => {
    btn.addEventListener('click', () => switchTab(btn.dataset.jumpTab || 'overview'));
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
      await triggerBillingAction('checkout', 'full_analysis');
    });
  }

  const productGrid = byId('subscription-product-grid');
  if (productGrid) {
    productGrid.addEventListener('click', async (event) => {
      const button = event.target.closest('.subscription-product-action');
      if (!button || button.disabled) return;
      await triggerBillingAction('checkout', button.dataset.productCode || null);
    });
  }

  const overviewProductGrid = byId('overview-product-grid');
  if (overviewProductGrid) {
    overviewProductGrid.addEventListener('click', async (event) => {
      const button = event.target.closest('.subscription-product-action');
      if (!button || button.disabled) return;
      await triggerBillingAction('checkout', button.dataset.productCode || null);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  registerEvents();
  switchTab('overview');
  recentScansPage = 1;
  loadDashboard();
});
