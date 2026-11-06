import { PageHeader, StatePanel } from '../components/ui';

export function LockedStatePage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Product State"
        title="Funktion nicht freigeschaltet"
        description="Der aktuelle Tenant ist gültig, aber das angeforderte Produktmerkmal ist durch den serverseitigen Entitlement-Status gesperrt."
      />
      <StatePanel title="Locked" tone="locked">
        <p>Die Oberfläche zeigt keine Premium-Daten als Vorschau und erzeugt keine Ersatzwerte.</p>
        <a className="button button-brand" href="#subscription">Subscription anzeigen</a>
      </StatePanel>
    </div>
  );
}
