let currentSelectedScanId = null;
let currentSelectedIssueIndex = null;
let recentScansPage = 1;
const RECENT_SCANS_PAGE_SIZE = 12;
let currentDashboardState = null;
let currentDashboardLanguage = 'en';
let currentDashboardUi = {};
let dashboardLanguageOverride = null;

const LOCAL_DASHBOARD_UI = {
  en: {
    overview: 'Overview',
    analytics: 'Analytics',
    scans: 'Scans',
    issues: 'Issues',
    actions: 'Actions',
    reports: 'Reports',
    subscription: 'Subscription',
    settings: 'Settings',
    support: 'Support',
    documentation: 'Documentation',
    logout: 'Logout',
    language: 'Language',
    dark_mode: 'Dark mode',
    overview_subtitle: 'Executive overview of your data quality and business impact',
    analytics_subtitle: 'Score, loss and distribution analysis for the selected scan',
    scans_subtitle: 'Available scan runs and dashboard context',
    issues_subtitle: 'Review detected data quality issues, business impact and affected records.',
    issue_detail: 'Issue detail',
    issue_detail_subtitle: 'Detailed issue context, impact and recommendation',
    actions_subtitle: 'Prioritized actions to reduce data quality risk and business impact.',
    reports_subtitle: 'Generate and review executive, operational and impact reports.',
    subscription_access: 'Subscription & Access',
    subscription_subtitle: 'Manage your product access, monitoring status and available scan credits.',
    subscription_no_products_title: 'No additional subscription needed',
    subscription_no_products_body: 'Monitoring is active. All current dashboard features are already available for this tenant.',
    business_impact_title: 'Business Impact',
    business_impact_subtitle: 'Executive view of current business effects.',
    business_impact_info: 'Estimated business impact based on current scan context',
    business_impact_summary_free: 'Limited preview of financial, operational and governance impact based on the available scan context.',
    business_impact_summary_full: 'Executive impact view based on the current full analysis. Values are estimates and support prioritization.',
    business_impact_summary_monitoring: 'Business impact remains visible as an executive control signal for the active monitoring context.',
    business_impact_summary_empty: 'Business impact appears after scan results are available.',
    business_impact_financial: 'Financial Impact',
    business_impact_financial_helper: 'Estimated annual exposure from the current scan context.',
    business_impact_operational: 'Operational Impact',
    business_impact_operational_helper: 'Affected records indicate operational review pressure.',
    business_impact_governance: 'Governance Impact',
    business_impact_governance_helper: 'Business control relevance derived from the current score band.',
    business_impact_potential: 'Potential Saving',
    business_impact_potential_helper: 'Estimated potential, not a guaranteed result.',
    business_impact_not_available: 'Not available',
    business_impact_records: 'records',
    business_impact_signals: 'signals',
    business_impact_review_needed: 'Review needed',
    business_impact_elevated: 'Elevated',
    business_impact_stable: 'Stable',
    business_impact_estimate_label: 'Estimate',
    business_impact_estimate_note: 'Amounts are estimates based on available scan context and are not guaranteed results.',
    business_impact_demo_note: 'Demo Preview uses sample data.',
    top_risk_modules_title: 'Top Risk Modules',
    top_risk_modules_subtitle: 'Executive ranking of the modules with the highest current risk.',
    top_risk_modules_info: 'Top risk modules from the existing dashboard payload',
    top_risk_modules_empty: 'No risk modules are available in the current scan context.',
    top_risk_modules_rank: 'Rank',
    top_risk_modules_score: 'Module score',
    top_risk_modules_share: 'Risk share',
    top_risk_modules_impact: 'Business impact',
    top_risk_modules_context: 'Executive risk context from existing module data.',
    top_risk_modules_payload_top: 'Prioritized by dashboard payload.',
    top_risk_modules_payload_fallback: 'Shown from module scores because no top risk module payload is available.',
    top_risk_modules_not_available: 'Not available',
    executive_issue_list_title: 'Executive Issue List',
    executive_issue_list_subtitle: 'Prioritized findings from the current scan context.',
    executive_issue_list_empty: 'Executive findings will appear after the next scan.',
    executive_issue_list_free_note: 'Limited preview based on available free scan findings.',
    executive_issue_list_full_note: 'Full analysis view based on available scan findings.',
    executive_issue_list_monitoring_note: 'Monitoring context uses the latest available findings without adding monitoring widgets.',
    executive_issue_list_source_note: 'Existing dashboard preview data.',
    executive_issue_list_status_open: 'Open',
    executive_issue_list_status_review: 'Review',
    settings_subtitle: 'Configure your account and preferences',
  },
  de: {
    overview: 'Ãœberblick',
    analytics: 'Analytics',
    scans: 'Scans',
    issues: 'Issues',
    actions: 'Actions',
    reports: 'Reports',
    subscription: 'Produktzugriff',
    settings: 'Settings',
    support: 'Support',
    documentation: 'Dokumentation',
    logout: 'Logout',
    language: 'Sprache',
    dark_mode: 'Dark Mode',
    overview_subtitle: 'Executive Overview deiner DatenqualitÃ¤t und Business-Auswirkung',
    analytics_subtitle: 'Score-, Verlust- und Verteilungsanalyse fÃ¼r den ausgewÃ¤hlten Scan',
    scans_subtitle: 'VerfÃ¼gbare Scan-LÃ¤ufe und Dashboard-Kontext',
    issues_subtitle: 'PrÃ¼fe erkannte DatenqualitÃ¤ts-Issues, Business Impact und betroffene DatensÃ¤tze.',
    issue_detail: 'Issue Detail',
    issue_detail_subtitle: 'Detaillierter Issue-Kontext, Impact und Empfehlung',
    actions_subtitle: 'Priorisierte Aktionen zur Reduzierung von DatenqualitÃ¤tsrisiko und Business Impact.',
    reports_subtitle: 'Reports erstellen und Executive-, Operational- und Impact-Auswertungen prÃ¼fen.',
    subscription_access: 'Subscription & Access',
    subscription_subtitle: 'Verwalte Produktzugriff, Monitoring-Status und verfÃ¼gbare Scan Credits.',
    subscription_no_products_title: 'Keine weitere Subscription erforderlich',
    subscription_no_products_body: 'Monitoring ist aktiv. Alle aktuellen Dashboard-Funktionen sind fuer diesen Tenant bereits verfuegbar.',
    business_impact_title: 'Business Impact',
    business_impact_subtitle: 'Executive-Sicht auf aktuelle geschaeftliche Auswirkungen.',
    business_impact_info: 'Geschaetzter Business Impact auf Basis des aktuellen Scan-Kontexts',
    business_impact_summary_free: 'Begrenzte Vorschau auf finanziellen, operativen und Governance-Impact aus dem verfuegbaren Scan-Kontext.',
    business_impact_summary_full: 'Executive Impact View aus der aktuellen Full Analysis. Werte sind Schaetzungen und unterstuetzen die Priorisierung.',
    business_impact_summary_monitoring: 'Business Impact bleibt als Executive-Kontrollsignal fuer den aktiven Monitoring-Kontext sichtbar.',
    business_impact_summary_empty: 'Business Impact erscheint, sobald Scan-Ergebnisse verfuegbar sind.',
    business_impact_financial: 'Financial Impact',
    business_impact_financial_helper: 'Geschaetzte jaehrliche Auswirkung aus dem aktuellen Scan-Kontext.',
    business_impact_operational: 'Operational Impact',
    business_impact_operational_helper: 'Betroffene Datensaetze zeigen operativen Pruefdruck.',
    business_impact_governance: 'Governance Impact',
    business_impact_governance_helper: 'Business-Control-Relevanz aus dem aktuellen Score-Band.',
    business_impact_potential: 'Potential Saving',
    business_impact_potential_helper: 'Geschaetztes Potenzial, kein garantiertes Ergebnis.',
    business_impact_not_available: 'Nicht verfuegbar',
    business_impact_records: 'Datensaetze',
    business_impact_signals: 'Signale',
    business_impact_review_needed: 'Pruefung erforderlich',
    business_impact_elevated: 'Erhoeht',
    business_impact_stable: 'Stabil',
    business_impact_estimate_label: 'Schaetzung',
    business_impact_estimate_note: 'Betraege sind Schaetzungen auf Basis des verfuegbaren Scan-Kontexts und keine garantierten Ergebnisse.',
    business_impact_demo_note: 'Demo Preview verwendet Beispieldaten.',
    top_risk_modules_title: 'Top Risk Modules',
    top_risk_modules_subtitle: 'Executive Ranking der Module mit dem hoechsten aktuellen Risiko.',
    top_risk_modules_info: 'Top Risk Modules aus dem bestehenden Dashboard-Payload',
    top_risk_modules_empty: 'Im aktuellen Scan-Kontext sind keine Risikomodule verfuegbar.',
    top_risk_modules_rank: 'Rang',
    top_risk_modules_score: 'Modul-Score',
    top_risk_modules_share: 'Risikoanteil',
    top_risk_modules_impact: 'Business Impact',
    top_risk_modules_context: 'Executive-Risikokontext aus vorhandenen Moduldaten.',
    top_risk_modules_payload_top: 'Durch Dashboard-Payload priorisiert.',
    top_risk_modules_payload_fallback: 'Aus Modul-Scores angezeigt, weil kein Top-Risk-Module-Payload verfuegbar ist.',
    top_risk_modules_not_available: 'Nicht verfuegbar',
    executive_issue_list_title: 'Executive Issue List',
    executive_issue_list_subtitle: 'Priorisierte Findings aus dem aktuellen Scan-Kontext.',
    executive_issue_list_empty: 'Executive Findings erscheinen nach dem naechsten Scan.',
    executive_issue_list_free_note: 'Begrenzte Vorschau aus verfuegbaren Free-Scan-Findings.',
    executive_issue_list_full_note: 'Full-Analysis-Sicht auf verfuegbare Scan-Findings.',
    executive_issue_list_monitoring_note: 'Monitoring-Kontext nutzt die letzten verfuegbaren Findings ohne Monitoring Widgets.',
    executive_issue_list_source_note: 'Bestehende Dashboard-Preview-Daten.',
    executive_issue_list_status_open: 'Offen',
    executive_issue_list_status_review: 'Pruefung',
    settings_subtitle: 'Account und Präferenzen konfigurieren',
  },
};

