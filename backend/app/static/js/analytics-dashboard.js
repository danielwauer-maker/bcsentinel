let currentSelectedScanId = null;
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

function safeNumber(value, defaultValue = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : defaultValue;
}

function formatPercent(value) {
  const number = safeNumber(value);
  return `${formatNumber(Math.round(number))}%`;
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

  setTextContent('[data-tab="overview"]', t('overview', 'Overview'));
  setTextContent('[data-tab="analytics"]', t('analytics', 'Analytics'));
  setTextContent('[data-tab="scans"]', t('scans', 'Scans'));
  setTextContent('[data-tab="issues"]', t('issues', 'Issues'));
  setTextContent('[data-tab="actions"]', t('actions', 'Actions'));
  setTextContent('[data-tab="reports"]', t('reports', 'Reports'));
  setTextContent('[data-tab="subscription"]', t('subscription', 'Subscription'));
  setTextContent('[data-tab="settings"]', t('settings', 'Settings'));
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
  setTextContent('#subscription-tab h3', t('subscription', 'Subscription'));

  const subscriptionLabels = document.querySelectorAll('.subscription-card .stat-label');
  const subscriptionHelpers = document.querySelectorAll('.subscription-card .stat-helper');
  const subscriptionLabelKeys = ['product_access', 'scan_credits', 'dashboard_access_until', 'issue_access_until', 'monthly_price', 'annual_cost'];
  const subscriptionHelperKeys = ['','scan_credits_helper', 'dashboard_access_helper', 'issue_access_helper', 'monthly_price_helper', 'annual_cost_helper'];
  subscriptionLabels.forEach((el, index) => { if (subscriptionLabelKeys[index]) el.textContent = t(subscriptionLabelKeys[index], el.textContent); });
  subscriptionHelpers.forEach((el, index) => { if (subscriptionHelperKeys[index]) el.textContent = t(subscriptionHelperKeys[index], el.textContent); });
}

