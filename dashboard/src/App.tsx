import { useEffect, useState } from 'react';
import { AppShell } from './foundation/AppShell';
import { FoundationProviders } from './foundation/contexts';
import {
  ActionsPage,
  FinancialImpactPage,
  FindingsPage,
  MonitoringPage,
  OverviewPage,
  ReportsPage,
  ScansPage,
  ServiceBoundaryPage,
} from './core/CorePages';

function currentRoute() {
  const raw = window.location.hash.replace(/^#/, '') || 'overview';
  return raw.split('?')[0] || 'overview';
}

function RoutedPage({ route }: { route: string }) {
  switch (route) {
    case 'overview': return <OverviewPage />;
    case 'findings': return <FindingsPage />;
    case 'actions': return <ActionsPage />;
    case 'financial': return <FinancialImpactPage />;
    case 'reports': return <ReportsPage />;
    case 'scans': return <ScansPage />;
    case 'monitoring': return <MonitoringPage />;
    case 'settings': return <ServiceBoundaryPage title="Settings" />;
    case 'subscription': return <ServiceBoundaryPage title="Subscription / Billing" />;
    default: return <OverviewPage />;
  }
}

export default function App() {
  const [route, setRoute] = useState(currentRoute);

  useEffect(() => {
    const sync = () => setRoute(currentRoute());
    window.addEventListener('hashchange', sync);
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  return (
    <FoundationProviders>
      <AppShell activeRoute={route}>
        <RoutedPage route={route} />
      </AppShell>
    </FoundationProviders>
  );
}
