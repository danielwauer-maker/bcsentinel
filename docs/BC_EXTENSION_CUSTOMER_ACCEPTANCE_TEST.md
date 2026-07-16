# BCSentinel Extension – Customer Acceptance Test

Stand: 16.07.2026  
Audit: GL-EXT-AUDIT-01  
Ziel: reproduzierbarer Kundenabnahmelauf in einer Business-Central-Sandbox

## 1. Testregeln

- Jeder Test wird mit Mandant, Environment, Company, BC-Version, Extension-Version, Benutzer, Permission Sets, Sprache, Startzeit und Ergebnis protokolliert.
- `PASS` erfordert das erwartete sichtbare Ergebnis, korrekten Backendzustand und keine unerwartete Telemetrie-/Berechtigungsabweichung.
- `FAIL` erhält Screenshot/Fehlertext, Backend Request-ID, Run-ID und Reproduktionsschritte.
- `BLOCKED` ist nur zulässig, wenn eine externe Voraussetzung fehlt; ein Produktfehler ist `FAIL`.
- Tests mit `ohne SUPER` werden mit einem Benutzer ausgeführt, der ausschließlich die angegebene BCSentinel-Rolle und dokumentierte BC-Basisrolle besitzt.

## 2. Voraussetzungen

- Frische BC-Sandbox und zweite Sandbox/Company für Isolationstests.
- Releasekandidat aus CI, signiertes `.app`, passende Symbole und Analyzerprotokoll.
- Backend-Staging mit HTTPS, Mail-Sink, Datenbankzugriff für Read-only-Verifikation und Telemetrie.
- Testidentitäten: Admin, Setup User, Scan User, Viewer, Benutzer ohne BCSentinel-Rechte.
- Testprodukte: kein Produkt, Assessment mit 1 Credit, Full Analysis, Monitoring aktiv/abgelaufen.
- Beispieldaten mit bekannten Customer-/Vendor-/Item-/Belegfehlern und mindestens einer anderen LCY als EUR.
- Alle offenen P0-Gaps müssen vor dem formalen Lauf geschlossen sein.

## 3. Abnahmetests CAT-01 bis CAT-23

### CAT-01 – Frische Installation

**Rolle/Voraussetzung:** Extension Admin; leere Company; Paket noch nicht installiert.  
**Schritte:** Paket installieren; Extension Management öffnen; Setup-Datensatz und Berechtigungen prüfen; BCSentinel über Suche öffnen.  
**Erwartung:** Installation ohne SUPER-spezifischen Workaround; genau ein idempotent initialisiertes Setup; keine Fehlermeldung; Version entspricht Manifest.  
**Auditstatus:** `NOT_EXECUTED`; aktuell keine Install-Codeunit und kein Sandboxzugang.  
**Evidenz:** `app.json`, fehlender `Subtype = Install`.

### CAT-02 – Assisted Setup und Registrierung

**Rolle/Voraussetzung:** BCS SETUP; gültiger Invite; noch kein Tenant.  
**Schritte:** Assisted Setup starten; E-Mail/Invite erfassen; registrieren; Setup schließen und erneut öffnen.  
**Erwartung:** genau ein Tenant; Token nicht sichtbar; Zugang bleibt nach neuer Sitzung erhalten; App-Version und BC-Kontext korrekt im Backend.  
**Auditstatus:** `FAIL_EXPECTED`; nicht idempotente Zufalls-Tenant-Erzeugung und App-Version `0.4.0`.

### CAT-03 – Registrierungswiederholung und Recovery

**Rolle/Voraussetzung:** CAT-02 bestanden; Backendantwort beim ersten Versuch nach Annahme künstlich unterbrechen.  
**Schritte:** Registrierung auslösen; Antwortverbindung abbrechen; denselben Vorgang wiederholen; Recovery verwenden.  
**Erwartung:** derselbe Tenant und dieselben Entitlements; kein zweiter DashboardUser; keine manuelle Datenbankkorrektur.  
**Auditstatus:** `FAIL_EXPECTED`; stabiler Idempotency-/Recovery-Key fehlt.

### CAT-04 – Portal-Einladung

**Rolle/Voraussetzung:** registrierter Tenant, Mail-Sink.  
**Schritte:** Einladung empfangen; Link einmal verwenden; erneut verwenden; Ablauf simulieren; Resend aus BC ausführen.  
**Erwartung:** Token einmalig/zeitbegrenzt; korrektes Tenantkonto; verständlicher Ablauf- und Resend-Flow.  
**Auditstatus:** `PARTIAL`; Hash/TTL backendseitig getestet, BC-Resend fehlt.

