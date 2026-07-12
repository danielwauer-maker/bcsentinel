# REPORT-01G – Final Executive Visual Design

## Ziel

REPORT-01G finalisiert den kostenlosen Executive Report als hochwertigen, deutschsprachigen Enterprise Executive Brief. HTML und Chromium-PDF verwenden dieselbe dynamische HTML/CSS/SVG-Quelle und bleiben exakt zweitseitig im Format DIN A4 Hochformat.

## Ausgangsprobleme

- Der Score-Hero war vertikal überdimensioniert und visuell nicht eng genug an der Referenz.
- KPI-Karten waren in der schmalen rechten Spalte verschachtelt; dadurch konnten Geldbeträge einschließlich `EUR` abgeschnitten werden.
- Statusklassen lagen global am `body` und konnten unbeabsichtigt andere Bereiche beeinflussen.
- Modulnamen wurden im deutschen visuellen Report teilweise englisch dargestellt.
- Seite 2 wirkte durch ihre frühere Spaltenstruktur eher wie eine Landingpage.
- Diagramme, Icongewichtung, Schatten und Footer benötigten den finalen visuellen Feinschliff.

## Geänderte Dateien

- `backend/app/templates/executive_report.html`
- `backend/app/static/reports/executive-free-report.css`
- `backend/app/services/executive_report_service.py`
- `backend/tests/test_executive_report.py`
- `backend/scripts/generate_report01g_sample.py`
- `CHANGELOG.md`
- `docs/reports/REPORT-01F_KPI_KARTEN_FINAL.md`

## Seite 1

- Ausbalancierter Header mit finalem lokalen BCSentinel-Logo, Reporttitel, Untertitel und UTC-Zeitstempel.
- Horizontaler Score-Hero mit größerem Inline-SVG-Ring, Status-Badge, Handlungsempfehlung, Risikotext und dezenter Wellenform.
- Management-Zusammenfassung als klar gegliederte Executive Message mit drei semantischen Inline-SVG-Icons.
- Vier gleich große KPI-Karten über die volle Reportbreite.
- Kräftigere Balken, feinere Rasterlinien und zentral lokalisierte Bereichsnamen.
- Größerer Inline-SVG-Donut mit Anzahl, `Probleme` und `Gesamt` im Zentrum sowie deutscher Legende.
- Produktsignatur und Seitennummer `01` im Footer.

## Seite 2

- Horizontale, gleichwertige Empfehlungskarten für vollständige Analyse und Monitoring.
- Fachlich getrennte Leistungslisten und eindeutige rote beziehungsweise blaue CTA-Flächen.
- Vier kompakte Nutzenbereiche in einer horizontalen Reportstruktur.
- Nur vorhandene Berichtsinformationen werden ausgegeben.
- Vollständiger rechtlicher Hinweis, BCSentinel-Signatur und Seitennummer `02`.

## Hero-Statuslogik

Die bestehenden, bereits in REPORT-01C dokumentierten visuellen Schwellenwerte bleiben unverändert:

- Score unter 60: `hero-critical`, Rot
- Score 60 bis 84: `hero-warning`, Orange
- Score ab 85: `hero-good`, Grün

Die dynamische Klasse befindet sich ausschließlich am Hero. KPI-Karten, Diagramme, Seite 2 und Footer behalten ihre stabilen Markenfarben.

## KPI- und Währungsdarstellung

Die Reihenfolge aus REPORT-01F bleibt unverändert: finanzielle Auswirkung, potenzielle Einsparung, betroffene Datensätze und Prüfungen. Geldwerte verwenden eine eigene `kpi-value-money`-Klasse mit `white-space: nowrap`, tabellarischen Ziffern und einer kontrollierten kleineren Schrift für lange Werte. Der Browser-QA-Test bestätigt auch für `1.250.480,75 EUR` und `125.480,75 EUR`, dass `scrollWidth <= clientWidth` gilt.

## Modul-Lokalisierung

`module_label()` lokalisiert Module zentral im Service beziehungsweise HTML-Presenter. Unterstützt werden Groß-/Kleinschreibung, Bindestriche, Unterstriche und technische Varianten. Die Kernzuordnung lautet:

- Inventory → Lager
- Purchasing → Einkauf
- Manufacturing → Produktion
- Finance → Finanzen
- Sales → Vertrieb

Unbekannte Werte werden in eine lesbare Titel-Schreibweise überführt; leere Werte werden als `Bereich` dargestellt.

## Icon-System, Typografie und Tiefe

Alle funktionalen Icons sind lokale Inline-SVGs mit gemeinsamer `24 × 24`-ViewBox, konsistenter Strichstärke sowie runden Linienenden und Verbindungen. Es gibt keine externen Fonts, Icon-CDNs oder Bibliotheken. Die lokal eingebundene Inter-Schrift, feinere Gewichte für Zwischenüberschriften, tabellarische Ziffern, dezente Rahmen und zweistufige Premium-Schatten bilden die gemeinsame visuelle Sprache.

## PDF-Runtime

Die gehärtete Playwright-/Chromium-Pipeline bleibt unverändert: `document.fonts.ready`, A4, `print_background=True`, `prefer_css_page_size=True` und Nullränder. Der Emergency-Fallback bleibt ausschließlich für echte Renderer-Ausfälle erhalten.

## Tests und visuelle Iterationen

Die Regressionstests decken HTML/PDF-Endpunkte, Statusklassen, deutsche Modulnamen, korrekte Schreibweise, große Geldwerte, leere Findings, Angebotsabgrenzung, lokalen Font-/Iconbetrieb und Metadaten ab.

Es wurden drei Chromium-Iterationen durchgeführt:

1. Grundproportionen, Header, Hero, Management Summary und erste KPI-Anordnung.
2. Vollbreite KPI-Reihe, EUR-Overflow-Fix, Balken, Donut, Typografie und Footer.
3. Seite 2, Edge Cases, exakte PDF-Seitenzahl und finaler Overflow-/Pixel-Check.

Das finale PDF enthält exakt zwei Seiten. Beide `.report-page`-Elemente messen im Chromium-Test `794 × 1123` CSS-Pixel ohne horizontalen oder vertikalen Scroll-Overflow.

## Artefakte

- `output/pdf/bcsentinel-report-01g-sample.html`
- `output/pdf/bcsentinel-report-01g-sample.pdf`
- `output/pdf/bcsentinel-report-01g-page-1.png`
- `output/pdf/bcsentinel-report-01g-page-2.png`

## Bekannte Restriktionen

- Die visuelle Abnahme nutzt den im Repository verfügbaren Chromium-Build; minimale Unterschiede zwischen Betriebssystem-Rasterizierungen sind möglich.
- Sehr lange unbekannte Modul- oder Firmennamen werden kontrolliert umbrochen beziehungsweise in den kompakten Metadatenbereich eingepasst.
