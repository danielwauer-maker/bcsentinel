import { AppShell } from './foundation/AppShell';
import { FoundationProviders } from './foundation/contexts';

export default function App() {
  return (
    <FoundationProviders>
      <AppShell>
        <section className="foundation-card" aria-labelledby="foundation-title">
          <p className="eyebrow">Dashboard Foundation</p>
          <h1 id="foundation-title">BCSentinel Web Runtime</h1>
          <p>
            App shell, tenant-aware API client and entitlement boundary are active. Core page implementation follows in D7.
          </p>
        </section>
      </AppShell>
    </FoundationProviders>
  );
}