const STATIC_TEXT_TRANSLATIONS = [
  ['static_active_issues', 'Active Issues', 'Aktive Issues'],
  ['static_recent_critical_issues', 'Executive Issue List', 'Executive Issue List'],
  ['static_recent_critical_helper', 'Highest impact findings from the selected scan', 'Findings mit hÃ¶chstem Impact aus dem ausgewÃ¤hlten Scan'],
  ['static_recommended_actions', 'Recommended Actions', 'Empfohlene Aktionen'],
  ['static_recommended_actions_helper', 'Highest impact actions based on the selected scan.', 'Aktionen mit hÃ¶chstem Impact basierend auf dem ausgewÃ¤hlten Scan.'],
  ['static_module_distribution_records', 'Module Distribution & Records', 'Modulverteilung & DatensÃ¤tze'],
  ['static_issue_distribution_percent', 'Issue Distribution (by %)', 'Issue-Verteilung (in %)'],
  ['static_records_by_module', 'Records by Module', 'DatensÃ¤tze nach Modul'],
  ['static_business_impact_breakdown', 'Business Impact Breakdown', 'Business Impact AufschlÃ¼sselung'],
  ['static_view_all_issues', 'View all issues', 'Alle Issues anzeigen'],
  ['static_view_all_modules', 'View all modules', 'Alle Module anzeigen'],
  ['static_view_full_impact_report', 'View full impact report', 'VollstÃ¤ndigen Impact Report anzeigen'],
  ['static_unlock_next_step', 'Unlock the next step', 'NÃ¤chsten Schritt freischalten'],
  ['static_unlock_next_step_helper', 'Choose the access level that matches what you want to do next.', 'WÃ¤hle den Zugriff, der zu deinem nÃ¤chsten Schritt passt.'],
  ['static_feature_comparison', 'Feature Comparison', 'Feature-Vergleich'],
  ['static_feature_comparison_helper', 'Free Score, paid scan access and Monitoring at a glance.', 'Free Score, bezahlter Scan-Zugriff und Monitoring auf einen Blick.'],
  ['static_feature', 'Feature', 'Feature'],
  ['static_free', 'Free', 'Free'],
  ['full_analysis', 'Full Analysis', 'Full Analysis'],
  ['validation_check', 'Validation Check', 'Validation Check'],
  ['static_validation', 'Validation', 'Validation'],
  ['static_assessment', 'Assessment', 'Assessment'],
  ['monitoring', 'Monitoring', 'Monitoring'],
  ['static_date', 'Date', 'Datum'],
  ['static_type', 'Type', 'Typ'],
  ['static_score', 'Score', 'Score'],
  ['static_status', 'Status', 'Status'],
  ['static_headline', 'Headline', 'Headline'],
  ['free_data_score', 'Free Data Score', 'Free Data Score'],
  ['full_premium_analysis', 'Full Premium Analysis', 'Full Premium Analysis'],
  ['premium_analytics', 'Premium analytics', 'Premium-Analyse'],
  ['estimated_loss_trend', 'Estimated Loss Trend', 'GeschÃ¤tzter Verlust-Trend'],
  ['score_history_after_scans_short', 'Score history appears after at least two scans.', 'Score-Historie erscheint nach mindestens zwei Scans.'],
  ['loss_history_after_scans_short', 'Loss history appears after at least two scans.', 'Verlust-Historie erscheint nach mindestens zwei Scans.'],
  ['scan_history', 'Scan History', 'Scan-Historie'],
  ['scan_history_helper', 'Uses the existing dashboard payload; no additional scan API call is required.', 'Verwendet den bestehenden Dashboard-Payload; kein zusÃ¤tzlicher Scan-API-Aufruf erforderlich.'],
  ['scan_context_hint', 'Select an available scan to refresh the dashboard context.', 'WÃ¤hle einen verfÃ¼gbaren Scan aus, um den Dashboard-Kontext zu aktualisieren.'],
  ['status_loaded', 'Loaded', 'Geladen'],
  ['status_incomplete', 'Incomplete', 'UnvollstÃ¤ndig'],
  ['status_available', 'Available', 'VerfÃ¼gbar'],
  ['no_scans', 'No scans available yet.', 'Noch keine Scans verfÃ¼gbar.'],
  ['static_issue_detail_empty', 'Issue detail is available from the Issues page.', 'Issue Details sind Ã¼ber die Issues-Seite verfÃ¼gbar.'],
  ['static_back_to_issues', 'Back to Issues', 'ZurÃ¼ck zu Issues'],
  ['static_current_access', 'Current Access', 'Aktueller Zugriff'],
  ['static_monitoring_status', 'Monitoring Status', 'Monitoring-Status'],
  ['static_scan_credits', 'Scan Credits', 'Scan Credits'],
  ['static_available_scan_credits', 'Available Scan Credits', 'VerfÃ¼gbare Scan Credits'],
  ['static_products', 'Products', 'Produkte'],
  ['settings', 'Settings', 'Settings'],
  ['reports', 'Reports', 'Reports'],
  ['actions', 'Actions', 'Actions'],
  ['issues', 'Issues', 'Issues'],
  ['static_issue_code', 'Issue Code', 'Issue-Code'],
  ['static_module_category', 'Module / Category', 'Modul / Kategorie'],
  ['static_general', 'General', 'Allgemein'],
  ['static_open', 'Open', 'Offen'],
  ['static_locked', 'Locked', 'Gesperrt'],
  ['static_not_available', 'Not available', 'Nicht verfÃ¼gbar'],
  ['static_not_calculated_yet', 'Not calculated yet', 'Noch nicht berechnet'],
  ['static_affected_records', 'Affected Records', 'Betroffene DatensÃ¤tze'],
  ['static_issue', 'Issue', 'Fehler'],
  ['static_module', 'Module', 'Modul'],
  ['static_severity', 'Severity', 'Schweregrad'],
  ['static_action', 'Action', 'Aktion'],
  ['static_total_issues', 'Total Issues', 'Fehler gesamt'],
  ['static_full_issue_list_helper', 'Full issue list from the existing dashboard payload', 'VollstÃ¤ndige Fehlerliste aus dem bestehenden Dashboard-Payload'],
  ['static_free_issue_access_note', 'Free access shows severity and business value without exposing protected issue details.', 'Kostenloser Zugriff zeigt Schweregrad und Business Value, ohne geschÃ¼tzte Fehlerdetails offenzulegen.'],
  ['premium_issue_details', 'Premium issue details', 'Premium-Fehlerdetails'],
  ['view_locked_details', 'View locked details', 'Gesperrte Details anzeigen'],
  ['view_details', 'View Details', 'Details anzeigen'],
  ['issue_detail_description_locked', 'Detailed description is available after the full analysis.', 'Die detaillierte Beschreibung ist nach der Full Analysis verfÃ¼gbar.'],
  ['issue_detail_recommendation_locked', 'Recommendation will be generated after the full analysis.', 'Die Empfehlung wird nach der Full Analysis erzeugt.'],
  ['issue_detail_score_impact_empty', 'Score impact details will appear when available.', 'Score-Impact-Details erscheinen, sobald sie verfÃ¼gbar sind.'],
  ['issue_detail_business_impact_locked', 'Business impact details are protected for the current access level.', 'Business-Impact-Details sind fÃ¼r den aktuellen Zugriff geschÃ¼tzt.'],
  ['static_estimated_impact_loss', 'Estimated Impact / Loss', 'GeschÃ¤tzter Impact / Verlust'],
  ['static_last_scan_updated', 'Last Scan / Last Updated', 'Letzter Scan / Letzte Aktualisierung'],
  ['static_estimated_loss', 'Estimated Loss', 'GeschÃ¤tzter Verlust'],
  ['static_potential_savings', 'Potential Savings', 'Potenzielle Einsparungen'],
  ['static_unlock_issue_details', 'Unlock full issue details', 'Issue Details freischalten'],
  ['static_bc_link_unavailable', 'Business Central link not available', 'Business-Central-Link nicht verfÃ¼gbar'],
  ['static_locked_access', 'Locked access', 'Gesperrter Zugriff'],
  ['static_full_issue_access', 'Full issue access', 'Voller Issue-Zugriff'],
  ['static_no_scan_timestamp', 'No scan timestamp', 'Kein Scan-Zeitpunkt'],
  ['static_saving_pending', 'Saving pending', 'Einsparung ausstehend'],
  ['static_full_action_access', 'Full action access', 'Voller Actions-Zugriff'],
  ['static_high_priority', 'High Priority', 'Hohe PrioritÃ¤t'],
  ['static_open_actions', 'Open Actions', 'Offene Aktionen'],
  ['static_prioritized_recommendations', 'Prioritized recommendations', 'Priorisierte Empfehlungen'],
  ['static_critical_high_priority', 'Critical and high priority', 'Kritische und hohe PrioritÃ¤t'],
  ['static_potential_saving', 'Potential Saving', 'Potenzielle Einsparung'],
  ['static_executive_summary', 'Executive Summary', 'Executive Summary'],
  ['static_data_quality_report', 'Data Quality Report', 'Data Quality Report'],
  ['static_issue_detail_report', 'Issue Detail Report', 'Issue Detail Report'],
  ['static_business_impact_report', 'Business Impact Report', 'Business Impact Report'],
  ['static_action_plan_report', 'Action Plan Report', 'Action Plan Report'],
  ['static_trend_report', 'Trend Report', 'Trend Report'],
  ['static_after_scan', 'After scan', 'Nach Scan'],
  ['static_available_after_scan', 'Available after scan', 'Nach Scan verfÃ¼gbar'],
  ['static_unlock_reports', 'Unlock reports', 'Reports freischalten'],
  ['static_monitoring_only', 'Monitoring only', 'Nur Monitoring'],
  ['static_available', 'Available', 'VerfÃ¼gbar'],
  ['static_current_plan', 'Current Plan', 'Aktueller Plan'],
  ['static_product_access', 'Product Access', 'Produktzugriff'],
  ['static_dashboard_access', 'Dashboard Access', 'Dashboard-Zugriff'],
  ['static_issue_access', 'Issue Access', 'Issue-Zugriff'],
  ['static_active', 'Active', 'Aktiv'],
  ['static_inactive', 'Inactive', 'Inaktiv'],
  ['static_expired', 'Expired', 'Abgelaufen'],
  ['static_trial', 'Trial', 'Testphase'],
  ['static_renewal_date', 'Renewal Date', 'VerlÃ¤ngerungsdatum'],
  ['static_period_end', 'Period End', 'Periodenende'],
  ['static_yes', 'Yes', 'Ja'],
  ['static_no', 'No', 'Nein'],
  ['static_buy_now', 'Buy Now', 'Jetzt kaufen'],
  ['static_contact_sales', 'Contact Sales', 'Sales kontaktieren'],
  ['static_company_tenant', 'Company & Tenant', 'Unternehmen & Tenant'],
  ['static_language_localization', 'Language & Localization', 'Sprache & Lokalisierung'],
  ['static_dashboard_preferences', 'Dashboard Preferences', 'Dashboard-PrÃ¤ferenzen'],
  ['static_contact', 'Contact', 'Kontakt'],
  ['static_notification_settings', 'Notification Settings', 'Benachrichtigungseinstellungen'],
];

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

  const emptyLabel = options.emptyLabel || 'Historical trends available after additional scans';
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
    <span class="kpi-trend-arrow kpi-trend-arrow-${arrow}" aria-hidden="true">${isDown ? 'â†“' : 'â†‘'}</span>
    <strong>${escapeHtml(formatPercent(Math.abs(value)))}</strong>
    <span>vs. last month</span>
  `;
}

function t(key, fallback) {
  return currentDashboardUi?.[key] || LOCAL_DASHBOARD_UI[currentDashboardLanguage]?.[key] || fallback || key;
}

function translateStaticDashboardText() {
  const root = document.querySelector('.page-shell');
  if (!root) return;
  const lookup = new Map();
  STATIC_TEXT_TRANSLATIONS.forEach(([key, en, de]) => {
    const fallback = currentDashboardLanguage === 'de' ? de : en;
    const value = t(key, fallback);
    lookup.set(en, value);
    lookup.set(de, value);
  });
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach((node) => {
    const original = node.nodeValue || '';
    const trimmed = original.trim();
    if (!trimmed || !lookup.has(trimmed)) return;
    node.nodeValue = original.replace(trimmed, lookup.get(trimmed));
  });
}

function setTextContent(selector, value) {
  const el = document.querySelector(selector);
  if (el) el.textContent = value;
}

function applyDashboardUi(ui, language) {
  currentDashboardLanguage = language === 'de' ? 'de' : 'en';
  currentDashboardUi = ui || {};
  document.documentElement.lang = currentDashboardLanguage;
  const languageToggle = byId('dashboard-language-toggle');
  if (languageToggle) languageToggle.value = currentDashboardLanguage;

  setTextContent('[data-tab="overview"] .nav-label', t('overview', 'Overview'));
  setTextContent('[data-tab="analytics"] .nav-label', t('analytics', 'Analytics'));
  setTextContent('[data-tab="scans"] .nav-label', t('scans', 'Scans'));
  setTextContent('[data-tab="issues"] .nav-label', t('issues', 'Issues'));
  setTextContent('[data-tab="actions"] .nav-label', t('actions', 'Actions'));
  setTextContent('[data-tab="reports"] .nav-label', t('reports', 'Reports'));
  setTextContent('[data-tab="subscription"] .nav-label', t('subscription', 'Subscription'));
  setTextContent('[data-tab="settings"] .nav-label', t('settings', 'Settings'));
  setTextContent('.sidebar-footer a[href^="mailto"] span', t('support', 'Support'));
  setTextContent('.sidebar-footer a[href="/docs"] span', t('documentation', 'Documentation'));
  setTextContent('#logout-button span', t('logout', 'Logout'));
  setTextContent('#language-toggle-label', t('language', 'Language'));
  setTextContent('.dark-mode-toggle > span:first-child', t('dark_mode', 'Dark mode'));
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
  setTextContent('#scans-page-panel h3', t('scan_history', 'Scan History'));
  setTextContent('#scans-page-panel .panel-title-block .muted', t('scan_history_helper', 'Uses the existing dashboard payload; no additional scan API call is required.'));
  setTextContent('#scans-page-panel .placeholder-note', t('scan_context_hint', 'Select an available scan to refresh the dashboard context.'));
  const scanPageHeaders = document.querySelectorAll('#scans-page-panel thead th');
  const scanPageHeaderKeys = ['static_date', 'static_type', 'static_score', 'issues', 'static_status', 'static_headline'];
  scanPageHeaders.forEach((el, index) => { if (scanPageHeaderKeys[index]) el.textContent = t(scanPageHeaderKeys[index], el.textContent); });
  setTextContent('#recent-scans-prev', t('previous', 'Previous'));
  setTextContent('#recent-scans-next', t('next', 'Next'));
  setTextContent('#score-trend-panel h3', t('score_trend', 'Score Trend'));
  setTextContent('#score-trend-panel .muted', t('score_trend_helper', 'History of selected scans'));
  setTextContent('#loss-trend-panel h3', t('loss_trend', 'Loss Trend'));
  setTextContent('#loss-trend-panel .muted', t('loss_trend_helper', 'Estimated annual impact'));
  setTextContent('#business-impact-title', t('business_impact_title'));
  setTextContent('#business-impact-subtitle', t('business_impact_subtitle'));
  const businessImpactBadge = byId('business-impact-badge');
  if (businessImpactBadge) businessImpactBadge.setAttribute('title', t('business_impact_info'));
  setTextContent('#top-risk-modules-title', t('top_risk_modules_title'));
  setTextContent('#top-risk-modules-subtitle', t('top_risk_modules_subtitle'));
  const topRiskModulesBadge = byId('top-risk-modules-badge');
  if (topRiskModulesBadge) topRiskModulesBadge.setAttribute('title', t('top_risk_modules_info'));
  setTextContent('[data-dashboard-slot="critical-issues"] h3', t('executive_issue_list_title'));
  setTextContent('[data-dashboard-slot="critical-issues"] .muted', t('executive_issue_list_subtitle'));
  setTextContent('#analytics-tab article:nth-child(1) .panel-header h3', t('score_trend', 'Score Trend'));
  setTextContent('#analytics-tab article:nth-child(1) .panel-header .muted', t('premium_analytics', 'Premium analytics'));
  setTextContent('#analytics-tab article:nth-child(2) .panel-header h3', t('estimated_loss_trend', 'Estimated Loss Trend'));
  setTextContent('#analytics-tab article:nth-child(2) .panel-header .muted', t('premium_analytics', 'Premium analytics'));
  setTextContent('#access-unlock-panel h3', t('paid_scan_access', 'Paid scan access'));
  setTextContent('.preview-title', t('scan_preview', 'Scan preview'));
  setTextContent('.preview-title-row .muted', t('scan_preview_helper', 'Record details, recommendations, actions'));
  setTextContent('.pricing-breakdown-title', t('estimated_monitoring_pricing', 'Estimated monitoring pricing'));
  setTextContent('#access-findings-panel h3', t('findings', 'Findings'));
  setTextContent('#access-findings-panel .muted', t('findings_helper', 'Visible with paid scan access, actionable in Business Central'));
  setTextContent('.issues-list-panel h3', t('issues', 'Issues'));
  setTextContent('.issues-list-panel .panel-title-block .muted', t('static_full_issue_list_helper', 'Full issue list from the existing dashboard payload'));
  setTextContent('#issues-unlock-button', t('static_unlock_issue_details', 'Unlock full issue details'));
  setTextContent('#issues-locked-note strong', t('static_unlock_issue_details', 'Unlock full issue details'));
  setTextContent('#issues-locked-note span', t('static_free_issue_access_note', 'Free access shows severity and business value without exposing protected issue details.'));
  const issuesHeaders = document.querySelectorAll('.issues-table thead th');
  const issuesHeaderKeys = ['static_issue', 'static_module', 'static_severity', 'static_affected_records', 'static_estimated_loss', 'static_status', 'static_action'];
  issuesHeaders.forEach((el, index) => { if (issuesHeaderKeys[index]) el.textContent = t(issuesHeaderKeys[index], el.textContent); });
  setTextContent('#subscription-tab .subscription-page-intro h2', 'Subscription & Access');
}

function updatePageHeader(tab) {
  const data = currentDashboardState || {};
  const companyName = getDashboardCompanyName(data);
  const pageCopy = {
    overview: [t('overview', 'Overview'), t('overview_subtitle', 'Executive overview of your data quality and business impact')],
    analytics: [t('analytics', 'Analytics'), t('analytics_subtitle', 'Score, loss and distribution analysis for the selected scan')],
    scans: [t('scans', 'Scans'), t('scans_subtitle', 'Available scan runs and dashboard context')],
    issues: [t('issues', 'Issues'), t('issues_subtitle', 'Review detected data quality issues, business impact and affected records.')],
    'issue-detail': [t('issue_detail', 'Issue detail'), t('issue_detail_subtitle', 'Detailed issue context, impact and recommendation')],
    actions: [t('actions', 'Actions'), t('actions_subtitle', 'Prioritized actions to reduce data quality risk and business impact.')],
    reports: [t('reports', 'Reports'), t('reports_subtitle', 'Generate and review executive, operational and impact reports.')],
    subscription: [t('subscription_access', 'Subscription & Access'), t('subscription_subtitle', 'Manage your product access, monitoring status and available scan credits.')],
    settings: [t('settings', 'Settings'), t('settings_subtitle', 'Configure your account and preferences')],
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
  if (!raw || raw === 'â€”') return 'â€”';

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

function topRiskModuleSource(data) {
  if (Object.prototype.hasOwnProperty.call(data || {}, 'top_risk_modules') && Array.isArray(data?.top_risk_modules)) {
    return { items: data.top_risk_modules, source: 'top' };
  }
  return { items: Array.isArray(data?.module_scores) ? data.module_scores : [], source: 'fallback' };
}

function normalizeTopRiskModule(item) {
  const rawName = item?.name || item?.label || item?.module || '';
  if (!rawName) return null;
  const key = moduleKey(rawName);
  const rawScore = safeNumber(item?.score ?? item?.value, null);
  const score = rawScore === null ? null : Math.max(0, Math.min(100, rawScore));
  const variant = item?.variant || (score === null ? 'moderate' : scoreBand(score));
  const share = firstFiniteNumber([item?.risk_share, item?.share, item?.risk_percent, item?.percent]);
  const impact = firstFiniteNumber([item?.impact_eur, item?.estimated_loss_eur, item?.estimated_impact_eur]);
  return {
    key,
    name: canonicalDashboardModuleName(key, rawName),
    score,
    variant,
    share,
    impact,
  };
}

function topRiskModuleMetric(item) {
  if (item.share !== null) {
    return {
      label: t('top_risk_modules_share'),
      value: formatPercent(item.share),
    };
  }
  if (item.impact !== null) {
    return {
      label: t('top_risk_modules_impact'),
      value: formatKpiCurrency(item.impact),
    };
  }
  return {
    label: t('top_risk_modules_score'),
    value: item.score === null ? t('top_risk_modules_not_available') : `${formatNumber(item.score)}/100`,
  };
}

function renderOverviewModuleScores(data) {
  const host = byId('overview-module-score-grid');
  if (!host) return;

  const source = topRiskModuleSource(data);
  const rows = source.items.map(normalizeTopRiskModule).filter(Boolean);

  if (rows.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty top-risk-modules-empty">${escapeHtml(t('top_risk_modules_empty'))}</div>`;
    return;
  }

  const sourceLabel = source.source === 'top'
    ? t('top_risk_modules_payload_top')
    : t('top_risk_modules_payload_fallback');

  host.innerHTML = rows.map((item, index) => {
    const metric = topRiskModuleMetric(item);
    const scoreValue = item.score === null ? 0 : item.score;
    return `
      <article class="module-score-card top-risk-module-card">
        <div class="top-risk-module-rank"><span>${escapeHtml(t('top_risk_modules_rank'))}</span><strong>${formatNumber(index + 1)}</strong></div>
        <div class="module-score-title">${escapeHtml(item.name)}</div>
        <div class="module-score-gauge ${escapeHtml(item.variant)}" style="--score:${scoreValue}">
          <div>
            <strong>${item.score === null ? '-' : formatNumber(item.score)}</strong>
            <span>/100</span>
          </div>
        </div>
        <div class="module-score-status ${escapeHtml(item.variant)}">${escapeHtml(item.score === null ? t('top_risk_modules_not_available') : scoreLabel(item.score))}</div>
        <div class="top-risk-module-meta"><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(metric.value)}</strong></div>
        <p class="top-risk-module-context">${escapeHtml(t('top_risk_modules_context'))}</p>
        <small class="top-risk-module-source">${escapeHtml(sourceLabel)}</small>
      </article>
    `;
  }).join('');
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

