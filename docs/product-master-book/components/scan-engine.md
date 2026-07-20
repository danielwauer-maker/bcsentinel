# Scan Engine und Checks

## Zusammenfassung
Die Datenerhebung/Checks laufen primär in AL; das Backend verwaltet Startberechtigung, Lebenszyklus, Ergebnisse, Scores und Historie.

## Erkannte Verantwortlichkeiten
Quick Scan, Data Health Score/Deep Scan, Modulauswahl, Findings, Status/Heartbeat/Lease, Recovery und Abgleich.

## Erkannte Unterbereiche
`DHQuickScanMgt`, `DHDeepScanMgt`, `DHDeepScanRunner`, `DHScanCheckMgt`, `DHDataProfilingMgt`, `scans.py`, `scan_status_service.py`, `scoring_service.py`.

## Vorhandene Features
EXT-SCAN-001, EXT-SCAN-002, EXT-SCHED-001, SCAN-DEEP-001, SCAN-SYNC-001, SCAN-LIFE-001, SCAN-REC-001, SCAN-SCORE-001.

## Teilweise vorhandene Features
Keine statisch unvollständige Scan-Funktion; reale Laufzeit, Datenmenge und Scheduler-Ausführung bleiben manuell zu verifizieren.

## Stubs oder statische Inhalte
Keine eindeutigen Scan-Stubs gefunden.

## APIs und Schnittstellen
`/scan/quick`, `/scan/start`, `/scan/sync`, `/scan/reconcile`, Status-, History- und Trendrouten.

## Datenmodelle
Backend: `Scan`, `ScanIssueRecord`, `ScanRunStatus`, Module/Event; AL: Run/Finding/Header/Issue/Trend.

## Tests
`test_scans.py`, `test_scan_status.py`, `test_p0b_atomic_credit.py`, `test_p0c_scan_lifecycle.py`, optionale PostgreSQL-Konkurrenztests.

## Dokumentation
`docs/checks/`, `docs/scan-stability.md`, Lifecycle-Audits.

## Technische Auffälligkeiten
Backend erzwingt terminale Resultatpersistenz und Lease-Token; Retry behält denselben Run und verbraucht laut Testvertrag keinen zweiten Credit.

## Manuell zu prüfen
Große BC-Datenbestände, Laufzeit, Sperrverhalten und Scheduler.

## Belegverzeichnis
Obige Codeunits und `backend/app/routers/scans.py`.
