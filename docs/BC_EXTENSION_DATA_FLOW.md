# BCSentinel Extension – Data Flow and Protection

Stand: 16.07.2026  
Audit: GL-EXT-AUDIT-01

## Systemgrenzen

Die Extension liest Business-Central-Daten, berechnet den Großteil der Prüfungen lokal und überträgt für Quick Scans Aggregatwerte sowie für Deep Scans aggregierte Profile, Scores und Findings an `https://api.bcsentinel.com`. Tenant-ID und API-Token authentisieren jeden geschützten Backend-Aufruf. Das Backend stellt Lizenz-, Dashboard- und Reportdaten bereit. Ausnahmen bleiben lokal in Business Central.

## Flow-Katalog

| Flow | Quelle in BC | ausgehende Daten | Backendziel / Speicherung | Rückgabe nach BC | Schutz | Retention / Löschung | Auditrisiko |
|---|---|---|---|---|---|---|---|
| Registrierung | Setup, Kontaktdaten, Sprache | `environment_name=BC Cloud`, `app_version=0.4.0`, E-Mail, Einladungscode | `/tenant/register`; Tenant, gehashter API-Token, DashboardUser/Invite | zufällige Tenant-ID, einmaliger API-Token, Invite-Status | TLS nur durch Default-URL; AL erlaubt HTTP | kein AL-Recovery; Reset löscht alten Backend-Tenant nicht | P0: nicht idempotent, keine stabile BC-Identität, HTTP möglich |
| API-Authentisierung | Isolated Storage + Setup Tenant-ID | Header `X-Tenant-Id`, `X-Api-Token`, teilweise Sprache | Auth-Middleware; Tokenhashvergleich | HTTP-Status/JSON | Token in AL Isolated Storage Company Scope; Backend PBKDF-Hash | Rotation/Revocation im Kundenflow fehlt | P1 |
| Portal-Einladung | Kontakt-E-Mail | E-Mail/Invitekontext | DashboardUser, gehashter Invite, 7-Tage-Ablauf, SMTP | Status oder SMTP-Fehler | Invite gehasht | Resend nur administrativ | P1 |
| License Snapshot | Tenant-ID/Token | keine Fachdaten | Lizenz-, Kauf-, Credit- und Monitoringtabellen | Plan, Status, Features, Credits, Access-until, Can-Flags | tenantgebundener API-Aufruf | AL cached Werte ohne sichere Ablaufprüfung | P0 lokal stale |
| Quick Scan | Customer/Vendor/Item und Ledger-/Belegtabellen | Counts: fehlende Felder, blocked counts und Record Counts | Scan-/Analytics-Historie | Status/Ergebnis | tenantgebunden; keine Einzelrecords | explizites Delete/Reconcile; keine automatische Policy belegt | P1 Retention |
| Deep-Scan-Start | Setup und Run-Header | Run-ID, Modus, Modulzahl, Company-Name, Environment | `/scan/start`; Scan und Credit | Startstatus, Creditverbrauch | tenantgebunden | Scan-ID ist backendseitig idempotent | P0 Parallelität/AL-Retry |
| Scan-Fortschritt | lokaler Run | Status, Prozent, Modul/Schritt, Events, Fehler/Warnungen | Scanstatus/Events | Bestätigung | tenantgebunden | keine technische Retention belegt | P1 Fehler-/PII-Prüfung |
| Deep-Scan-Sync | lokale Prüfergebnisse | Score, Checks/Issues, Aggregate, Modul-Scores, Issue Code/Kategorie/Titel/Severity/Betroffene/Premium/Empfehlung | Scan-/Findingtabellen | Bestätigung | tenantgebunden | Delete/Reconcile explizit | keine Rohdatensätze, aber Findings können Geschäftsrisiken offenbaren |
| Dashboard-Token | Company, Environment, Tenant, Sprache, Modus, BC-Drilldown-URL | Queryparameter plus Authheader | `/analytics/get-token` | kurzlebiges JWT | Tenant Query muss Header entsprechen; JWT scope-/tenantgebunden | 303 entfernt Token in Cookie-Flow | P2: Token initial in URL/Logs |
| Dashboard-Inhalt | Backend-Scan-/Lizenzdaten | Embed-Token/Cookie | `/analytics/embed/data` und Sections | Scores, Findings, Access Locks | Secure/HttpOnly Cookie in Produktion; serverseitige Entitlements | Backendretention nicht automatisch belegt | Backendschutz gut; AL-lokaler Schutz defekt |
| Executive Report | abgeschlossener Run | Run-ID und Format | `/reports/executive/{scan}/share-link` | 15-Minuten-Share-URL | JWT an Tenant, Scan, Typ und Ablauf gebunden | Link verfällt; Reportdaten folgen Scanretention | P2: Token in URL |
| Ausnahmen | Customer/Vendor/Item/SystemId, Regel, Grund | keine Übertragung | lokale Exception-Tabelle | lokale Skip-Entscheidung | BC-Permissions | kein Cleanup bei gelöschtem Quelldatensatz belegt | P1: Grund/Audit unvollständig |
| Reset/Reconcile | lokaler Tenant/History | Run-ID-Liste oder leere Liste | Backend löscht/reconciliert Scans | Zähler/Status | Confirm default false | lokaler Token/History gelöscht, alter Tenant/Entitlements bleiben | P0 Identitäts-/Kaufverlust |

