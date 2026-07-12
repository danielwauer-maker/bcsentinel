# REPORT-01F - Finale KPI-Karten

## Ziel

Letzte Go-Live-Anpassung der vier KPI-Karten unter der Management-Zusammenfassung. Alle anderen Reportbereiche bleiben unverändert.

## Änderungen

- Die KPI-Karte `Datenqualitäts-Score` wurde entfernt.
- Die Anzahl der KPI-Karten bleibt vier.
- Neue Reihenfolge:
  1. Finanzielle Auswirkung
  2. Potenzielle Einsparung
  3. Betroffene Datensätze
  4. Prüfungen durchgeführt
- Finanzielle Auswirkung verwendet die kritische Rotfarbe.
- Potenzielle Einsparung verwendet die Erfolgs-Grünfarbe.
- Betroffene Datensätze und Prüfungen durchgeführt verwenden Blau.

## Karteninhalte

- Finanzielle Auswirkung: dynamischer `estimated_loss_eur`, Status `JÄHRLICH`.
- Potenzielle Einsparung: dynamischer `potential_saving_eur`, Status `POTENZIAL`.
- Betroffene Datensätze: dynamischer `affected_records`, Status `GESAMT`.
- Prüfungen durchgeführt: dynamischer `checks_count`, Status `DURCHGEFÜHRT`.

Währungswerte behalten ausreichend Innenabstand und werden mit der zentralen deutschen EUR-Formatierung ausgegeben.

## Tests

Die Reporttests prüfen die neue Reihenfolge, das Fehlen der Score-Kachel, den neuen Einsparungswert, HTML/PDF-Endpunkte und die bestehende Zwei-Seiten-Garantie.

## Artefakte

- `output/pdf/bcsentinel-report-01f-sample.html`
- `output/pdf/bcsentinel-report-01f-sample.pdf`
- `output/pdf/bcsentinel-report-01f-page-1.png`
- `output/pdf/bcsentinel-report-01f-page-2.png`
