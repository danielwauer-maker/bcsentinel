# GL-EXT-UX01 – Customer-Friendly Setup Page & Information Hierarchy

Stand: 20.07.2026  
Scope: Business-Central-Extension, Setup-Page 53100  
Status: **auf Code- und Artefaktebene abgeschlossen; Sandbox-CAT BLOCKED**

## Ausgangslage

Die Setup-Page war funktional umfangreich, stellte aber technische Konfiguration, Produktzugriff, Schedulerdiagnose und Scanwerte nahezu gleichrangig dar. Die P0A–P0E-Schutzlogik war vorhanden und durfte nicht verändert werden. Es gab keine Business-Central-Sandbox und keine AL-Test-App; die Prüfung kombiniert deshalb vollständige statische Rückverfolgung, echten AL-Compile/Analyzer und vorbereitete, ausdrücklich nicht bestandene Sandbox-CATs.

## Bisherige Struktur

| Reihenfolge | FastTab | Inhalt/Befund |
|---:|---|---|
| 1 | Subscription & Status | Produktzugriff, Monitoring, Ablaufdaten, Credits und technische letzte Lizenzprüfung gemischt |
| 2 | Scan Configuration | Modul-/Checkzusammenfassung und Bereitschaft |
| 3 | Scheduled Scans | Konfiguration, Ergebnis, Fehlerdiagnose und Task-ID in einer Gruppe |
| 4 | Connection | API, Kontakt, Consent, Registrierung und technische Tenant-/Tokenwerte |
| 5 | Module Health Scores | zehn lokale Modulwerte des letzten Scans |
| 6 | Last Scan | Run-ID, Datum, Score, Issues, Impact, Dauer und Status |

Die Page enthielt 52 sichtbare Felder/Anzeigevariablen und 21 Actions. Editierbar waren API-URL, Kontakt-E-Mail, Consent und Schedulerparameter. Tenant-, Registration- und Task-IDs waren bereits read-only, aber prominent. `OnOpenPage` führte keinen Backend-Refresh aus; der letzte Scan wurde lokal über `SetCurrentKey`/`FindFirst` gelesen.

## Neue Informationshierarchie

1. **Overview and Status / Übersicht und Status** steht oben und zeigt Connection, Registration, aktuellen Produktplan, letzten Score, Bewertung, letzten Scan/Status, nächsten Lauf und Monitoring.
2. **Product and Access / Produkt und Zugriff** bündelt Produktzugriff, Dashboard-/Finding-/Reportzugriff, Monitoring sowie Assessment-/Validation-Credits.
3. Die wichtigsten Actions sind promoted: modusspezifischer Scanstart, Dashboard, Produktzugriff aktualisieren, Historie, Findings, letzter Report und Scheduler.
4. **Connection and Registration / Verbindung und Registrierung** enthält nur kundenrelevante Konfiguration und Consent.
5. **Scheduled Scans** erklärt ausdrücklich die Business-Central-Aufgabenwarteschlange.
6. Scan-Konfiguration, Modulwerte und Details des letzten Scans bleiben lokal und unverändert fachlich.
7. **Advanced Information / Erweiterte Informationen** enthält Supportidentitäten und Snapshotdiagnose.
8. **Administrative Actions** trennt den Registrierungs-Cache-Reset von normalen Actions.

`Expanded = false` ist für diesen Gruppenkontext in Runtime 16 nicht zulässig (`AL0124`). Die Gruppe ist ein eigener FastTab, ihr initialer Collapse-Zustand muss in der Sandbox beziehungsweise per Page-Personalisierung geprüft werden.

## Geänderte und verschobene Felder