### CAT-05 – Dashboard und Tenant-Kontext

**Rolle/Voraussetzung:** BCS VIEWER; zwei Tenants und Companies.  
**Schritte:** Dashboard aus beiden Companies öffnen; URL nach Redirect prüfen; Token/Tenant manipulieren.  
**Erwartung:** richtige Company/Environment/Sprache; keine Cross-Tenant-Daten; Token nach Redirect nicht in sichtbarer URL; Manipulation 403.  
**Auditstatus:** `PARTIAL`; Backend-Security-Tests bestanden, BC-Runtime nicht ausgeführt.

### CAT-06 – Lizenzsnapshot und Ablauf

**Rolle/Voraussetzung:** Scan User; aktiver und anschließend abgelaufener Zugang.  
**Schritte:** Status aktualisieren; Findings öffnen; Zugang serverseitig ablaufen lassen; ohne Seitenneustart erneut Drilldown öffnen.  
**Erwartung:** Plan/Credits/Datum korrekt; nach Ablauf sofortige Sperre aller Premiumdetails.  
**Auditstatus:** `FAIL_EXPECTED`; lokale Gates nutzen stale `Premium Enabled`.

### CAT-07 – Creditgenauigkeit und Parallelstart

**Rolle/Voraussetzung:** genau 1 Assessment-Credit; zwei Sessions.  
**Schritte:** denselben Run doppelt starten; dann zwei verschiedene Runs gleichzeitig starten; Antwortverlust und Retry simulieren.  
**Erwartung:** derselbe Run verbraucht höchstens einmal; bei verschiedenen Runs gewinnt genau einer; Retry setzt denselben Run fort.  
**Auditstatus:** `FAIL_EXPECTED`; kein atomarer DB-Lock/Constraint und AL-Retry erzeugt neue Run-ID.

### CAT-08 – Manueller Deep Scan erfolgreich

**Rolle/Voraussetzung:** BCS SCAN ohne SUPER; 1 Credit; bekannte Datenfehler.  
**Schritte:** Scan starten; Client während Ausführung weiter bedienen; Monitor beobachten; Ergebnis öffnen.  
**Erwartung:** asynchron, laufender Fortschritt, genau ein Credit, Completed, korrekte Counts/Findings.  
**Auditstatus:** `FAIL_EXPECTED`; Runner ist synchron, Monitor-Polling nicht verdrahtet.

### CAT-09 – Scanfehler und Wiederaufnahme

**Rolle/Voraussetzung:** CAT-08; Backend beim Sync oder AL-Prüfung gezielt fehlschlagen lassen.  
**Schritte:** Scan starten; Fehler injizieren; Historie prüfen; Retry/Repair ausführen.  
**Erwartung:** terminal `Failed` oder dokumentiert `Partial`; kein ewiges `Running`; Creditzustand erklärbar; Retry ohne Doppelverbrauch.  
**Auditstatus:** `FAIL_EXPECTED`; Failure-Codeunit ist nicht mit dem direkten Runner-Aufruf verbunden.

### CAT-10 – Geplanter Scan täglich/wöchentlich/monatlich

**Rolle/Voraussetzung:** Monitoring aktiv; Scheduler-Servicebenutzer ohne SUPER.  
**Schritte:** jede Frequenz planen; Zeitpunkt abwarten/vorziehen; Erfolg, Fehler und Skip auslösen; Company neu öffnen.  
**Erwartung:** genau ein Task; richtige lokale Zeit inklusive DST; nach jedem Ausgang exakt einmal neu geplant.  
**Auditstatus:** `NOT_EXECUTED`; statisch vorhanden, keine Sandbox-/Servicepermission-Evidenz.

### CAT-11 – Scheduler nach Lizenzablauf

**Rolle/Voraussetzung:** geplanter Task; Monitoring vor Ausführung ablaufen lassen.  
**Schritte:** Task laufen lassen; Status, Credit und nächsten Termin prüfen.  
**Erwartung:** kein Scan/Creditverbrauch; verständlicher Skip; definierte Replan-/Deaktivierungsregel.  
**Auditstatus:** `NOT_EXECUTED`; Backendgate vorhanden, End-to-End-Verhalten offen.

### CAT-12 – Scan-Historie und Löschung

