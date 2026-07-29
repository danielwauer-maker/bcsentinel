# PILOT-E2E-01B – Real BC Sandbox Execution

## Ziel

Dieser Sprint macht die reale Business-Central-Abnahme reproduzierbar und fail-closed. Ein grüner Backend- oder Compile-Lauf ersetzt keinen echten Sandbox-Nachweis. Der Sprint gilt erst als vollständig bestanden, wenn alle Gates `PILOT-BC-002` bis `PILOT-BC-006` und `PILOT-UAT-001` mit Evidence auf `PASS` stehen.

## Automatisiert

- maschinenlesbares Evidence-Protokoll
- Prüfung auf Sandbox statt Production
- Prüfung auf DEV/STAGING-Backend und HTTP 200
- Prüfung von BC-, App-, Company- und Commit-Identität
- Pflicht-Evidence für jedes PASS-Gate
- Schutz gegen absolute Pfade und `..`-Pfadflucht
- vollständiger Gate-Satz ohne Duplikate
- Sicherheitsattest: keine Produktion, keine Kundendaten, keine Secrets
- CI-Contract-Test bei Pull Requests
- manueller GitHub-Actions-Gate für das fertige Evidence-Paket

## Nicht automatisierbar ohne deine Microsoft-Umgebung

- Zugriff auf das BC Admin Center
- Bereitstellung einer Sandbox und Test-Company
- Upload/Installation der `.app`
- interaktive Anmeldung/MFA oder Entra-Consent
- echte BC-Seiten, Job Queue, Reports und Upgrade
- visuelle und fachliche UAT

## Sicherheitsgrenze

Verwende ausschließlich:

- Environment Type `Sandbox`
- reine Testdaten
- Backend Tier `dev` oder `staging`
- Stripe Testmode oder dokumentierte nichtproduktive Freischaltung

Nie in Evidence aufnehmen:

- Passwörter
- Client Secrets
- API Tokens
- vollständige Connection Strings
- produktive Kundendaten

## Evidence-Paket anlegen

1. Kopiere `quality/pilot-e2e/sandbox_evidence.template.json` nach:

   `quality/pilot-e2e/sandbox_evidence.json`

2. Lege lokal oder auf einem sicheren Arbeitsbranch den Ordner an:

```text
pilot-e2e-01b-evidence/
  01-environment/
  02-installation/
  03-registration-free/
  04-assessment-validation/
  05-monitoring/
  06-upgrade/
  07-uat/
```

3. Trage in `sandbox_evidence.json` nur relative Dateipfade ein.

4. Prüfe lokal zunächst ohne vollständiges PASS-Gate:

```powershell
python scripts/validate_pilot_sandbox_evidence.py quality/pilot-e2e/sandbox_evidence.json --evidence-root .
```

5. Nach Abschluss aller Schritte:

```powershell
python scripts/validate_pilot_sandbox_evidence.py quality/pilot-e2e/sandbox_evidence.json --evidence-root . --require-all-pass
```

## Ausführungsreihenfolge für Daniel

### 1. Sandbox bestätigen

- BC Admin Center öffnen.
- Environment Type muss `Sandbox` sein.
- Environment Name, BC-Version und Region dokumentieren.
- Test-Company `BCSentinel Pilot E2E` verwenden oder neu anlegen.
- Company System ID dokumentieren.
- Staging-Backend über `/health/ready` prüfen; Ergebnis muss HTTP 200 sein.
- Evidence: Environment-Übersicht, Company Information, Health-Ausgabe.

STOP bei Production, echten Kundendaten, ungültigem TLS oder Backend ungleich DEV/STAGING.

### 2. APP-Identität und Installation – PILOT-BC-002

- `.app` nur aus dem grünen BC-Compile-Artefakt des freigegebenen Staging-Commits verwenden.
- Commit SHA, App-Version, Dateiname und Größe dokumentieren.
- In `Extension Management` hochladen und installieren.
- Deployment Status auf Fehler prüfen.
- PASS: installiert, richtige Version, keine Dependency-/Permission-/Schemafehler.
- Evidence: Artefaktquelle, installierte Extension, Deployment Status.

