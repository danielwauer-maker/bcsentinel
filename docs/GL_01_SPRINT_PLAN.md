# GL-01 Sprint Plan – Product Completion

**Planungsbasis:** `staging@5177b8e969a0cc1e0d7fad1bec4fdcbe3dae8c55`, 22. Juli 2026

**Ziel:** funktional konsistenter, dokumentierter und fixierter Release Candidate für einen streng betreuten Design-Partner
**Planungslogik:** relative Größen statt Scheintermine; jeder Sprint besitzt eine sichere Commit-Grenze

## 1. Reihenfolge und Übersicht

| Reihenfolge | Sprint | Ergebnis | Aufwand | Hauptabhängigkeit |
|---:|---|---|---|---|
| 1 | GL-01A | Delivery Baseline und Discovery | S | Executive Assessments und Repository |
| 2 | GL-01B | DH-Ausnahmen Domain Contract & Safety Freeze | M | Founder-/Product-System-Entscheidungen |
| 3 | GL-01C1 | Exception Backend Persistence & Audit | M | GL-01B signiert |
| 4 | GL-01C2 | Exception API, Snapshot & Contract Tests | M | C1 |
| 5 | GL-01D1 | BC Legacy Migration & Sync Client | M | C2 |
| 6 | GL-01D2 | BC Guided User Flow & Permissions | M | D1 |
| 7 | GL-01E1 | Raw/Adjusted Scan & Score Integration | L | D2, Golden Vectors |
| 8 | GL-01E2 | Dashboard/Report Disclosure & Reconciliation | M | E1 |
| 9 | GL-01F | Onboarding/Welcome Runtime Acceptance | M | erreichbare Sandbox, SMTP, Browser |
| 10 | GL-01G | Setup Experience & Captions Final | M | F und Access-Matrix stabil |
| 11 | GL-01H | Pilot UX Polish | M | G, E2 |
| 12 | GL-01I | Pilot Documentation Pack | S | stabile Journey/UX |
| 13 | GL-01J | Product Completion Release Candidate | L | alle GL-01-Gates |

GL-01C, D und E wurden in je zwei Commit-sichere Inkremente geteilt. Dadurch kann Codex Persistenz, Vertrag, BC-Verbrauch und Scorewirkung getrennt implementieren und regressionsprüfen.

## 2. Sprintkarten

### GL-01A – Product-Completion-Inventur und Delivery Baseline

- **Ziel:** autoritative, evidenzbasierte Baseline und Roadmap erstellen.
- **Business Value:** verhindert Investition in bereits gelöste oder falsch verstandene Themen.
- **Pilot Value:** macht Blocker, Restnachweise und Gates sichtbar.
- **Scope:** Git/Versionen/Artefakte; GL-01-Inventur; Exceptions Discovery; GL-01–GL-07 Roadmap; Management-PDF.
- **Nicht enthalten:** Produktcode, CI, Product System oder Master Book ändern.
- **Komponenten:** ausschließlich `docs/` und PDF.
- **Abhängigkeiten:** vorhandene Assessments, Repository und Git-Historie.
- **Risiken:** fehlendes lokales Product System; veraltete Master-Book-Kennzahlen.
- **Teststrategie:** Repository-Suchen, Validatoren, Markdown-/PDF-Prüfung, `git diff --check`, Scope-Check.
- **Definition of Done:** alle fünf Artefakte vorhanden; PDF vollständig gerendert/visuell geprüft; nur Planungsdateien geändert.
- **Aufwand:** S.
- **Commit-Grenze:** genau die vier Markdown-Dateien plus PDF.

### GL-01B – DH-Ausnahmen Domain Contract & Safety Freeze

