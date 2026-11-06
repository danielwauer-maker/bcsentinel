import { useMemo, useState } from 'react';
import { useActionsData, useDashboardData, useExecutiveReport, useLatestScanStatus, type AsyncState } from './hooks';
import { experienceMode, type AnalyticsDashboardData, type RemediationAction } from './types';
import {
  EmptyValue,
  LockedPanel,
  MetricCard,
  PageHeader,
  RiskBars,
  ScoreGauge,
  SectionCard,
  StatePanel,
  StatusBadge,
  TrendChart,
} from '../components/ui';

const euro = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
const integer = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 });

function SessionRequired() {
  return (
    <StatePanel title="Runtime-Sitzung erforderlich" tone="warning">
      <p>Die Dashboard-Seite ist implementiert, benötigt für Live-Daten aber eine authentifizierte Tenant-Sitzung. Die Identity-/Session-Bindung wird in D8/E1 an den produktiven Login gekoppelt.</p>
    </StatePanel>
  );
}

function LoadingState() {
  return <StatePanel title="Daten werden geladen">BCSentinel liest die aktuelle, tenant-isolierte Runtime-Projektion.</StatePanel>;
}

function ErrorState({ state }: { state: Extract<AsyncState<unknown>, { status: 'error' }> }) {
  const title = state.code === 403 ? 'Zugriff nicht erlaubt' : state.code === 404 ? 'Daten nicht gefunden' : 'Daten konnten nicht geladen werden';
  return <StatePanel title={title} tone="error">{state.error}</StatePanel>;
}

function DashboardBoundary({ children }: { children: (data: AnalyticsDashboardData) => React.ReactNode }) {
  const state = useDashboardData();
  if (state.status === 'session_required') return <SessionRequired />;
  if (state.status === 'loading') return <LoadingState />;
  if (state.status === 'error') return <ErrorState state={state} />;
  return <>{children(state.data)}</>;
}

function Hero({ data }: { data: AnalyticsDashboardData }) {
  const mode = experienceMode(data);
  const modeLabel = mode === 'monitoring' ? 'Monitoring' : mode === 'assessment' ? 'Assessment' : 'Free Entry';
  return (
    <section className="executive-hero">
      <div className="hero-copy">
        <span className="hero-kicker">{modeLabel}</span>
        <h2>{data.hero.headline_prefix} <em>{data.hero.headline_highlight}</em> {data.hero.headline_suffix}</h2>
        <p>{data.hero.eyebrow}</p>
        <div className="hero-meta">
          <span>{data.scan_mode_label}</span>
          <span>Stand: {data.last_updated}</span>
          {data.selected_scan_id && <span>Scan {data.selected_scan_id}</span>}
        </div>
      </div>
      <div className="hero-score">
        <ScoreGauge score={data.kpis.health_score} />
        <div>
          <strong>Health Score</strong>
          <span>Runtime-Metrik aus dem ausgewählten Scan</span>
        </div>
      </div>
    </section>
  );
}

function CriticalFindingMetric({ data }: { data: AnalyticsDashboardData }) {
  const critical = data.top_findings.filter((finding) => finding.severity.toLowerCase() === 'critical');
  if (!critical.length) {
    return <MetricCard label="Critical Findings" value={<EmptyValue />} helper="Die aktuelle Analytics-Projektion liefert noch keinen separaten Critical-KPI; High wird nicht stillschweigend als Critical umgedeutet." />;
  }
  return <MetricCard label="Critical Findings" value={integer.format(critical.length)} tone="critical" helper="Explizit als critical klassifiziert" />;
}

