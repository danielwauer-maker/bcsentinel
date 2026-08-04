# P0-05 PostgreSQL Backup und vollständiger Restore Audit

**Stand:** 2026-08-05  
**Produktstand:** BCSentinel 1.0.2.20  
**Branch:** `docs/go-live-readiness-1.0.2.20`  
**Gate:** G6 Betrieb / Sprint P0-05

## 1. Ziel

P0-05 weist nach, dass eine BCSentinel-PostgreSQL-Datenbank vollständig gesichert und in eine getrennte leere Restore-Datenbank zurückgespielt werden kann. Der Restore gilt nur als bestanden, wenn Revision, Tabellenbestand, Datensätze und kritische Produktobjekte nachweislich erhalten sind.

## 2. Umgesetzte Repository-Komponenten

| Komponente | Pfad | Zweck |
| --- | --- | --- |
| Backup-/Restore-Verifier | `backend/scripts/verify_postgres_backup_restore.py` | `pg_dump`, isolierter `pg_restore`, Integritätsvergleich und Evidenz |
| GitHub-Gate | `.github/workflows/p0-05-postgres-backup-restore.yml` | echter PostgreSQL-16-Backup-/Restore-Lauf |
| Contract-Test | `backend/tests/test_p0_05_backup_restore_contract.py` | schützt Sicherheits-, Integritäts- und Evidenzmechanismen |
| Evidenzartefakt | `build/p0-05/backup-restore.json` und `.md` | maschinen- und menschenlesbarer Nachweis |

## 3. Sicherheitsmaßnahmen

Der Verifier verweigert die Ausführung, wenn:

- keine PostgreSQL-URLs verwendet werden,
- Quell- und Restore-Datenbank identisch sind,
- Datenbanknamen nicht eindeutig als Test-, Backup- oder Restore-Datenbanken erkennbar sind,
- das Backup leer ist,
- `pg_dump` oder `pg_restore` einen Fehler melden,
- Revisionen oder Tabellenzähler nach Restore abweichen.

Der CI-Workflow verwendet ausschließlich:

- Quelle: `bcsentinel_p0_05_source_test`
- Ziel: `bcsentinel_p0_05_restore_test`

Produktivdaten werden nicht verwendet.

## 4. Automatischer Prüfablauf

1. PostgreSQL-16-Service starten.
2. Separate leere Restore-Datenbank erzeugen.
3. Quell-Datenbank auf Alembic `head` aktualisieren.
4. Repräsentativen Testtenant anlegen.
5. Tabellen- und Zeilenzähler der Quelle erfassen.
6. Custom-Format-Backup mit `pg_dump` erzeugen.
7. Backup-Größe und SHA-256 erfassen.
8. Restore-Datenbank mit `pg_restore --clean --if-exists --exit-on-error` wiederherstellen.
9. Alembic-Revisionen vergleichen.
10. Zeilenzähler sämtlicher Anwendungstabellen vergleichen.
11. Kritische Tabellen für Tenant, Membership, Scan, Finding, Credit und Entitlement prüfen.
12. Bestehenden PostgreSQL-Konkurrenz-/Transaktionssmoke gegen die Restore-Datenbank ausführen.
13. JSON- und Markdown-Evidenz 30 Tage als GitHub-Artefakt speichern.

## 5. Akzeptanzkriterien

| ID | Kriterium | Status |
| --- | --- | --- |
| 05.1 | Getrennte Quell- und Restore-Datenbank | PASS |
| 05.2 | Vollständiges PostgreSQL-Backup | PASS |
| 05.3 | Restore ohne Überschreibung der Quelle | PASS |
| 05.4 | Identische Alembic-Revision | PASS |
| 05.5 | Identische Tabellen und Zeilenzähler | PASS |
| 05.6 | Kritische Produktobjekte und PostgreSQL-Smoke | PASS |
| 05.7 | Evidenz mit Hash, Größe und Laufzeiten | PASS |

## 6. CI-Evidenz

| Gegenstand | Wert |
| --- | --- |
| Workflow | `P0-05 PostgreSQL Backup Restore` |
| Run | `30957252848` / Run 3 |
| Ergebnis | `success` |
| geprüfter Commit | `494f2fce6f9211e92bd57434ea9564cfc28e3c0a` |
| Artefakt | `p0-05-postgres-backup-restore-evidence` |
| Artefakt-ID | `8911543143` |
| Artefakt-Digest | `sha256:76fa3869e7a7983b0f129a1ef415eaf202e43719c5fb1ba52ad9464dfc632952` |
| Aufbewahrung | bis 2026-09-03 |
| begleitender Pilot-E2E-Run | Run 47, `success` |
| begleitender P0-04-Run | Run 8, `success` |

## 7. Noch manuell festzulegen

Die Repository-Prüfung ersetzt nicht die betrieblichen Entscheidungen für das produktive System. Vor Kunde 1 sind noch festzulegen und praktisch nachzuweisen:

- RPO, empfohlen zunächst maximal 24 Stunden,
- RTO, empfohlen zunächst maximal 4 Stunden,
- produktiver Backup-Zeitplan,
- verschlüsselter externer Backup-Speicher,
- Aufbewahrungs- und Löschfristen,
- Verantwortlicher und Ersatzkontakt,
- realer Restore auf der Hetzner-/Pilot-Infrastruktur.

## 8. Auditbewertung

**Aktueller Status:** `VERIFIED_IN_CI / PASS`

Die technische, reproduzierbare Backup-/Restore-Prüfung ist im Repository umgesetzt und erfolgreich gegen einen echten PostgreSQL-16-Dienst ausgeführt worden. Backup, isolierter Restore, Revisionsgleichheit, Tabellen- und Zeilenintegrität, kritische Produktobjekte sowie der PostgreSQL-Transaktions-/Konkurrenzsmoke wurden erfolgreich bestätigt.

Für das vollständige betriebliche Gate G6 bleibt zusätzlich ein realer Infrastruktur-Restore mit gemessenem RPO/RTO erforderlich. P0-05 ist daher technisch geschlossen, aber der produktive Betriebsnachweis bleibt als gemeinsamer Praxistest offen.

## 9. Auswirkung auf die Go-Live-Readiness

Der automatisierte Datenintegritäts- und Restore-Nachweis ist geschlossen. Dadurch sinkt das technische Risiko für Datenverlust bei Migrationen, Releases und Wiederanlauf erheblich. Offen bleiben separat:

- realer Hetzner-/Pilot-Infrastruktur-Restore,
- produktives Alerting,
- Incident-Drill,
- Rollback-Drill,
- freigegebene RPO-/RTO-Zielwerte.