- **Ziel:** verbindlichen v1-Vertrag festlegen, bevor vorhandene scorewirksame Fragmente erweitert werden.
- **Business Value:** verhindert Scoremanipulation und widersprüchliche Produktwahrheiten.
- **Pilot Value:** Ausnahmen werden erklärbar, prüfbar und begrenzt.
- **Scope:** Status/Typen; erlaubte Übergänge; Grund/Gültigkeit/Review; Roh-/bereinigter Score; Disclosure; Datenautorität; Offline-/Staleness-Regel; Legacy-Mapping; Rollen; API-Schema; Golden-Testvektoren.
- **Nicht enthalten:** Migration, API-Implementierung, BC-UI oder Scorecode.
- **Komponenten:** Product-System-Decision Record, API-/Domain-Spezifikation, Testvektoren. Änderungen am Product System nur in einem separat autorisierten Umsetzungssprint.
- **Abhängigkeiten:** Founder/Product Owner; stabile Check-ID/-Version aus Catalog.
- **Risiken:** fachliche Entscheidung wird als technische Detailfrage vertagt.
- **Teststrategie:** Zustands-/Entscheidungstabellen, Beispielreconciliation, Threat Review.
- **Definition of Done:** signierter Vertrag; alle Discovery-Fragen entschieden oder bewusst deferred; Akzeptanzvektoren eindeutig.
- **Aufwand:** M.
- **Commit-Grenze:** nur normative Vertrags-/Decision-Artefakte.

### GL-01C1 – Exception Backend Persistence & Audit

- **Ziel:** tenant-/companygebundene Persistenz und append-only Auditgrundlage schaffen.
- **Business Value:** zentrale, supportfähige Wahrheit.
- **Pilot Value:** Änderungen bleiben über Scans und Clients nachvollziehbar.
- **Scope:** Modelle, Constraints, Migration, Repository/Service, Lifecycle-Validation, Legacy-Import-Grundlage.
- **Nicht enthalten:** öffentliche/BC API, UI, Scorewirkung.
- **Komponenten:** Backend Models/Services, Alembic, Tests.
- **Abhängigkeiten:** GL-01B.
- **Risiken:** falscher Composite Key, mutable Auditdaten, Migration bestehender BC-Daten.
- **Teststrategie:** Model-/Service-/Constraint-/Migration-/Tenant-Tests.
- **Definition of Done:** Migration vorwärts erfolgreich; doppelte aktive Identitäten verhindert; Audit append-only; keine Scanänderung.
- **Aufwand:** M.
- **Commit-Grenze:** Backend Persistence plus Tests; kein Verbraucher.

### GL-01C2 – Exception API, Snapshot & Contract Tests

- **Ziel:** versionierten, idempotenten Vertrag für BC, Dashboard und Support bereitstellen.
- **Business Value:** eine konsistente Integrationsgrenze.
- **Pilot Value:** sichere Wiederholung und Reconciliation bei Netzwerkfehlern.
- **Scope:** Commands/Queries, Rollen, Tenant/Company Guard, optimistic version, idempotency, Snapshot-Version/TTL, Fehlercodes, OpenAPI/AL Contract Tests.
- **Nicht enthalten:** BC-UI oder produktive Scoreaktivierung.
- **Komponenten:** Backend Router/Schemas/Services, Contract Tests.
- **Abhängigkeiten:** C1.
- **Risiken:** Cross-Tenant-Zugriff, stale snapshot, rückwärtsinkompatibler Scanvertrag.
- **Teststrategie:** positive/negative API-, Auth-, concurrency-, idempotency- und failure tests.
- **Definition of Done:** fremde Tenant/Company/Role-Aufrufe sicher abgewiesen; Snapshot deterministisch; bestehende Scan-API kompatibel.
- **Aufwand:** M.
- **Commit-Grenze:** API + Contract Tests.

### GL-01D1 – BC Legacy Migration & Sync Client

- **Ziel:** vorhandene BC-Ausnahmen ohne Datenverlust in den neuen Vertrag überführen.
- **Business Value:** Investitionsschutz und Upgrade-Sicherheit.
- **Pilot Value:** kein stilles Löschen oder Umklassifizieren bestehender Ausnahmen.
- **Scope:** neue Felder/Mapping, `legacy_unclassified`, idempotenter Client, Snapshot Cache/Version, Reconciliation, sichere Fehler-/Stalenessanzeige.
- **Nicht enthalten:** finale UX und scorewirksame Umschaltung.
- **Komponenten:** AL-Tabellen/Upgrade-Codeunit/API Client, AL-Testapp.
- **Abhängigkeiten:** C2, Testtenant/Companies.
- **Risiken:** Duplikate, unvollständige Syncs, alte SystemIds, fehlende Rollbackdaten.
- **Teststrategie:** Upgrade, repeated sync, partial failure, multi-company, no-SUPER.
- **Definition of Done:** Legacy-Counts reconciliert; Wiederholung idempotent; bei Fehler kein stiller Erfolg; Scorepfad unverändert.
- **Aufwand:** M.
- **Commit-Grenze:** Migration/Client/Tests, Feature noch nicht scoreaktiv.

