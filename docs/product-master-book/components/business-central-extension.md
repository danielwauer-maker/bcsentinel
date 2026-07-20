# Business-Central-Extension

## Zusammenfassung
AL-App `BCSentinel` 1.0.2.8 für Runtime/Platform 27; 88 Objektdeklarationen im Bereich 53100–53199.

## Erkannte Verantwortlichkeiten
Einrichtung/Registrierung, Datenprofiling, Quick-/Deep-Scan, lokale Historie/Findings, Scheduler, Dashboard-/Reportzugriff, Drilldowns und Berechtigungen.

## Erkannte Unterbereiche
11 Tables, 30 Pages, 6 Page Extensions, 27 Codeunits, 2 Queries, 6 Enums/Extensions, 5 Permission Sets und 1 Control Add-in; siehe [Objektliste](../evidence/business-central-objects.md).

## Vorhandene Features
EXT-REG-001, EXT-SCAN-001, EXT-SCAN-002, EXT-SCHED-001, EXT-DRILL-001, EXT-INSTALL-001, EXT-UPG-001.

## Teilweise vorhandene Features
EXT-LOC-001: XLF vorhanden; Vollständigkeit nur durch Skript/Runtime bewertbar.

## Stubs oder statische Inhalte
Keine AL-Objektstubs eindeutig nachgewiesen.

## APIs und Schnittstellen
`DHApiClient`, `DHApiUrlPolicy`, `DHTenantIdentityMgt`; HTTP zu Tenant-, License-, Scan-, Analytics- und Reportrouten; Control Add-in `AnalyticsFrameAddIn`.

## Datenmodelle
`DH Setup`, Scan Header/Issue/Trend, Deep Scan Run/Finding, Check Selection, Exceptions, Action Log und Duplicate Buffer.

## Tests
Python-Vertragstests lesen AL-Quelltext (`test_pilot_fix01_al_contract.py`); keine AL-Test-App gefunden.

## Dokumentation
`bc-extension/README.md`, `APP_SOURCE_READINESS.md`, `docs/BC_EXTENSION_*.md`.

## Technische Auffälligkeiten
API-Token wird über `DHSecretMgt` verwaltet; Access-Snapshots werden beim Upgrade invalidiert. Objekt-ID 53194 wird sowohl für Permission Set als auch Table genutzt, was in AL nach Objekttyp zulässig ist.

## Manuell zu prüfen
Sandbox-Installation, TaskScheduler, Rollen ohne SUPER, Upgrade und AppSource-Analyzerlauf.

## Belegverzeichnis
`bc-extension/app.json`; `bc-extension/app/src/`; `bc-extension/Translations/`.