| Feld/Wert | Neu/verschoben | Quelle | Editierbar |
|---|---|---|---|
| Connection Status | neu, oben | lokale API-URL + sicher gespeicherter Token vorhanden | nein |
| Registration Status | neu, oben | `Registered`, Tenant-ID und Token | nein |
| Current Product Plan | neu, oben | bestehendes `GetProductAccessDisplay()` | nein |
| Latest Score/Rating/Scan/Status | neu, oben | letzter lokaler `DH Deep Scan Run` | nein |
| Next Scheduled Scan/Monitoring | neu, oben | `DH Setup` | nein |
| Assessment/Validation Credits | Produktgruppe | zentraler Access Snapshot | nein |
| Report Access Until | Produktgruppe | zentraler Access Snapshot | nein |
| Entra Tenant, Environment, Company System ID | Advanced | `DH Tenant Identity Mgt.` | nein |
| Registration-/Task-/Last-Scan-ID | aus Hauptgruppen nach Advanced | bestehende lokale Werte | nein |
| Snapshot Received/Expires/Version/Correlation | Advanced | zentraler Access Snapshot | nein |
| API-Token | nicht angezeigt | ausschließlich `IsolatedStorage`; nur boolescher Konfigurationsstatus | n/a |

Es wurde kein Tabellenfeld, kein FlowField, keine Migration und kein Backendaufruf ergänzt. Ein nicht vorhandenes Plan-Enddatum wird nicht geraten. Leere DateTime-/Textwerte bleiben leer; „No scan yet / Noch kein Scan“ wird nur für abgeleitete Textanzeigen verwendet.

## Hauptaktionen

- `Start Free Data Health Score`, `Start Full Analysis or Validation Scan` und `Start Monitoring Scan` verwenden unverändert `StartAvailableScan()` und die bestehende Scanlogik.
- `Open Analytics Dashboard` ruft unverändert `DH Access Guard.EnsureDashboardAccess()` vor der Tokenanforderung auf.
- `Open Findings` ruft `EnsureIssuesAccess()` auf und öffnet gefiltert die Findings des letzten lokalen Runs; die Zielpage prüft zusätzlich beim Öffnen.
- `Open Latest Report` delegiert über eine schmale öffentliche Page-Methode an die bereits vorhandene Reportlogik im Deep-Scan-Monitor. Dort bleibt `EnsureReportAccess()` autoritativ; HTTP-/Tokenlogik wurde nicht dupliziert.
- Produktzugriff aktualisieren, Scan-Historie und Scheduleraktivierung verwenden ihre bestehenden Manager/Guards.

## Administrative Aktion und Confirm

Die bisherige Reset-Action ist aus der Connection-Gruppe ausgeblendet und als `Reset Cached Registration` in `Administrative Actions` neu exponiert. Der Dialog hat `Default = false` und beschreibt exakt die Codewirkung: lokaler Registrierungs-/Access-Cache wird zurückgesetzt; stabile Tenant-Identität, API-Token, Käufe und Scan-Historie bleiben erhalten. Ein Abbruch kehrt vor jeder Mutation zurück. Es werden weder Backendregistrierung noch Historie gelöscht.

## Sichtbarkeit, Editierbarkeit und Berechtigungen

- Technische Felder sind ausnahmslos `Editable = false`.
- Scan-Captions und Sichtbarkeit folgen dem bereits berechneten Scan-/Monitoringzustand; die Fachentscheidung bleibt im Scanmanager/API-Client.
- Findings, Dashboard und Report sind im UI nur sinnvoll aktivierbar; ihre Handler erzwingen unabhängig davon die frischen P0D-Guards.
- Schedulerfelder verwenden weiterhin `CanUseScheduler`/`CanEditSchedulerDetails`.
- Die Page ist nur über die bestehenden Permission Sets `BCSENTINEL SETUP` und `BCSENTINEL ADMIN` ausführbar. Viewer und Scheduler erhalten keinen Setupzugriff. Permission Sets wurden in UX01 nicht erweitert.

## Performanceentscheidungen

- keine API-Abfrage in `OnOpenPage`, `OnAfterGetCurrRecord` oder pro Feld;
- Access Snapshot ausschließlich aus `DH Setup`, Refresh nur über bestehende Action/Guardlogik;
- ein lokaler, indexgestützter Latest-Run-Lookup für Anzeige; zusätzliche `IsEmpty`-Prüfung nur für Report-Enablement;
- keine Findingabfrage beim Page-Refresh; Findings werden erst durch die Action gefiltert geöffnet;
- Plattformidentitäten werden lokal über `Environment Information`/`Company Information` gelesen;
- keine Scan-History-Schleife und keine neue FlowField-Berechnung.

## Localization