### GL-01D2 – BC Guided User Flow & Permissions

- **Ziel:** verständliches Beantragen, Genehmigen, Reviewen und Widerrufen.
- **Business Value:** kontrollierbare fachliche Verantwortung.
- **Pilot Value:** Design-Partner kann Ausnahmen ohne Support-Workaround nutzen.
- **Scope:** Finding-/Record-Einstieg, Pflichtgrund, Typ, Gültigkeit, Approval, Status/Expiry, FactBox/Liste, Widerruf statt Delete, Rollen.
- **Nicht enthalten:** Dashboard/Report und Scoreumschaltung.
- **Komponenten:** AL Pages/PageExtensions/Permission Sets/XLF/Tests.
- **Abhängigkeiten:** D1.
- **Risiken:** direkte Tabellenrechte umgehen Workflow; unverständliche Terminologie.
- **Teststrategie:** AL-Unit, Rollen-Negativtests, BC-Sandbox-CAT DE/EN.
- **Definition of Done:** vollständiger v1-Lifecycle bedienbar; keine ungeprüfte Dauerunterdrückung; DE/EN und Tooltips vollständig.
- **Aufwand:** M.
- **Commit-Grenze:** BC UX/Rechte/Übersetzung/Tests.

### GL-01E1 – Raw/Adjusted Scan & Score Integration

- **Ziel:** Ausnahmeeffekt deterministisch, messbar und nicht irreführend in Scan/Finding/Score integrieren.
- **Business Value:** fachliche Glaubwürdigkeit des Kernprodukts.
- **Pilot Value:** Design-Partner sieht Rohbefund und akzeptierte Wirkung.
- **Scope:** Snapshot-Bindung, raw/excepted/effective counts, Raw-/Adjusted-Score, Ablauf/Widerruf/Check-Version, Re-Check, Scanresult schema.
- **Nicht enthalten:** finale Dashboard-/PDF-Darstellung.
- **Komponenten:** Scan Engine, Sync Contract, Result Model, Tests.
- **Abhängigkeiten:** D2, Golden Dataset, Catalog-Versionierung.
- **Risiken:** historische Scores ändern sich; Financial Impact wird falsch reduziert; Teil-Snapshot.
- **Teststrategie:** Golden Results, Regression aller Checks, boundary/failure, historical comparison.
- **Definition of Done:** Rohresultat reproduzierbar; Delta vollständig reconciliert; kein stilles Drop; fachliche Freigabe der Golden-Ergebnisse.
- **Aufwand:** L.
- **Commit-Grenze:** Engine/Result Contract/Golden Tests.

### GL-01E2 – Dashboard/Report Disclosure & Reconciliation

- **Ziel:** überall dieselbe, transparente Ausnahmeaussage anzeigen.
- **Business Value:** Management- und Auditvertrauen.
- **Pilot Value:** BC, Dashboard und Executive Report widersprechen sich nicht.
- **Scope:** Ausnahmeanzahl/-typen, Score-Delta, Expiry/Review, Drilldown, Report/PDF Disclosure, Reconciliation.
- **Nicht enthalten:** allgemeines Dashboard-Redesign.
- **Komponenten:** Analytics/Dashboard, Report Service/Templates, BC Links, Tests.
- **Abhängigkeiten:** E1.
- **Risiken:** zu komplexe Darstellung oder Verschleierung im Executive Summary.
- **Teststrategie:** API/UI/report snapshots, cross-layer reconciliation, PDF visual QA.
- **Definition of Done:** identische Counts/Deltas; aktive Ausnahmen im Executive Report sichtbar; no-data/error states vorhanden.
- **Aufwand:** M.
- **Commit-Grenze:** Anzeige/Report/Reconciliation Tests.

