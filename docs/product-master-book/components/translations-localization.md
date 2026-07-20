# Übersetzungen und Lokalisierung

## Zusammenfassung
Deutsch/Englisch in Website und Dashboard sowie deutsche XLF für AL.

## Erkannte Verantwortlichkeiten
Sprachwahl/-persistenz, Site-/Dashboardtexte, Issue-Texte, Reportlabels und AL-Captions.

## Erkannte Unterbereiche
JSON-Sprachdateien, Translation-Services, XLF und Prüfskripte.

## Vorhandene Features
TRANS-SITE-001, TRANS-DASH-001, TRANS-ISSUE-001.

## Teilweise vorhandene Features
EXT-LOC-001: vollständige XLF-Abdeckung ist ein separater Prüfschritt.

## Stubs oder statische Inhalte
Keine Sprachdatei als Stub; Fallbacktexte im JS/Python vorhanden.

## APIs und Schnittstellen
Admin-Translationsrouten, öffentliche Site-Dateien, Tenant `preferred_language`.

## Datenmodelle
Tenant-Sprachfeld; Siteübersetzungen dateibasiert, Dashboardkatalog service-/JSON-basiert.

## Tests
`test_localization.py`, `test_issue_text_localization.py`, Pricing/Report-Lokalisierung; `scripts/check_al_localization.py`.

## Dokumentation
`docs/localization-check.md`, `BC_EXTENSION_LOCALIZATION_GAPS.md`.

## Technische Auffälligkeiten
Dashboardtexte existieren sowohl in JSON als auch im Python-Service/JS-Fallback.

## Manuell zu prüfen
Laufzeitvollständigkeit, Textqualität und Sonderzeichen in allen Oberflächen.

## Belegverzeichnis
`landingpage*/lang/`; `backend/app/translations/`; `bc-extension/Translations/`.
