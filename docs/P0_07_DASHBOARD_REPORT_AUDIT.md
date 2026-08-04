# P0-07 Dashboard und Executive Report Audit

**Stand:** 2026-08-05  
**Produktstand:** BCSentinel 1.0.2.20  
**Gate:** Produktoberflächen / Sprint P0-07

## 1. Ziel

P0-07 schützt die zentralen Kundenoberflächen Dashboard und Executive Report gegen Regressionen. Der CI-Nachweis konzentriert sich auf verfügbare Routen, Mandantenbindung, Session-Sicherheit, Report-Freigaben und die unterstützten Ausgabeformate JSON, HTML und PDF.

## 2. Umgesetzte Komponenten

| Komponente | Pfad | Zweck |
| --- | --- | --- |
| Contract- und Security-Tests | `backend/tests/test_p0_07_dashboard_report_contract.py` | prüft Dashboard- und Report-Routen sowie zentrale Sicherheitsverträge |
| GitHub-Gate | `.github/workflows/p0-07-dashboard-report-contract.yml` | führt die Tests aus und publiziert Evidenz |
| Evidenzartefakt | `build/p0-07/` | JUnit, Pytest-Log und Markdown-Zusammenfassung |

## 3. Dashboard-Prüfungen

Der Test deckt mindestens folgende Verträge ab:

- Dashboard-Portal und Einladungsseite vorhanden,
- Einladung aktivierbar,
- Login und Logout vorhanden,
- Tenantliste vorhanden,
- Tenantdetail vorhanden,
- Tenantwechsel vorhanden,
- Analytics-Token nur über eine Dashboard-Session,
- Session enthält Benutzer-, Membership-, Rollen- und aktive Tenant-ID,
- Session-Cookie ist `HttpOnly`, in Produktion `Secure` und `SameSite=Strict`,
- Dashboard-Template ist vorhanden und enthält Login-/Kennwortfunktionen.

## 4. Executive-Report-Prüfungen

Der Test deckt mindestens folgende Verträge ab:

- Executive Report als strukturiertes JSON,
- HTML-Report,
- PDF-Report,
- zeitlich begrenzter Share-Link,
- geteilte HTML- und PDF-Ansicht,
- Share-Token ist an Tenant, Company, Scan-ID, Reporttyp und Report-Capability gebunden,
- falsche Scan-ID oder falscher Reporttyp wird mit HTTP 403 abgelehnt,
- PDF-Antwort verwendet `application/pdf`,
- Dateiname folgt dem stabilen BCSentinel-Reportvertrag,
- Reportzugriff bleibt an `CAPABILITY_REPORT` gebunden.

## 5. Akzeptanzkriterien

| ID | Kriterium | Status |
| --- | --- | --- |
| 07.1 | Dashboard-Kernrouten vollständig vorhanden | PASS |
| 07.2 | Dashboard-Session an Benutzer, Membership und Tenant gebunden | PASS |
| 07.3 | Cookie-Härtung und Dashboard-Template geprüft | PASS |
| 07.4 | JSON-, HTML- und PDF-Reportverträge vorhanden | PASS |
| 07.5 | Share-Token gegen Scan-/Typwechsel geschützt | PASS |
| 07.6 | Report-Capability und PDF-Antwortvertrag geprüft | PASS |
| 07.7 | JUnit-, Log- und Markdown-Evidenz erzeugt | PASS |

## 6. CI-Evidenz

- Workflow: `P0-07 Dashboard Report Contract`
- Run: `#2`
- Run-ID: `30958804497`
- Ergebnis: `success`
- Head-SHA: `a3cf83be8a047e20f8e409513acc61f0cda3445e`
- Evidenzartefakt: `p0-07-dashboard-report-evidence`
- Artefakt-ID: `8912114323`
- Digest: `sha256:61a3fd868d2248403e9b19d3e5e2a69f1f0d65a89cb823cb982a6163191ce94e`
- Aufbewahrung bis: `2026-09-03`

Zusätzlich erfolgreich auf demselben Head:

- `PILOT-E2E-01A Automated Readiness #59`
- `P0-04 PostgreSQL Migration Cycle #20`
- `P0-05 PostgreSQL Backup Restore #15`
- `P0-06 Operator Alerting #8`

## 7. Auditstatus

**Aktueller Status:** `VERIFIED_IN_CI / PASS`

Die technischen Dashboard- und Reportverträge sind auf dem aktuellen PR-Head erfolgreich geprüft. Der automatisierte Mindestnachweis für Routen, Session-/Tenant-Bindung, Cookie-Härtung, Reportformate und Share-Token-Schutz ist damit geschlossen.

## 8. Grenzen des automatisierten Nachweises

Der Contract-Test ersetzt keine vollständige visuelle und fachliche Abnahme. Zusätzlich offen bleiben:

- visuelle Prüfung auf Desktop, Tablet und Mobilgerät,
- echte Login-/Einladungsjourney mit produktivem SMTP,
- reale Darstellung eines leeren Tenants, eines normalen Tenants und eines Tenants mit vielen Findings,
- visuelle Prüfung langer Firmennamen, großer Geldbeträge und mehrseitiger Reports,
- Vergleich von HTML- und PDF-Inhalt mit echten Pilotdaten,
- manuelle Prüfung aller Links und Browser-Konsolenfehler.

## 9. Bewertung

Die Repository- und CI-Seite von P0-07 ist abgeschlossen. Die reale visuelle Pilotabnahme bleibt ein separates gemeinsames Gate.
