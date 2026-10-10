import { PropsWithChildren, useState } from 'react';
import { useTenant } from './contexts';

const navItems = [
  { route: 'overview', label: 'Overview' },
  { route: 'findings', label: 'Findings' },
  { route: 'actions', label: 'Actions' },
  { route: 'financial', label: 'Financial Impact' },
  { route: 'reports', label: 'Reports' },
  { route: 'scans', label: 'Scans' },
  { route: 'monitoring', label: 'Monitoring' },
  { route: 'settings', label: 'Settings' },
  { route: 'subscription', label: 'Subscription' },
  { route: 'support', label: 'Support' },
];

export function AppShell({ children, activeRoute }: PropsWithChildren<{ activeRoute: string }>) {
  const [open, setOpen] = useState(false);
  const tenant = useTenant();
  const tenantLabel = tenant?.tenantId ? `${tenant.tenantId.slice(0, 8)}…` : 'Session pending';

  return (
    <div className="app-shell" data-nav-open={open ? 'true' : 'false'}>
      <aside className="sidebar" aria-label="Primary navigation">
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
              {item.label}
            </a>
          ))}
        </nav>
        <div className="sidebar-plan">
          <span>Product Runtime</span>
          <strong>Read-only Dashboard</strong>
          <small>Operative Steuerung bleibt in Business Central.</small>
        </div>
      </aside>
      {open && <button className="nav-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}
      <div className="main-column">
        <header className="topbar">
          <button className="menu-button" aria-label="Open navigation" onClick={() => setOpen(true)}>☰</button>
          <span className="topbar-title">BCSentinel</span>
          <span className="topbar-context">Tenant {tenantLabel}</span>
        </header>
        <main className="page-content">{children}</main>
        <footer className="app-footer">
          <span>BCSentinel</span>
          <span>Runtime data · tenant isolated · read-only web surface</span>
        </footer>
      </div>
    </div>
  );
}