function executiveSummaryVariant(data) {
  const isMonitoring = Boolean(data?.product_access?.monitoring_active || data?.monitoring_preview?.status === 'active');
  const isPremium = Boolean(data?.visibility?.is_premium);
  if (isMonitoring) return 'monitoring';
  if (isPremium) return 'full';
  return 'free';
}

function executiveTrendCopy(data) {
  const scoreTrend = trendFromSeries(data?.score_trend);
  const lossTrend = trendFromSeries(data?.loss_trend);
  if (Number.isFinite(Number(scoreTrend))) {
    const direction = Number(scoreTrend) >= 0 ? 'improved' : 'declined';
    return `Health score ${direction} ${formatPercent(Math.abs(scoreTrend))} versus the previous scan.`;
  }
  if (Number.isFinite(Number(lossTrend))) {
    const direction = Number(lossTrend) <= 0 ? 'reduced' : 'increased';
    return `Estimated loss ${direction} ${formatPercent(Math.abs(lossTrend))} versus the previous scan.`;
  }
  return 'Trend comparison becomes available after additional scans.';
}

function executiveTopRiskLabel(data) {
  const risks = Array.isArray(data?.top_risk_modules) && data.top_risk_modules.length > 0
    ? data.top_risk_modules
    : (Array.isArray(data?.module_scores) ? data.module_scores : []);
  const normalized = risks
    .map((item) => ({
      label: item?.label || item?.name || item?.module || '',
      score: safeNumber(item?.score ?? item?.value, 100),
    }))
    .filter((item) => item.label)
    .sort((a, b) => a.score - b.score);
  if (!normalized.length) return 'No module risk is available yet.';
  return `${normalized[0].label} is the top risk area.`;
}

