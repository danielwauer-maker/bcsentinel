# BCSentinel Role and Permission Matrix

Stand: 20.07.2026  
Status: **statisch definiert; BC-Sandbox-Negativtests BLOCKED**

BC-Permission und SaaS-Capability sind kumulativ. `Ja*` bedeutet: nur bei passender SaaS-Capability. Keine Rolle erhält einen SaaS-Bypass.

| Funktion | Admin | Viewer | Scan User | Scheduler | Ohne Rechte |
|---|---:|---:|---:|---:|---:|
| Setup öffnen | Ja | Nein | Nein | Nein | Nein |
| Registrierung | Ja | Nein | Nein | Nein | Nein |
| API URL ändern | Ja | Nein | Nein | Nein | Nein |
| Lizenz manuell aktualisieren | Ja | Nein | Nein | Nein | Nein |
| Scan starten | Ja* | Nein | Ja* | Monitoring* | Nein |
| Scanstatus lesen | Ja | Ja | Ja | technisch | Nein |
| Finding Summary sehen | Ja* | Ja* | Ja* | Nein | Nein |
| Finding Details öffnen | Ja* | Ja* | Ja* | Nein | Nein |
| Exceptions lesen | Ja | Ja | Ja | technisch | Nein |
| Exceptions anlegen/aktivieren/deaktivieren | Ja | Nein | Ja | Nein | Nein |
| Scheduler konfigurieren | Ja | Nein | Nein | Nein | Nein |
| Scheduler ausführen | Ja* | Nein | Nein | Ja* | Nein |
| Dashboard öffnen | Ja* | Ja* | Nein | Nein | Nein |
| Report öffnen | Ja* | Ja* | Nein | Nein | Nein |
| geschützte lokale Tabellen direkt lesen | Adminbetrieb | Nein | Scan-Schreibpfad | technischer Schreibpfad | Nein |
| Reset ausführen | Ja | Nein | Nein | Nein | Nein |

## Permission Sets

- `BCSENTINEL VIEWER`: kontrollierte Pages; kein direktes Lesen der drei geschützten Finding-Tabellen.
- `BCSENTINEL SCAN`: Scanerzeugung und operative DH-Ausnahmen (RIM ohne Delete); keine Setupverwaltung.
- `BCSENTINEL SETUP`: Setup, Registrierung und Planung; kein allgemeiner Findings-Adminzugriff.
- `BCSENTINEL ADMIN`: vollständige Extensionverwaltung; SaaS-Guards bleiben aktiv.
- `BCSENTINEL SCHEDULER`: minimaler nichtinteraktiver Extensionpfad für geplante Scans.

Die Schedulerrolle enthält absichtlich keine pauschalen Rechte auf Customer, Vendor, Item, Ledger, Sales oder Purchase. Ein Serviceuser benötigt zusätzlich eine fachlich freigegebene Business-Central-Standardrolle mit Read-Rechten auf die tatsächlich aktivierten Scanmodule. Diese Kombination ist ohne `SUPER` in der Sandbox zu testen.

## Verpflichtende Negativtests

Alle sind derzeit `BLOCKED`: direkte Page-ID ohne Permission; Viewer-Direktzugriff auf TableData; BC-Permission ohne SaaS-Zugriff; SaaS-Zugriff ohne BC-Permission; Scheduler ohne Basisdatenrolle; Scheduler ohne Subscription; User versucht Setup/API-URL/Reset; Companywechsel; abgelaufener Access-Snapshot.