**Rolle/Voraussetzung:** Quick-, Deep-, Monitoring-, Failed- und Alt-Run.  
**Schritte:** sortieren/filtern; jeden Run öffnen; einzeln und mehrfach löschen; Reconcile ausführen.  
**Erwartung:** korrekter Typ/Status; Confirm default No; lokaler und Backendbestand konsistent; Viewer verursacht keine Writes.  
**Auditstatus:** `FAIL_EXPECTED`; `EnsureSortFields()` schreibt beim Öffnen, Partial/Altstatus unklar.

### CAT-13 – Sprache Englisch

**Rolle/Voraussetzung:** Benutzersprache EN-US.  
**Schritte:** Setup, Scans, Monitor, Historie, Findings, Exceptions, Dashboard und Report durchlaufen.  
**Erwartung:** vollständig verständliches Englisch, keine deutschen Texte/Mojibake.  
**Auditstatus:** `FAIL_EXPECTED`; AL-Lokalisierungschecker fehlgeschlagen.

### CAT-14 – Sprache Deutsch

**Rolle/Voraussetzung:** Benutzersprache DE-DE.  
**Schritte:** dieselben Oberflächen wie CAT-13; Fehler- und Leerezustände einschließen.  
**Erwartung:** vollständiges, korrekt codiertes Deutsch; Terminologie konsistent; `Überblick` korrekt.  
**Auditstatus:** `FAIL_EXPECTED`; Mischtexte/Encoding; Backendtest erwartet veraltete Umschrift.

### CAT-15 – Currency Formatting in EUR

**Rolle/Voraussetzung:** LCY EUR; positive, negative, null und große Werte.  
**Schritte:** alle Impact-/Saving-Felder in Setup, Historie, Findings und Worklists vergleichen.  
**Erwartung:** einheitliche Dezimal-/Tausenderformatierung und fachlich identische Werte.  
**Auditstatus:** `PARTIAL`; Formatter vorhanden, keine AL-Tests.

### CAT-16 – Currency Formatting außerhalb EUR

**Rolle/Voraussetzung:** separate Company mit LCY USD oder GBP; Backendwerte in EUR.  
**Schritte:** Scan synchronisieren; AL-Anzeigen mit Backend/Umrechnungskurs vergleichen.  
**Erwartung:** entweder nachweislich umgerechnete LCY-Werte mit Kurs/Datum oder klare EUR-Kennzeichnung.  
**Auditstatus:** `FAIL_EXPECTED`; Code hängt LCY an unveränderten EUR-Wert.

### CAT-17 – Findings und Zugriffsschutz

**Rolle/Voraussetzung:** Viewer, Scan User, abgelaufener Nutzer, Nutzer ohne Rolle.  
**Schritte:** Listen, FactBoxes, Drilldown, direkte Page-URL und Tabelle über alle Rollen öffnen.  
**Erwartung:** nur berechtigte aktuelle Nutzer sehen Premiumdetail/Empfehlung; keine Page-OnOpen-Permissionfehler.  
**Auditstatus:** `FAIL_EXPECTED`; stale Gate und direkte Read-Rechte.

### CAT-18 – Ausnahmen

**Rolle/Voraussetzung:** betroffene Customer-, Vendor-, Item- und Worklist-Datensätze.  
**Schritte:** Ausnahme mit Pflichtgrund anlegen; Scan wiederholen; deaktivieren/reaktivieren; Quelldatensatz löschen.  
**Erwartung:** Regel wird exakt übersprungen; Audittrail mit Wer/Wann/Warum; klare Reaktivierung; keine verwaisten Records.  
**Auditstatus:** `FAIL_EXPECTED`; Grund nicht zwingend, Aktion semantisch irreführend, Cleanup offen.

### CAT-19 – Executive Report HTML/PDF

**Rolle/Voraussetzung:** abgeschlossener Run; berechtigter Nutzer.  
**Schritte:** HTML/PDF-Link erzeugen; ohne Authheader öffnen; Typ/Scan/Token ändern; Ablauf simulieren.  
**Erwartung:** korrekter Report; falscher Typ/Scan 403; Link nach TTL ungültig; Tenantdaten isoliert.  
**Auditstatus:** `PARTIAL_PASS`; Backendtests bestanden, BC-/Browser-Sandboxlauf offen.

### CAT-20 – Secret- und Token-Lifecycle

**Rolle/Voraussetzung:** registrierter Tenant.  
**Schritte:** Setup-/Tabellendaten prüfen; Session/Company wechseln; Token rotieren/revoken; Extension deinstallieren/reinstallieren.  
**Erwartung:** Token nie in normaler Tabelle/UI/Log; Company-isoliert; Rotation/Recovery ohne Tenantverlust.  
**Auditstatus:** `FAIL_EXPECTED`; Isolated Storage vorhanden, Rotation/Recovery fehlen.