Alle neuen Captions, Tooltips, Status-/Rating-Labels, Schedulerhinweise und Confirmtexte liegen als übersetzbare AL-Properties beziehungsweise `Label` vor. `BCSentinel.g.xlf` wurde aus dem finalen Compile synchronisiert; alle Setup-Units besitzen in `BCSentinel.de-DE.xlf` ein nichtleeres, quellsynchrones deutsches Target. Ergebnis: 0 fehlende Setup-Units, 0 leere Targets, 0 Source-Mismatches, 0 doppelte IDs. Der globale Checker bleibt mit 81 historischen Treffern rot; UX01 erzeugt keinen neuen harten deutschen AL-Text.

## Tests und Ergebnisse

| Prüfung | Ergebnis |
|---|---|
| ReleaseCloud Compile, 84 Dateien, Compiler 17.0.34.45391 | **PASS**, 0 Fehler |
| CodeCop + PerTenantExtensionCop | **PASS**, 0 Fehler; 307 bestehende Warnungen/84 Infos |
| AppSourceCop | **FAIL wie Baseline**: EULA, Logo, `contextSensitiveHelpUrl`, ID-Range; A.I.-Warnung |
| XLF/JSON Parse | **PASS** |
| Setup-XLF-Vollständigkeit | **PASS**, 0/0/0/0 Abweichungen |
| Localization Checker | **FAIL**, 81 historische Treffer; keine UX01-Regression |
| Backend-Pytest finaler Dockerlauf | **PASS**, 255 bestanden, 6 übersprungen, 40 Warnungen, 664,93 s |
| erster Pytest-Versuch | Harnessfehler: read-only SQLite-Testpfad; kein Produktbefund |
| zweiter Pytest-Versuch | 234 bestanden/6 skipped/21 Harnessfehler durch fehlende Root-Mounts |
| `git diff --check` | **PASS** |

Die Backend-Suite umfasst keine AL-UI-Automation. Sie bestätigt, dass die nicht geänderten Backend-/P0-Verträge weiter grün sind.

## Sandbox-Schritte

Die 20 UX01-Fälle in `BC_EXTENSION_CUSTOMER_ACCEPTANCE_TEST.md` sind `BLOCKED`: keine authentisierte Business-Central-Sandbox. Sie dürfen nicht als manuell bestanden gelten. Zu prüfen sind insbesondere leerer/registrierter Zustand, kein/letzter Scan, Schedulerdaten, EN/DE, modusspezifische Actions, P0D-Guards, Confirm-Abbruch, API-Call-Anzahl, Rollen und FastTab-Collapsezustand.

Screenshots vorher/nachher sind mangels Sandbox nicht verfügbar.

## Bekannte Grenzen und verbleibende UX-Gaps

1. Initial eingeklappter Zustand von „Erweiterte Informationen“ ist mit dem Zielruntime-Property nicht erzwingbar und muss per Runtime/Personalisierung bestätigt werden.
2. API URL und Kontakt-E-Mail sind für beide bestehenden Setup-berechtigten Rollen editierbar; eine feinere Trennung erfordert ein bewusstes Permission-/Rollen-Design und wurde nicht improvisiert.
3. Die globale Localization-Baseline (81 Treffer) bleibt P1.
4. Analyzer-Warnungen, darunter fehlende Tooltips an historischen Wochentags-/Modulfeldern, bleiben bestehen; UX01 hat keine neuen Fehler eingeführt.
5. Visuelle Dichte, Action-Promotions und Tablet-/kleine Viewports sind ohne Sandbox nicht verifiziert.

## Abschlussbewertung

- Sprint abgeschlossen: **Ja** (Code, XLF, Compile, Analyzer und Dokumentation; Sandboxevidenz separat BLOCKED)
- Setup-Page kundentauglich: **Ja auf Codeebene**, Runtime-Abnahme ausstehend
- Regressionen festgestellt: **Nein**; zwei Test-Harnessfehler wurden alternativ aufgelöst
- bereit für GL-EXT-UX02: **Ja**, sofern UX01-Sandbox-CATs als verpflichtender Carry-over vor Pilot ausgeführt werden

Commit-Vorschlag: `refactor(extension): improve setup page information hierarchy`
