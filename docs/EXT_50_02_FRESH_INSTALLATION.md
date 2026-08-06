# EXT-50-02 – Frische Installation auf leerem Business-Central-Tenant

**Stand:** 2026-08-06  
**Basis:** EXT-50-01 `VERIFIED_IN_CI / PASS`  
**Extension:** `1.0.2.20`  
**Ziel:** Nachweis einer vollständigen Neuinstallation ohne vorhandene BCSentinel-Version oder bestehende BCSentinel-Daten.

## 1. Verbindliche Testumgebung

- Business Central SaaS Sandbox
- Environment: `BCSentinel-Pilot-Fresh`
- kompatibler BC-27-Stand
- Company: `CRONUS DE` oder neue leere Testcompany
- kein zuvor installiertes BCSentinel-Paket
- kein übernommenes BCSentinel-Setup
- kein vorhandener BCSentinel Job Queue Entry
- keine manuelle Datenbankkorrektur

## 2. Benutzer und Berechtigungen

Für die Installation wird ein Benutzer mit Berechtigung zum Hochladen und Installieren von PTE-Extensions benötigt.

Nach der Installation werden zwei Rollen verwendet:

1. **Installations-/Setup-Administrator**
   - darf Extension installieren,
   - BCSentinel Setup öffnen,
   - Registrierung durchführen,
   - Permission Sets zuweisen,
   - Monitoring konfigurieren.

2. **BCSentinel Test User**
   - kein SUPER als Dauerlösung,
   - nur die im Paket gelieferten BCSentinel Permission Sets plus notwendige BC-Basisrechte,
   - führt Free Scan, Historie, Findings und Reporttests aus.

Die exakten gelieferten Permission-Set-Namen werden während der Runtime-Prüfung aus der installierten Extension dokumentiert. Fehlende oder unklare Permission Sets gelten als Befund und werden nicht durch dauerhaftes SUPER kaschiert.

## 3. Verifiziertes Installationsartefakt

- Datei: `BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.20.app`
- SHA-256: `62a5a5d380008f3d212bbc2834429ad4b3f3d36787b4ee567b7e68a2f4e78756`
- Quelle: grüner `BC AL Compile and Cop Gate #60`

## 4. Testreihenfolge

### A. Vorprüfung

1. Sandboxname und BC-Version dokumentieren.
2. Companynamen dokumentieren.
3. Extension Management öffnen.
4. bestätigen, dass BCSentinel nicht installiert ist.
5. prüfen, dass kein BCSentinel Job Queue Entry vorhanden ist.
6. APP-Hash lokal gegen die Release-Baseline prüfen.

### B. Upload und Installation

1. APP hochladen.
2. Schema-Synchronisierung zulassen.
3. Installation abschließen.
4. installierte Version 1.0.2.20 prüfen.
5. Installationszeitpunkt dokumentieren.
6. Eventuelle Warnungen vollständig erfassen.

### C. Berechtigungen

1. mit Installationsadministrator BCSentinel Setup öffnen.
2. gelieferte BCSentinel Permission Sets auflisten.
3. Test User ohne SUPER einrichten.
4. notwendige BCSentinel Permission Sets zuweisen.
5. mit Test User anmelden.
6. Setupseite öffnen und fehlende Berechtigungen dokumentieren.

### D. Setup und Registrierung

1. Backend-Endpunkt prüfen.
2. Registrierung starten.
3. Tenant, Environment und Company im Backend kontrollieren.
4. Registrierung erneut auslösen.
5. bestätigen, dass keine zweite Tenant-/Company-Bindung erzeugt wird.
6. verständliche Rückmeldung für bestehende Registrierung prüfen.

### E. Free Scan

1. Free Scan starten.
2. Startstatus dokumentieren.
3. vollständigen Abschluss abwarten.
4. Historieneintrag kontrollieren.
5. Score, Module, Checks und Findings kontrollieren.
6. bestätigen, dass kein kostenpflichtiger Credit verbraucht wurde.
7. zweiten Free Scan versuchen und erwartete Sperre dokumentieren.

### F. Ergebnisoberflächen

1. Findings öffnen.
2. mindestens einen Drilldown prüfen.
3. HTML Executive Report öffnen.
4. PDF Executive Report öffnen.
5. Dashboard-Link öffnen.
6. Tenant-/Company-Zuordnung der angezeigten Daten prüfen.

### G. Monitoring

1. Monitoring-Entitlement für den Testtenant freigeben.
2. manuellen Monitoring-Scan starten.
3. Abschluss und Historie kontrollieren.
4. Scheduler konfigurieren.
5. ersten geplanten Lauf abwarten.
6. bestätigen, dass genau ein neuer Lauf entsteht.

## 5. Pflichtscreenshots

- Sandboxübersicht mit Environmentname und BC-Version
- Extension Management vor Installation
- Upload-/Installationsbestätigung
- installierte Version 1.0.2.20
- gelieferte BCSentinel Permission Sets
- BCSentinel Setup nach frischer Installation
- erfolgreiche Registrierung
- Free-Scan-Start
- abgeschlossener Free Scan
- Historieneintrag
- Findings
- HTML-Report
- PDF-Report
- Dashboard-Link
- manueller Monitoring-Scan
- geplanter Monitoring-Lauf

Keine Secrets, Tokens oder vollständigen URLs mit Zugangsdaten in Screenshots aufnehmen.

## 6. Abnahmekriterien

EXT-50-02 ist PASS, wenn:

- APP ohne Installations- oder Schemafehler installiert wird,
- Version 1.0.2.20 sichtbar ist,
- Setup ohne vorhandene BCSentinel-Daten initialisiert wird,
- ein Benutzer ohne dauerhafte SUPER-Abhängigkeit arbeiten kann,
- Registrierung genau eine korrekte Tenant-/Environment-/Company-Bindung erzeugt,
- Free Scan erfolgreich abschließt,
- Historie, Findings, HTML, PDF und Dashboard-Link funktionieren,
- Monitoring manuell und geplant erfolgreich läuft,
- keine Dubletten, Creditfehler oder manuellen DB-Korrekturen erforderlich sind.

## 7. Stop-Kriterien

Sofort stoppen und nicht weiter testen bei:

- Schema- oder Installationsfehler,
- Tenant- oder Company-Verwechslung,
- doppelter Registrierung,
- ungewolltem Creditverbrauch,
- Datenzugriff auf einen fremden Tenant,
- wiederholtem Doppelstart des Schedulers,
- Notwendigkeit einer manuellen Produktionsdatenbankkorrektur.

## 8. Status

`AWAITING_MANUAL_BC_RUNTIME_EVIDENCE`