### GL-01F – Customer Onboarding & Welcome Runtime Acceptance

- **Ziel:** den bereits weitgehend implementierten Flow unter realen Pilotbedingungen abnehmen und nur evidenzbasierte Restfehler schließen.
- **Business Value:** wiederholbares Kunden-Onboarding ohne Founder-Datenbankeingriff.
- **Pilot Value:** Registrierung bis erster Dashboard-Session funktioniert nachvollziehbar.
- **Scope:** Registrierung/Wiederholung, Invite/Welcome-Mail, erster Login, Tenant-Auswahl/-Wechsel, Session-Rotation/Logout, Dashboard-Link, Access Snapshot, Fehler/Recovery, Background-Scan-Restabnahme.
- **Nicht enthalten:** neues Identity-System, Enterprise SSO, öffentliche Self-Service-Strecke.
- **Komponenten:** BC Sandbox, Backend Staging, SMTP, Browser, fokussierte Fixes nur bei reproduzierter Abweichung.
- **Abhängigkeiten:** reale SMTP-/Sandbox-/Browserumgebung.
- **Risiken:** Unit-Evidenz wird mit Runtime-Evidenz verwechselt; Mail/URL/Token-Leak.
- **Teststrategie:** Journey-CAT DE/EN, multi-company/tenant, retry/rate limit, manipulated session, historical free tenant.
- **Definition of Done:** signiertes Protokoll; Mail zugestellt; Sessionwechsel/Logout korrekt; keine Tokenanzeige; Free-/Paid-Matrix korrekt.
- **Aufwand:** M.
- **Commit-Grenze:** Acceptance-Protokoll und je reproduziertem Defekt ein eigener Fix-Commit.

### GL-01G – Setup Experience & Captions Final

- **Ziel:** Setup task-basiert, verständlich und sprachlich konsistent machen.
- **Business Value:** weniger Support und Konfigurationsfehler.
- **Pilot Value:** Partner versteht Registrierung, Access, Scan und Scheduler.
- **Scope:** Informationsarchitektur, progressive Details, Captions/Tooltips, DE/EN XLF, Actions, Lizenz-/Capability-Matrix, Scheduler/Monitoring-Hinweise, Success/Error/Empty States.
- **Nicht enthalten:** Lizenz-, Scheduler- oder Monitoring-Architektur ändern.
- **Komponenten:** `DH Setup`, Labels/XLF, Navigation, Contract/AL tests.
- **Abhängigkeiten:** F, stabile Produktterminologie.
- **Risiken:** große Seite bleibt trotz Textpolish überladen; Übersetzung deckt Runtime nicht ab.
- **Teststrategie:** localization validator, AL build/tests, DE/EN visual CAT, role matrix.
- **Definition of Done:** keine sichtbaren Restbegriffe ohne freigegebene Übersetzung; Aufgabenpfade eindeutig; Advanced Info getrennt.
- **Aufwand:** M.
- **Commit-Grenze:** Setup/XLF/Tests.

### GL-01H – Pilot UX Polish

- **Ziel:** konsistente Zustände und Navigation über die kanonische Pilot Journey.
- **Business Value:** vertrauenswürdige Produkterfahrung.
- **Pilot Value:** Fehler und leere Zustände sind selbst erklärend.
- **Scope:** Empty/Loading/Error/Confirmation; Statuskatalog; Free vs Full; Upgrade-/Access-Hinweise; Branding; Navigation; Dashboard/BC-Texte.
- **Nicht enthalten:** Landingpage-Neubau oder Public Accessibility-Zertifizierung.
- **Komponenten:** BC und Dashboard UI, Texte, Tests.
- **Abhängigkeiten:** E2, G.
- **Risiken:** kosmetischer Scope verdrängt Kernfehler; divergent terms.
- **Teststrategie:** Journey-State-Matrix, responsive/browser smoke, DE/EN, accessibility smoke.
- **Definition of Done:** definierte Journey besitzt für jeden Zustand erwartete Anzeige/Aktion; keine Sackgassen.
- **Aufwand:** M.
- **Commit-Grenze:** BC und Dashboard getrennt, jeweils mit Tests.

