# Executive Reporting

## Zusammenfassung
JSON-, HTML-, Share-Link- und PDF-Ausgabe für Executive Reports.

## Erkannte Verantwortlichkeiten
KPI-/Findingaggregation, Lokalisierung, Zugriffsprüfung, Shared Tokens, Jinja-Rendering und Chromium-PDF.

## Erkannte Unterbereiche
`reports.py`, `executive_report_service.py`, Schema, Template, CSS, lokale Fonts/Bilder.

## Vorhandene Features
REP-DATA-001 als primäres Feature; REP-HTML-001, REP-PDF-001 und REP-SHARE-001 als Subfeatures.

## Teilweise vorhandene Features
Keine statisch erkennbare Teilimplementierung; Laufzeitdarstellung bleibt manuell.

## Stubs oder statische Inhalte
Beispiel-PDFs sind Artefakte, keine Stubs.

## APIs und Schnittstellen
Sechs `/executive/{scan_id}*`-Routen; Playwright Chromium.

## Datenmodelle
`ExecutiveReport` und Unterschemas; Scan/Issue/Entitlement.

## Tests
`test_executive_report.py`, Runtime-Packagingtests und Generatorskripte.

## Dokumentation
`docs/EXECUTIVE_REPORT_READINESS.md`, `docs/reports/`, `output/pdf/`.

## Technische Auffälligkeiten
PDF-Runtime wird im Docker-Build gestartet und geprüft; lokaler BOOK-Test konnte wegen fehlender Python-Testabhängigkeit nicht laufen.

## Manuell zu prüfen
Große Datenmengen, Seitenumbrüche, Fonts, reale Freigabe.

## Belegverzeichnis
Obige Dateien und `backend/Dockerfile`.