function renderExecutiveHero(data) {
  const kpis = data?.kpis || {};
  const hasScan = Boolean(data?.selected_scan_id);
  const healthScore = Math.max(0, Math.min(100, safeNumber(kpis.health_score)));
  const band = scoreBand(healthScore);
  const variant = executiveSummaryVariant(data);
  const isDemo = Boolean(data?.is_demo || data?.data_source === 'demo_preview');
  const issueSummary = data?.free_insights?.active_issues_summary || data?.critical_issues_summary || {};
  const criticalCount = safeNumber(issueSummary.critical);
  const highCount = safeNumber(issueSummary.high);
  const totalIssues = safeNumber(kpis.issues_count);
  const affectedRecords = safeNumber(kpis.affected_records);
  const checksRun = safeNumber(kpis.checks_run);
  const estimatedLoss = safeNumber(kpis.estimated_loss_eur);
  const potentialSaving = safeNumber(kpis.potential_saving_eur);
  const monitoringPreview = data?.monitoring_preview || {};

  const config = {
    free: {
      eyebrow: isDemo ? 'Demo Preview - Executive Summary' : 'Executive Summary - Free Dashboard',
      summary: hasScan
        ? `Health Score ${formatNumber(healthScore)} (${scoreLabel(healthScore)}). Full Analysis is required to unlock record-level evidence and prioritized remediation.`
        : 'Run the first scan to generate an executive overview of data quality, business risk and next action.',
      ctaLabel: 'Unlock Full Analysis',
      ctaTab: 'subscription',
      note: 'Limited visibility: free view shows executive signals, not full issue evidence.',
    },
    full: {
      eyebrow: 'Executive Summary - Full Analysis',
      summary: `Business risk is visible: ${formatKpiCurrency(estimatedLoss)} estimated annual loss and ${formatKpiCurrency(potentialSaving)} potential savings are currently in scope.`,
      ctaLabel: 'Review Critical Risks',
      ctaTab: 'issues',
      note: 'Full Analysis access is active. Monitoring is not active yet.',
    },
    monitoring: {
      eyebrow: 'Executive Summary - Monitoring',
      summary: monitoringPreview?.alert || `Monitoring context is active. ${executiveTrendCopy(data)}`,
      ctaLabel: 'Review Critical Changes',
      ctaTab: 'issues',
      note: monitoringPreview?.frequency || 'Monitoring status is summarized here; detailed widgets remain outside this build.',
    },
  }[variant];

  const hero = data?.hero || {};
  const headlinePrefix = hasScan
    ? (hero.headline_prefix || 'Your data health is')
    : 'Your Data Health Summary will appear after the first scan.';
  const headlineHighlight = hasScan ? (hero.headline_highlight || scoreLabel(healthScore).toLowerCase()) : '';
  const headlineSuffix = hasScan ? (hero.headline_suffix || 'and requires executive attention.') : '';

  setText('hero-eyebrow', config.eyebrow);
  setText('hero-prefix', headlinePrefix);
  setText('hero-highlight', headlineHighlight);
  setText('hero-suffix', headlineSuffix);
  setText('overview-summary', config.summary);

  const highlight = byId('hero-highlight');
  if (highlight) {
    highlight.className = `hero-highlight ${hasScan ? band : 'hidden'}`;
    highlight.classList.toggle('hidden', !headlineHighlight);
  }

  const points = hasScan
    ? [
        `${formatNumber(totalIssues)} issues across ${formatNumber(affectedRecords)} affected records.`,
        `${formatNumber(checksRun)} checks evaluated in the selected scan.`,
        executiveTopRiskLabel(data),
      ]
    : ['No scan data is available yet.', 'The dashboard will use real scan data as soon as it exists.'];
  renderHeroPoints(points);

  const context = byId('overview-context');
  if (!context) return;
  context.classList.remove('hidden');
  context.className = `overview-context executive-summary-context executive-summary-${variant}`;
  context.innerHTML = `
    <div class="executive-summary-meta">
      <span class="executive-summary-badge ${escapeHtml(band)}">${escapeHtml(scoreLabel(healthScore))}</span>
      ${isDemo ? '<span class="executive-summary-badge is-demo">Demo Preview</span>' : ''}
      <span class="executive-summary-updated">${escapeHtml(formatDateTime(data?.last_updated))}</span>
    </div>
    <div class="executive-summary-metrics" aria-label="Executive summary metrics">
      <div class="executive-summary-metric">
        <span>Health Score</span>
        <strong class="${escapeHtml(band)}">${hasScan ? escapeHtml(formatNumber(healthScore)) : '-'}</strong>
      </div>
      <div class="executive-summary-metric">
        <span>Estimated Loss</span>
        <strong>${hasScan ? escapeHtml(formatKpiCurrency(estimatedLoss)) : '-'}</strong>
      </div>
      <div class="executive-summary-metric">
        <span>Potential Savings</span>
        <strong>${hasScan ? escapeHtml(formatKpiCurrency(potentialSaving)) : '-'}</strong>
      </div>
      <div class="executive-summary-metric">
        <span>Critical / High</span>
        <strong>${escapeHtml(formatNumber(criticalCount + highCount))}</strong>
      </div>
    </div>
    <p class="executive-summary-note">${escapeHtml(config.note)}</p>
    <button type="button" class="primary-button executive-summary-cta" data-executive-target="${escapeHtml(config.ctaTab)}">
      ${escapeHtml(config.ctaLabel)}
    </button>
  `;

  const cta = context.querySelector('.executive-summary-cta');
  if (cta) cta.addEventListener('click', () => switchTab(cta.dataset.executiveTarget || 'subscription'));
}
function getHealthScoreValue(data) {
  const value = Number(data?.kpis?.health_score);
  if (!Number.isFinite(value)) return null;
  return Math.max(0, Math.min(100, value));
}

function healthScoreInterpretation(score) {
  const band = scoreBand(score);
  const copy = {
    critical: 'Immediate review is recommended. The data quality score indicates critical risk.',
    warning: 'Action is recommended. Several data quality signals need attention.',
    moderate: 'The score is acceptable, but the current data quality still needs review.',
    good: 'Your data quality is currently in a healthy range.',
    excellent: 'Your data quality is currently in a strong range.',
  };
  return copy[band] || 'The score appears after the first completed scan.';
}

function healthScoreActionCopy(score) {
  const band = scoreBand(score);
  if (band === 'critical') return 'Review the score context before continuing with business-critical processes.';
  if (band === 'warning') return 'Prioritize follow-up review to reduce data quality risk.';
  if (band === 'moderate') return 'Review the most relevant findings when Full Analysis is available.';
  return 'No immediate action is required from the score alone. Continue regular review.';
}

function healthScoreVariantCopy(data, hasScore) {
  if (!hasScore) return 'No completed scan is available yet. Run a validation check to calculate the Data Health Score.';
  const variant = executiveSummaryVariant(data);
  if (variant === 'monitoring') return 'Monitoring uses this score as part of ongoing control. Detailed monitoring widgets remain outside this build.';
  if (variant === 'full') return 'Full Analysis explains this score in the complete scan context. Score breakdown details remain separate.';
  return 'Free view explains the score at executive level. Full Analysis unlocks causes and action context.';
}

function healthScoreTrendText(data, hasScore) {
  if (!hasScore) return 'Trend becomes available after at least two completed scans.';
  const trend = trendFromSeries(data?.score_trend);
  if (!Number.isFinite(Number(trend))) return 'Trend becomes available after at least two completed scans.';
  const value = Number(trend);
  if (Math.abs(value) < 0.5) return 'Stable versus previous scan.';
  const direction = value > 0 ? 'improved' : 'declined';
  return `Score ${direction} ${formatPercent(Math.abs(value))} versus previous scan.`;
}