## Lokal gespeicherte sensible Daten

| Speicherort | Daten | Schutzbewertung |
|---|---|---|
| `DH Setup` | Tenant-ID, API-URL, Einladungscode, Lizenz-/Access-Cache, Scheduler-Konfiguration | normale BC-Tabelle; Einladungscode sollte nach Nutzung entfernt oder geschützt werden |
| Isolated Storage | API-Token unter festem Key, Company Scope | angemessene Basisspeicherung; Rotation und Recovery fehlen |
| Scan Header/Run/Issue/Recommendation | Scores, Findings, Empfehlungen, finanzielle Auswirkungen | Permission Sets geben Viewer Leserechte; lokale Ablaufprüfung ist unzureichend |
| Exception-Tabelle | SystemId/Recordbezug, Regel und Grund | Auditfelder/Grundpflicht unzureichend |

## Tenant-Isolation

Backendseitig ist die Isolation überwiegend konsequent: Authheader werden geprüft, Payload-/Query-Tenant muss übereinstimmen, Dashboard- und Reporttokens sind an Tenant und Scope gebunden. Kritisch ist nicht eine nachgewiesene Cross-Tenant-Backendabfrage, sondern die Registrierung: Das Backend erzeugt bei jeder Registrierung einen neuen zufälligen Tenant und bindet ihn nicht an Azure-/BC-Tenant, Environment und Company. Dadurch gibt es keine belastbare Wiederanbindung an bestehende Käufe.

## Datenminimierung

Positiv ist, dass Quick Scans nur Aggregate übertragen und Deep Scans keine vollständigen Customer-, Vendor-, Item- oder Ledgerdatensätze senden. Findings enthalten dennoch Titel, Empfehlungen, betroffene Anzahlen und finanzielle Wirkung und sind damit schützenswerte Geschäftsmetadaten. Vor Go-Live sind Datenklassifizierung, Datenschutzerklärung und technisch erzwungene Retention mit den tatsächlichen Payloads abzugleichen.

## Erforderliche Kontrollen

- HTTPS-only mit Allowlist für Produktionsendpunkte.
- stabile, serverseitig verifizierte Tenant-/Environment-/Company-Bindung.

## Datenfluss-Delta GL-EXT-P0A (16. Juli 2026)

Die ursprüngliche Tabelle oben dokumentiert den Audit-Ausgangszustand. Seit P0A gelten für die betroffenen Flows folgende Korrekturen:

