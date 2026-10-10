import { PropsWithChildren, useState } from 'react';

const navItems = ['Overview', 'Findings', 'Actions', 'Financial Impact', 'Reports', 'Scans', 'Monitoring', 'Settings'];

export function AppShell({ children }: PropsWithChildren) {
  const [open, setOpen] = useState(false);
  return (
    <div className="app-shell" data-nav-open={open ? 'true' : 'false'}>
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand">BCSentinel</div>
        <nav>
          {navItems.map((item) => <a key={item} href="#" className="nav-item">{item}</a>)}
        </nav>
      </aside>
      {open && <button className="nav-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}
      <div className="main-column">
        <header className="topbar">
          <button className="menu-button" aria-label="Open navigation" onClick={() => setOpen(true)}>☰</button>
          <span className="topbar-title">BCSentinel</span>
          <span className="topbar-context">Tenant context</span>
        </header>
        <main className="page-content">{children}</main>
        <footer className="app-footer">BCSentinel · Product runtime foundation</footer>
      </div>
    </div>
  );
}