function FindingsTable({ data, limit }: { data: AnalyticsDashboardData; limit?: number }) {
  const findings = typeof limit === 'number' ? data.top_findings.slice(0, limit) : data.top_findings;
  if (!findings.length) return <StatePanel title="Keine Detail-Findings verfügbar">Die Runtime liefert für diesen Zugriff keine freigegebenen Finding-Details.</StatePanel>;
  return (
    <div className="table-scroll" role="region" aria-label="Findings" tabIndex={0}>
      <table className="data-table">
        <thead><tr><th>Finding</th><th>Bereich</th><th>Severity</th><th>Betroffen</th><th>Modeled Financial Impact</th><th>Empfehlung</th><th>BC</th></tr></thead>
        <tbody>
          {findings.map((finding) => (
            <tr key={finding.code}>
              <td><strong>{finding.title}</strong><span className="table-subline">{finding.code}</span></td>
              <td>{finding.group}</td>
              <td><StatusBadge value={finding.severity_label || finding.severity} /></td>
              <td>{integer.format(finding.count)}</td>
              <td>{euro.format(finding.impact_eur)}</td>
              <td>{finding.recommendation_preview || <EmptyValue label="Keine Empfehlung in der aktuellen Projektion" />}</td>
              <td>{finding.open_in_bc_url ? <a className="text-link" href={finding.open_in_bc_url} target="_blank" rel="noreferrer">Öffnen</a> : <EmptyValue />}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MonitoringLocked() {
  return <LockedPanel title="Monitoring ist für diesen Zugriff nicht aktiv" body="Assessment zeigt den aktuellen Zustand. Monitoring ergänzt erst bei aktivem Monitoring-Vertrag Historie, Trends und fortlaufende Signale." actionLabel="Subscription / Billing" />;
}

export function OverviewPage() {
  return (
    <DashboardBoundary>
      {(data) => {
        const mode = experienceMode(data);
        const paid = mode !== 'free';
        return (
          <div className="page-stack">
            <PageHeader eyebrow="Dashboard" title="Overview" description="Executive Sicht auf Datenqualität, Risiken und erlaubte nächste Schritte — ohne operative BC-Schreibaktionen." />
            <Hero data={data} />

            {mode === 'free' ? (
              <div className="metric-grid metric-grid-4">
                <MetricCard label="Health Score" value={`${data.kpis.health_score}/100`} />
                <MetricCard label="Geprüfte Datensätze" value={integer.format(data.kpis.total_records)} />
                <MetricCard label="Risikobereiche" value={integer.format(data.issue_groups.length)} helper="Aggregiert; keine Finding-Details" />
                <MetricCard label="Finanzieller Einfluss" value="Erkannt" helper="Konkrete Werte sind im Assessment verfügbar" tone="brand" />
              </div>
            ) : (
              <div className="metric-grid metric-grid-4">
                <MetricCard label="Health Score" value={`${data.kpis.health_score}/100`} />
                <CriticalFindingMetric data={data} />
                <MetricCard label="Estimated Loss" value={data.selected_scan_id ? euro.format(data.kpis.estimated_loss_eur) : <EmptyValue />} helper="Modelliertes jährliches wirtschaftliches Risiko · fin-v1" tone="warning" />
                <MetricCard label="Potential Saving" value={data.selected_scan_id ? euro.format(data.kpis.potential_saving_eur) : <EmptyValue />} helper="Modelliertes Potenzial, nicht realisierte Einsparung" tone="brand" />
              </div>
            )}

            <div className="two-column-grid">
              <SectionCard title={mode === 'free' ? 'Aggregierte Risikobereiche' : 'Top Risks'} subtitle={mode === 'free' ? 'Free Entry zeigt nur aggregierte Signale.' : 'Priorisiert aus der aktuellen Runtime-Projektion.'}>
                {mode === 'free' ? <RiskBars items={data.issue_groups} /> : <FindingsTable data={data} limit={5} />}
              </SectionCard>
              <SectionCard title="Business Impact" subtitle="Financial KPIs werden im Web nicht neu berechnet.">
                {paid ? (
                  <div className="impact-summary">
                    <div><span>Estimated Loss</span><strong>{euro.format(data.kpis.estimated_loss_eur)}</strong></div>
                    <div><span>Potential Saving</span><strong>{euro.format(data.kpis.potential_saving_eur)}</strong></div>
                    <p>Methodik: <strong>fin-v1</strong>. Potential Saving ist kein garantierter oder bereits realisierter Nutzen.</p>
                  </div>
                ) : (
                  <LockedPanel title="Finanzielle Detailwerte sind gesperrt" body="Free Entry bestätigt, ob ein finanzieller Einfluss erkannt wurde. Estimated Loss und Potential Saving werden erst im Assessment offengelegt." actionLabel="Assessment ansehen" />
                )}
              </SectionCard>
            </div>

            {paid && (
              <SectionCard title="Recommendations & Decision Paths" subtitle="Das Web erklärt und navigiert; operative Änderungen bleiben in Business Central.">
                <div className="decision-grid">
                  <a className="decision-card" href="#findings"><strong>Findings verstehen</strong><span>Evidenz, Betroffenheit und Empfehlungen prüfen.</span></a>
                  <a className="decision-card" href="#financial"><strong>Financial Impact</strong><span>Gespeicherte fin-v1-Projektion nachvollziehen.</span></a>
                  <a className="decision-card" href="#actions"><strong>Actions verfolgen</strong><span>Read-only Remediation-Status aus Business Central.</span></a>
                  <a className="decision-card" href="#reports"><strong>Executive Report</strong><span>Management-Sicht auf denselben Scan öffnen.</span></a>
                </div>
              </SectionCard>
            )}

            {mode === 'monitoring' ? (
              <SectionCard title="Monitoring Snapshot" subtitle="Historische Werte werden nicht addiert und nicht als realisierte Einsparung dargestellt.">
                <div className="two-column-grid compact-grid">
                  <TrendChart points={data.score_trend} ariaLabel="Health Score Verlauf" valueFormatter={(value) => `${Math.round(value)}/100`} />
                  <TrendChart points={data.loss_trend} ariaLabel="Estimated Loss Verlauf" valueFormatter={(value) => euro.format(value)} />
                </div>
              </SectionCard>
            ) : <MonitoringLocked />}
          </div>
        );
      }}
    </DashboardBoundary>
  );
}

export function FindingsPage() {
  return (
    <DashboardBoundary>
      {(data) => {
        const mode = experienceMode(data);
        return (
          <div className="page-stack">
            <PageHeader eyebrow="Risk Intelligence" title="Findings" description="Finding-Evidenz und Empfehlungen aus der Runtime. Änderungen an BC-Daten oder Findings sind hier bewusst nicht möglich." />
            {mode === 'free' ? (
              <>
                <SectionCard title="Aggregierte Risikobereiche"><RiskBars items={data.issue_groups} /></SectionCard>
                <LockedPanel title="Finding-Details sind im Free Entry gesperrt" body="Assessment öffnet Finding-Evidenz, betroffene Datensätze, Empfehlungen und priorisierte Business-Impact-Sicht." actionLabel="Assessment / Billing" />
              </>
            ) : (
              <>
                <div className="metric-grid metric-grid-4">
                  <MetricCard label="Findings" value={integer.format(data.kpis.issues_count)} />
                  <MetricCard label="Affected Records" value={integer.format(data.kpis.affected_records)} />
                  <CriticalFindingMetric data={data} />
                  <MetricCard label="Scan" value={data.selected_scan_id || <EmptyValue />} helper={data.last_updated} />
                </div>
                <SectionCard title="Finding Register" subtitle="Read-only. Ein BC-Deep-Link erscheint nur, wenn die Runtime ihn sicher liefert."><FindingsTable data={data} /></SectionCard>
              </>
            )}
          </div>
        );
      }}
    </DashboardBoundary>
  );
}

function actionDueLabel(action: RemediationAction) {
  if (!action.due_at_utc) return '—';
  const date = new Date(action.due_at_utc);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('de-DE');
}

export function ActionsPage() {
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const filters = useMemo(() => ({ status: status || undefined, priority: priority || undefined }), [status, priority]);
  const state = useActionsData(filters);

  if (state.status === 'session_required') return <SessionRequired />;
  if (state.status === 'loading') return <LoadingState />;
  if (state.status === 'error') return <ErrorState state={state} />;

  const { metrics, actions } = state.data;
  return (
    <div className="page-stack">
      <PageHeader eyebrow="Remediation" title="Actions" description="Read-only Spiegel der echten Remediation Actions. Recommendation ist nicht Action; completed bedeutet nicht automatisch validated resolved." />
      <div className="metric-grid metric-grid-5">
        <MetricCard label="Open" value={metrics.open} />
        <MetricCard label="In Progress" value={metrics.in_progress} />
        <MetricCard label="Blocked" value={metrics.blocked} tone="warning" />
        <MetricCard label="Completed" value={metrics.completed} tone="success" />
        <MetricCard label="Overdue" value={metrics.overdue} tone="critical" />
      </div>
      <SectionCard title="Action Register" subtitle="Status, Priorität, Owner und Fälligkeit werden in Business Central gepflegt.">
        <div className="filter-row">
          <label>Status<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">Alle</option><option value="open">Open</option><option value="in_progress">In Progress</option><option value="blocked">Blocked</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select></label>
          <label>Priorität<select value={priority} onChange={(event) => setPriority(event.target.value)}><option value="">Alle</option><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label>
        </div>
        {!actions.length ? <StatePanel title="Keine Actions für diesen Filter">Es werden keine Recommendations als Ersatz-Actions erfunden.</StatePanel> : (
          <div className="table-scroll" role="region" aria-label="Remediation Actions" tabIndex={0}>
            <table className="data-table"><thead><tr><th>Action</th><th>Finding</th><th>Priorität</th><th>Status</th><th>Owner</th><th>Fällig</th><th>Validation</th></tr></thead><tbody>
              {actions.map((action) => <tr key={action.action_id}>
                <td><strong>{action.title}</strong><span className="table-subline">{action.action_id}</span></td>
                <td>{action.finding_key}</td>
                <td><StatusBadge value={action.priority} /></td>
                <td><StatusBadge value={action.status} /></td>
                <td>{action.owner_display_name || <EmptyValue />}</td>
                <td>{actionDueLabel(action)}</td>
                <td>{action.validation_result_ref ? 'Validation verknüpft' : <span className="muted">Nicht validiert</span>}</td>
              </tr>)}
            </tbody></table>
          </div>
        )}
      </SectionCard>
      <StatePanel title="Operative Authority: Business Central">Erstellen, Status ändern, Owner/Priorität bearbeiten, abschließen oder reaktivieren ist im Web nicht verfügbar.</StatePanel>
    </div>
  );
}

export function FinancialImpactPage() {
  return (
    <DashboardBoundary>
      {(data) => {
        const mode = experienceMode(data);
        return (
          <div className="page-stack">
            <PageHeader eyebrow="Business Impact" title="Financial Impact" description="Eine gemeinsame Backend-Projektion für Estimated Loss und Potential Saving. Keine clientseitige Neuberechnung." />
            {mode === 'free' ? <LockedPanel title="Financial Impact ist im Assessment verfügbar" body="Free Entry zeigt keine konkreten finanziellen Beträge. Dadurch bleibt die Entitlement-Grenze eindeutig." actionLabel="Assessment / Billing" /> : !data.selected_scan_id ? (
              <StatePanel title="Noch keine Financial-Projektion">Es liegt noch kein ausgewählter Scan vor. Fehlende Werte werden nicht als 0 € interpretiert.</StatePanel>
            ) : (
              <>
                <div className="metric-grid metric-grid-4">
                  <MetricCard label="Estimated Loss" value={euro.format(data.kpis.estimated_loss_eur)} helper="Modelliertes jährliches wirtschaftliches Risiko" tone="warning" />
                  <MetricCard label="Potential Saving" value={euro.format(data.kpis.potential_saving_eur)} helper="Modelliertes wiedergewinnbares Potenzial; nicht garantiert" tone="brand" />
                  <MetricCard label="Methodology" value="fin-v1" helper="Aktuelle gemeinsame Runtime-Methodik" />
                  <MetricCard label="Projection Reference" value={data.selected_scan_id} helper={data.last_updated} />
                </div>
                <SectionCard title="Impact by Finding / Area" subtitle="Die Finding-Impact-Werte stammen aus derselben gespeicherten Scan-Projektion."><FindingsTable data={data} /></SectionCard>
                <SectionCard title="Methodology Disclosure">
                  <div className="prose-block">
                    <p><strong>Estimated Loss</strong> ist ein modelliertes, annualisiertes wirtschaftliches Risiko und kein bestätigter buchhalterischer Verlust.</p>
                    <p><strong>Potential Saving</strong> ist modelliertes Potenzial und weder garantiert noch bereits realisiert.</p>
                    <p>Validierte Verbesserung wird erst gezeigt, wenn eine passende Baseline und Validation-Evidence vorhanden ist. Ein Realized-Saving-KPI ist in V1 nicht freigegeben.</p>
                  </div>
                </SectionCard>
              </>
            )}
          </div>
        );
      }}
    </DashboardBoundary>
  );
}

function ReportBody({ data }: { data: AnalyticsDashboardData }) {
  const enabled = experienceMode(data) !== 'free' && Boolean(data.selected_scan_id);
  const state = useExecutiveReport(data.selected_scan_id, enabled);
  if (!enabled) return <LockedPanel title="Executive Report ist nicht verfügbar" body="Ein aktiver Assessment-, Validation- oder Monitoring-Zugriff und ein vorhandener Scan sind erforderlich." actionLabel="Subscription / Billing" />;
  if (state.status === 'session_required') return <SessionRequired />;
  if (state.status === 'loading') return <LoadingState />;
  if (state.status === 'error') return <ErrorState state={state} />;
  if (!state.data) return <StatePanel title="Kein Report verfügbar">Die Runtime liefert aktuell keinen Executive Report.</StatePanel>;
  const report = state.data;
  return (
    <>
      <div className="metric-grid metric-grid-4">
        <MetricCard label="Health Score" value={`${report.data_health_score}/100`} />
        <MetricCard label="Findings" value={integer.format(report.issues_count)} />
        <MetricCard label="Estimated Loss" value={euro.format(report.estimated_loss_eur)} tone="warning" />
        <MetricCard label="Potential Saving" value={euro.format(report.potential_saving_eur)} tone="brand" />
      </div>
      <SectionCard title="Executive Summary"><p className="report-summary">{report.executive_summary}</p></SectionCard>
      <SectionCard title="Top Risks" subtitle="Modeled Financial Impact — nicht realisierter Nutzen.">
        {!report.top_risks.length ? <StatePanel title="Keine Top Risks im Report">Die Report-Projektion enthält keine Top-Risk-Einträge.</StatePanel> : (
          <div className="risk-list">{report.top_risks.map((risk) => <article key={risk.code}><div><StatusBadge value={risk.severity} /><strong>{risk.title}</strong></div><span>{risk.category} · {integer.format(risk.affected_count)} betroffen · {euro.format(risk.estimated_impact_eur)}</span><p>{risk.recommendation}</p></article>)}</div>
        )}
      </SectionCard>
      <SectionCard title="Recommended Actions">
        {!report.recommended_actions.length ? <StatePanel title="Keine Report-Empfehlungen">Keine Empfehlungen in der aktuellen Report-Projektion.</StatePanel> : <ol className="recommendation-list">{report.recommended_actions.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ol>}
      </SectionCard>
      <StatePanel title="Export-Contract folgt in D10">D7 zeigt das bestehende Report-Read-Model. Der verbindliche gemeinsame Web/HTML/PDF-Datenvertrag wird in D10 finalisiert; deshalb erfindet diese Seite keinen zweiten Exportpfad.</StatePanel>
    </>
  );
}

export function ReportsPage() {
  return <DashboardBoundary>{(data) => <div className="page-stack"><PageHeader eyebrow="Executive Reporting" title="Reports" description="Management-Sicht auf denselben Scan und dieselben gespeicherten Financial Values." /><ReportBody data={data} /></div>}</DashboardBoundary>;
}

function ScanStatusPanel() {
  const state = useLatestScanStatus();
  if (state.status === 'session_required' || state.status === 'loading') return null;
  if (state.status === 'error' || !state.data) return <StatePanel title="Kein aktiver Runtime-Status">Scan-Historie bleibt verfügbar; es liegt kein aktueller Laufstatus vor.</StatePanel>;
  const status = state.data;
  return (
    <SectionCard title="Latest Runtime Status" subtitle="Read-only Status; ein Scan wird im Web weder gestartet noch erneut ausgeführt.">
      <div className="runtime-status"><StatusBadge value={status.status || 'unknown'} /><strong>{typeof status.progress_percent === 'number' ? `${status.progress_percent}%` : '—'}</strong><span>{status.current_module || status.current_step || 'Keine Detailphase'}</span></div>
    </SectionCard>
  );
}

export function ScansPage() {
  return (
    <DashboardBoundary>
      {(data) => (
        <div className="page-stack">
          <PageHeader eyebrow="Scan History" title="Scans" description="Historie und Status aus der Runtime. Scope, Scheduler und Scan-Ausführung bleiben in Business Central." />
          <ScanStatusPanel />
          <SectionCard title="Scan History" subtitle="Kein Start-, Rerun- oder Scope-Edit im Web.">
            {!data.recent_scans.length ? <StatePanel title="Noch keine Scans">Es liegt noch keine Scan-Historie vor.</StatePanel> : (
              <div className="table-scroll" role="region" aria-label="Scan Historie" tabIndex={0}>
                <table className="data-table"><thead><tr><th>Datum</th><th>Typ</th><th>Health Score</th><th>Findings</th><th>Headline</th><th>Referenz</th></tr></thead><tbody>
                  {data.recent_scans.map((scan) => <tr key={scan.scan_id} className={scan.is_selected ? 'selected-row' : undefined}><td>{scan.generated_at}</td><td>{scan.scan_type}</td><td>{scan.data_score}/100</td><td>{scan.issues_count}</td><td>{scan.headline || <EmptyValue />}</td><td><a className="text-link" href={`#overview?scan=${encodeURIComponent(scan.scan_id)}`}>{scan.scan_id}</a></td></tr>)}
                </tbody></table>
              </div>
            )}
          </SectionCard>
        </div>
      )}
    </DashboardBoundary>
  );
}

export function MonitoringPage() {
  return (
    <DashboardBoundary>
      {(data) => {
        if (experienceMode(data) !== 'monitoring') return <div className="page-stack"><PageHeader eyebrow="Continuous Intelligence" title="Monitoring" description="Fortlaufende Sicht wird nur bei aktivem Monitoring freigeschaltet." /><MonitoringLocked /></div>;
        return (
          <div className="page-stack">
            <PageHeader eyebrow="Continuous Intelligence" title="Monitoring" description="Historie, Trends und Statussignale aus vergleichbaren Runtime-Daten — ohne Scheduler- oder Scan-Schreibaktionen." />
            <div className="metric-grid metric-grid-4">
              <MetricCard label="Health Score" value={`${data.kpis.health_score}/100`} />
              <CriticalFindingMetric data={data} />
              <MetricCard label="Estimated Loss" value={euro.format(data.kpis.estimated_loss_eur)} tone="warning" />
              <MetricCard label="Potential Saving" value={euro.format(data.kpis.potential_saving_eur)} tone="brand" helper="Nicht über Zeit summieren" />
            </div>
            <div className="two-column-grid">
              <SectionCard title="Health Score History"><TrendChart points={data.score_trend} ariaLabel="Health Score Historie" valueFormatter={(value) => `${Math.round(value)}/100`} /></SectionCard>
              <SectionCard title="Estimated Loss History"><TrendChart points={data.loss_trend} ariaLabel="Estimated Loss Historie" valueFormatter={(value) => euro.format(value)} /></SectionCard>
            </div>
            <SectionCard title="Monitoring History"><div className="table-scroll" role="region" aria-label="Monitoring Historie" tabIndex={0}><table className="data-table"><thead><tr><th>Datum</th><th>Scan</th><th>Health Score</th><th>Findings</th></tr></thead><tbody>{data.recent_scans.map((scan) => <tr key={scan.scan_id}><td>{scan.generated_at}</td><td>{scan.scan_type}</td><td>{scan.data_score}/100</td><td>{scan.issues_count}</td></tr>)}</tbody></table></div></SectionCard>
            <div className="two-column-grid">
              <StatePanel title="Change Signals: Partial Data" tone="warning">Die aktuelle Analytics-Projektion liefert Historie, aber noch keinen eigenen backendseitigen New/Regressed/Resolved-Signalblock. D7 zeigt deshalb keinen clientseitig erfundenen Delta-KPI.</StatePanel>
              <StatePanel title="Validated Outcomes: Evidence gated">Validated Improvement erscheint erst, wenn Baseline und Validation-Evidence gemeinsam geliefert werden. Estimated-Loss-Differenzen werden nicht als realisierte Einsparung bezeichnet.</StatePanel>
            </div>
          </div>
        );
      }}
    </DashboardBoundary>
  );
}

export function ServiceBoundaryPage({ title }: { title: string }) {
  return <div className="page-stack"><PageHeader eyebrow="Service Surface" title={title} description="Diese Service-Seite gehört planmäßig zu D8." /><StatePanel title="D8 Boundary">Die Dashboard Foundation und Navigation stehen. Auth, Settings, Subscription/Billing, Support sowie globale Locked/Error-Surfaces werden im nächsten Service-Page-Sprint produktiv gebunden.</StatePanel></div>;
}
