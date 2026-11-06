import { useEffect, useMemo, useState } from 'react';
import { ApiError } from '../api/client';
import {
  confirmAssessmentScope,
  getAssessmentScope,
  type AssessmentScopeResponse,
} from '../api/assessmentScope';
import { MetricCard, PageHeader, SectionCard, StatePanel, StatusBadge } from '../components/ui';
import { useTenant } from '../foundation/contexts';
import { useDashboardData } from './hooks';

type ScopeDecision = 'include' | 'exclude' | 'inherit';

function errorText(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Die Tenant-Sitzung ist nicht mehr gültig.';
    if (error.status === 403) return 'Scope-Bestätigung ist nur mit aktivem Full Assessment verfügbar.';
    if (error.status === 404) return 'Der ausgewählte Scan wurde nicht gefunden.';
  }
  return 'Der Assessment Scope konnte nicht geladen werden.';
}

function suggestedDecision(module: NonNullable<AssessmentScopeResponse['modules']>[number]): ScopeDecision {
  if (module.module_code === 'system') return 'include';
  if (module.decision === 'include' || module.decision === 'exclude') return module.decision;
  if (module.detection_status === 'active') return 'include';
  if (module.detection_status === 'not_detected') return 'exclude';
  return 'inherit';
}

export function AssessmentScopePage() {
  const tenant = useTenant();
  const dashboard = useDashboardData();
  const scanId = dashboard.status === 'loaded' ? dashboard.data.selected_scan_id : null;
  const [scope, setScope] = useState<AssessmentScopeResponse | null>(null);
  const [decisions, setDecisions] = useState<Record<string, ScopeDecision>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tenant || !scanId) return;
    let active = true;
    setLoading(true);
    setError(null);
    getAssessmentScope(tenant, scanId)
      .then((value) => {
        if (!active) return;
        setScope(value);
        const next: Record<string, ScopeDecision> = {};
        value.modules?.forEach((module) => { next[module.module_code] = suggestedDecision(module); });
        setDecisions(next);
      })
      .catch((reason) => active && setError(errorText(reason)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [tenant, scanId]);

  const previewIncluded = useMemo(() => {
    if (!scope?.modules) return scope?.included_modules ?? 0;
    return scope.modules.filter((module) => {
      const decision = decisions[module.module_code] ?? 'inherit';
      if (module.module_code === 'system') return true;
      if (decision === 'include') return true;
      if (decision === 'exclude') return false;
      return module.included_in_score;
    }).length;
  }, [scope, decisions]);

  const save = async () => {
    if (!tenant || !scanId || !scope?.modules) return;
    setSaving(true);
    setError(null);
    try {
      const confirmed = await confirmAssessmentScope(tenant, scanId, decisions);
      setScope(confirmed);
      const next: Record<string, ScopeDecision> = {};
      confirmed.modules?.forEach((module) => { next[module.module_code] = suggestedDecision(module); });
      setDecisions(next);
    } catch (reason) {
      setError(errorText(reason));
    } finally {
      setSaving(false);
    }
  };

  if (dashboard.status === 'session_required') {
    return <StatePanel title="Tenant-Sitzung erforderlich">Für den Assessment Scope ist eine aktive Tenant-Sitzung erforderlich.</StatePanel>;
  }
  if (dashboard.status === 'loading' || loading) {
    return <StatePanel title="Assessment Scope wird geladen">BCSentinel liest die automatische Standard-Modul-Erkennung für den aktuellen Scan.</StatePanel>;
  }
  if (dashboard.status === 'error') {
    return <StatePanel title="Scan-Kontext nicht verfügbar" tone="error">{dashboard.error}</StatePanel>;
  }
  if (!scanId) {
    return <StatePanel title="Noch kein Scan verfügbar">Der Scope kann nach dem ersten vollständigen Data Health Scan bestätigt werden.</StatePanel>;
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Full Assessment"
        title="Assessment Scope"
        description="BCSentinel bewertet unterstützte Microsoft Dynamics 365 Business Central Standardbereiche. Drittanbieter-Extensions und Custom Logic sind nicht Teil des Scores, solange sie nicht ausdrücklich unterstützt werden."
      />

      {error && <StatePanel title="Assessment Scope nicht verfügbar" tone="error">{error}</StatePanel>}

      {scope && (
        <>
          <div className="metric-grid metric-grid-4">
            <MetricCard label={scope.state === 'confirmed' ? 'Confirmed Baseline' : 'Preliminary Score'} value={`${scope.score}/100`} />
            <MetricCard label="Unterstützte Module" value={scope.supported_modules} />
            <MetricCard label="Im Scope" value={previewIncluded} />
            <MetricCard label="Unklar erkannt" value={scope.unknown_modules} helper="Unknown wird nicht automatisch negativ gewertet." />
          </div>

          {!scope.modules ? (
            <StatePanel title="Scope-Bestätigung ist im Full Assessment verfügbar" tone="locked">
              Free und Quick Assessment verwenden den automatisch erkannten Standard-Scope. Eine Modul- oder Checkauswahl ist dort bewusst nicht möglich.
            </StatePanel>
          ) : (
            <>
              <SectionCard title="Standardmodule bestätigen" subtitle="BCSentinel schlägt auf Basis des vorhandenen Scans einen Scope vor. Änderungen bewerten denselben Scan neu und starten keinen weiteren Scan.">
                <div className="table-scroll" role="region" aria-label="Assessment Scope" tabIndex={0}>
                  <table className="data-table">
                    <thead><tr><th>Standardbereich</th><th>Erkennung</th><th>Modulscore</th><th>Bewertung</th><th>Evidenz</th></tr></thead>
                    <tbody>
                      {scope.modules.map((module) => (
                        <tr key={module.module_code}>
                          <td><strong>{module.display_name}</strong><span className="table-subline">{module.module_code}</span></td>
                          <td><StatusBadge value={module.detection_status} /></td>
                          <td>{module.module_score}/100</td>
                          <td>
                            <select
                              value={decisions[module.module_code] ?? suggestedDecision(module)}
                              disabled={module.module_code === 'system' || saving}
                              onChange={(event) => setDecisions((current) => ({ ...current, [module.module_code]: event.target.value as ScopeDecision }))}
                              aria-label={`${module.display_name} Scope-Entscheidung`}
                            >
                              <option value="include">Include</option>
                              <option value="exclude">Exclude</option>
                              <option value="inherit">Automatische Erkennung übernehmen</option>
                            </select>
                          </td>
                          <td>{module.detection_reason || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </SectionCard>

              <StatePanel title="Score-Änderung ist keine Verbesserung" tone="warning">
                Wenn sich der Score durch die Scope-Bestätigung ändert, ist das ausschließlich eine fachliche Scope-Anpassung. Erst die spätere Validation nach umgesetzten Maßnahmen misst eine echte Verbesserung.
              </StatePanel>

              <SectionCard title="Confirmed Baseline erstellen" subtitle={`Scan ${scanId} bleibt unverändert; es wird nur eine neue versionierte Scope-Bewertung gespeichert.`}>
                <button className="button button-brand" type="button" onClick={() => void save()} disabled={saving}>
                  {saving ? 'Scope wird bestätigt…' : scope.state === 'confirmed' ? 'Scope erneut versioniert bestätigen' : 'Assessment Scope bestätigen'}
                </button>
                {scope.state === 'confirmed' && <p className="muted">Bestätigte Scope-Version: {scope.version}. Diese Baseline ist die fachliche Grundlage für die spätere Validation.</p>}
              </SectionCard>
            </>
          )}

          <SectionCard title="Assessment Coverage" subtitle="Transparente Produktgrenze">
            <dl className="detail-grid">
              <div><dt>BC Standardbereiche</dt><dd><StatusBadge value="assessed" /></dd></div>
              <div><dt>Custom Extensions gescort</dt><dd><StatusBadge value={scope.custom_extensions_scored ? 'yes' : 'no'} /></dd></div>
              <div><dt>Third-party / Custom Logic</dt><dd>Nicht bewertet, sofern nicht ausdrücklich unterstützt</dd></div>
              <div><dt>Technischer Scan</dt><dd>Unverändert · kein Re-Scan durch Scope-Bestätigung</dd></div>
            </dl>
          </SectionCard>
        </>
      )}
    </div>
  );
}
