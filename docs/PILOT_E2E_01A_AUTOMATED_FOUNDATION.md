# PILOT-E2E-01A – Automated Pilot Test Foundation

Status: In Progress

## Ziel

Dieser Sprint schafft einen reproduzierbaren, fail-closed Pilot-Nachweis. Er ordnet vorhandene automatisierte Tests den realen Kundenpfaden zu, führt die vollständige Backend-Regression aus und erzeugt einen maschinenlesbaren sowie lesbaren Evidence Report.

Der Sprint darf eine echte Business-Central-Sandbox-Abnahme nicht als bestanden darstellen. BC-Runtime-, PostgreSQL- und UAT-Gates bleiben `BLOCKED` oder `MANUAL`, bis separate Beweise vorliegen.

## Bestandteile

- `quality/pilot-e2e/pilot_test_matrix.json`
  - kanonische Testmatrix
  - P0/P1-Priorisierung
  - erwartete Ergebnisse
  - Automatisierungsart
  - Evidence-Anforderung
  - explizite Umgebungsblocker
- `scripts/generate_pilot_e2e_evidence.py`
  - findet bestehende Test- und Contract-Dateien
  - liest JUnit-Ergebnisse
  - erzeugt JSON- und Markdown-Evidence
  - behandelt fehlende automatisierte P0-Abdeckung als Fehler
  - lässt manuelle und Sandbox-Gates niemals durch ein grünes JUnit-Ergebnis auf PASS wechseln
- `backend/tests/test_pilot_e2e_evidence_contract.py`
  - validiert Matrix und eindeutige Test-IDs
  - prüft fail-closed Verhalten
  - prüft, dass Sandbox- und UAT-Gates offen bleiben
- `.github/workflows/pilot-e2e-01a.yml`
  - vollständige Backend-Regression
  - JUnit-Ausgabe
  - Evidence-Generierung
  - GitHub Step Summary
  - 14 Tage gespeichertes Evidence-Artefakt

## Automatisch geprüfte Bereiche

Die Matrix versucht vorhandene Tests für folgende Pfade zuzuordnen:

1. Registrierung und Identität
2. Tenant-/Company-Isolation
3. Free Scan und permanente Free-Ergebnisrechte
4. kanonisches Produktmodell und Legacy Guard
5. Runtime Policy Drift
6. atomarer Credit-Verbrauch
7. Scan Lifecycle
8. Lease, Heartbeat und Recovery
9. Executive Report und PDF
10. Data-Health-Ausnahmen
11. Monitoring und Scheduler
12. Checkout und Webhook-Idempotenz
13. Ablauf und Downgrade
14. BC AL Compile und Cop Gate als externer CI-Nachweis

Die Zuordnung allein ist kein PASS. Für automatisierte Einträge gelten gleichzeitig:

- mindestens eine passende Test- oder Contract-Datei muss existieren;
- die vollständige Backend-Regression muss ein JUnit-Ergebnis liefern;
- das JUnit-Ergebnis darf keine Failures oder Errors enthalten.

## Bewusst offene Gates

- echte PostgreSQL-Transaktion gegen eine disposable PostgreSQL-Testdatenbank
- Installation in echter BC-Sandbox
- Registrierung und Free Scan aus BC
- Paid Assessment, Findings, Report und Validation in BC
- Monitoring Job Queue in BC
- Extension-Upgrade in BC
- visuelle und fachliche UAT

## Evidence-Artefakt

Der Workflow veröffentlicht `pilot-e2e-01a-evidence` mit:

- `pilot-e2e-evidence.json`
- `pilot-e2e-evidence.md`
- `pilot-e2e-junit.xml`
- `pilot-e2e-pytest.log`

## Entscheidungsregel

- Automatisierte P0-Gates müssen PASS sein.
- Externe BC-Compile-, echte PostgreSQL-, BC-Sandbox- und manuelle Gates benötigen eigene Beweise.
- Solange mindestens ein P0-Gate offen ist, lautet die Gesamtentscheidung `NOT_READY`.
- Dieser Sprint erteilt keine Pilot- oder Go-Live-Freigabe.

## Nicht Bestandteil

- keine Produktionsdaten
- keine produktive Stripe-Ausführung
- keine Secrets im Repository
- keine automatische Erstellung oder Veränderung einer Microsoft-365-/BC-Umgebung
- keine AppSource-Einreichung
- kein Merge ohne ausdrückliche Freigabe