### 3. Registrierung und Free Scan – PILOT-BC-003

- BCSentinel Setup öffnen.
- Staging-URL eintragen und `Test Connection` ausführen.
- Tenant/Environment/Company registrieren.
- Registrierung mit identischen Daten wiederholen; keine zweite Zuordnung darf entstehen.
- Free Data Health Score starten.
- Run ID, Start-/Endzeit, Statusfolge und Correlation ID dokumentieren.
- Free Dashboard, Findings-Zusammenfassung und Free Report öffnen.
- Nach mindestens 2 Minuten und neuem Login Access Snapshot aktualisieren.
- PASS: terminal `completed`, richtige Company, permanenter Free-Zugriff, keine bezahlten Rechte.

### 4. Assessment und Validation – PILOT-BC-004

- Assessment ausschließlich im Testpfad freischalten.
- License Snapshot in BC aktualisieren.
- Credit vor Start dokumentieren.
- Assessment-Scan starten und bis `completed` verfolgen.
- Credit nach Start dokumentieren; genau ein Credit muss verbraucht sein.
- Findings und Executive Report öffnen.
- Zweiten Start ohne Credit prüfen; kein Run darf entstehen.
- Validation Testrecht/Credit bereitstellen und Validation ausführen.
- PASS: keine Free-Downgrade-Logik, korrekter Creditverbrauch, Reports/Findings verfügbar.

### 5. Monitoring und Job Queue – PILOT-BC-005

- Monitoring im Testpfad aktivieren.
- `Refresh License` ausführen.
- Scheduled Scans aktivieren und Frequenz setzen.
- Job Queue Entry prüfen.
- kontrollierten Lauf ausführen oder Schedulerfenster abwarten.
- Run ID und Historie dokumentieren.
- einen kontrollierten Fehler provozieren, anschließend Retry/Recovery prüfen.
- PASS: genau eine Ausführung pro Fälligkeit, kein Creditverbrauch, Historie korrekt, Recovery ohne Duplikat.

### 6. Upgrade – PILOT-BC-006

- Vorherige installierbare Version und aktuelle Version bereithalten.
- Vor Upgrade Setup, Tenant-ID, Company-ID, History und Access-Kontext dokumentieren.
- neue Version hochladen und installieren.
- dieselben Werte nach Upgrade erneut prüfen.
- PASS: Installation erfolgreich, Konfiguration und Historie erhalten, keine erneute fremde Registrierung.

### 7. UAT – PILOT-UAT-001

Ein normaler Testanwender ohne Entwicklerhilfe führt aus:

- Setup-Seite finden
- Status verstehen
- Free Scan starten
- Ergebnis und Findings finden
- Report öffnen
- verständliche nächste Aktion benennen

Dokumentiere Beobachtungen und jede unklare Meldung. PASS nur, wenn keine P0/P1-Verständnishürde verbleibt.

## GitHub-Actions-Abschlussgate

Nach Commit des bereinigten Evidence-Pakets:

1. Actions öffnen.
2. Workflow `PILOT-E2E-01B BC Sandbox Evidence` wählen.
3. `Run workflow` wählen.
4. Evidence Path: `quality/pilot-e2e/sandbox_evidence.json`.
5. `require_all_pass` aktiviert lassen.
6. Run starten.
7. Artefakt `pilot-e2e-01b-sandbox-validation` sichern.

Ein fehlendes Gate, fehlende Evidence, Production-Nutzung oder unsicherer Pfad führt absichtlich zu FAIL.

## Abschlusskriterium

PILOT-E2E-01B ist erst `PASS`, wenn:

- alle sechs Gates PASS sind,
- der Evidence-Validator mit `--require-all-pass` erfolgreich ist,
- der GitHub-Actions-Abschlussgate grün ist,
- keine Secrets oder Kundendaten im Evidence-Paket enthalten sind.
