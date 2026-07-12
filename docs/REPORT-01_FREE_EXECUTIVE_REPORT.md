# REPORT-01 Free Executive Report

## Scope

Der Executive Free Report wurde als eigenstaendiges 2-seitiges DIN-A4-Hochformat-Layout umgesetzt. Die Aenderung betrifft nur den bestehenden Executive-Report-HTML/PDF-Endpunkt und die dafuer benoetigte Free-Report-Datenaufbereitung.

Nicht Bestandteil dieser Aenderung:

- Full-Report-Detailtabellen
- Monitoring-Report-Logik
- Business-Central-Extension-Seiten
- Dashboard- oder Landingpage-Layouts

## Layout

Das Template `backend/app/templates/executive_report.html` rendert exakt zwei `.report-page`-Abschnitte:

1. Data Health Ueberblick mit Brand, kompakter Free-Report-Hinweisbox, Score, Management-Zusammenfassung, vier KPI-Kacheln, Modul-Balkendiagramm und Severity-Donut.
2. Next Steps & Report Information mit Upgrade-Pfad, Monitoring-Nutzen, CTA-Karte und Report Information.

Die Druck- und PDF-Basis liegt in `backend/app/static/reports/executive-free-report.css`:

- `@page { size: A4 portrait; margin: 0; }`
- feste A4-Seitenbreite von `210mm`
- Seitenumbrueche ueber `.report-page`
- print-safe Farben via `print-color-adjust`

## Daten

Der Free Report nutzt vorhandene Scan-, Tenant- und Finding-Daten. Fuer eine stabile Free-Report-Demoansicht werden nur dort robuste Fallbacks genutzt, wo der aktuelle Payload keine sinnvolle Datenbasis liefert:

- Modul-Scores: feste Executive-Reihenfolge Inventory, Finance, Purchasing, Sales, Manufacturing, CRM, System; fehlende oder leere Werte erhalten Free-Report-Fallbackwerte.
- Severity-Verteilung: echte Findings werden gezaehlt; nur wenn gar keine Findings vorhanden sind, werden Demo-Verteilungswerte genutzt.
- Checks Total: mindestens `165`, andernfalls vorhandene `checks_count`-Werte.
- Betroffene Datensaetze: Summe der betroffenen Findings; bei leerer Anzeige nutzt das Template einen konservativen Demo-Fallback.

## Entfernte Free-Report-Inhalte

Folgende Detailbereiche werden im Free-HTML nicht mehr angezeigt:

- Top 10 Risks
- Quick Wins
- Critical Findings
- Data Quality Finding-Tabellen
- Financial Risks
- Priority Matrix

## Business-Central-Integration

Die bestehenden Aktionen im Scan-Monitor `DH Deep Scan Monitor` verwenden weiterhin den Share-Link-Endpunkt:

- `Executive Report` -> `/reports/executive/{scan_id}/share-link` mit `report_type = html`
- `Executive PDF` -> `/reports/executive/{scan_id}/share-link` mit `report_type = pdf`

Der Share-Link-Endpunkt und die HTML/PDF-Renderpfade liefern jetzt den Free Executive Report und benoetigen fuer den eigenen Scan keinen aktiven Full-Analysis-, Validation- oder Monitoring-Zugriff. Die JSON-Detailroute `/reports/executive/{scan_id}` bleibt weiterhin hinter der bisherigen Report-Berechtigung, damit Detaildaten nicht ueber den Free-Report freigegeben werden.

## PDF-Verhalten

Der `/pdf`-Endpunkt nutzt denselben Report-Inhalt wie der HTML-Endpunkt. `render_executive_report_pdf()` rendert `executive_report.html` mit inline eingebettetem `executive-free-report.css` und erzeugt daraus per Playwright/Chromium ein A4-PDF:

- Format: A4
- CSS-Seitengroesse bevorzugt
- `print_background=True`
- Rand: `0`

`playwright` ist in `backend/requirements.txt` fest gepinnt. Das Backend-Dockerfile installiert Chromium und seine Linux-Abhaengigkeiten dauerhaft mit `python -m playwright install --with-deps chromium` in `/ms-playwright`; manuelle Installationen im laufenden Container sind nicht erforderlich. Details und Smoke-Test: `docs/reports/REPORT-RUNTIME-01_PLAYWRIGHT_CHROMIUM.md`.

Wenn Playwright oder Chromium zur Laufzeit nicht verfuegbar ist, greift ein Notfall-Fallback. Dieser Fallback ist bewusst auf Free-Scope begrenzt, enthaelt keine Top-10-Findings, keine Quick Wins, keine Finding-Tabellen und keine konkreten Detail-Empfehlungen. Er ist nur eine technische Ausfallsicherung, nicht der Zielpfad.

## Spaetere Erweiterung

Full Analysis und Monitoring koennen spaeter eigene Templates oder zusaetzliche Detailseiten erhalten. Der Free Report zeigt absichtlich nur aggregierte Management-Kennzahlen, Modul-Scores, Severity-Verteilung, Next Steps, Upgrade-Hinweise und Report Information.