| Flow | Neuer Datenvertrag | Serververarbeitung | Schutz/Idempotenz | Aktueller Status |
|---|---|---|---|---|
| Registrierung | Entra Tenant ID, Environment Name/Type, Company SystemId/Name, echte App-Version, Kontakt/Sprache, optional bestehende Tenant-ID | Normalisierung, SHA-256 Identity-Key, Unique Constraint, transaktionaler Upsert | stabiler Tenant/Token; Legacy-Bindung nur mit gültigen Authheadern | P0-02 geschlossen |
| Transport | absolute API-Basis-URL ohne Credentials/Query/Fragment | Production-Middleware prüft HTTPS/Forwarded Proto; Settings durchlaufen dieselbe Policy | HTTP nur non-production auf exakt localhost/127.0.0.1/::1 | P0-01 geschlossen |
| Portal-Einladung | Kontakt-E-Mail am bestehenden Tenant | genau ein DashboardUser; Erstinvite nur bei Neuanlage; expliziter authentisierter Resend | Mailfehler rollt Registrierung nicht zurück; Retry sendet nicht erneut | Registrierungspfad vollständig |
| Dashboard-Token | Tenant-Auth plus Entra-/Environment-/Company-Kontext | exact match gegen gebundene Backend-Identität vor Tokenausgabe | 409 bei fehlendem Kontext, 403 bei Mismatch; Query-Tenant allein genügt nie | Kontextbindung vollständig |
| Reset/Reconcile | Tenant-ID und API-Token bleiben lokal erhalten | idempotente Re-Registrierung findet denselben Backend-Tenant | Reset löscht nur Caches; Confirm Default Nein; Käufe/History bleiben | P0-02 geschlossen |

Der Backend-Token liegt weiterhin nur gehasht vor; der AL-Token bleibt wie zuvor im Company-scope Isolated Storage. Legacy-Datensätze erhalten nullable Identity-Felder und werden nicht automatisch zugeordnet.
- Tokenrotation, Revocation, Recovery und sichere Löschung des verwendeten Invite Codes.
- atomare Credit-Transaktion mit Unique-Constraint auf verbrauchte Scan-ID/Credit-Zuordnung.
- frische Access-Prüfung vor jeder lokalen Anzeige oder Aktion mit Premiumdaten.
- dokumentierte und technisch erzwungene Retention für Scans, Events, Findings und Einladungen.
- Redaction für Token in URLs/Logs sowie durchgängige Request-ID im AL-Fehlerdialog.
- keine Roh-Exception-/SMTP-Fehler an Endnutzer; strukturierte Fehlercodes und Supportpfad.

## Datenfluss-Delta GL-EXT-P0B (16. Juli 2026)

| Flow | Neuer Vertrag | Atomare Speicherung | Retry/Schutz |
|---|---|---|---|
| manueller/Scheduler-Start | Tenant + stabile Client Request GUID + Run-ID + Modus + Kontext | Request, passender Credit, Scan, Runstatus und Ledger in einem Commit | gleicher Payload liefert denselben Scan; anderer Payload 409 |
| Assessment | ausschließlich Assessment-/`full_analysis`-Credit | Claim per Row Lock und bedingtem Statusupdate | genau eine `SCAN_CONSUMED`-Buchung |
| Validation | ausschließlich `validation_check` | identische Transaktionsgrenze | kein Assessment-Fallback |
| Monitoring | aktive Subscription/Entitlement im authentisierten Tenant | Scan/Request ohne Creditbuchung | Ablauf blockiert neue Starts |
| Free Score | serverseitiger Tenant-Free-Slot | Unique `(tenant, free_scan_slot)` | ein Start, beliebig sichere identische Retries |
| Legacy Sync | deterministische tenant-/scanbasierte UUIDv5 | nutzt denselben Startservice | kein zweiter Consume-Pfad |

AL speichert nur die nicht sensitive Request-GUID sowie Status-/Versuchsdaten. Das Ledger enthält keine Secrets oder personenbezogenen Daten. P0-04-Lifecycle und P0-05-Findingschutz bleiben unverändert.