### GL-01I – Pilot Documentation Pack

- **Ziel:** ein einziges aktuelles, kunden- und supportfähiges Pilotpaket.
- **Business Value:** reproduzierbare Einführung und geringeres Haftungs-/Support-Risiko.
- **Pilot Value:** Installation bis Troubleshooting ohne Repositorykenntnis.
- **Scope:** Installation, Setup, Registrierung, Scan, Findings, Exceptions, Dashboard, Report, Support, Known Issues, Troubleshooting, Pilotgrenzen, Datenschutz-/Kontaktpfade.
- **Nicht enthalten:** Public-Marketing oder Enterprise-Handbuch.
- **Komponenten:** Dokumentation/PDFs, Links, Release Notes.
- **Abhängigkeiten:** stabile UX aus H.
- **Risiken:** bestehende Dokumente widersprechen neuem Flow.
- **Teststrategie:** Link-/Schrittprüfung, Dry Run durch Nicht-Entwickler, Screenshot-/Versionsprüfung.
- **Definition of Done:** kanonisches Paket; Owner/Version; Known Issues vollständig; Dry Run bestanden.
- **Aufwand:** S.
- **Commit-Grenze:** nur Pilotdokumentation.

### GL-01J – Product Completion Release Candidate

- **Ziel:** reproduzierbaren, eindeutig fixierten und reversiblen RC bereitstellen.
- **Business Value:** kontrollierte Pilotinvestition.
- **Pilot Value:** exakt getestete Version statt beweglichem Branch.
- **Scope:** Commit/Tag, Versionsmatrix, Migration Baseline, Config Manifest, Backend-/AL Builds, Tests, smoke, Sandbox, release notes, backup/restore/rollback evidence, known risks, signed gate decision.
- **Nicht enthalten:** Public oder Enterprise Release.
- **Komponenten:** gesamtes Produkt und Releaseakte.
- **Abhängigkeiten:** A–I; fachliches Golden Dataset; Operations-/Pilotgates.
- **Risiken:** CI ohne Testgate, Artefaktdrift, ungetestetes Restore, generische Git-Historie.
- **Teststrategie:** clean rebuild, backend suite auf PostgreSQL, AL build/test, migration, smoke/CAT, security/isolation, rollback/restore drill.
- **Definition of Done:** RC-Commit und Artefakte unveränderlich referenziert; alle Pilot-P0-Gates PASS oder explizit akzeptierte, vertraglich begrenzte Restpunkte; Go/No-Go signiert.
- **Aufwand:** L.
- **Commit-Grenze:** finaler RC-Commit; danach keine inhaltliche Änderung ohne neuen RC.

## 3. Gemeinsame Delivery-Regeln

- Kein Sprint gilt nur wegen vorhandener Dateien als COMPLETE.
- Produktcode, Migration, API, UI und Dokumentation erhalten getrennte Commit-Grenzen, wenn Rollback oder Review sonst unsicher wäre.
- Jeder Sprint aktualisiert Evidence, Risiken und betroffene Contract Tests.
- Echte BC-Sandbox-, SMTP-, PostgreSQL-, Browser- und Restore-Nachweise werden als eigene Gates protokolliert.
- Public- und Enterprise-Anforderungen werden nicht in GL-01 hineingezogen, außer sie sind für Tenant-/Datensicherheit oder Pilot-Recovery unverzichtbar.

## 4. Pilot-Freigabekette

GL-01J darf nur an GL-04 übergeben werden, wenn mindestens folgende Evidenz vorliegt:

1. signierter Exceptions-Domain-/Scorevertrag und Golden Results;
2. kanonische Journey Registrierung → Scan → Findings/Ausnahmen → Dashboard/Report;
3. BC-Sandbox-CAT mit realistischen Rollen ohne `SUPER`;
4. tenant-/companybezogene Negativtests;
5. reproduzierbare Build-/Migration-/Config-Matrix;
6. Backup/Restore-/Rollback-Nachweis oder formales No-Go;
7. Pilotdokumentation, Support-/Incidentweg und Known Issues;
8. fixer RC-Commit und unverwechselbare Artefaktversionen.