function updatePageHeader(tab) {
  const data = currentDashboardState || {};
  const pageCopy = {
    overview: ['Overview', 'Executive overview of your data quality and business impact'],
    analytics: ['Analytics', 'Score, loss and distribution analysis for the selected scan'],
    scans: ['Scans', 'Available scan runs and dashboard context'],
    issues: ['Issues', 'All data quality issues found in your system'],
    actions: ['Actions', 'Recommended actions to improve your data quality'],
    reports: ['Reports', 'Create and download reports about your data quality'],
    subscription: ['Subscription', 'Manage product access, scan credits and usage'],
    settings: ['Settings', 'Configure your account and preferences'],
  };
  const [title, fallbackSubtitle] = pageCopy[tab] || pageCopy.overview;
  setText('page-title', title);
  setText('page-subtitle', tab === 'overview' && data?.subtitle ? `${fallbackSubtitle} - ${data.subtitle}` : fallbackSubtitle);
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

function renderOverviewContext(data) {
  const host = byId('overview-context');
  if (!host) return;
  const items = [
    data?.subtitle ? ['Context', data.subtitle] : null,
    data?.scan_mode_label ? ['Scan', data.scan_mode_label] : null,
    data?.last_updated ? ['Last scan', formatDateTime(data.last_updated)] : null,
  ].filter(Boolean);

  host.innerHTML = items.map(([label, value]) => `
    <span class="overview-context-chip"><strong>${escapeHtml(label)}</strong>${escapeHtml(value)}</span>
  `).join('');
}

function renderOverviewKpis(data) {
  const kpis = data?.kpis || {};
  const healthScore = Math.max(0, Math.min(100, safeNumber(kpis.health_score)));
  const totalRecords = safeNumber(kpis.total_records);
  const checksRun = safeNumber(kpis.checks_run);
  const estimatedLoss = safeNumber(kpis.estimated_loss_eur);
  const potentialSaving = safeNumber(kpis.potential_saving_eur);
  const hasScan = Boolean(data?.selected_scan_id);

  setText('kpi-health-label-title', 'Health Score');
  setText('kpi-loss-label-title', 'Estimated Loss');
  setText('kpi-savings-label-title', 'Potential Savings');
  setText('kpi-records-label-title', 'Total Records');
  setText('kpi-checks-label-title', 'Validation Checks');
  setText('kpi-health-score', formatNumber(healthScore));
  setText('kpi-health-label', hasScan ? scoreLabel(healthScore) : 'Not calculated yet');
  setText('kpi-health-helper', hasScan ? 'Overall data quality' : 'Run a validation check to unlock this KPI');
  const healthGauge = byId('kpi-health-gauge');
  if (healthGauge) healthGauge.style.setProperty('--score', String(healthScore));
  const healthScoreEl = byId('kpi-health-score');
  if (healthScoreEl) healthScoreEl.className = `stat-value score-value ${scoreBand(healthScore)}`;

  setText('kpi-loss', hasScan ? formatCurrency(estimatedLoss) : 'Not calculated yet');
  setText('kpi-loss-helper', estimatedLoss > 0 ? 'Estimated annual impact' : 'Available after full analysis');
  setText('kpi-savings', hasScan ? formatCurrency(potentialSaving) : 'Not calculated yet');
  setText('kpi-savings-helper', potentialSaving > 0 ? 'Estimated improvement potential' : 'Run a validation check to unlock this KPI');
  setText('kpi-records', hasScan ? formatNumber(totalRecords) : 'Not calculated yet');
  setText('kpi-records-helper', totalRecords > 0 ? 'Records analyzed' : 'Available after scan sync');
  setText('kpi-checks', hasScan ? formatNumber(checksRun) : 'Not calculated yet');
  setText('kpi-checks-helper', checksRun > 0 ? 'Validation checks run' : 'Run a validation check to unlock this KPI');
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

  const maxIssue = Math.max(...moduleItems.map((item) => item.count), 1);
  const maxRecords = Math.max(...recordItems.map((item) => item.count), 1);
  const issueMarkup = moduleItems.slice(0, 5).map((item) => `
    <div class="module-row">
      <span>${escapeHtml(item.name)}</span>
      <div class="distribution-track"><div class="distribution-fill" style="width:${Math.max((item.count / maxIssue) * 100, 3)}%"></div></div>
      <strong>${formatNumber(item.count)}</strong>
    </div>
  `).join('') || `<div class="empty-state executive-empty compact-empty">No issue module data yet.</div>`;
  const recordMarkup = recordItems.slice(0, 5).map((item) => `
    <div class="module-row">
      <span>${escapeHtml(item.name)}</span>
      <div class="distribution-track"><div class="distribution-fill record-fill" style="width:${Math.max((item.count / maxRecords) * 100, 3)}%"></div></div>
      <strong>${formatNumber(item.count)}</strong>
    </div>
  `).join('') || `<div class="empty-state executive-empty compact-empty">No record module data yet.</div>`;

  host.innerHTML = `
    <div class="module-distribution-column">
      <h4>Issue Distribution</h4>
      ${issueMarkup}
    </div>
    <div class="module-distribution-column">
      <h4>Records by Module</h4>
      ${recordMarkup}
    </div>
  `;
}

function renderOverviewRecentIssues(data) {
  const host = byId('overview-recent-issues');
  if (!host) return;
  const isPremium = Boolean(data?.visibility?.is_premium);
  const premiumItems = Array.isArray(data?.top_findings) ? data.top_findings : [];
  const freeItems = Array.isArray(data?.free_insights?.top_findings) ? data.free_insights.top_findings : [];
  const items = (isPremium ? premiumItems : freeItems).slice(0, 5);

  if (items.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">Recent issues will appear after the next scan.</div>`;
    return;
  }

  host.innerHTML = items.map((item, index) => {
    const title = isPremium ? (item?.title || 'Issue') : `Locked issue ${index + 1}`;
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
  }).join('') + (!isPremium ? `<div class="placeholder-note">Issue details are protected. Full Analysis, Validation Check or Monitoring unlocks record-level actions.</div>` : '');
}

function renderBusinessImpact(data) {
  const host = byId('overview-business-impact');
  if (!host) return;
  const kpis = data?.kpis || {};
  const healthScore = safeNumber(kpis.health_score);
  const estimatedLoss = safeNumber(kpis.estimated_loss_eur);
  const potentialSaving = safeNumber(kpis.potential_saving_eur);
  const roi = safeNumber(kpis.roi_eur);
  const issuesCount = safeNumber(kpis.issues_count);

  if (!data?.selected_scan_id) {
    host.innerHTML = `<div class="empty-state executive-empty">Business impact will be calculated after scan results are available.</div>`;
    return;
  }

  const headline = estimatedLoss > 0
    ? `${formatCurrency(estimatedLoss)} estimated annual impact`
    : 'Business impact not calculated yet';
  const summary = potentialSaving > 0
    ? `${formatCurrency(potentialSaving)} potential savings are available from the existing scan economics.`
    : 'Run a validation check or full analysis to unlock a stronger business impact view.';

  host.innerHTML = `
    <div class="business-impact-headline">${escapeHtml(headline)}</div>
    <p>${escapeHtml(summary)}</p>
    <div class="business-impact-grid">
      <div><span>Health Score</span><strong>${formatNumber(healthScore)}/100</strong></div>
      <div><span>Issues Found</span><strong>${formatNumber(issuesCount)}</strong></div>
      <div><span>Potential Savings</span><strong>${formatCurrency(potentialSaving)}</strong></div>
      <div><span>ROI</span><strong>${formatCurrency(roi)}</strong></div>
    </div>
  `;
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

function renderIssuesPage(data) {
  const host = byId('issues-page-body');
  if (!host) return;
  const page = data?.issues_page || {};
  const items = Array.isArray(page.items) ? page.items : [];
  if (page.locked) {
    host.innerHTML = `<tr><td colspan="7" class="table-empty">${escapeHtml(t('paid_access', 'Paid Access'))}</td></tr>`;
    return;
  }
  if (items.length === 0) {
    host.innerHTML = `<tr><td colspan="7" class="table-empty">${escapeHtml(t('no_findings', 'No findings are available for this scan.'))}</td></tr>`;
    return;
  }
  host.innerHTML = items.map((item) => `
    <tr>
      <td><strong>${escapeHtml(item?.title)}</strong></td>
      <td>${escapeHtml(item?.group)}</td>
      <td><span class="severity severity-${escapeHtml(item?.severity)}">${escapeHtml(item?.severity_label || item?.severity)}</span></td>
      <td>${formatNumber(item?.count)}</td>
      <td>${formatCurrency(item?.impact_eur)}</td>
      <td>Open</td>
      <td>${escapeHtml(formatDateTime(data?.last_updated))}</td>
    </tr>
  `).join('');
}

function renderActionsPage(data) {
  const host = byId('actions-page-body');
  if (!host) return;
  const page = data?.actions_page || {};
  const items = Array.isArray(page.items) ? page.items : [];
  if (page.locked) {
    host.innerHTML = `<tr><td colspan="5" class="table-empty">${escapeHtml(t('paid_access', 'Paid Access'))}</td></tr>`;
    return;
  }
  if (items.length === 0) {
    host.innerHTML = `<tr><td colspan="5" class="table-empty">${escapeHtml(t('no_findings', 'No actions are available for this scan.'))}</td></tr>`;
    return;
  }
  host.innerHTML = items.map((item) => `
    <tr>
      <td>${escapeHtml(item?.issue)}</td>
      <td>${escapeHtml(item?.suggested_action)}</td>
      <td><span class="severity severity-${escapeHtml(item?.priority)}">${escapeHtml(item?.priority)}</span></td>
      <td>${formatCurrency(item?.potential_saving_eur)}</td>
      <td>${escapeHtml(item?.effort || 'TBD')}</td>
    </tr>
  `).join('');
}

function renderReportsPage(data) {
  const host = byId('reports-page-grid');
  if (!host) return;
  const page = data?.reports_page || {};
  const items = Array.isArray(page.items) ? page.items : [];
  if (page.locked) {
    host.innerHTML = `<div class="empty-state">${escapeHtml(t('paid_access', 'Paid Access'))}</div>`;
    return;
  }
  host.innerHTML = items.map((item) => `
    <article class="report-card">
      <h4>${escapeHtml(item?.title)}</h4>
      <p class="muted">${escapeHtml(item?.available ? 'Ready for this scan.' : 'Available with monitoring history.')}</p>
      <button type="button" class="pager-button" ${item?.available ? '' : 'disabled'}>Open</button>
    </article>
  `).join('') || `<div class="empty-state">${escapeHtml(t('no_findings', 'No reports are available for this scan.'))}</div>`;
}

function renderSettingsPage(data) {
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

function renderSubscriptionProducts(data) {
  const host = byId('subscription-product-grid');
  if (!host) return;
  const prices = data?.tenant_pricing?.prices || {};
  const items = [
    ['full_analysis', 'Full Analysis', 'Buy Full Analysis'],
    ['validation_check', 'Validation Check', 'Buy Validation Check'],
    ['monitoring_monthly', 'Monitoring Monthly', 'Start Monitoring Monthly'],
    ['monitoring_annual', 'Monitoring Annual', 'Start Monitoring Annual'],
  ];
  host.innerHTML = items.map(([key, title, cta]) => {
    const price = prices[key] || {};
    const isContact = Boolean(price.contact_sales);
    const amount = isContact ? 'Contact Sales' : formatCurrency(price.amount_eur);
    return `
      <article class="subscription-product-card">
        <h4>${escapeHtml(title)}</h4>
        <div class="subscription-product-price">${escapeHtml(amount)}</div>
        <button type="button" class="pager-button subscription-product-action" data-product-code="${escapeHtml(key)}" ${isContact ? 'disabled' : ''}>${escapeHtml(isContact ? 'Contact Sales' : cta)}</button>
      </article>
    `;
  }).join('');
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
    ? t('monitoring_active', 'Monitoring active')
    : (hasPaidAccess ? t('assessment_validation_active', 'Full Analysis / Validation active') : t('credits_needed', 'Credits needed'));

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
  const tenantPricing = data?.tenant_pricing || {};
  const monthlyPrice = tenantPricing?.prices?.monitoring_monthly || {};
  const annualPrice = tenantPricing?.prices?.monitoring_annual || {};
  const hasMonthlyQuote = monitoringActive || monthlyPrice.amount_eur !== undefined || monthlyPrice.contact_sales;
  const hasAnnualQuote = monitoringActive || annualPrice.amount_eur !== undefined || annualPrice.contact_sales;

  setText('subscription-plan', data?.subscription?.plan_label || t('assessment_needed', 'Full Analysis needed'));
  setText('subscription-note', data?.subscription?.plan_note || '');
  setText('subscription-cta', data?.subscription?.cta_label || t('buy_assessment', 'Buy Full Analysis'));
  setText('subscription-scan-credits', formatNumber(data?.product_access?.scan_credits_available));
  setText('subscription-dashboard-until', formatDateTime(data?.product_access?.dashboard_access_until));
  setText('subscription-issue-until', formatDateTime(data?.product_access?.issue_access_until));

  if (priceCard) priceCard.classList.toggle('hidden', !hasMonthlyQuote);
  if (annualCard) annualCard.classList.toggle('hidden', !hasAnnualQuote);
  if (buyMoreButton) buyMoreButton.classList.toggle('hidden', monitoringActive || !hasPaidAccess);

  if (monitoringActive) {
    setText('subscription-price', formatCurrency(data?.subscription?.price_monthly));
    setText('subscription-annual', formatCurrency(data?.subscription?.annual_cost));
  } else if (tenantPricing?.contact_sales) {
    setText('subscription-price', 'Contact Sales');
    setText('subscription-annual', 'Contact Sales');
  } else {
    setText('subscription-price', monthlyPrice.amount_eur === null ? 'Contact Sales' : formatCurrency(monthlyPrice.amount_eur));
    setText('subscription-annual', annualPrice.amount_eur === null ? 'Contact Sales' : formatCurrency(annualPrice.amount_eur));
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
    const isActive = btn.dataset.tab === tab;
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
    setText('hero-eyebrow', data?.hero?.eyebrow || 'Data Health Score first. Full Analysis unlocks the details.');
    setText('hero-prefix', data?.hero?.headline_prefix || 'Your data health is');
    setText('hero-highlight', data?.hero?.headline_highlight || 'critical');
    setText('hero-suffix', data?.hero?.headline_suffix || '');
    setText('overview-summary', data?.subtitle ? `Executive overview for ${data.subtitle}.` : 'Executive overview of your data quality and business impact.');
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
}

document.addEventListener('DOMContentLoaded', () => {
  registerEvents();
  switchTab('overview');
  recentScansPage = 1;
  loadDashboard();
});
