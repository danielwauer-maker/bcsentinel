# Test-Inventur

## Bestand

27 Dateien unter `backend/tests/test_*.py` enthalten 224 `test_`-Funktionen. Abgedeckt sind API, Admin, Dashboard-Mitgliedschaften, Tenantregistrierung/-isolation, Security Header, Billing/Stripe-Mocks, Pricing, Entitlements, Reports/PDF-Vertrag, Scanstatus/Lifecycle/Recovery, Lokalisierung, Observability, Deployment-Readiness und optionale PostgreSQL-Konkurrenz.

## Unterscheidung

| Aussage | Befund |
|---|---|
| Testdatei vorhanden | Ja, 27 Python-Testdateien |
| Testfunktion vorhanden | Ja, 224 Funktionen |
| Feature zugeordnet | Ja, in `data/features.yaml` und `data/tests.yaml` |
| Erfolgs-/Fehlerfälle | Beide in mehreren Suites, z. B. `test_p0a_*`, `test_p0c_*`, `test_billing.py` |
| CI-Ausführung | Nicht nachgewiesen; `.github/workflows/deploy.yml` enthält nur Paketierung/Deployment/Healthchecks |
| Ausführung in BOOK-000C bestätigt | Nein |

Die normalisierten Suite- und Feature-Teststatus lauten ausschließlich `none`, `identified`, `partial`, `broad`, `manual_only` und `execution_unconfirmed`. Vorhandene, in diesem Sprint nicht ausgeführte Suites stehen auf `execution_unconfirmed`; fehlende Suites auf `none`.

## Ausführungsversuche

1. `python -m pytest -p no:cacheprovider tests` aus `backend/`: nicht gestartet, `python` nicht im PATH.
2. `C:\Users\Daniel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -p no:cacheprovider tests`: nicht gestartet, Modul `pytest` fehlt.

Es wurden gemäß Sprintregel keine Abhängigkeiten installiert. Die Suite selbst legt standardmäßig `backend/tests/.pytest.sqlite3` an; kein Testprozess erreichte diesen Schritt. PostgreSQL-Tests benötigen `BCSENTINEL_TEST_DATABASE_URL` und werden ohne diese Umgebung übersprungen.

## Nicht nachgewiesen

- Keine AL-Test-App oder AL-Testcodeunits unter `bc-extension/`.
- Keine eigenständige Browser-E2E-Suite für die Landingpage.
- Keine Last-/Performance-Suite.
- Keine CI-Teststufe.

Vollständige Zuordnung: [data/tests.yaml](data/tests.yaml).
