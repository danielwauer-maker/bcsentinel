# P0-09 Pilotdokumente und Operatorpaket Audit

**Stand:** 2026-08-05  
**Produktstand:** BCSentinel 1.0.2.20  
**Gate:** Dokumentation, Support und Operatorbetrieb

## 1. Ziel

P0-09 stellt sicher, dass die betreute Pilotphase nicht nur technisch, sondern auch organisatorisch reproduzierbar betrieben werden kann. Dafür werden Operatorhandbuch, Support-/Eskalationsprozess, Known Limitations sowie Onboarding-/Offboarding-Checklisten als versionierte Repository-Artefakte bereitgestellt und automatisiert auf Mindestinhalte geprüft.

## 2. Umgesetzte Komponenten

| Komponente | Pfad |
| --- | --- |
| Operatorhandbuch | `docs/pilot/OPERATOR_HANDBOOK_1.0.2.20.md` |
| Support- und Eskalationsprozess | `docs/pilot/SUPPORT_ESCALATION_PROCESS.md` |
| Known Limitations | `docs/pilot/KNOWN_LIMITATIONS_1.0.2.20.md` |
| Onboarding-/Offboarding-Checkliste | `docs/pilot/PILOT_ONBOARDING_OFFBOARDING_CHECKLIST.md` |
| Contract-Test | `backend/tests/test_p0_09_operator_package_contract.py` |
| CI-Workflow | `.github/workflows/p0-09-operator-package.yml` |

## 3. Abgedeckte Betriebsbereiche

- täglicher Systemcheck,
- Onboarding und Offboarding,
- Produkt-/Entitlement-/Creditfreischaltung,
- Scan- und Monitoringbetrieb,
- Incidentablauf,
- Backup und Restore,
- Rollback,
- SMTP-Ausfall,
- P0/P1/P2-Klassifizierung,
- Eskalationsmatrix und Runbook-Zuordnung,
- Kundenkommunikation,
- Known Limitations,
- Sieben-Tage-Nachkontrolle.

## 4. Automatisierter Nachweis

Der P0-09-Workflow prüft:

1. alle Pflichtdokumente sind vorhanden,
2. Dokumente sind nicht leer oder nur Platzhalter,
3. zwingende Kapitel sind enthalten,
4. offene reale Gates werden transparent benannt,
5. Onboarding und Offboarding enthalten die erforderlichen Lebenszykluskontrollen,
6. JUnit-, Pytest- und Markdown-Evidenz wird erzeugt.

Verifizierter Abschlussstand:

- Head-SHA: `a6391d9d42877a958e4c474d914e6274146be362`
- `P0-09 Operator Package #3`: `success`
- `PILOT-E2E-01A Automated Readiness #69`: `success`

## 5. Auditstatus

**Aktueller Status:** `VERIFIED_IN_CI / PASS`

Der Repository-, Struktur- und Contract-Test-Teil von P0-09 ist abgeschlossen. Die vollständige Backend-Regression und das Pilot-E2E-Gate sind auf demselben Head ebenfalls erfolgreich.

## 6. Noch manuell offen

Vor Kunde 1 müssen ergänzt oder freigegeben werden:

- primärer Supportkanal,
- Ersatzkontakt,
- konkrete Pilot-Reaktionszeiten,
- reale Hosting- und Logpfade,
- Backup-Speicherort,
- Wartungsfenster,
- Screenshots der Operatoransichten,
- finale rechtliche und kaufmännische Freigabe,
- unterschriebenes Pilot-Abnahmeprotokoll.

## 7. Bewertung

Mit P0-09 ist der automatisierbare Kern des Operator- und Supportpakets umgesetzt und CI-verifiziert. Der Sprint schließt keine externen oder unternehmerischen Entscheidungen, reduziert aber das Risiko inkonsistenter Onboardings, unklarer Incidents und nicht dokumentierter manueller Eingriffe deutlich.
