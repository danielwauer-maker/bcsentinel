import { useEffect, useState } from 'react';
import { ApiError } from '../api/client';
import {
  getNotificationSettings,
  getSubscriptionStatus,
  openBillingPortal,
  type NotificationSettingsResponse,
  type SubscriptionStatus,
} from '../api/servicePages';
import { PageHeader, SectionCard, StatePanel, StatusBadge } from '../components/ui';
import { useAuth, useTenant } from '../foundation/contexts';

function formatDate(value?: string | null) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium' }).format(date);
}

function formatMoney(value: number, currency: string) {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: currency || 'EUR' }).format(value || 0);
}

function requestMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Die Laufzeitsitzung ist nicht mehr gültig. Bitte erneut anmelden.';
    if (error.status === 403) return 'Diese Information ist für den aktuellen Tenant nicht freigegeben.';
    if (error.status === 404) return 'Für diesen Tenant liegen noch keine entsprechenden Daten vor.';
  }
  return 'Die Daten konnten nicht geladen werden. Es werden keine Ersatzwerte erzeugt.';
}

export function AuthRuntimePage() {
  const auth = useAuth();
  return (
    <div className="standalone-state">
      <div className="standalone-state-card">
        <p className="eyebrow">BCSentinel Runtime</p>
        <h1>{auth.authenticated ? 'Tenant-Zuordnung erforderlich' : 'Anmeldung erforderlich'}</h1>
        <p>
          {auth.authenticated
            ? 'Die Identität ist bekannt, aber es wurde noch keine gültige Tenant-Sitzung an das Dashboard übergeben.'
            : 'Das Dashboard benötigt eine etablierte BCSentinel-Laufzeitsitzung. Authentifizierung allein erteilt keinen Produktzugriff.'}
        </p>
        <StatePanel title="Sicherheitsgrenze" tone="neutral">
          Authentication → Tenant Membership → Tenant Status → Entitlements → Product Access.
        </StatePanel>
      </div>
    </div>
  );
}

export function SettingsPage() {
  const tenant = useTenant();
  const [data, setData] = useState<NotificationSettingsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tenant) return;
    let active = true;
    setLoading(true);
    getNotificationSettings(tenant)
      .then((value) => active && setData(value))
      .catch((reason) => active && setError(requestMessage(reason)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [tenant]);

  return (
    <div className="page-stack">
      <PageHeader eyebrow="Service" title="Settings" description="Tenant- und Benachrichtigungseinstellungen werden hier ausschließlich angezeigt. Operative Änderungen bleiben in Business Central." />
      <SectionCard title="Runtime-Kontext" subtitle="Die Weboberfläche ist keine zweite Administrationsoberfläche.">
        <dl className="detail-grid">
          <div><dt>Tenant</dt><dd>{tenant?.tenantId ?? '—'}</dd></div>
          <div><dt>Modus</dt><dd><StatusBadge value="read_only" /></dd></div>
          <div><dt>Sprache</dt><dd>{tenant?.preferredLanguage ?? 'Runtime default'}</dd></div>
        </dl>
      </SectionCard>

      {loading && <StatePanel title="Settings werden geladen">Die serverseitige Read-Model-Projektion wird abgerufen.</StatePanel>}
      {error && <StatePanel title="Settings nicht verfügbar" tone="error">{error}</StatePanel>}
      {!loading && !error && data?.items.length === 0 && (
        <StatePanel title="Noch keine Notification-Konfiguration">Es liegt noch keine aus Business Central synchronisierte Konfiguration vor.</StatePanel>
      )}
      {data?.items.map((item) => (
        <SectionCard key={item.company_id} title={`Company ${item.company_id}`} subtitle="Benachrichtigungen werden in Business Central verwaltet.">
          <dl className="detail-grid">
            <div><dt>Status</dt><dd><StatusBadge value={item.notifications_enabled ? 'enabled' : 'disabled'} /></dd></div>
            <div><dt>Aktive Events</dt><dd>{item.enabled_event_types.length} / {item.configured_event_types.length}</dd></div>
            <div><dt>Empfänger</dt><dd>{item.recipient_summary.enabled} / {item.recipient_summary.configured}</dd></div>
            <div><dt>Kanäle</dt><dd>{item.channel_summary.join(', ') || '—'}</dd></div>
            <div><dt>Sprachen</dt><dd>{item.template_language_summary.join(', ') || '—'}</dd></div>
            <div><dt>BC aktualisiert</dt><dd>{formatDate(item.bc_updated_at_utc)}</dd></div>
          </dl>
          <div className="inline-note">Änderungen an Regeln, Empfängern, Vorlagen und Events erfolgen ausschließlich in Business Central.</div>
        </SectionCard>
      ))}
    </div>
  );
}