### CAT-21 – Permissions ohne SUPER

**Rolle/Voraussetzung:** je ein Benutzer nur mit VIEWER, SCAN, SETUP, ADMIN plus dokumentierter Basisrolle.  
**Schritte:** erlaubte und verbotene Aktionen pro Rolle ausführen; Scheduler laufen lassen.  
**Erwartung:** alle erlaubten Flows funktionieren; verbotene Aktionen werden sauber blockiert; kein SUPER nötig.  
**Auditstatus:** `NOT_EXECUTED`; Basisdatenrechte/Serviceidentität fehlen, Least Privilege statisch zweifelhaft.

### CAT-22 – Upgrade N-1 auf Releasekandidat

**Rolle/Voraussetzung:** Sandbox mit produktionsnahen Daten auf Version 1.0.2.5 und aktivem Scheduler/Token/History.  
**Schritte:** Upgrade auf 1.0.2.6+; Daten, Secret, Task, Exceptions und History prüfen; Scan ausführen; Roll-forward wiederholen.  
**Erwartung:** keine Daten-/Tokenverluste, keine Dubletten, idempotente Migration, funktionierender Scan.  
**Auditstatus:** `FAIL_EXPECTED`; keine Upgrade-Codeunit/Tests; Manifestversionen driften.

### CAT-23 – Deinstallation, Retention und Supportdiagnose

**Rolle/Voraussetzung:** Tenant mit History, Findings, Share-Link und Ausnahmen.  
**Schritte:** Datenexport/Retentionfrist prüfen; Extension deinstallieren; Backendlöschung anfordern; Fehler mit Request-ID an Support geben.  
**Erwartung:** dokumentierte Datenwirkung, technisch erzwungene Retention/Löschung, keine gültigen Altlinks/Tokens, reproduzierbare Supportdiagnose.  
**Auditstatus:** `FAIL_EXPECTED`; automatische Retention und durchgängige Correlation-/Deletion-Evidenz fehlen.

## 4. Abnahmekriterium

Für `PILOT GO` müssen CAT-01 bis CAT-23 ausgeführt sein; kein P0/P1-Test darf fehlschlagen. `NOT_EXECUTED`, `BLOCKED` oder `FAIL_EXPECTED` zählt nicht als bestanden. Für `CUSTOMER GO` sind zusätzlich Upgrade, Retention, Permissions und Recovery mit produktionsnaher Datenmenge zu wiederholen. Für `APPSOURCE READY` kommen AppSourceCop, technische Validierung, Marketing-/Privacy-Artefakte und Einreichungscheck hinzu.

## CAT-Delta GL-EXT-P0B – Credit und Idempotenz

Alle folgenden Tests sind vorbereitet und mangels BC-Sandbox/PostgreSQL-Staging **NOT_EXECUTED**. Pro Test sind AL Request-ID, Backend Scan-ID, Creditstatus und Ledgerzeile zu sichern.

| Test | Schritte | Erwartung |
|---|---|---|
| P0B-CAT-01 Assessment | einen Credit grantieren, Scan starten | ein Scan, Credit consumed, ein Ledger `-1` |
| P0B-CAT-02 Doppelklick | Startaktion unmittelbar doppelt auslösen | dieselbe Request-/Scan-ID, keine zweite Buchung |
| P0B-CAT-03 Timeout | Antwort nach Backend-Commit unterbrechen, erneut starten | lokaler Retry nutzt dieselbe GUID; Replay |
| P0B-CAT-04 Parallelstart | zwei verschiedene Starts bei einem Credit | genau einer angenommen, einer No Credit |
| P0B-CAT-05 Validation | passenden Validation-Credit verwenden | Validation verbraucht ihn, keinen Assessment-Credit |
| P0B-CAT-06 Validation ohne Credit | nur Assessment-Credit bereitstellen | 402/verständlicher No-Credit-Fehler, Bestand unverändert |
| P0B-CAT-07 Monitoring aktiv | aktive Subscription, Start und Retry | kein Credit, ein Scan |
| P0B-CAT-08 Monitoring abgelaufen | Laufzeit beenden, neuen Start versuchen | blockiert, keine Teilanlage |
| P0B-CAT-09 Scheduler doppelt | dieselbe geplante Ausführung zweimal triggern | dieselbe gespeicherte GUID, ein Scan/eine Buchung |
| P0B-CAT-10 Restart | Backend nach Commit vor Antwort neu starten | Retry findet persistiertes Ergebnis |