function renderHealthScoreExperience(data) {
  const score = getHealthScoreValue(data);
  const hasScore = Boolean(data?.selected_scan_id && score !== null);
  const band = hasScore ? scoreBand(score) : 'is-empty';
  const isDemo = Boolean(data?.is_demo || data?.data_source === 'demo_preview');

  setText('kpi-health-label-title', 'Data Health Score');
  setText('kpi-health-score', hasScore ? formatNumber(score) : '-');
  setText('kpi-health-label', hasScore ? scoreLabel(score) : 'Not calculated yet');
  setText('kpi-health-scale', `${isDemo ? 'Demo Preview - ' : ''}Scale 0-100`);
  setText('kpi-health-interpretation', hasScore ? healthScoreInterpretation(score) : 'The score appears after the first completed scan.');
  setText('kpi-health-data-status', `Last updated: ${hasScore ? formatDateTime(data?.last_updated) : 'Not available'}`);
  setText('kpi-health-context', hasScore ? `${healthScoreActionCopy(score)} ${healthScoreVariantCopy(data, hasScore)}` : healthScoreVariantCopy(data, hasScore));
  setText('kpi-health-helper', healthScoreTrendText(data, hasScore));

  const healthLabelEl = byId('kpi-health-label');
  if (healthLabelEl) healthLabelEl.className = `kpi-status ${band}`;
  const healthGauge = byId('kpi-health-gauge');
  if (healthGauge) {
    healthGauge.style.setProperty('--score', String(hasScore ? score : 0));
    healthGauge.className = `health-gauge ${band}`;
    healthGauge.setAttribute('aria-label', hasScore ? `Data Health Score ${formatNumber(score)} of 100, ${scoreLabel(score)}.` : 'Data Health Score not calculated yet.');
  }
  const healthScoreEl = byId('kpi-health-score');
  if (healthScoreEl) healthScoreEl.className = `stat-value score-value ${band}`;
}
function scoreBreakdownStatus(score) {
  const band = scoreBand(score);
  const copy = {
    critical: 'Critical influence',
    warning: 'Needs attention',
    moderate: 'Watch area',
    good: 'Healthy influence',
    excellent: 'Strong influence',
  };
  return copy[band] || 'Not available';
}

function scoreBreakdownMeaning(score) {
  const band = scoreBand(score);
  const copy = {
    critical: 'This area is currently a negative influence on the Data Health Score.',
    warning: 'This area likely reduces confidence in the current score.',
    moderate: 'This area has visible quality signals and should stay under review.',
    good: 'This area currently supports a healthier score.',
    excellent: 'This area is currently a strong positive signal for the score.',
  };
  return copy[band] || 'No score signal is available for this area yet.';
}

