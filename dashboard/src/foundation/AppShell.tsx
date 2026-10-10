import { PropsWithChildren, useState } from 'react';
import { useTenant, useTenantSwitcher } from './contexts';

const navItems = [
  { route: 'overview', de: 'Übersicht', en: 'Overview' },
  { route: 'findings', de: 'Findings', en: 'Findings' },
  { route: 'actions', de: 'Maßnahmen', en: 'Actions' },
  { route: 'financial', de: 'Finanzieller Impact', en: 'Financial Impact' },
  { route: 'reports', de: 'Executive Report', en: 'Executive Report' },
  { route: 'scans', de: 'Scans', en: 'Scans' },
  { route: 'monitoring', de: 'Monitoring', en: 'Monitoring' },
  { route: 'settings', de: 'Einstellungen', en: 'Settings' },
  { route: 'subscription', de: 'Subscription', en: 'Subscription' },
  { route: 'support', de: 'Support', en: 'Support' },
] as const;

function displayLanguage(preferredLanguage?: string) {
  return (preferredLanguage || '').toLowerCase().startsWith('en') ? 'en' : 'de';
}

function productLabel(value?: string) {
  const normalized = (value || '').replaceAll('_', ' ').trim();
  return normalized || 'Free Entry';
}

export function AppShell({ children, activeRoute }: PropsWithChildren<{ activeRoute: string }>) {
  const [open, setOpen] = useState(false);
  const tenant = useTenant();
  const switcher = useTenantSwitcher();
  const language = displayLanguage(tenant?.preferredLanguage);
  const tenantSummary = switcher.tenants.find((item) => item.tenant_id === tenant?.tenantId);
  const tenantLabel = tenantSummary?.environment_name || tenant?.tenantLabel || (tenant?.tenantId ? `${tenant.tenantId.slice(0, 8)}…` : 'Session pending');

  const onTenantChange = async (tenantId: string) => {
    if (!tenantId || tenantId === tenant?.tenantId) return;
    try {
      await switcher.switchTenant(tenantId);
      window.location.hash = '#overview';
    } catch {
      // The switcher context exposes a sanitized message in the shell.
    }
  };

  return (
    <div className="app-shell" data-nav-open={open ? 'true' : 'false'}>
      <aside className="sidebar" aria-label={language === 'de' ? 'Hauptnavigation' : 'Primary navigation'}>
        <div className="brand">BCSentinel</div>
        <nav>
          {navItems.map((item) => (
            <a
              key={item.route}
              href={`#${item.route}`}
              className="nav-item"
              data-active={activeRoute === item.route ? 'true' : 'false'}
              aria-current={activeRoute === item.route ? 'page' : undefined}
              onClick={() => setOpen(false)}
            >
              {item[language]}
            </a>
          ))}
        </nav>
        <div className="sidebar-plan">
          <span>{language === 'de' ? 'Produkt-Runtime' : 'Product Runtime'}</span>
          <strong>{language === 'de' ? 'Read-only Dashboard' : 'Read-only Dashboard'}</strong>
          <small>
            {language === 'de'
              ? 'Operative Steuerung bleibt in Business Central.'
              : 'Operational control remains in Business Central.'}
          </small>
        </div>
      </aside>
      {open && <button className="nav-backdrop" aria-label={language === 'de' ? 'Navigation schließen' : 'Close navigation'} onClick={() => setOpen(false)} />}
      <div className="main-column">
        <header className="topbar">
          <button className="menu-button" aria-label={language === 'de' ? 'Navigation öffnen' : 'Open navigation'} onClick={() => setOpen(true)}>☰</button>
          <span className="topbar-title">BCSentinel</span>
          <div className="tenant-context" aria-label={language === 'de' ? 'Aktiver Tenant' : 'Active tenant'}>
            <span className="tenant-context-label">{language === 'de' ? 'Tenant' : 'Tenant'}</span>
            {switcher.canSwitch ? (
              <select
                className="tenant-select"
                value={tenant?.tenantId || ''}
                onChange={(event) => void onTenantChange(event.target.value)}
                disabled={switcher.switching || switcher.loading}
                aria-label={language === 'de' ? 'Tenant wechseln' : 'Switch tenant'}
              >
                {switcher.tenants.map((item) => (
                  <option key={item.tenant_id} value={item.tenant_id}>
                    {item.environment_name} · {productLabel(item.current_plan)} · {item.role}
                  </option>
                ))}
              </select>
            ) : (
              <span className="tenant-context-value" title={tenant?.tenantId}>{tenantLabel}</span>
            )}
            {tenantSummary && (
              <span className="tenant-context-meta">
                {productLabel(tenantSummary.current_plan)} · {tenantSummary.role}
              </span>
            )}
            {switcher.switching && <span className="tenant-context-status">{language === 'de' ? 'Wechsel…' : 'Switching…'}</span>}
            {switcher.error && <span className="tenant-context-error" role="status">{switcher.error}</span>}
          </div>
        </header>
        <main className="page-content" key={tenant?.tenantId}>{children}</main>
        <footer className="app-footer">
          <span>BCSentinel</span>
          <span>
            {language === 'de'
              ? 'Runtime-Daten · tenant-isoliert · read-only Weboberfläche'
              : 'Runtime data · tenant isolated · read-only web surface'}
          </span>
        </footer>
      </div>
    </div>
  );
}
