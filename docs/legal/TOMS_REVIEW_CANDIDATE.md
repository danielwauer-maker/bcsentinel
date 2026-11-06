# BCSentinel Technische und organisatorische Maßnahmen (TOMs) – Review Candidate

**Version:** 0.9-review  
**Stand:** 2026-10-10  
**Status:** Interner Review Candidate; technische Kontrollen müssen vor PROD gegen die tatsächliche Infrastruktur evidenzbasiert bestätigt werden.

## Zugriff und Mandantentrennung

- Tenantgebundene Authentifizierung und Autorisierung; ein authentifizierter Benutzer erhält nur Zugriff auf explizite Tenant-Memberships.
- Rollen werden je Tenant ausgewertet; ein Benutzer kann in unterschiedlichen Tenants unterschiedliche Rollen besitzen.
- Tenant-Wechsel erzeugt eine neue tenantgebundene Session statt eines clientseitigen Scope-Wechsels.
- Lebenszyklusprüfung für aktive, suspendierte und deaktivierte Tenants.
- Web-Dashboard ist primär read-only; operative Business-Central-Schreibvorgänge bleiben in Business Central.
- Supportzugriff im Controlled Pilot zunächst Diagnostics-only, tenantautorisiert, zeitlich begrenzt und auditierbar.

## Authentifizierung und Session-Sicherheit

- Kurzlebige Dashboard-Sessions; Rotation von Tenant-Credentials invalidiert abhängige Sessions.
- Account- und Tenant-Session sind getrennte Sicherheitskontexte.
- Keine Ablage von Dashboard-Authentifizierungsdaten in `localStorage` als Produktvertrag.
- Zugangsdaten und Secrets dürfen nicht in Git oder Release-Manifeste aufgenommen werden.

## Datenintegrität und Nachvollziehbarkeit

- Audit Trails für relevante Konfigurations-, Membership-, Commercial- und Remediation-Änderungen.
- Historische Scan-Ausnahmen werden pro Scan unveränderlich eingefroren; spätere Änderungen an aktiven Ausnahmen verändern historische Reports nicht rückwirkend.
- Stripe-Webhooks und zentrale Provider-Ereignisse werden idempotent verarbeitet.
- Datenbankmigrationen werden als versionierte Alembic-Kette geführt und in CI auf einen eindeutigen Head geprüft.

## Transport- und Anwendungssicherheit

- HTTPS/TLS ist für DEV/PROD Pflicht.
- Security Header einschließlich CSP, X-Content-Type-Options, Referrer-Policy und Frame-Protection werden serverseitig gesetzt.
- CORS ist auf freigegebene BCSentinel-Ursprünge begrenzt.
- Sensible Fehlermeldungen werden nach außen bereinigt; Request-IDs ermöglichen interne Korrelation.
- Admin-POST-Flows verwenden CSRF-Schutz, sofern cookiebasierte Admin-Oberflächen betroffen sind.

## Verfügbarkeit und Wiederherstellung

- Release-Pfad: DEV → Release Candidate → PROD.
- Versionierte Rollback-Referenz auf die vorherige Applikationsversion ist verpflichtend.
- Datenbank-Backups und Restore-Drills sind Teil des Go-Live-Gates; ein Schema-Downgrade wird nicht pauschal als sicher angenommen.
- Readiness-/Health-Endpunkte prüfen mindestens Applikation und Datenbank.
- Reale Off-Host-Backup-, Restore-, RTO-/RPO- und Alarmierungsnachweise bleiben vor PROD als Betriebs-Gate erforderlich.

## Datenminimierung und Aufbewahrung

- Feature- und Produkt-Telemetrie soll keine unnötigen Kundeninhalte erfassen.
- Export-, Lösch- und Retention-Anforderungen werden als nachvollziehbarer Lifecycle-Prozess behandelt.
- Logs, Audit-Evidence, Reports, operative Daten und Backups können unterschiedlichen Fristen unterliegen; finale Fristen sind vor PROD verbindlich zu harmonisieren.

## Entwicklungs- und Release-Prozess

- Pull Requests mit automatisierten Regressionen für Backend, Dashboard und Produktverträge.
- Sicherheits-, Entitlement-, Pricing-, Notification-, Report- und UI-Verträge werden in CI separat geprüft.
- Synthetischer Demo-Tenant ist für Screenshots, Produktdemo und visuelle Tests vorgesehen; echte Kundendaten dürfen dafür nicht verwendet werden.
- GitHub/Core ist technische Source of Truth; wichtige Readiness-Kennzahlen sollen nicht mehrfach manuell gepflegt werden.

## Vor PROD noch evidenzpflichtig

- tatsächliche Hosting-/Netzwerkarchitektur und Standort,
- produktive Verschlüsselung at rest und Schlüsselverwaltung,
- produktive Backup-Aufbewahrung, Restore-Test und RTO/RPO,
- produktive Monitoring-/Alerting-Kanäle,
- produktive SMTP-/DNS-Konfiguration,
- Stripe-/Billing-Provider-Konfiguration,
- Betriebs- und Incident-Response-Kontakte,
- finale Subprozessoren und etwaige Drittlandtransfers.