function normalizeScoreBreakdown(data) {
  const moduleScores = Array.isArray(data?.module_scores) ? data.module_scores.filter(Boolean) : [];
  const topRiskModules = Array.isArray(data?.top_risk_modules) ? data.top_risk_modules.filter(Boolean) : [];
  const modules = moduleScores.length ? moduleScores : topRiskModules;
  return modules
    .map((item) => {
      const rawScore = Number(item?.score ?? item?.value);
      if (!Number.isFinite(rawScore)) return null;
      const score = Math.max(0, Math.min(100, rawScore));
      const label = item?.label || item?.name || item?.module || '';
      if (!label) return null;
      const band = item?.variant || scoreBand(score);
      return {
        label,
        score,
        band,
        status: scoreBreakdownStatus(score),
        meaning: scoreBreakdownMeaning(score),
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.score - b.score || a.label.localeCompare(b.label));
}

function scoreBreakdownSummaryCopy(data, items, visibleItems) {
  if (!data?.selected_scan_id) return 'No completed scan is available yet. Score influences will appear after scan results are available.';
  if (!items.length) return 'No score influence areas are available for this scan yet.';
  const variant = executiveSummaryVariant(data);
  const lowest = visibleItems[0];
  const suffix = lowest ? ` ${lowest.label} currently needs the most attention.` : '';
  if (variant === 'monitoring') return `Monitoring uses the same visible score influences without adding widgets or history in this view.${suffix}`;
  if (variant === 'full') return `Full Analysis shows the available influence areas behind the current Data Health Score.${suffix}`;
  return `Free view shows a limited preview of the strongest visible score influences.${suffix} Full Analysis shows all available influence areas.`;
}

function renderScoreBreakdown(data) {
  const summary = byId('score-breakdown-summary');
  const grid = byId('score-breakdown-grid');
  if (!summary || !grid) return;

  const items = normalizeScoreBreakdown(data);
  const hasScan = Boolean(data?.selected_scan_id);
  const variant = executiveSummaryVariant(data);
  const visibleItems = variant === 'free' ? items.slice(0, 3) : items;
  const isDemo = Boolean(data?.is_demo || data?.data_source === 'demo_preview');

  summary.innerHTML = `
    <div class="score-breakdown-copy">
      <span class="score-breakdown-eyebrow">${escapeHtml(isDemo ? 'Demo Preview - Score influences' : 'Score influences')}</span>
      <p>${escapeHtml(scoreBreakdownSummaryCopy(data, items, visibleItems))}</p>
      <span class="score-breakdown-note">No formulas, internal weights or rule-engine details are shown.</span>
    </div>
  `;

  if (!hasScan || !items.length) {
    grid.innerHTML = `<div class="empty-state executive-empty">Score breakdown becomes available after scan results include score influence areas.</div>`;
    return;
  }

  grid.innerHTML = visibleItems.map((item) => `
    <article class="score-breakdown-card ${escapeHtml(item.band)}" aria-label="${escapeHtml(item.label)} score influence ${formatNumber(item.score)} of 100, ${escapeHtml(item.status)}">
      <div class="score-breakdown-card-header">
        <span>${escapeHtml(item.label)}</span>
        <strong>${escapeHtml(formatNumber(item.score))}<small>/100</small></strong>
      </div>
      <div class="score-breakdown-bar" aria-hidden="true">
        <span style="width:${Math.max(item.score, 4)}%"></span>
      </div>
      <div class="score-breakdown-status ${escapeHtml(item.band)}">${escapeHtml(item.status)}</div>
      <p>${escapeHtml(item.meaning)}</p>
    </article>
  `).join('');
}
function renderOverviewKpis(data) {
  const kpis = data?.kpis || {};
  const totalRecords = safeNumber(kpis.total_records);
  const checksRun = safeNumber(kpis.checks_run);
  const estimatedLoss = safeNumber(kpis.estimated_loss_eur);
  const potentialSaving = safeNumber(kpis.potential_saving_eur);
  const hasScan = Boolean(data?.selected_scan_id);
  const lossTrend = trendFromFields(kpis, ['estimated_loss_change_percent', 'estimated_loss_trend_percent', 'estimated_loss_delta_percent', 'loss_change_percent']) ?? trendFromSeries(data?.loss_trend);
  const savingsTrend = trendFromFields(kpis, ['potential_saving_change_percent', 'potential_savings_change_percent', 'potential_saving_trend_percent', 'potential_savings_trend_percent']);
  const recordsTrend = trendFromFields(kpis, ['total_records_change_percent', 'records_change_percent', 'scanned_records_change_percent']);
  const checksTrend = trendFromFields(kpis, ['checks_run_change_percent', 'validation_checks_change_percent', 'checks_change_percent']);

  renderHealthScoreExperience(data);
  setText('kpi-loss-label-title', 'Estimated Loss');
  setText('kpi-savings-label-title', 'Potential Savings');
  setText('kpi-records-label-title', 'Total Records');
  setText('kpi-checks-label-title', 'Validation Checks');
  const scanTrendLabel = 'Historical trends available after additional scans';

  setText('kpi-loss', hasScan ? formatKpiCurrency(estimatedLoss) : 'Not calculated yet');
  renderKpiTrend('kpi-loss-helper', hasScan && estimatedLoss > 0 ? lossTrend : null, {
    emptyLabel: hasScan ? scanTrendLabel : 'Available after full analysis',
    variant: Number(lossTrend) < 0 ? 'positive' : 'negative',
  });
  setText('kpi-savings', hasScan ? formatKpiCurrency(potentialSaving) : 'Not calculated yet');
  renderKpiTrend('kpi-savings-helper', hasScan && potentialSaving > 0 ? savingsTrend : null, { emptyLabel: hasScan ? scanTrendLabel : 'Run a validation check to unlock this KPI' });
  setText('kpi-records', hasScan ? formatNumber(totalRecords) : 'Not calculated yet');
  renderKpiTrend('kpi-records-helper', hasScan && totalRecords > 0 ? recordsTrend : null, { emptyLabel: hasScan ? scanTrendLabel : 'Available after scan sync' });
  setText('kpi-checks', hasScan ? formatNumber(checksRun) : 'Not calculated yet');
  renderKpiTrend('kpi-checks-helper', hasScan && checksRun > 0 ? checksTrend : null, { emptyLabel: hasScan ? scanTrendLabel : 'Run a validation check to unlock this KPI' });
}

function renderIssueDistribution(data) {
  const host = byId('overview-issue-distribution');
  if (!host) return;
  const summary = data?.free_insights?.active_issues_summary || {};
  const rows = [
    ['critical', t('active_critical_issues', currentDashboardLanguage === 'de' ? 'Kritische Issues' : 'Critical Issues'), safeNumber(summary.critical)],
    ['high', t('active_high_issues', currentDashboardLanguage === 'de' ? 'Hohe Issues' : 'High Issues'), safeNumber(summary.high)],
    ['medium', t('active_medium_issues', currentDashboardLanguage === 'de' ? 'Mittlere Issues' : 'Medium Issues'), safeNumber(summary.medium)],
    ['low', t('active_low_issues', currentDashboardLanguage === 'de' ? 'Niedrige Issues' : 'Low Issues'), safeNumber(summary.low)],
  ];
  const total = rows.reduce((sum, row) => sum + row[2], 0);

  if (total <= 0) {
    host.innerHTML = `<div class="empty-state executive-empty">No issue distribution is available for this scan yet.</div>`;
    return;
  }

  host.innerHTML = `
    <div class="active-issues-list">
      ${rows.map(([key, label, count]) => `
        <div class="active-issue-row active-issue-${escapeHtml(key)}">
          <span class="active-issue-count">${formatNumber(count)}</span>
          <span class="active-issue-label">${escapeHtml(label)}</span>
        </div>
      `).join('')}
    </div>
    <button type="button" class="active-issues-link" data-jump-tab="issues">View all issues <span aria-hidden="true">&rarr;</span></button>
  `;
  const link = host.querySelector('.active-issues-link');
  if (link) link.addEventListener('click', () => switchTab('issues'));
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

const WEIGHTED_PRIORITY_COLORS = [
  '#991b1b',
  '#dc2626',
  '#ef4444',
  '#f97316',
  '#f59e0b',
  '#eab308',
  '#84cc16',
  '#16a34a',
  '#14b8a6',
  '#2563eb',
];
const WEIGHTED_ZERO_COLOR = '#cbd5e1';

function getWeightedPalette(items, valueAccessor, keyAccessor = (item) => item?.key || item?.name) {
  const entries = (Array.isArray(items) ? items : [])
    .filter(Boolean)
    .map((item, index) => ({
      item,
      index,
      key: String(keyAccessor(item) ?? index),
      value: Math.max(safeNumber(valueAccessor(item)), 0),
    }));
  const positiveEntries = entries
    .filter((entry) => entry.value > 0)
    .sort((a, b) => b.value - a.value || a.index - b.index);
  const palette = new Map();
  positiveEntries.forEach((entry, index) => {
    palette.set(entry.key, WEIGHTED_PRIORITY_COLORS[index % WEIGHTED_PRIORITY_COLORS.length]);
  });
  entries.filter((entry) => entry.value <= 0).forEach((entry) => {
    palette.set(entry.key, WEIGHTED_ZERO_COLOR);
  });
  return palette;
}

function knownDashboardModules() {
  if (currentDashboardLanguage === 'de') {
    return ['System', 'Finanzen', 'Verkauf', 'Einkauf', 'Lager', 'CRM', 'Fertigung', 'Service', 'Projekte', 'HR'];
  }
  return ['System', 'Finance', 'Sales', 'Purchasing', 'Inventory', 'CRM', 'Manufacturing', 'Service', 'Jobs', 'HR'];
}

function moduleKey(value) {
  const normalized = String(value || '').trim().toLowerCase();
  const aliases = {
    finance: 'finance',
    finanzen: 'finance',
    sales: 'sales',
    verkauf: 'sales',
    purchasing: 'purchasing',
    einkauf: 'purchasing',
    inventory: 'inventory',
    lager: 'inventory',
    manufacturing: 'manufacturing',
    fertigung: 'manufacturing',
    produktion: 'manufacturing',
    production: 'manufacturing',
    jobs: 'jobs',
    projekte: 'jobs',
    projects: 'jobs',
    system: 'system',
    crm: 'crm',
    service: 'service',
    hr: 'hr',
    personal: 'hr',
    personnel: 'hr',
  };
  return aliases[normalized] || normalized;
}

function canonicalDashboardModuleName(key, fallback) {
  const names = {
    en: {
      system: 'System',
      finance: 'Finance',
      sales: 'Sales',
      purchasing: 'Purchasing',
      inventory: 'Inventory',
      crm: 'CRM',
      manufacturing: 'Manufacturing',
      service: 'Service',
      jobs: 'Jobs',
      hr: 'HR',
    },
    de: {
      system: 'System',
      finance: 'Finanzen',
      sales: 'Verkauf',
      purchasing: 'Einkauf',
      inventory: 'Lager',
      crm: 'CRM',
      manufacturing: 'Fertigung',
      service: 'Service',
      jobs: 'Projekte',
      hr: 'HR',
    },
  };
  return names[currentDashboardLanguage]?.[key] || names.en[key] || fallback;
}

function mergeModuleRows(...sources) {
  const rows = new Map();
  const ensureRow = (name) => {
    const key = moduleKey(name);
    if (!rows.has(key)) rows.set(key, { key, name: canonicalDashboardModuleName(key, name), count: 0, percent: 0 });
    return rows.get(key);
  };

  knownDashboardModules().forEach((name) => ensureRow(name));
  sources.flat().filter(Boolean).forEach((item) => {
    const name = item?.name || item?.label || '';
    if (!name) return;
    const row = ensureRow(name);
    row.name = canonicalDashboardModuleName(row.key, name);
    row.count = Math.max(row.count, safeNumber(item?.count ?? item?.value));
    row.percent = Math.max(row.percent, safeNumber(item?.percent));
  });

  const order = knownDashboardModules().map(moduleKey);
  return Array.from(rows.values()).sort((a, b) => {
    const indexA = order.indexOf(a.key);
    const indexB = order.indexOf(b.key);
    return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
  });
}

function mergeBcModuleRows(...sources) {
  const rows = new Map();
  knownDashboardModules().forEach((name) => {
    const key = moduleKey(name);
    rows.set(key, { key, name: canonicalDashboardModuleName(key, name), count: 0, percent: 0 });
  });
  sources.flat().filter(Boolean).forEach((item) => {
    const name = item?.name || item?.label || '';
    if (!name) return;
    const key = moduleKey(name);
    const row = rows.get(key) || { key, name: canonicalDashboardModuleName(key, name), count: 0, percent: 0 };
    row.name = canonicalDashboardModuleName(key, name);
    row.count = Math.max(row.count, safeNumber(item?.count ?? item?.value));
    row.percent = Math.max(row.percent, safeNumber(item?.percent));
    rows.set(key, row);
  });
  return Array.from(rows.values());
}

function moduleNameRows(items) {
  return Array.isArray(items)
    ? items.filter(Boolean).map((item) => ({
        name: item?.name || item?.label || '',
        count: 0,
        percent: 0,
      })).filter((item) => item.name)
    : [];
}

function sortModuleRowsByCount(rows) {
  const order = knownDashboardModules().map(moduleKey);
  return rows.slice().sort((a, b) => {
    const countDiff = safeNumber(b.count) - safeNumber(a.count);
    if (countDiff !== 0) return countDiff;
    const indexA = order.indexOf(a.key);
    const indexB = order.indexOf(b.key);
    return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
  });
}

function renderModuleDistribution(data) {
  const host = byId('overview-module-distribution');
  if (!host) return;
  const issueItems = normalizeDistributionItems(data?.free_insights?.module_distribution);
  const recordItems = normalizeDistributionItems(data?.free_insights?.records_by_module);
  const issueGroups = normalizeDistributionItems(data?.issue_groups);
  const moduleItems = sortModuleRowsByCount(mergeBcModuleRows(issueItems.length > 0 ? issueItems : issueGroups));
  const recordRows = sortModuleRowsByCount(mergeBcModuleRows(recordItems));

  if (moduleItems.length === 0 && recordRows.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">Module distribution will appear after scan results are available.</div>`;
    return;
  }

  const maxRecords = Math.max(...recordRows.map((item) => item.count), 1);
  const issueDistribution = normalizePercentDistribution(moduleItems);
  const moduleColors = getWeightedPalette(issueDistribution, (item) => item.percent, (item) => item.key);
  const recordColors = getWeightedPalette(recordRows, (item) => item.count, (item) => item.key);
  let start = 0;
  const donutSegments = issueDistribution.map((item) => {
    const percent = Math.max(Math.min(safeNumber(item.percent), 100), 0);
    const color = moduleColors.get(item.key) || WEIGHTED_ZERO_COLOR;
    const segment = percent > 0 ? `
      <circle cx="50" cy="50" r="39" pathLength="100" class="module-donut-segment"
        style="stroke:${color};stroke-dasharray:${percent} ${100 - percent};stroke-dashoffset:${-start};"></circle>
    ` : '';
    const end = start + percent;
    start = end;
    return segment;
  }).join('');
  const issueMarkup = issueDistribution.length > 0 ? `
    <div class="module-donut-wrap">
      <div class="module-donut">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <circle cx="50" cy="50" r="39" class="module-donut-track"></circle>
          ${donutSegments}
        </svg>
        <div><strong>100%</strong><span>Issues</span></div>
      </div>
      <div class="module-legend">
        ${issueDistribution.map((item) => {
          const color = moduleColors.get(item.key) || WEIGHTED_ZERO_COLOR;
          return `
          <div class="module-legend-row">
            <span class="module-legend-dot" style="background:${color}"></span>
            <span>${escapeHtml(item.name)}</span>
            <strong style="color:${color}">${formatPercent(item.percent)}</strong>
          </div>
        `;
        }).join('')}
      </div>
    </div>
  ` : `<div class="empty-state executive-empty compact-empty">No issue module data yet.</div>`;
  const recordMarkup = recordRows.map((item) => {
    const color = item.count > 0 ? (recordColors.get(item.key) || WEIGHTED_ZERO_COLOR) : WEIGHTED_ZERO_COLOR;
    return `
    <div class="module-record-row">
      <span>${escapeHtml(item.name)}</span>
      <div>
        <div class="distribution-track"><div class="distribution-fill record-fill" style="--weighted-color:${color};width:${item.count > 0 ? Math.max((item.count / maxRecords) * 100, 3) : 0}%"></div></div>
      </div>
      <strong style="color:${color}">${formatCompactRecords(item.count)}</strong>
    </div>
  `;
  }).join('') || `<div class="empty-state executive-empty compact-empty">No record module data yet.</div>`;

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

function executiveIssueSourceItems(data) {
  const sources = [
    data?.issue_preview,
    data?.top_findings,
    data?.free_insights?.top_findings,
    data?.premium_preview_findings,
  ];
  const source = sources.find((items) => Array.isArray(items) && items.length > 0);
  return Array.isArray(source) ? source : [];
}

function executiveIssueAccessNote(data) {
  if (data?.product_access?.monitoring_active) return t('executive_issue_list_monitoring_note');
  if (data?.visibility?.is_premium) return t('executive_issue_list_full_note');
  return t('executive_issue_list_free_note');
}

function normalizeExecutiveIssue(item, index) {
  const title = item?.title || item?.issue || item?.name || `${t('static_issue', 'Issue')} ${index + 1}`;
  const category = item?.group || item?.module || item?.area || t('static_module_category', 'Module / Category');
  const severity = normalizeIssueSeverity(item?.severity || item?.priority);
  const status = String(item?.status || '').trim() || t('executive_issue_list_status_open', 'Open');
  return {
    title,
    category,
    severity,
    severityLabel: issueSeverityLabel(severity, item?.severity_label || item?.priority_label),
    status,
  };
}

function renderExecutiveIssueList(data) {
  const host = byId('overview-recent-issues');
  if (!host) return;
  const severityRank = { critical: 0, high: 1, medium: 2, low: 3, unknown: 4 };
  const items = executiveIssueSourceItems(data)
    .filter(Boolean)
    .map((item, index) => normalizeExecutiveIssue(item, index))
    .sort((a, b) => (severityRank[a.severity] ?? 9) - (severityRank[b.severity] ?? 9))
    .slice(0, data?.visibility?.is_premium ? 5 : 3);

  if (items.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">${escapeHtml(t('executive_issue_list_empty'))}</div>`;
    return;
  }

  host.innerHTML = `
    <div class="executive-issue-list-note">${escapeHtml(executiveIssueAccessNote(data))}</div>
    ${items.map((item) => `
      <article class="executive-issue-row executive-issue-${escapeHtml(item.severity)}">
        <div class="executive-issue-main">
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(item.category)}</span>
        </div>
        <div class="executive-issue-meta" aria-label="${escapeHtml(t('static_status', 'Status'))}">
          <span class="severity severity-${escapeHtml(item.severity)}">${escapeHtml(item.severityLabel)}</span>
          <span class="status-badge status-open">${escapeHtml(item.status)}</span>
        </div>
      </article>
    `).join('')}
    <div class="executive-issue-list-source">${escapeHtml(t('executive_issue_list_source_note'))}</div>
  `;
}

function renderOverviewRecentIssues(data) {
  renderExecutiveIssueList(data);
}

function overviewActionCandidates(data) {
  const isPremium = Boolean(data?.visibility?.is_premium);
  const premiumItems = Array.isArray(data?.top_findings) ? data.top_findings : [];
  const freeItems = Array.isArray(data?.free_insights?.top_findings) ? data.free_insights.top_findings : [];
  const sourceItems = isPremium && premiumItems.length > 0 ? premiumItems : freeItems;
  return sourceItems
    .filter(Boolean)
    .map((item) => ({
      title: item?.title || item?.issue || item?.name || 'Recommended action',
      saving: safeNumber(item?.potential_saving_eur ?? item?.potential_savings_eur ?? item?.impact_eur ?? item?.estimated_loss_eur),
      openInBcUrl: String(item?.open_in_bc_url || item?.open_in_business_central_url || item?.bc_url || ''),
      severity: normalizeIssueSeverity(item?.severity || item?.priority),
    }))
    .sort((a, b) => safeNumber(b.saving) - safeNumber(a.saving));
}

function renderRecommendedActions(data) {
  const host = byId('overview-recommended-actions');
  if (!host) return;
  const items = overviewActionCandidates(data).slice(0, 3);

  if (items.length === 0) {
    host.innerHTML = `<div class="empty-state executive-empty">Recommended actions will appear after scan insights are available.</div>`;
    return;
  }

  host.innerHTML = items.map((item, index) => {
    const bcAction = item.openInBcUrl
      ? `<a href="${escapeHtml(item.openInBcUrl)}" class="pager-button recommended-action-bc" target="_blank" rel="noopener noreferrer">Open in BC</a>`
      : `<button type="button" class="pager-button recommended-action-bc" disabled>BC link unavailable</button>`;
    return `
      <article class="recommended-action-row recommended-action-${escapeHtml(item.severity)}">
        <div class="recommended-action-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 4 21 20H3z"/><path d="M12 9v5"/><path d="M12 17h.01"/></svg>
        </div>
        <div class="recommended-action-main">
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(issueSeverityLabel(item.severity))}</span>
        </div>
        <div class="recommended-action-saving">
          <span>Potential Saving</span>
          <strong>${item.saving > 0 ? formatKpiCurrency(item.saving) : 'Calculated after full analysis'}</strong>
        </div>
        ${bcAction}
      </article>
    `;
  }).join('');
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

  knownDashboardModules().forEach((name) => {
    grouped.set(moduleKey(name), { key: moduleKey(name), name, impact: 0 });
  });

  sourceItems.forEach((item) => {
    const name = item?.group || item?.module || item?.module_name || item?.category || item?.title || '';
    const impact = safeNumber(item?.impact_eur ?? item?.estimated_loss_eur ?? item?.estimated_impact_eur);
    if (!name || impact <= 0) return;
    const key = moduleKey(name);
    const current = grouped.get(key) || { key, name, impact: 0 };
    current.name = canonicalDashboardModuleName(key, name);
    current.impact += impact;
    grouped.set(key, current);
  });

  moduleNameRows(data?.module_scores).forEach((item) => {
    const key = moduleKey(item.name);
    if (!grouped.has(key)) grouped.set(key, { key, name: canonicalDashboardModuleName(key, item.name), impact: 0 });
  });

  const order = knownDashboardModules().map(moduleKey);
  return Array.from(grouped.values()).sort((a, b) => {
    const impactDiff = safeNumber(b.impact) - safeNumber(a.impact);
    if (impactDiff !== 0) return impactDiff;
    const indexA = order.indexOf(a.key);
    const indexB = order.indexOf(b.key);
    return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
  });
}

function businessImpactVariant(data) {
  if (data?.product_access?.monitoring_active || data?.monitoring_preview?.status === 'active') return 'monitoring';
  if (data?.visibility?.is_premium) return 'full';
  return 'free';
}

function businessImpactCurrencyValue(value) {
  const amount = safeNumber(value);
  return amount > 0 ? formatKpiCurrency(amount) : t('business_impact_not_available');
}

function businessImpactOperationalValue(kpis) {
  const affectedRecords = safeNumber(kpis?.affected_records);
  const issueSignals = safeNumber(kpis?.issues_count);
  if (affectedRecords > 0) return `${formatNumber(Math.round(affectedRecords))} ${t('business_impact_records', 'records')}`;
  if (issueSignals > 0) return `${formatNumber(Math.round(issueSignals))} ${t('business_impact_signals', 'signals')}`;
  return t('business_impact_not_available');
}

function businessImpactGovernanceValue(score, hasScanContext = true) {
  if (!hasScanContext) return t('business_impact_not_available');
  const band = scoreBand(score);
  if (band === 'critical' || band === 'warning') return t('business_impact_review_needed');
  if (band === 'moderate') return t('business_impact_elevated');
  if (band === 'good' || band === 'excellent') return t('business_impact_stable');
  return t('business_impact_not_available');
}

function renderBusinessImpact(data) {
  const host = byId('overview-business-impact');
  if (!host) return;

  const summaryHost = byId('business-impact-summary');
  const kpis = data?.kpis || {};
  const hasScanContext = Boolean(data?.selected_scan_id || data?.is_demo || safeNumber(kpis?.checks_run) > 0 || safeNumber(kpis?.health_score) > 0);
  const variant = businessImpactVariant(data);
  const summaryKey = hasScanContext ? `business_impact_summary_${variant}` : 'business_impact_summary_empty';
  const demoNote = data?.is_demo || data?.data_source === 'demo_preview'
    ? `<span class="business-impact-demo-note">${escapeHtml(t('business_impact_demo_note'))}</span>`
    : '';

  if (summaryHost) {
    summaryHost.innerHTML = `
      <p>${escapeHtml(t(summaryKey))}</p>
      ${demoNote}
    `;
  }

  const cards = [
    {
      label: t('business_impact_financial'),
      value: businessImpactCurrencyValue(kpis?.estimated_loss_eur),
      helper: t('business_impact_financial_helper'),
    },
    {
      label: t('business_impact_operational'),
      value: businessImpactOperationalValue(kpis),
      helper: t('business_impact_operational_helper'),
    },
    {
      label: t('business_impact_governance'),
      value: businessImpactGovernanceValue(kpis?.health_score, hasScanContext),
      helper: t('business_impact_governance_helper'),
    },
    {
      label: t('business_impact_potential'),
      value: businessImpactCurrencyValue(kpis?.potential_saving_eur),
      helper: t('business_impact_potential_helper'),
    },
  ];

  host.innerHTML = `
    ${cards.map((card) => `
      <article class="business-impact-card">
        <div class="business-impact-card-header">
          <span>${escapeHtml(card.label)}</span>
          <small>${escapeHtml(t('business_impact_estimate_label'))}</small>
        </div>
        <strong>${escapeHtml(card.value)}</strong>
        <p>${escapeHtml(card.helper)}</p>
      </article>
    `).join('')}
    <p class="business-impact-estimate-note">${escapeHtml(t('business_impact_estimate_note'))}</p>
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
    const statusLabel = item?.is_selected
      ? t('status_loaded', 'Loaded')
      : (item?.is_valid === false ? t('status_incomplete', 'Incomplete') : t('status_available', 'Available'));
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
  if (fallback && !['critical', 'high', 'medium', 'low', 'unknown'].includes(String(fallback).toLowerCase())) return String(fallback);
  const labels = {
    critical: t('severity_critical', currentDashboardLanguage === 'de' ? 'Kritisch' : 'Critical'),
    high: t('severity_high', currentDashboardLanguage === 'de' ? 'Hoch' : 'High'),
    medium: t('severity_medium', currentDashboardLanguage === 'de' ? 'Mittel' : 'Medium'),
    low: t('severity_low', currentDashboardLanguage === 'de' ? 'Niedrig' : 'Low'),
    unknown: t('severity_unknown', currentDashboardLanguage === 'de' ? 'Unbekannt' : 'Unknown'),
  };
  return labels[normalized] || labels.unknown;
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
    rawTitle: title || t('issue_detail', 'Issue detail'),
    title: isLocked ? t('premium_issue_details', 'Premium issue details') : (title || t('static_issue', 'Issue')),
    group: group || t('static_general', 'General'),
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
  const accessLabel = isLocked ? t('static_locked_access', 'Locked access') : t('static_full_issue_access', 'Full issue access');
  const scanLabel = data?.last_updated ? `${t('recent_scans', 'Last scan')} ${formatDateTime(data.last_updated)}` : t('static_no_scan_timestamp', 'No scan timestamp');

  host.innerHTML = `
    <span class="placeholder-status">${formatNumber(totalIssues)} ${escapeHtml(t('issues', 'Issues'))}</span>
    <span class="placeholder-status">${escapeHtml(scanLabel)}</span>
    <span class="placeholder-status">${escapeHtml(accessLabel)}</span>
  `;
}

function renderIssueSeverityCards(data, normalizedItems) {
  const host = byId('issues-severity-cards');
  if (!host) return;
  const counts = severityCountsForIssues(data, normalizedItems);
  const totalIssues = safeNumber(data?.kpis?.issues_count, Object.values(counts).reduce((sum, value) => sum + value, 0) || normalizedItems.length);
  const cards = [
    ['total', t('static_total_issues', 'Total Issues'), totalIssues],
    ['critical', issueSeverityLabel('critical'), counts.critical],
    ['high', issueSeverityLabel('high'), counts.high],
    ['medium', issueSeverityLabel('medium'), counts.medium],
    ['low', issueSeverityLabel('low'), counts.low],
  ];

  host.innerHTML = cards.map(([key, label, count]) => `
    <article class="stat-card panel issue-severity-card issue-severity-${key}">
      <div class="stat-label">${escapeHtml(label)}</div>
      <div class="stat-value">${formatNumber(count)}</div>
    </article>
  `).join('');
}

function issueInfoRows(issue) {
  return [
    [t('static_issue_code', 'Issue Code'), issue.id],
    [t('static_module_category', 'Module / Category'), issue.group || t('static_general', 'General')],
    [t('static_severity', 'Severity'), issue.severityLabel],
    [t('static_status', 'Status'), issue.status || t('static_open', 'Open')],
    [t('static_affected_records', 'Affected Records'), issue.locked ? t('static_locked', 'Locked') : formatNumber(issue.count)],
    [t('static_estimated_impact_loss', 'Estimated Impact / Loss'), issue.locked ? t('static_locked', 'Locked') : (issue.impact > 0 ? formatCurrency(issue.impact) : t('static_not_calculated_yet', 'Not calculated yet'))],
    [t('static_last_scan_updated', 'Last Scan / Last Updated'), issue.detectedOn ? formatDateTime(issue.detectedOn) : t('static_not_available', 'Not available')],
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

  const title = issue.locked ? t('premium_issue_details', 'Premium issue details') : (issue.title || issue.rawTitle || t('issue_detail', 'Issue detail'));
  const affectedLabel = issue.locked ? t('static_locked', 'Locked') : formatNumber(issue.count);
  const lossLabel = issue.locked ? t('static_locked', 'Locked') : (issue.impact > 0 ? formatCurrency(issue.impact) : t('static_not_calculated_yet', 'Not calculated yet'));
  const description = issue.locked
    ? t('issue_detail_description_locked', 'Detailed description is available after the full analysis.')
    : (issue.description || t('issue_detail_description_locked', 'Detailed description is available after the full analysis.'));
  const recommendation = issue.locked
    ? t('issue_detail_recommendation_locked', 'Recommendation will be generated after the full analysis.')
    : (issue.recommendation || t('issue_detail_recommendation_locked', 'Recommendation will be generated after the full analysis.'));
  const scoreImpact = issue.locked
    ? t('issue_detail_score_impact_empty', 'Score impact details will appear when available.')
    : (issue.scoreImpact ? String(issue.scoreImpact) : t('issue_detail_score_impact_empty', 'Score impact details will appear when available.'));
  const businessImpactBody = issue.locked
    ? `<div class="locked-detail-state">${escapeHtml(t('issue_detail_business_impact_locked', 'Business impact details are protected for the current access level.'))}</div>`
    : `
      <div class="business-impact-grid">
        <div><span>Estimated Loss</span><strong>${escapeHtml(lossLabel)}</strong></div>
        <div><span>Affected Records</span><strong>${escapeHtml(affectedLabel)}</strong></div>
        <div><span>${escapeHtml(t('static_severity', 'Severity'))}</span><strong>${escapeHtml(issue.severityLabel)}</strong></div>
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
          ${escapeHtml(item.locked ? t('view_locked_details', 'View locked details') : t('view_details', 'View Details'))}
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
      action: isLocked ? t('static_unlock_issue_details', 'Unlock full issue details') : deriveActionText(item, issue),
      relatedIssue: isLocked ? t('paid_access', 'Paid Access') : (explicitIssueTitle || issue?.rawTitle || issue?.title || t('issues', 'Issue')),
      module: issue?.group || item?.module || item?.group || t('static_general', 'General'),
      priority,
      priorityLabel: issueSeverityLabel(priority, item?.priority_label || item?.severity_label),
      effort: isLocked ? t('static_locked', 'Locked') : deriveActionEffort(item, issue),
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
  const accessLabel = isLocked ? t('static_locked_access', 'Locked access') : t('static_full_action_access', 'Full action access');
  host.innerHTML = `
    <span class="placeholder-status">${formatNumber(actions.length)} ${escapeHtml(t('actions', 'Actions'))}</span>
    <span class="placeholder-status">${escapeHtml(potentialSaving > 0 ? formatCurrency(potentialSaving) : t('static_saving_pending', 'Saving pending'))}</span>
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
    [t('static_recommended_actions', 'Recommended Actions'), formatNumber(recommended), t('static_prioritized_recommendations', 'Prioritized recommendations')],
    [t('static_high_priority', 'High Priority'), formatNumber(highPriority), t('static_critical_high_priority', 'Critical and high priority')],
    [t('static_potential_saving', 'Potential Saving'), potentialSaving > 0 ? formatCurrency(potentialSaving) : t('static_not_calculated_yet', 'Not calculated yet'), t('estimated_annual_loss_helper', 'Existing scan economics')],
    [t('static_open_actions', 'Open Actions'), formatNumber(openItems), t('static_open', 'Open')],
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
      <div class="subscription-value stat-value-small">${escapeHtml(value || 'â€”')}</div>
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
  if (rawUntil && rawUntil !== 'Ã¢â‚¬â€') {
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

function availableSubscriptionProductKeys(data, { overview = false } = {}) {
  const access = data?.product_access || {};
  const monitoringActive = Boolean(access.monitoring_active || access.can_use_monitoring || data?.monitoring_status === 'active');
  if (monitoringActive) return new Set();

  const hasFullOrPremiumAccess = Boolean(
    access.full_analysis_access_active ||
    access.assessment_access_active ||
    access.validation_check_access_active ||
    access.validation_access_active ||
    access.can_view_issues ||
    data?.visibility?.is_premium
  );

  if (hasFullOrPremiumAccess) {
    return new Set(overview
      ? ['validation_check', 'monitoring_monthly']
      : ['validation_check', 'monitoring_monthly', 'monitoring_annual']);
  }

  return new Set(overview
    ? ['full_analysis', 'monitoring_monthly']
    : ['full_analysis', 'monitoring_monthly', 'monitoring_annual']);
}

function renderNoSubscriptionNeeded(host) {
  host.innerHTML = `
    <article class="subscription-empty-state">
      <h4>${escapeHtml(t('subscription_no_products_title') || 'No additional subscription needed')}</h4>
      <p>${escapeHtml(t('subscription_no_products_body') || 'Monitoring is active. All current dashboard features are already available for this tenant.')}</p>
    </article>
  `;
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
  const allowedProducts = availableSubscriptionProductKeys(data);
  const items = [
    ['full_analysis', 'Full Analysis', 'Complete Data Health Assessment', 'Buy Now', activeAssessment, 'Most Popular'],
    ['validation_check', 'Validation Check / New Credit', 'Validate improvements after remediation', 'Buy Now', activeValidation, 'After Fixes'],
    ['monitoring_monthly', 'Monitoring Monthly', 'Continuous monitoring with trends and alerts', 'Start Monitoring', monitoringActive, 'Recommended'],
    ['monitoring_annual', 'Monitoring Annual', 'Best value annual monitoring plan', 'Start Annual Monitoring', monitoringActive, 'Best Value'],
  ].filter(([key]) => allowedProducts.has(key));
  if (!items.length) {
    renderNoSubscriptionNeeded(host);
    return;
  }
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
  const allowedProducts = availableSubscriptionProductKeys(data, { overview: true });
  const items = [
    ['full_analysis', 'Full Analysis', 'Complete insights for 7 days: issue details, affected records, recommendations, actions and reports.', 'Buy Full Analysis', activeAssessment, 'Most Popular'],
    ['validation_check', 'Validation Check / New Credit', 'New scan comparison for 7 days: validate fixes after remediation and update your score.', 'Buy Validation Check', activeValidation, 'After Fixes'],
    ['monitoring_monthly', 'Monitoring', 'One full month of recurring monitoring: trends, scan history, alerts, prioritized actions and executive reporting.', 'Start Monitoring', monitoringActive, 'Best for ongoing control'],
  ].filter(([key]) => allowedProducts.has(key));
  if (!items.length) {
    renderNoSubscriptionNeeded(host);
    return;
  }
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

function applyDashboardTheme(isDark) {
  document.documentElement.classList.toggle('dashboard-dark', Boolean(isDark));
  document.documentElement.classList.toggle('dashboard-light', !Boolean(isDark));
  document.body.classList.toggle('dashboard-dark', Boolean(isDark));
  document.body.classList.toggle('dashboard-light', !Boolean(isDark));
  const toggle = byId('dashboard-dark-toggle');
  if (toggle) toggle.checked = Boolean(isDark);
}

const DASHBOARD_SHELL_SLOTS = [
  'executive-summary',
  'health-score',
  'score-breakdown',
  'business-impact',
  'top-risks',
  'critical-issues',
  'recommended-actions',
  'issue-list',
  'monitoring',
];

function initDashboardShell() {
  const root = byId('dashboard-root');
  if (root) root.dataset.shellReady = 'true';
  document.body.dataset.dashboardShell = 'ready';

  document.querySelectorAll('[data-dashboard-slot]').forEach((slot) => {
    slot.classList.add('dashboard-slot');
    slot.dataset.shellReady = 'true';
    if (!slot.hasAttribute('role')) slot.setAttribute('role', 'region');
    if (!slot.hasAttribute('aria-label')) {
      const label = String(slot.dataset.dashboardSlot || '').replaceAll('-', ' ');
      slot.setAttribute('aria-label', label ? `Dashboard slot: ${label}` : 'Dashboard slot');
    }
  });

  DASHBOARD_SHELL_SLOTS.forEach((slotName) => {
    if (!document.querySelector(`[data-dashboard-slot="${slotName}"]`)) {
      console.warn(`Dashboard shell slot missing: ${slotName}`);
    }
  });
}
function initDarkModeToggle() {
  const toggle = byId('dashboard-dark-toggle');
  const stored = localStorage.getItem('bcsentinel-dashboard-theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialDark = stored ? stored === 'dark' : prefersDark;
  applyDashboardTheme(initialDark);
  if (!toggle) return;
  toggle.addEventListener('change', () => {
    const isDark = toggle.checked;
    localStorage.setItem('bcsentinel-dashboard-theme', isDark ? 'dark' : 'light');
    applyDashboardTheme(isDark);
  });
}

function resolveDashboardLanguage(data = currentDashboardState) {
  return dashboardLanguageOverride || data?.language || 'en';
}

function renderDashboardFromState(data) {
  if (!data) return;
  applyDashboardUi(data?.ui || {}, resolveDashboardLanguage(data));
  const activeTab = document.querySelector('.topnav-link.is-active')?.dataset?.tab || 'overview';
  updatePageHeader(activeTab);
  setText('last-updated', `${t('last_updated', 'Last updated')}: ${formatDateTime(data?.last_updated)}`);
  renderExecutiveHero(data);

  renderOverviewKpis(data);
  renderScoreBreakdown(data);
  renderBusinessImpact(data);
  renderRecommendedActions(data);
  renderOverviewModuleScores(data);
  renderProfileCards(data?.module_scores || [], data?.profile_cards || []);
  renderModuleVolume(data);
  renderRecentScans(data?.recent_scans || []);
  renderRecentScansPagination(data?.recent_scans_pagination || {});
  renderScansPage(data);
  updateOverviewTrendVisibility(data);
  renderTrend('trend-chart', data?.score_trend || [], false, t('score_history_after_scans', 'Score history appears after at least two scans. Monitoring keeps this trend useful over time.'));
  renderTrend('loss-chart', data?.loss_trend || [], true, t('loss_history_after_scans', 'Loss history appears after at least two scans. Monitoring adds the historical business context.'));
  renderTrend('analytics-score-trend', data?.score_trend || [], false, t('score_history_after_scans_short', 'Score history appears after at least two scans.'));
  renderTrend('analytics-loss-trend', data?.loss_trend || [], true, t('loss_history_after_scans_short', 'Loss history appears after at least two scans.'));
  renderIssueDistribution(data);
  renderModuleDistribution(data);
  renderOverviewRecentIssues(data);
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
  translateStaticDashboardText();
}

function initLanguageToggle() {
  const toggle = byId('dashboard-language-toggle');
  const stored = localStorage.getItem('bcsentinel-dashboard-language');
  if (stored === 'de' || stored === 'en') dashboardLanguageOverride = stored;
  if (toggle) {
    toggle.value = dashboardLanguageOverride || currentDashboardLanguage;
    toggle.addEventListener('change', () => {
      dashboardLanguageOverride = toggle.value === 'de' ? 'de' : 'en';
      localStorage.setItem('bcsentinel-dashboard-language', dashboardLanguageOverride);
      if (currentDashboardState) renderDashboardFromState(currentDashboardState);
    });
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
    ? t('full_premium_analysis', 'Full Premium Analysis')
    : (hasPaidAccess ? t('full_premium_analysis', 'Full Premium Analysis') : t('free_data_score', 'Free Data Score'));

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
    currentSelectedScanId = data?.selected_scan_id || null;
    renderDashboardFromState(data);
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
  initDashboardShell();
  initDarkModeToggle();
  initLanguageToggle();
  registerEvents();
  switchTab('overview');
  recentScansPage = 1;
  loadDashboard();
});



