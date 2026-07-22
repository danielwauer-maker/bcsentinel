# GL-01C DH Exceptions v1 Implementation

**Stand:** 22. Juli 2026  
**Entscheidung:** lokales GO; Pilot-/Produktionsfreigabe bleibt bis zur BC-Sandbox-Evidenz gesperrt

## Discovery und Ursache der fehlenden Sichtbarkeit

Vor GL-01C bestanden bereits Tabellen 53150/53151, Codeunit 53152, Page 53153, zwei FactBoxes, sechs Card/List Extensions und Exception-Aktionen in Findings-Listen. Der Deep Scan verwendete 44 direkte Customer-/Vendor-/Item-Exclusion-Aufrufe. Aktive Treffer wurden bereits vor Finding- und Penalty-Aggregation übersprungen.

Das Modul wirkte verschwunden, weil im Setup kein zentraler Einstieg vorhanden war, nur ADMIN die Page ausführen durfte und `BCSENTINEL SCAN` auf Exception-TableData nur R hatte. Zusätzlich war die Deaktivierungsaktion als „Reactivate Check“ beschriftet. Git-Historie enthält keine gelöschte parallele Implementierung.

## Änderungen und Datenfluss

- Bestehende Exception-Page wurde als schreibgeschützte zentrale Liste mit Create/Activate/Deactivate/Open Record/History und Views weitergeführt.
- Ein StandardDialog zeigt Record, Issue Code, Pflichtgrund und Scorewirkung. Findings-Aktionen verwenden denselben Dialog.
- Codeunit 53152 erzwingt Pflichtgrund, verhindert aktive Dubletten, reaktiviert bestehende Zeilen ohne Created-Metadaten zu überschreiben und schreibt EXCLUDED/INCLUDED append-artig.
- Der Deep Scan setzt vor jedem Lauf einen Counter zurück. `IsIssueExcluded` registriert die Entry No. nur beim tatsächlichen aktiven Treffer und höchstens einmal pro Scan.
- `DH Deep Scan Run` und `DH Scan Header` erhalten additiv `Applied Exception Count`. Der AL-Sync sendet `applied_exception_count`.
- Backend-Sync akzeptiert das Feld mit Default 0, persistiert es auf `Scan`, und der Executive Report übernimmt es. Das Template zeigt nur bei Count > 0 einen kompakten DE-/EN-Hinweis.

## Migration und Kompatibilität

BC-Schlüssel und bestehende Exception-Felder bleiben unverändert; kein Datensatz wird gelöscht oder umgeschlüsselt. Die zwei Scan-Count-Felder sind additiv. Backend-Revision `0028_exception_count` ergänzt eine nicht-nullbare Integer-Spalte mit Server-Default 0; ältere Payloads bleiben gültig. Downgrade entfernt nur diese neue Spalte.

## Geänderte Bereiche

- `bc-extension/app/src/tables`: Exception-Validierung und additive Count-Felder
- `bc-extension/app/src/codeunits`: Lifecycle, Applied-Tracking, konsistente recordbezogene Checks und Payload
- `bc-extension/app/src/pages`, `pageextensions`, `permissionsets`: zentrale UX, Dialog, History, Setup-Einstieg und Least Privilege
- `backend/app`: Scanmodell/-sync, Reportschema/-service, HTML/CSS
- `backend/alembic/versions/0028_applied_exception_count.py`
- Backend- und statische AL-Contract-Tests sowie GL-01B/C-/Kundendokumentation

## Testergebnisse

- AL-Compile mit CodeCop und PTECop: erfolgreich, keine Compilerfehler.
- Statischer GL-01C-AL-Contract-Test: 7/7 Verträge erfolgreich.
- Deutsche XLIFF-Vollständigkeitsprüfung: erfolgreich.
- Backend-Gesamtsuite in isolierten SQLite-Batches: 350 erfolgreich, 7 PostgreSQL-spezifische Tests übersprungen, 89 bestehende Deprecation-Warnungen.
- Alembic-Evidenz: Upgrade bis Head, Downgrade auf `0027_check_catalog` und erneutes Upgrade bis Head erfolgreich.
- PDF-Smoke mit echtem Chromium: zwei A4-Seiten, Ausnahmehinweis bei Count 4 sichtbar, kein Seiten- oder KPI-Overflow; beide Seiten visuell geprüft.
- AppSourceCop: erwartete bestehende Manifest-/ID-Range-Baselinefehler (fehlende EULA/Logo/ContextSensitiveHelpUrl und AppSource-ungeeigneter Objektbereich 53100..53199); kein durch GL-01C eingeführter AL-Compilefehler.

Das Repository besitzt keine AL-Test-App. Deshalb ersetzen AL-Compile und Source-Contract-Test keine echte BC-Sandbox-CAT-Matrix.

## Bekannte Restpunkte

Offen bis zur Pilotfreigabe: echte BC-Sandbox-CAT für Lifecycle, Cross-Company und Permission Sets ohne SUPER sowie Installation/Upgrade einer vorhandenen App mit Legacy-Daten. Diese Evidenz darf nicht durch statische Tests ersetzt werden.

## Go/No-Go

**Lokales GO** für Code, Migration, Backend und Bericht. **Noch kein Pilot-/Produktions-GO**, weil BC-Sandbox-CAT, reale Least-Privilege-Prüfung, Companywechsel und Legacy-App-Upgrade in dieser Umgebung nicht ausführbar waren.
