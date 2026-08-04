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

| ID | Kriterium | Status vor Workflowlauf |
| --- | --- | --- |
| 07.1 | Dashboard-Kernrouten vollständig vorhanden | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 07.2 | Dashboard-Session an Benutzer, Membership und Tenant gebunden | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 07.3 | Cookie-Härtung und Dashboard-Template geprüft | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 07.4 | JSON-, HTML- und PDF-Reportverträge vorhanden | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 07.5 | Share-Token gegen Scan-/Typwechsel geschützt | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 07.6 | Report-Capability und PDF-Antwortvertrag geprüft | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 07.7 | JUnit-, Log- und Markdown-Evidenz erzeugt | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |

## 6. Auditstatus

**Aktueller Status:** `IMPLEMENTED_NOT_YET_CI_VERIFIED`

Nach grünem Workflow kann die technische Vertrags- und Sicherheitsprüfung auf `VERIFIED_IN_CI / PASS` gesetzt werden.

## 7. Grenzen des automatisierten Nachweises

Der Contract-Test ersetzt keine vollständige visuelle und fachliche Abnahme. Zusätzlich offen bleiben:

- visuelle Prüfung auf Desktop, Tablet und Mobilgerät,
- echte Login-/Einladungsjourney mit produktivem SMTP,
- reale Darstellung eines leeren Tenants, eines normalen Tenants und eines Tenants mit vielen Findings,
- visuelle Prüfung langer Firmennamen, großer Geldbeträge und mehrseitiger Reports,
- Vergleich von HTML- und PDF-Inhalt mit echten Pilotdaten,
- manuelle Prüfung aller Links und Browser-Konsolenfehler.

## 8. Bewertung

P0-07 schließt die bisher fehlende automatisierte Mindestabsicherung für Dashboard- und Reportverträge. Bei grünem CI-Lauf steigt die technische Nachweisqualität beider Produktkomponenten deutlich; die reale visuelle Pilotabnahme bleibt ein separates gemeinsames Gate.
