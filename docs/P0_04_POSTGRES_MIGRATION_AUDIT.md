# P0-04 PostgreSQL Migration Upgrade/Downgrade/Upgrade Audit

**Stand:** 2026-08-05  
**Produktstand:** BCSentinel 1.0.2.20  
**Branch:** `docs/go-live-readiness-1.0.2.20`  
**Gate:** G5 Datenbank / Sprint P0-04

## 1. Ziel

P0-04 weist nach, dass der aktuelle Alembic-Stand auf einer echten PostgreSQL-Datenbank reproduzierbar erreicht, auf den direkten Vorgänger zurückgesetzt und anschließend ohne Schema-Drift wieder auf `head` aktualisiert werden kann. Zusätzlich muss ein vorhandener Testdatensatz den Zyklus überstehen und der bestehende PostgreSQL-Konkurrenz-/Transaktionsnachweis weiterhin erfolgreich sein.

## 2. Umgesetzte Repository-Komponenten

| Komponente | Pfad | Zweck |
| --- | --- | --- |
| Migration-Cycle-Verifier | `backend/scripts/verify_postgres_migration_cycle.py` | Upgrade → Downgrade → Upgrade, Revisionsprüfung, Schema-Fingerprint und Datenerhalt |
| GitHub-Gate | `.github/workflows/p0-04-postgres-migration-cycle.yml` | echter PostgreSQL-16-Lauf bei PR, Push nach `staging` und manuellem Dispatch |
| Contract-Test | `backend/tests/test_p0_04_migration_cycle_contract.py` | verhindert Entfernung der Sicherheits-, Drift- und Evidenzprüfungen |
| Evidenzartefakt | `build/p0-04/migration-cycle.json` und `.md` | maschinen- und menschenlesbarer PASS/FAIL-Nachweis |

## 3. Sicherheitsmaßnahmen

Der Verifier verweigert die Ausführung, wenn:

- keine PostgreSQL-URL verwendet wird,
- die Zieldatenbank nicht klar als Test-/Migration-Datenbank erkennbar ist,
- mehr als ein Alembic-Head vorhanden ist,
- der aktuelle Head keinen direkten Downgrade-Punkt besitzt,
- der Head eine Merge-Revision mit mehrdeutigem Rücksprung ist.

Der CI-Workflow verwendet ausschließlich die temporäre Datenbank `bcsentinel_p0_04_test`. Produktivdaten und produktive Datenbanken sind nicht Bestandteil des Tests.

## 4. Automatischer Prüfablauf

1. Temporären PostgreSQL-16-Service starten.
2. Backend-Abhängigkeiten installieren.
3. P0-04-Contract-Test ausführen.
4. Alembic auf den aktuellen `head` aktualisieren.
5. Revisionsstand und vollständigen Schema-Fingerprint erfassen.
6. Einen eindeutig markierten Sentinel-Tenant anlegen.
7. Auf den direkten Vorgänger des Heads downgraden.
8. Den erreichten Rücksprungpunkt kontrollieren.
9. Erneut auf `head` aktualisieren.
10. Endrevision mit dem erwarteten Head vergleichen.
11. Schema vor und nach dem Zyklus byte-stabil vergleichen.
12. Erhalt des Sentinel-Tenants bestätigen.
13. Bestehende echte PostgreSQL-Konkurrenz-/Transaktionstests ausführen.
14. JSON- und Markdown-Evidenz 30 Tage als GitHub-Artefakt speichern.

## 5. Akzeptanzkriterien

| ID | Kriterium | Status |
| --- | --- | --- |
| 04.1 | Reproduzierbare PostgreSQL-Testdatenbank ohne Produktivdaten | PASS |
| 04.2 | Upgrade auf aktuellen Alembic-Head | PASS |
| 04.3 | Downgrade auf direkten freigegebenen Rücksprungpunkt | PASS |
| 04.4 | Erneutes Upgrade ohne Schema-Drift | PASS |
| 04.5 | Datenerhalt plus PostgreSQL-Konkurrenz-/Transaktionssmoke | PASS |
| 04.6 | Migrationsreport mit Revisionen, Hashes und Laufzeit | PASS |

## 6. Evidenz

- Workflow: `P0-04 PostgreSQL Migration Cycle`
- Run: `#3`
- Run-ID: `30956859723`
- Ergebnis: `success`
- Commit: `36f8d29ad659ca6d9671e610bac3bfa87a72f2c2`
- Evidenzartefakt: `p0-04-postgres-migration-evidence`
- Artefakt-ID: `8911382870`
- Artefakt-Digest: `sha256:e25e05e1c4c4d383aff5d92e0aa772c34d2aab42ed6da544a9e0df4d44d97b2d`
- Aufbewahrung bis: `2026-09-03`
- Begleitender PILOT-E2E-Run: `#42`, Ergebnis `success`

Der Report enthält mindestens:

- Startzeitpunkt in UTC,
- Alembic-Head,
- Downgrade-Ziel,
- finale Revision,
- Schema-SHA-256 vor dem Zyklus,
- Schema-SHA-256 nach dem Zyklus,
- Anzahl geprüfter Tabellen,
- Ergebnis des Sentinel-Datenerhalts,
- Gesamtlaufzeit,
- finalen Status `PASS`.

## 7. Auditbewertung

**Aktueller Status:** `VERIFIED / PASS`

Die technische Umsetzung von P0-04 ist vollständig im Repository vorhanden und wurde erfolgreich gegen einen echten PostgreSQL-16-Service ausgeführt. Upgrade, Downgrade, erneutes Upgrade, Schema-Drift-Prüfung, Sentinel-Datenerhalt sowie die vorhandenen PostgreSQL-Konkurrenz-/Transaktionstests waren erfolgreich.

## 8. Auswirkung auf die Go-Live-Readiness

Der bisher offene Punkt „PostgreSQL Migration Upgrade/Downgrade/Upgrade“ ist geschlossen. Das verbessert insbesondere:

- Datenbank- und Deployment-Sicherheit,
- Rollback-Fähigkeit,
- Reproduzierbarkeit des Pilot-Releases,
- formales Gate G5 für den ersten Pilotkunden.

Backup/Restore, produktives Alerting und der reale Recovery-Drill bleiben davon getrennte P0-Gates und werden durch diesen Test nicht ersetzt.
