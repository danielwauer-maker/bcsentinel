# Testing und Quality

## Zusammenfassung
224 Pytest-Funktionen; statische AL-/Pricing-/Localization-Skripte; keine bestätigte Ausführung in BOOK-000C.

## Erkannte Verantwortlichkeiten
Unit-/API-/Integrationsverträge, Security, Billing, Scanstatus, Report, Migration, Deployment und PostgreSQL-Konkurrenz.

## Erkannte Unterbereiche
`backend/tests/`, `scripts/check_*.py`, AL-Quellprüfungsskript, Releasechecklisten.

## Vorhandene Features
TEST-PY-001, TEST-PG-001.

## Teilweise vorhandene Features
Keine Teilimplementierung: `TEST-CI-001` hat Status `not_found`, weil der vorhandene Workflow keinen Testjob enthält.

## Stubs oder statische Inhalte
TEST-AL-001: Status `not_found`, keine AL-Test-App.

## APIs und Schnittstellen
Pytest/FastAPI TestClient, SQLite; optional PostgreSQL über `BCSENTINEL_TEST_DATABASE_URL`.

## Datenmodelle
Autouse-Fixture erstellt/dropt ORM-Schema; Testfixtures für Migrationen.

## Tests
Details in [05-test-inventory.md](../05-test-inventory.md) und [tests.yaml](../data/tests.yaml).

## Dokumentation
`backend/TESTING.md`, Smoke-/E2E-Matrizen und Releasechecklisten.

## Technische Auffälligkeiten
Lokale Runtime hatte kein `pytest`; Abhängigkeiten wurden nicht installiert. Testexistenz ist daher kein Ausführungsnachweis.

## Manuell zu prüfen
Vollständige Suite in vorgesehenem Docker-Testtarget, PostgreSQL-Suite, AL-Test-App und CI-Integration.

## Belegverzeichnis
`backend/tests/`; `backend/Dockerfile`; `.github/workflows/deploy.yml`.
