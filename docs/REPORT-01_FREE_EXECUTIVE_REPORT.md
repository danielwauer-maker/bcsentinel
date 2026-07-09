# REPORT-01 Free Executive Report

## Scope

Der Executive Free Report wurde als eigenstaendiges 3-seitiges DIN-A4-Hochformat-Layout umgesetzt. Die Aenderung betrifft nur den bestehenden Executive-Report-HTML-Endpunkt und die dafuer benoetigte Free-Report-Datenaufbereitung.

Nicht Bestandteil dieser Aenderung:

- Full-Report-Detailtabellen
- Monitoring-Report-Logik
- Business-Central-Extension-Seiten
- Dashboard- oder Landingpage-Layouts

## Layout

Das Template `backend/app/templates/executive_report.html` rendert exakt drei `.report-page`-Abschnitte:

1. Executive Overview mit Brand, Titel, Score, Management-Zusammenfassung, vier KPI-Kacheln und genau einem Upgrade-CTA.
2. Data Quality Overview mit Modul-Balkendiagramm, Severity-Donut und Free-Report-Hinweisbox.
3. Next Steps mit Upgrade-Pfad, Monitoring-Nutzen, CTA und Report Information.

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

## PDF-Hinweis

Das HTML/CSS ist fuer Chromium- bzw. Playwright-Rendering vorbereitet. Der bestehende `/pdf`-Endpunkt erzeugt weiterhin einen einfachen Text-PDF-Export, damit die bestehende API-Kompatibilitaet erhalten bleibt. Dieser Fallback enthaelt ebenfalls nur die Free-Report-Management-Zusammenfassung und keine Detail-Findings. Ein spaeterer Wechsel auf Playwright kann das neue HTML direkt als Renderquelle verwenden.