export function SubscriptionPage() {
  const tenant = useTenant();
  const [status, setStatus] = useState<SubscriptionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [portalBusy, setPortalBusy] = useState(false);
  const [portalError, setPortalError] = useState<string | null>(null);

  useEffect(() => {
    if (!tenant) return;
    let active = true;
    getSubscriptionStatus(tenant)
      .then((value) => active && setStatus(value))
      .catch((reason) => active && setError(requestMessage(reason)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [tenant]);

  const launchPortal = async () => {
    if (!tenant) return;
    setPortalBusy(true);
    setPortalError(null);
    try {
      const result = await openBillingPortal(tenant);
      if (!result.portal_url) throw new Error('missing portal url');
      window.location.assign(result.portal_url);
    } catch (reason) {
      setPortalError(requestMessage(reason));
      setPortalBusy(false);
    }
  };

  return (
    <div className="page-stack">
      <PageHeader eyebrow="Commercial" title="Subscription / Billing" description="Plan-, Lizenz- und Abrechnungsstatus stammen aus dem serverseitigen Billing-Modell; Preise werden hier nicht dupliziert." />
      {loading && <StatePanel title="Subscription wird geladen">Der aktuelle serverseitige Status wird abgerufen.</StatePanel>}
      {error && <StatePanel title="Subscription nicht verfügbar" tone="error">{error}</StatePanel>}
      {status && (
        <>
          <SectionCard title="Aktueller Produktstatus">
            <dl className="detail-grid">
              <div><dt>Plan</dt><dd>{status.current_plan || '—'}</dd></div>
              <div><dt>Lizenz</dt><dd><StatusBadge value={status.license_status || 'unknown'} /></dd></div>
              <div><dt>Subscription</dt><dd>{status.subscription_status ? <StatusBadge value={status.subscription_status} /> : '—'}</dd></div>
              <div><dt>Provider</dt><dd>{status.provider || '—'}</dd></div>
              <div><dt>Monatlicher Gegenwert</dt><dd>{formatMoney(status.amount_monthly, status.currency)}</dd></div>
              <div><dt>Aktuelle Periode bis</dt><dd>{formatDate(status.current_period_end_utc)}</dd></div>
            </dl>
          </SectionCard>
          <SectionCard title="Billing verwalten" subtitle="Änderungen an der Subscription werden über das sichere Provider-Portal ausgeführt.">
            <button className="button button-brand" type="button" onClick={launchPortal} disabled={portalBusy || !status.provider_subscription_id}>
              {portalBusy ? 'Portal wird geöffnet…' : 'Billing-Portal öffnen'}
            </button>
            {!status.provider_subscription_id && <p className="muted">Für diesen Tenant ist aktuell keine Provider-Subscription hinterlegt.</p>}
            {portalError && <StatePanel title="Billing-Portal nicht verfügbar" tone="error">{portalError}</StatePanel>}
          </SectionCard>
        </>
      )}
    </div>
  );
}

export function SupportPage() {
  return (
    <div className="page-stack">
      <PageHeader eyebrow="Service" title="Support & Docs" description="Schnelle Orientierung für Nutzung, Produktgrenzen und Support-Fälle." />
      <div className="service-grid">
        <SectionCard title="Business Central" subtitle="Operative Steuerung">
          <p>Scans, Monitoring-Setup, Notification-Konfiguration und Remediation bleiben in Business Central.</p>
          <a className="button button-secondary" href="#settings">Runtime-Kontext anzeigen</a>
        </SectionCard>
        <SectionCard title="Dashboard" subtitle="Management- und Analyseoberfläche">
          <p>Findings, Impact, Actions, Scan-Historie, Monitoring und Reports werden als Read-Model angezeigt.</p>
          <a className="button button-secondary" href="#overview">Zur Übersicht</a>
        </SectionCard>
        <SectionCard title="Support-Fall vorbereiten" subtitle="Ohne sensible Daten zu kopieren">
          <p>Tenant-ID, betroffene Seite, Zeitpunkt und sichtbare Fehlermeldung reichen als erste Diagnoseinformationen aus.</p>
        </SectionCard>
      </div>
    </div>
  );
}

export function ProductStatePage({ code }: { code: '403' | '404' | '500' }) {
  const copy = {
    '403': ['Kein Zugriff', 'Der aktuelle Tenant oder die aktuellen Entitlements erlauben diese Ansicht nicht.'],
    '404': ['Seite nicht gefunden', 'Die angeforderte Dashboard-Seite existiert nicht.'],
    '500': ['Service vorübergehend nicht verfügbar', 'Die Oberfläche zeigt bewusst keine erfundenen Ersatzdaten.'],
  }[code];
  return (
    <div className="page-stack">
      <PageHeader eyebrow={`Status ${code}`} title={copy[0]} description={copy[1]} />
      <StatePanel title="Nächster Schritt" tone={code === '500' ? 'error' : code === '403' ? 'locked' : 'neutral'}>
        <a className="button button-secondary" href="#overview">Zur Übersicht</a>
      </StatePanel>
    </div>
  );
}
