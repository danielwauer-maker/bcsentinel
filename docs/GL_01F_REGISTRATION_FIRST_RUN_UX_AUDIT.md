# GL-01F – Registration & First-Run UX Fix

## Bestandsanalyse vor Implementierung

### Registrierung

- Die Registrierungsaktion ist auf `DH Setup` als Action `RegisterTenant` in der Gruppe `ConnectionActions` definiert.
- `Enabled` wird über die Page-Variable `CanRegisterTenant` gesteuert.
- Vor GL-01F berücksichtigte `CanRegisterTenant` nur `Data Processing Consent` und eine nicht leere `API Base URL`.
- Die vorhandene fachliche E-Mail-Validierung liegt zentral auf `DH Setup` in `HasValidContactEmail()` und `EnsureValidContactEmail()`.
- Der Action-Handler prüfte die E-Mail erst nach dem Klick. Dadurch erklärte die deaktivierte Action den fehlenden oder ungültigen Zustand nicht.
- Die Feldvalidierungen für `Contact Email` und `Data Processing Consent` riefen zwar `UpdateActionState()`, aber kein gezieltes `CurrPage.Update(false)` auf. Sichtbarkeit, Statusfelder und Promoted Actions wurden deshalb nicht unmittelbar neu gezeichnet.
- Die eigentliche Registrierung erfolgt unverändert über `DH API Client.RegisterTenant()` und anschließend `RefreshLicenseStatus()` innerhalb von `TryRegisterTenantAndRefresh()`.

### Promoted Actions

- `OpenLatestFindings` ist auf `DH Setup` mit `Promoted = true` und ohne `Visible`-Bedingung definiert.
- Die Registrierungsaction war nicht promoted und dauerhaft sichtbar.
- GL-01F verwendet dieselbe Action sowohl im Menü als auch in der Schnellaktionsleiste. Es entsteht kein zweiter Registrierungsablauf.

### Manueller Scheduler-/Monitoring-Start

- `DH Setup.RunScheduledScanNow` ruft `DH Scan Scheduler Mgt.RunNow()` auf.
- `RunNow()` ruft `StartScheduledScan()` und darüber `DH Deep Scan Mgt.QueueDeepScanInBackground()` auf.
- `QueueDeepScanInBackground()` führt im analysierten Stand den `DH Deep Scan Runner` dennoch synchron bis zum Ende aus.
- Anschließend öffnet die Page-Action zusätzlich den Scan-Monitor mit `Page.Run`.
- Die Action kann deshalb erst nach der vollständigen Scanverarbeitung beziehungsweise nach dem Seitenaufruf zurückkehren. Dies ist die Ursache des sichtbaren Zustands „Wird bearbeitet…“.

## Minimale Architekturentscheidung

1. `DH Setup.IsRegistrationReady()` bündelt weiterhin ausschließlich vorhandene Voraussetzungen: nicht registriert, vorhandene E-Mail-Validierung, bestehendes Consent-Feld und konfigurierte API-URL.
2. Die Setup-Page zeigt vor der Registrierung einen rein variablen, nicht modalen Hinweisbereich mit E-Mail- und Consent-Status.
3. E-Mail- und Consent-OnValidate aktualisieren Action- und Hinweiszustand per `CurrPage.Update(false)`.
4. Die bestehende Registrierungsaction wird promoted und ruft eine lokale zentrale Page-Prozedur auf. `OpenLatestFindings` bleibt fachlich unverändert, ist aber vor Registrierung nicht sichtbar.
5. Nur der manuelle `Run Now`-Pfad startet den bereits vorhandenen TableNo-Codeunit `DH Deep Scan Runner` über `Session.StartSession`. Der automatische TaskScheduler-Pfad bleibt unverändert.
6. Nach erfolgreicher Session-Annahme aktualisiert die Page ihre Statusfelder, zeigt die bereits etablierte allgemeine Scan-Erfolgsmeldung und kehrt ohne `Page.Run` zurück.

Keine Backend-, API-, Datenbank-, Lizenz-, Credit-, Scanregel- oder Scheduler-Frequenzänderung ist erforderlich.

## Implementierungsergebnis

- Der nicht registrierte Zustand zeigt einen Hinweisbereich mit separatem Status für Kontakt-E-Mail und Datenschutzeinwilligung.
- Leere, ungültige und gültige E-Mail-Zustände verwenden ausschließlich `DH Setup.HasValidContactEmail()`.
- `RegisterTenant.Enabled` verwendet zentral `DH Setup.IsRegistrationReady()`.
- Die bestehende Registrierungsaction ist vor Registrierung sichtbar und promoted; nach Registrierung verschwindet sie.
- `OpenLatestFindings` ist vor Registrierung nicht sichtbar und verwendet danach unverändert seine bisherige Enabled- und Zugriffsschutzlogik.
- E-Mail-, Consent- und API-URL-Änderungen aktualisieren Page-Variablen und Promoted Actions mit `CurrPage.Update(false)`.
- Die Registrierungsaction delegiert vollständig an `RunTenantRegistration()`; der bestehende API-/Refresh-Pfad blieb unverändert.
- `Run Now` startet genau einen vorhandenen `DH Deep Scan Runner` über `Session.StartSession`, aktualisiert anschließend die Setup-Page, zeigt die allgemeine Scan-Erfolgsmeldung und beendet die Action ohne `Page.Run` oder `RunModal`.
- Der automatische Scheduler verwendet weiterhin `QueueDeepScanInBackground()` innerhalb seiner bestehenden TaskScheduler-Session.

## Verifikation

- GL-01F AL-Source-Vertragstest: bestanden.
- Betroffene GL-01A-2-/First-Run-Python-Vertragstests: 18 bestanden.
- AL-Source-Uniqueness: 89 Objektdeklarationen, ein kanonischer `app/src`-Baum, keine generierten AL-Quellen.
- de-DE-XLF: 1.460 eindeutige Translation-IDs, keine Duplikate; alle neuen GL-01F-IDs besitzen nicht leere deutsche Targets.
- AL-Build: 0 Fehler, 0 Warnungen.
- `git diff --check`: Exit Code 0; ausschließlich nicht blockierende CRLF-Hinweise von Git.
- Backend-Anwendung, API-Verträge, Datenbankmodelle und Alembic-Migrationen: unverändert.

## Releasebewertung

GO MIT RESTPUNKTEN: Quellvertrag, Übersetzungen und Build sind freigabefähig. Die manuellen Tests A–E, insbesondere die sichtbare Reaktivierung der Webclient-Page nach `Session.StartSession`, müssen noch einmal in einer echten Business-Central-Sandbox bestätigt werden, da in dieser Arbeitsumgebung keine BC-Webclient-Runtime verfügbar ist.
