# Task 5 Follow-up - BC Critical Severity

Stand: 2026-06-16

Dieses Dokument ist ein Follow-up fuer einen separaten Task. Die Umsetzung ist ausdruecklich nicht Bestandteil von Task 5.

## Aktueller Zustand

- Business Central bzw. die aktuell gespeicherten Issue-Daten kennen fuer Findings/Issues faktisch `High`, `Medium`, `Low`.
- Backend-Schemas verwenden fuer `severity` derzeit generisch `str`, erzwingen aber keine vierstufige Severity-Enum.
- `backend/app/routers/analytics.py` normalisiert Issue-Severity aktuell nur auf `high`, `medium`, `low`; unbekannte Werte fallen auf `low` zurueck.
- Das Dashboard-CSS hat Issue-Severity-Klassen fuer `high`, `medium`, `low`.
- Analytics hat zwar in `free_insights.active_issues_summary` bereits einen `critical` Bucket, dieser wird aktuell durch die Normalisierung nicht sinnvoll befuellt.
- Der Executive Report fuehrt eine Sektion "Critical Findings", wertet dafuer aktuell aber `severity == "high"` als kritisch.

## Zielzustand

Business Central und Backend sollen fuer Findings/Issues die Severity-Stufen unterstuetzen:

1. Critical
2. High
3. Medium
4. Low

Das Dashboard soll Critical als eigene Severity in Filtern, KPIs, Badges, Tabellen, Actions und Reports darstellen koennen.

## Betroffene Bereiche

### BC Enum/Option Severity

- BC Severity Enum/Option um `Critical` erweitern.
- Bestehende High/Medium/Low-Werte migrations- und abwaertskompatibel behandeln.
- Pruefen, ob Sortierung/Priorisierung in BC-Seiten, Reports und Scan-Ergebnissen angepasst werden muss.

### Findings/Issues Tabellen

- Backend-Tabelle `scan_issues.severity` kann technisch Strings speichern, braucht aber fachliche Normalisierung/Validierung fuer `critical`.
- Pruefen, ob bestehende Daten migriert oder nur neue Werte akzeptiert werden.
- Sortierlogik muss Critical vor High einordnen.

### API Payloads

- BC -> Backend Payloads:
  - `ScanIssuePayload.severity`
  - Quick Scan / Deep Scan Sync
  - ggf. BC-spezifische DTOs ausserhalb des Python-Backends
- Backend -> Dashboard Payloads:
  - `top_findings[].severity`
  - `issues_page.items[].severity`
  - `actions_page.items[].priority`
  - `free_insights.active_issues_summary`
- Report Payloads:
  - `ReportFinding.severity`
  - Executive Report `critical_findings`

### Dashboard Filter/KPI

- Severity-Badges und CSS fuer `critical` hinzufuegen.
- Severity-Ziel: Critical, High, Medium, Low.
- Filter/KPI fuer Critical Counts vorbereiten.
- Issue Distribution darf Critical nicht als Low normalisieren.

### Reports

- Executive Report sollte echte Critical Findings aus `severity == "critical"` ableiten.
- High Findings sollten weiterhin separat priorisierbar bleiben.
- Report CSS braucht `.severity-critical`.
- Texte wie "No high-severity findings" muessen fachlich ueberarbeitet werden, wenn Critical eingefuehrt ist.

### Tests

- Unit-/API-Tests fuer Severity-Normalisierung: critical, high, medium, low, unbekannt.
- Dashboard-Payload-Tests fuer Critical Count, Sorting und Labels.
- Report-Tests fuer echte Critical Findings.
- BC-seitige Tests fuer Enum/Option, Payload und UI-Anzeige.
- Regressionstests fuer bestehende High/Medium/Low-Daten.

## Nicht Bestandteil von Task 5

Diese Aenderung soll nicht in Task 5 umgesetzt werden. Task 5 Phase 1 dokumentiert nur den Gap; spaetere Task-5-Phasen sollten keine BC-Severity-Enum oder Backend-Severity-Semantik aendern.

## Vorschlag

Als separaten Task 6 umsetzen:

**Task 6 - Critical Severity End-to-End**

Ziel: Business Central, Backend, Dashboard und Reports unterstuetzen Critical, High, Medium, Low konsistent inklusive Datenvertrag, Sortierung, Gating-neutraler Anzeige und Tests.
