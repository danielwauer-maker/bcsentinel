import { useEffect, useState } from 'react';
import {
  ActionsPage,
  FinancialImpactPage,
  FindingsPage,
  MonitoringPage,
  OverviewPage,
  ReportsPage,
  ScansPage,
} from './core/CorePages';
import { AppShell } from './foundation/AppShell';
import { FoundationProviders, useTenant } from './foundation/contexts';
import { LockedStatePage } from './service/LockedStatePage';
import {
  AuthRuntimePage,
  ProductStatePage,
  SettingsPage,
  SubscriptionPage,
  SupportPage,
} from './service/ServicePages';

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
    case 'settings': return <SettingsPage />;
    case 'subscription': return <SubscriptionPage />;
    case 'support': return <SupportPage />;
    case 'locked': return <LockedStatePage />;
    case '403': return <ProductStatePage code="403" />;
    case '500': return <ProductStatePage code="500" />;
    default: return <ProductStatePage code="404" />;
  }
}

function RuntimeApp() {
  const [route, setRoute] = useState(currentRoute);
  const tenant = useTenant();

  useEffect(() => {
    const sync = () => setRoute(currentRoute());
    window.addEventListener('hashchange', sync);
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  if (!tenant) return <AuthRuntimePage />;

  return (
    <AppShell activeRoute={route}>
      <RoutedPage route={route} />
    </AppShell>
  );
}

export default function App() {
  return (
    <FoundationProviders>
      <RuntimeApp />
    </FoundationProviders>
  );
}
