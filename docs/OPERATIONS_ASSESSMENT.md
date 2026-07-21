# Operations Assessment

Stand: 2026-07-21

## Assessment Contract

Bewertet wird der freigegebene Repository-Stand `c3fa58734086e2f44fe29f6413ed0433be5c460e` auf Branch `staging`. Nicht commitierte Arbeitsbaumänderungen sind keine freigegebene, reproduzierbare Evidenz und wurden nicht bewertet. Sie wurden weder verändert noch zurückgesetzt.

Authority Model:

1. BCSentinel Product System, Commit `449702963f500096bce1837f4da69b84db7f99d0` — normatives Zielbild.
2. Product Master Book im bewerteten Repository-HEAD — deskriptiver Ist-Stand.
3. Repository-HEAD — Verifikation durch Code, Konfiguration, Tests und Dokumentation.

Das Product System fordert Enterprise Readiness, Decision Traceability, Evidence Before Opinion und Release-Grade by Default, enthält aber noch keine freigegebene Operations-Architektur mit SLOs, RTO/RPO, Observability-, On-call-, Secret-, DR- oder Capacity-Modell. Diese normative Lücke ist selbst ein Finding.

Die angeforderten Operations-, Support-, Security-Operations- und Quality-Begriffe werden als Review-Linsen verwendet. Bewertet wird ausschließlich mit Attributen des Product Intelligence Model. Level 1 bis 5 bedeuten bei Qualitätsattributen geringe bis hohe Reife und bei Risikoattributen geringes bis hohes Risiko. `ux=null` für alle Einheiten. `priority=null` und `target_release=unassigned`, weil keine Planung autorisiert ist. Readiness ist kein arithmetischer Score.

## Repository Snapshot

- Ein Workflow: `.github/workflows/deploy.yml`; kein CI-Testjob.
- Deployment bei Push auf `main` oder `staging` per SSH, `git reset --hard`, Migration und Compose-Rebuild.
- 29 Backend-Testdateien und 260 Testfunktionen im HEAD; Ausführung im CI nicht nachgewiesen.
- 27 lineare Alembic-Revisionen mit Upgrade/Downgrade-Funktionen; produktionsnaher Restore-/Upgrade-Drill nicht nachgewiesen.
- Keine AL-Test-App und keine nativen AL-Testcodeunits.
- Strukturierte JSON-Logs, Request-IDs, Liveness und DB-Readiness vorhanden.
- Keine nachgewiesene zentrale Logplattform, Metriken, Traces, Alarmierung oder On-call-Integration.
- Backup, Restore, Incident und Pilot-Support sind manuell dokumentiert; ausgeführte Drills fehlen.
- Ein Backendcontainer und eine PostgreSQL-Instanz auf einem Host; horizontale Skalierung und Hochverfügbarkeit nicht belegt.

## Product-Intelligence-Übersicht

| Capability | BV | CV | RI | SI | Sichtb. | Pilot | Go-live | Oper. | FC | Stabil. | Wartb. | Doku | Tests | Sec. Crit. | Tech Debt | Prod. Risiko | Oper. Risiko |
|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Deployment | 5 | 4 | 5 | 5 | 2 | true | true | true | 3 | 2 | 3 | 4 | 2 | 5 | 4 | 4 | 5 |
| Release Management | 5 | 4 | 5 | 5 | 1 | true | true | true | 2 | 2 | 2 | 3 | 1 | 4 | 4 | 4 | 5 |
| CI/CD | 5 | 4 | 5 | 5 | 1 | true | true | true | 2 | 2 | 2 | 3 | 1 | 4 | 4 | 5 | 5 |
| Build Pipeline | 5 | 4 | 4 | 5 | 1 | true | true | true | 4 | 3 | 4 | 4 | 3 | 4 | 2 | 3 | 3 |
| Teststrategie | 5 | 5 | 5 | 5 | 1 | true | true | true | 3 | 2 | 3 | 4 | 2 | 4 | 4 | 5 | 5 |
| Backend Tests | 5 | 5 | 5 | 5 | 1 | true | true | true | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 |
| AL Tests | 5 | 5 | 5 | 5 | 1 | true | true | true | 1 | 1 | 1 | 2 | 1 | 5 | 5 | 5 | 5 |
| Migrationen | 5 | 5 | 5 | 5 | 1 | true | true | true | 4 | 3 | 4 | 4 | 3 | 5 | 3 | 5 | 4 |
| Konfigurationsmanagement | 5 | 4 | 5 | 5 | 2 | true | true | true | 3 | 3 | 3 | 3 | 3 | 5 | 4 | 5 | 5 |
| Environment Management | 5 | 4 | 5 | 5 | 1 | true | true | true | 3 | 2 | 3 | 4 | 2 | 5 | 4 | 4 | 5 |
| Secrets Management | 5 | 5 | 5 | 5 | 1 | true | true | true | 2 | 2 | 3 | 3 | 2 | 5 | 4 | 5 | 5 |
| Scheduler | 4 | 4 | 4 | 4 | 2 | true | true | true | 3 | 2 | 3 | 3 | 2 | 4 | 4 | 4 | 4 |
| Background Jobs | 5 | 5 | 5 | 5 | 1 | true | true | true | 3 | 3 | 3 | 4 | 4 | 4 | 4 | 5 | 4 |
| Monitoring | 5 | 5 | 5 | 5 | 1 | true | true | true | 1 | 1 | 2 | 2 | 1 | 5 | 5 | 5 | 5 |
| Logging | 5 | 4 | 5 | 5 | 1 | true | true | true | 4 | 3 | 4 | 3 | 4 | 5 | 3 | 4 | 3 |
| Telemetry | 5 | 4 | 5 | 5 | 1 | true | true | true | 1 | 1 | 2 | 2 | 1 | 5 | 5 | 5 | 5 |
| Health Checks | 5 | 4 | 5 | 5 | 1 | true | true | true | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 4 | 4 |
| Alerting | 5 | 5 | 5 | 5 | 1 | true | true | true | 1 | 1 | 2 | 1 | 1 | 5 | 5 | 5 | 5 |
| Backup | 5 | 5 | 5 | 5 | 1 | true | true | true | 2 | 1 | 2 | 4 | 1 | 5 | 4 | 5 | 5 |
| Restore | 5 | 5 | 5 | 5 | 1 | true | true | true | 2 | 1 | 2 | 4 | 1 | 5 | 4 | 5 | 5 |
| Disaster Recovery | 5 | 5 | 5 | 5 | 1 | true | true | true | 1 | 1 | 1 | 2 | 1 | 5 | 5 | 5 | 5 |
| Incident Response | 5 | 5 | 5 | 5 | 2 | true | true | true | 2 | 1 | 2 | 3 | 1 | 5 | 5 | 5 | 5 |
| Supportfähigkeit | 5 | 5 | 5 | 5 | 3 | true | true | true | 3 | 2 | 3 | 4 | 1 | 4 | 4 | 4 | 4 |
| RBAC | 5 | 5 | 5 | 5 | 3 | true | true | true | 3 | 3 | 3 | 3 | 3 | 5 | 4 | 5 | 5 |
| Operational Security | 5 | 5 | 5 | 5 | 1 | true | true | true | 3 | 3 | 3 | 4 | 4 | 5 | 4 | 5 | 5 |
| Performance Evidence | 5 | 5 | 5 | 5 | 1 | true | true | true | 1 | 1 | 1 | 2 | 1 | 4 | 5 | 5 | 5 |
| Skalierbarkeit | 5 | 5 | 5 | 5 | 1 | false | true | true | 2 | 2 | 2 | 2 | 1 | 4 | 5 | 5 | 5 |
| Wartbarkeit | 5 | 5 | 5 | 5 | 1 | true | true | true | 3 | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 4 |
| Administrationsprozesse | 5 | 4 | 5 | 5 | 3 | true | true | true | 3 | 2 | 3 | 3 | 3 | 5 | 4 | 5 | 5 |

Abkürzungen: BV Business Value, CV Customer Value, RI Revenue Impact, SI Strategic Importance, FC Functional Completeness. Alle Security-Werte betreffen ausschließlich Security Operations, nicht eine vollständige Produktsicherheitsbewertung.

### Planning Attribute

Für jede Capability gilt `priority=null` und `target_release=unassigned`. Die Abhängigkeiten sind:

| Capability | `dependencies` |
|---|---|
| Deployment | CI/CD, Build Pipeline, Migrationen, Environments, Secrets, Health Checks, Rollback |
| Release Management | Branch Governance, CI/CD, Artefaktregistry, Change Approval, Support Handoff |
| CI/CD | GitHub Actions, Teststrategie, Secrets, Zielhost, Branch Protection |
| Build Pipeline | Docker, Pythonpakete, Playwright/Chromium, Registry, Image Security |
| Teststrategie | Backend-, AL-, PostgreSQL-, Provider-, Performance- und Recoveryumgebungen |
| Backend Tests | Docker-Testtarget, pytest, SQLite/PostgreSQL, Testdaten und CI |
| AL Tests | AL Toolchain, BC Sandbox, Test-App, Permission- und Upgradefixtures |
| Migrationen | Alembic, PostgreSQL, Backup, Release Manifest und Datenvolumen |
| Konfigurationsmanagement | Env, Admin, Datenbank, Defaults, Audit und Promotion |
| Environment Management | Hosts, Compose, DNS/TLS, Daten, Secrets und IaC |
| Secrets Management | GitHub Secrets, Host-Env, Anwendungssettings, Rotation und Zugriffskontrolle |
| Scheduler | Business Central TaskScheduler, Permission Set, Setup und Monitoring |
| Background Jobs | API-Prozess, PostgreSQL, Leases, Retrykonfiguration und Jobmonitoring |
| Monitoring | Logs, Metriken, Health, Infrastruktur, externe Dienste und SLOs |
| Logging | Anwendung, stdout collector, Retention, Zugriff und Redaction |
| Telemetry | Instrumentation, Collector, Backend, Trace-Propagation und Datenrichtlinie |
| Health Checks | API, PostgreSQL, Migrationstand, Jobs und Reverse Proxy |
| Alerting | Monitoringdaten, Schwellen/SLOs, On-call-Kanal und Runbooks |
| Backup | PostgreSQL, Off-host Storage, Verschlüsselung, Retention und Alerting |
| Restore | Backupkatalog, isolierte DB, Migrationen, Verifikation und Operator |
| Disaster Recovery | Backup/Restore, Ersatzinfrastruktur, DNS/TLS, Secrets, RTO/RPO |
| Incident Response | Detection, On-call, Rollen, Kommunikation, Runbooks und Postmortem |
| Supportfähigkeit | Logging, Ticketing, Diagnose, RBAC, Wissensbasis und Eskalation |
| RBAC | Identitäten, BC Permission Sets, Backend Admin, Audit und Access Reviews |
| Operational Security | Assetinventar, IAM, Secrets, Detection, Vulnerability- und Incident Management |
| Performance Evidence | Lastmodell, produktionsnahe Daten, Metriken, Testtool und SLOs |
| Skalierbarkeit | Stateless API, Jobownership, verteilte Limits, DB-HA und Capacity Model |
| Wartbarkeit | Code Ownership, Tests, Dokumentation, Automatisierung und Change Governance |
| Administrationsprozesse | Admin-RBAC, Audit, SOPs, Approval, Tickets und Rollback |

## Capability Reviews

### 1. Deployment

- **Executive Summary:** Ein realer DEV-/PROD-Deploypfad existiert, ist aber direkt, zustandsbehaftet und nicht durch ein Test- oder Freigabegate geschützt.
- **Operations Review:** Push auf `main`/`staging` löst SSH-Deployment auf einen festen Host aus; dort werden Branch, Migrationen und Compose-Stack aktualisiert. Healthchecks folgen, ein automatischer Rollback fehlt.
- **Quality Review:** Runbooks und Compose-Healthchecks sind gut; ausgeführter PROD-Dry-Run und Rollbackbeweis fehlen.
- **Security Operations Review:** GitHub Secrets schützen SSH-Daten, aber Hostzugriff, Keyrotation, Environment Approval und Deploymentidentität sind nicht dokumentiert.
- **Support Review:** Request IDs helfen nach Fehlern; ein Betreiber muss Deployment und Recovery manuell beherrschen.
- **Risiken / Empfehlungen:** Vor Deployment Tests, Approval, Artefakt-Digest und Concurrency Lock erzwingen; Blue/Green oder nachgewiesenen Rollbackpfad etablieren.
- **Operatorfragen:** Betrieb: nur erfahrenes kleines Team. Erkennung: Healthcheck teilweise. Behebung: manuell. Reproduzierbar: bedingt. Rollback: nicht bewiesen. Ursache: Logs/Commit teilweise. Nachtruhe: nein.
- **Evidence:** PS `PRODUCT_PRINCIPLES.md`, `09-release/`; PB `documentation-release.md`, `08-manual-review-required.md`; Repo `.github/workflows/deploy.yml`, Compose, `production-deployment.md`, `DEPLOYMENT_DRY_RUN.md`. Evidence Missing: ausgeführtes Deployment-/Rollbackprotokoll.

### 2. Release Management

- **Executive Summary:** Branch- und Versionsregeln existieren, aber kein geschlossener Produktreleaseprozess mit Release Candidate, Sign-off, Changelog, Artefakt und Rollbackentscheidung.
- **Operations Review:** `main` und `staging` steuern Umgebungen unmittelbar. Im Repository ist nur ein technischer Pre-Repo-Tag sichtbar, keine belastbare Releasehistorie.
- **Quality Review:** Product-System-Dokumente beschreiben SemVer und Reviews, nicht die operative Releasekontrolle des SaaS-Repositories.
- **Security Operations Review:** Keine belegte Trennung von Entwickler-, Reviewer- und Deployfreigabe.
- **Support Review:** Support kann Version, Image-Digest und bekannte Änderungen eines Kundensystems nicht sicher rekonstruieren.
- **Risiken / Empfehlungen:** Release Manifest mit Commit, Image-Digest, Migration, Konfiguration, Tests, Owner und Rollbackziel verbindlich machen.
- **Operatorfragen:** Betrieb: nur informell. Erkennung: Releasefehler nach Healthcheck. Behebung: manuell. Reproduzierbar: nein. Rollback: unklar. Ursache: Commit teilweise. Nachtruhe: nein.
- **Evidence:** PS `BRANCH_STRATEGY.md`, `VERSIONING.md`, `GIT_RELEASE.md`; PB Release-Komponente; Repo Git-Tags/-Log und Workflow. Evidence Missing: SaaS-Release-Policy, Sign-off, Releaseprotokolle.

### 3. CI/CD

- **Executive Summary:** CD ist vorhanden; CI im Sinne automatischer Qualitätsprüfung fehlt.
- **Operations Review:** Ein einziger Workflow paketiert und deployt direkt nach Push. Ein fehlgeschlagener Test kann das Deployment nicht blockieren, weil kein Testjob existiert.
- **Quality Review:** Checkout und Artifact Upload sind positiv; kein Lint-, Backend-, Migrations-, AL-, Security- oder Contract-Gate.
- **Security Operations Review:** Actions sind versionsgebunden, SSH-Ziel bleibt hochprivilegiert; OIDC, minimale Deployrechte und Secretrotation sind nicht belegt.
- **Support Review:** Fehler werden erst im Build, bei Migration oder Healthcheck sichtbar.
- **Risiken / Empfehlungen:** CI und CD trennen; immutable Artefakt einmal bauen, testen, signieren und kontrolliert promoten.
- **Operatorfragen:** Betrieb: riskant. Erkennung: spät. Behebung: manuell. Reproduzierbar: teilweise. Rollback: nein. Ursache: Workflowlogs teilweise. Nachtruhe: nein.
- **Evidence:** PS Release-Grade/Review; PB `TEST-CI-001=not_found`; Repo `.github/workflows/deploy.yml`. Evidence Missing: Branch Protection, Required Checks, Approval- und Promotionbeleg.

### 4. Build Pipeline

- **Executive Summary:** Das Docker-Build ist vergleichsweise solide, aber nicht als unveränderliches, nachverfolgbares Lieferartefakt operationalisiert.
- **Operations Review:** Multi-Stage-Build, gepinnte Pythonpakete, Chromium-Verifikation und non-root Runtime sind vorhanden. Produktion baut auf dem Zielhost neu.
- **Quality Review:** Ein Testtarget und Packagingtests existieren; CI baut und testet das Image nicht vor Promotion. Basisimages sind nicht per Digest fixiert.
- **Security Operations Review:** Non-root ist positiv; SBOM, Image Scan, Signatur und Provenance fehlen.
- **Support Review:** Fehlende Image-Digests erschweren exakte Reproduktion eines Kundenstands.
- **Risiken / Empfehlungen:** Image einmal in CI bauen, testen, scannen, signieren, mit Commit/Digest registrieren und unverändert deployen.
- **Operatorfragen:** Betrieb: grundsätzlich. Erkennung: Buildfehler ja. Behebung: rebuild. Reproduzierbar: bedingt. Rollback: ohne Digest unsicher. Ursache: Buildlog. Nachtruhe: bedingt.
- **Evidence:** PS Release-Grade; PB Testing/Release; Repo `backend/Dockerfile`, `requirements.txt`, Packagingtest. Evidence Missing: Registry-/SBOM-/Signaturbeleg.

### 5. Teststrategie

- **Executive Summary:** Breite Testideen und manuelle Checklisten existieren, aber keine verbindliche Testpyramide und keine releaseblockierende Ausführung.
- **Operations Review:** Risiken für Backend, PostgreSQL, Deployment und manuelle End-to-End-Flows sind identifiziert.
- **Quality Review:** Python ist stark vertreten; AL, Performance, Recovery, Browser und Provider-End-to-End sind lückenhaft oder manuell.
- **Security Operations Review:** Securitytests decken einzelne Controls ab, nicht regelmäßige adversariale oder operative Prüfungen.
- **Support Review:** Fehlerklassen können zwischen Dokument und Ausführung fallen.
- **Risiken / Empfehlungen:** Kanonische Release-Testmatrix mit Owner, Umgebung, Gate und Evidenzartefakt definieren.
- **Operatorfragen:** Betrieb: nicht zuverlässig freigegeben. Erkennung: vor Release unvollständig. Behebung: abhängig vom Experten. Reproduzierbar: nein. Rollback: nicht Testbestandteil. Ursache: teilweise. Nachtruhe: nein.
- **Evidence:** PS Evidence/Release Grade; PB `05-test-inventory.md`, `08-manual-review-required.md`; Repo Tests, Smoke- und Go-Live-Checklisten. Evidence Missing: aktueller kompletter Release-Candidate-Lauf.

### 6. Backend Tests

- **Executive Summary:** Umfangreiche Testbasis, deren Wert durch fehlende CI-Ausführung und SQLite-Dominanz begrenzt wird.
- **Operations Review:** 29 Dateien und 260 Funktionen im HEAD prüfen APIs, Tenancy, Billing, Lifecycle, Observability und Deployment.
- **Quality Review:** Gute Fehler- und Konkurrenzfälle; PostgreSQL-Suite ist optional und wird ohne Test-URL übersprungen. Standardfixture erstellt ORM-Schema statt vollständig über Migrationen zu gehen.
- **Security Operations Review:** Tenant-, Header-, Transport- und Redactiontests sind positiv.
- **Support Review:** Tests helfen Reproduktion, aber kein grüner Lauf ist für diesen Release belegt.
- **Risiken / Empfehlungen:** Vollsuite im Docker-Testtarget und PostgreSQL verpflichtend in CI ausführen; Ergebnis an Commit binden.
- **Operatorfragen:** Betrieb: Tests helfen, aber nicht garantiert. Erkennung: gut bei Ausführung. Behebung: reproduzierbar lokal bedingt. Deployment: nicht gegatet. Rollback: nein. Ursache: oft nachvollziehbar. Nachtruhe: noch nein.
- **Evidence:** PS Evidence Before Opinion; PB Testing-Komponente ist quantitativ hinter HEAD; Repo `backend/tests/`, `conftest.py`, Docker test target. Evidence Missing: grüner HEAD-Lauf.

### 7. AL Tests

- **Executive Summary:** Keine native AL-Test-App; damit fehlt ein wesentliches Gate für Business-Central-Betrieb.
- **Operations Review:** Scheduler, Permission Sets, Install/Upgrade und API-Client laufen in einer externen Plattform, werden aber nicht nativ automatisiert getestet.
- **Quality Review:** Python-Vertragstests und statische Suchen ersetzen keine AL-Runtime-, Permission- oder Upgrade-Tests.
- **Security Operations Review:** Least-Privilege- und Negativtests der Permission Sets fehlen als Ausführungsevidenz.
- **Support Review:** Fehler erscheinen voraussichtlich erst in Sandbox oder Kundentenant.
- **Risiken / Empfehlungen:** AL-Testprojekt und Sandboxpipeline für Install, Upgrade, Permissions, Scheduler, API-Fehler und Retries aufbauen.
- **Operatorfragen:** Betrieb: nicht zuverlässig. Erkennung: spät. Behebung: Expertenarbeit. Reproduzierbar: nein. Rollback: nicht getestet. Ursache: begrenzt. Nachtruhe: nein.
- **Evidence:** PS Enterprise Ready; PB `TEST-AL-001=not_found`; Repo keine Testcodeunits/Test-App. Evidence Missing: jeder native AL-Testlauf.

### 8. Migrationen

- **Executive Summary:** Lineare Alembic-Historie und Startup-Gate sind stark; Datenrealität, große Volumen und Rollback bleiben unbewiesen.
- **Operations Review:** 27 Revisionen, separater PROD-Migrationsservice und Schema-Head-Prüfung verhindern Start auf falscher Revision.
- **Quality Review:** Upgrade/Downgrade-Funktionen und einzelne Migrationstests existieren. Standardtests bilden Produktionsmigrationen nicht durchgehend ab.
- **Security Operations Review:** Migrationen verändern tenant- und zugriffsrelevante Daten; Freigabe-/Backup-Gate ist nur dokumentiert.
- **Support Review:** Ein fehlgeschlagener Migrationsschritt blockiert Start; kein automatisierter Recoverypfad.
- **Risiken / Empfehlungen:** Restore-Kopie mit Produktionsvolumen migrieren, Vor-/Nachchecks, Backup-ID und irreversible Grenzen im Release Manifest festhalten.
- **Operatorfragen:** Betrieb: bedingt. Erkennung: Startup klar. Behebung: manuell. Reproduzierbar: strukturell ja. Rollback: Code vorhanden, Wirkung unbewiesen. Ursache: meist. Nachtruhe: bedingt nein.
- **Evidence:** PS Decision Traceability; PB Migration-Komponente; Repo Alembic, `db.py`, Deploymenttest. Evidence Missing: produktionsnaher Upgrade-/Downgrade-Drill.

### 9. Konfigurationsmanagement

- **Executive Summary:** Viele Konfigurationsquellen sind vorhanden, aber Promotion, Vier-Augen-Prinzip und atomarer Rollback fehlen.
- **Operations Review:** Env, JSON-Defaults und DB-basierte Admin-Overrides steuern Laufzeit, Preise, Inhalte und Zugang.
- **Quality Review:** Settingsvalidierung und Admin-/Pricingtests sind positiv; Gesamtmodell und Driftprüfung fehlen.
- **Security Operations Review:** Eine einzelne Basic-Adminidentität kann große Wirkungen auslösen; Change Approval ist nicht belegt.
- **Support Review:** Audit Events helfen, aber Betreiber müssen Quellen und Fallbacks kennen.
- **Risiken / Empfehlungen:** Konfigurationskatalog, Owner, Typ, Scope, Promotion, Audit, Approval und Rollback pro Wert etablieren.
- **Operatorfragen:** Betrieb: nur durch Experten. Erkennung: Fehlkonfiguration oft spät. Behebung: manuell. Reproduzierbar: nein. Rollback: teilweise. Ursache: Audit teilweise. Nachtruhe: nein.
- **Evidence:** PS Enterprise/Traceability; PB Admin-/Configuration-Findings; Repo `settings.py`, JSON, Adminroutes/Audit. Evidence Missing: kontrollierte Environment-Promotion.

### 10. Environment Management

- **Executive Summary:** DEV und PROD sind getrennt benannt, aber nicht als reproduzierbare, isolierte Infrastruktur verwaltet.
- **Operations Review:** `staging` deployt in DEV, `main` in PROD; beide laufen per Compose auf festen Serverpfaden. Kein Infrastructure-as-Code, keine Ephemeral Environments.
- **Quality Review:** Prod-Validation verhindert einige Dev-Werte. Parity, Drift und Promotion werden nicht automatisch geprüft.
- **Security Operations Review:** Zugriffs-, Netzwerk- und Datenklassengrenzen zwischen Umgebungen sind nicht vollständig dokumentiert.
- **Support Review:** Fehler können environment-spezifisch sein und schwer reproduzierbar bleiben.
- **Risiken / Empfehlungen:** Umgebungsinventar, IaC, getrennte Accounts/Secrets/Daten, Driftcheck und Promotionvertrag einführen.
- **Operatorfragen:** Betrieb: klein skaliert. Erkennung: Health. Behebung: hostbezogen. Reproduzierbar: nein. Rollback: unklar. Ursache: teilweise. Nachtruhe: nein.
- **Evidence:** PS zukünftige Engineering-/Environment-Struktur; PB Deployment/manual review; Repo Compose DEV/PROD, Workflow, `.env.example`. Evidence Missing: IaC- und Driftbeleg.

### 11. Secrets Management

- **Executive Summary:** Secrets werden nicht im Code erwartet und Produktion validiert Mindeststärken; ein professioneller Lifecycle ist nicht belegt.
- **Operations Review:** `.env.prod` auf Host und GitHub Actions Secrets sind die sichtbaren Mechanismen.
- **Quality Review:** Startupvalidierung und Tokenhashing helfen; Inventar, Rotation, Ablauf, Owner, Notfallwiderruf und Leak-Scanning fehlen.
- **Security Operations Review:** Kein Vault/KMS, keine workload identity, kein regelmäßiger Rotationstest und kein Break-glass-Prozess.
- **Support Review:** Kompromittierung erfordert manuelle, potenziell mehrsystemische Rotation.
- **Risiken / Empfehlungen:** Secret-Inventar und Rotationsrunbook zuerst; anschließend zentralen Secret Store und kurzlebige Deployidentitäten nutzen.
- **Operatorfragen:** Betrieb: nur manuell. Erkennung: Leak nicht automatisch. Behebung: unbewiesen. Reproduzierbar: absichtlich nein. Rollback: nicht anwendbar/schwierig. Ursache: Audit fehlt. Nachtruhe: nein.
- **Evidence:** PS Trust/Enterprise; PB Security-Komponente; Repo `.env.example`, Settingsvalidierung, Actions Secrets, token hashing. Evidence Missing: Rotation-/Leak-Response-Protokoll.

### 12. Scheduler

- **Executive Summary:** Business Central TaskScheduler ist implementiert, aber reale Ausführung, Wiederanlauf und Betriebsbeobachtung sind nicht nachgewiesen.
- **Operations Review:** Runner, Failure Codeunit, Task-ID und nächste Ausführung sind modelliert; Clientkontext kann Scheduling verhindern.
- **Quality Review:** Kein nativer Scheduler-Test, keine belastbare Langzeitausführung.
- **Security Operations Review:** Eigenes Scheduler-Permission-Set ist positiv; reale Least-Privilege-Prüfung fehlt.
- **Support Review:** Setup speichert Fehler-/Statusdaten, jedoch kein zentraler Operatoralarm.
- **Risiken / Empfehlungen:** Sandbox-Drill für Plan, Ausfall, Retry, Rechte, Upgrade und doppelte Tasks; Status zentral beobachtbar machen.
- **Operatorfragen:** Betrieb: bedingt. Erkennung: lokal/reaktiv. Behebung: manuell. Reproduzierbar: unbewiesen. Rollback: Task Cancel teilweise. Ursache: Status teilweise. Nachtruhe: nein.
- **Evidence:** PS Enterprise Ready; PB Scheduled Jobs; Repo Scheduler-Codeunits/Setup/Permission Set. Evidence Missing: reale BC-Ausführung.

### 13. Background Jobs

- **Executive Summary:** Scan-Recovery besitzt gute Transaktions- und Retrymechanismen, läuft aber im API-Prozess ohne verteilte Ownership.
- **Operations Review:** Startup- und periodische Recovery reparieren stale Runs; bei mehreren Instanzen würden alle Schleifen starten. Kein separater Worker/Queue-Service.
- **Quality Review:** Lifecycle-, Lease-, Idempotenz- und PostgreSQL-Konkurrenztests sind stark, aber nicht CI-verpflichtend.
- **Security Operations Review:** Jobs nutzen denselben Prozess- und DB-Vertrauenskontext wie die API.
- **Support Review:** Events werden geloggt; Queue-Tiefe, Alter und Fehlerrate sind nicht messbar.
- **Risiken / Empfehlungen:** Single-Instance-Grenze formell festhalten oder Worker/Leader-Election entwerfen; Jobmetriken und Dead-letter-Prozess ergänzen.
- **Operatorfragen:** Betrieb: single instance bedingt. Erkennung: Logs, kein Alarm. Behebung: Recovery teilweise automatisch. Reproduzierbar: Tests teilweise. Rollback: nein. Ursache: Run/Request IDs gut. Nachtruhe: nur im begrenzten Pilot.
- **Evidence:** PS Enterprise/Scale; PB Scheduled Jobs; Repo `main.py`, scan lifecycle services/tests. Evidence Missing: Mehrinstanzbetrieb.

### 14. Monitoring

- **Executive Summary:** Operational Monitoring als Plattformfähigkeit ist nicht nachgewiesen; Produkt-Monitoring darf damit nicht verwechselt werden.
- **Operations Review:** Healthchecks und Logs existieren, aber keine zentrale Sicht auf Verfügbarkeit, Fehler, Latenz, Ressourcen, Jobs, DB oder Abhängigkeiten.
- **Quality Review:** Keine Monitoring-as-Code- oder Synthetic-Test-Evidenz.
- **Security Operations Review:** Keine Security-Signalüberwachung oder SIEM-Anbindung.
- **Support Review:** Incidents werden wahrscheinlich vom Kunden oder durch manuelle Checks entdeckt.
- **Risiken / Empfehlungen:** Minimales Monitoring für Verfügbarkeit, 5xx, Latenz, Ressourcen, DB, Jobs, Deployments und externe Abhängigkeiten einführen.
- **Operatorfragen:** Betrieb: nein. Erkennung: nicht zuverlässig. Behebung: zu spät. Reproduzierbar: nein. Rollback: unabhängig. Ursache: nur Logs. Nachtruhe: nein.
- **Evidence:** PS Enterprise Ready, Operations-Struktur nur zukünftig; PB `GAP-OPS-002`/Core Findings; Repo keine Prometheus/Grafana/Sentry/Datadog-Konfiguration. Evidence Missing: Monitoringplattform.

### 15. Logging

- **Executive Summary:** Strukturierte JSON-Logs und Korrelation sind eine starke Grundlage, aber noch kein vollständiger Logbetrieb.
- **Operations Review:** Request start/completion, Dauer, Status, Tenant und Request-ID werden nach stdout geschrieben; Startup/Recovery und Exceptions sind eventspezifisch.
- **Quality Review:** Tests prüfen Korrelation und Redaction von Validierungswerten.
- **Security Operations Review:** Sensible Payloadwerte werden teilweise redigiert; zentrale Zugriffskontrolle, Retention, Unveränderlichkeit und umfassende Leak-Prüfung fehlen.
- **Support Review:** Request-ID ist praktisch für Triage, sofern Logs verfügbar und auffindbar bleiben.
- **Risiken / Empfehlungen:** Zentral aggregieren, Retention/Access definieren, Feldschema und PII/Secret-Redaction automatisiert testen.
- **Operatorfragen:** Betrieb: bedingt. Erkennung: Logs nach Suche. Behebung: unterstützt. Reproduzierbar: ja mit ID. Rollback: nein. Ursache: oft nachvollziehbar. Nachtruhe: erst mit Aggregation/Alarm.
- **Evidence:** PS Trust/Traceability; PB Backend/Security; Repo `observability.py`, `main.py`, `test_observability.py`. Evidence Missing: zentraler Logbetrieb.

### 16. Telemetry

- **Executive Summary:** Metriken und Traces für den Plattformbetrieb fehlen.
- **Operations Review:** Requestdauer erscheint im Log, aber es gibt keine Zeitreihen, Verteilungen, Trace-Kontexte oder Abhängigkeitsansicht.
- **Quality Review:** Kein OpenTelemetry-/Metrics-Vertrag und keine Telemetrieprüfung.
- **Security Operations Review:** Keine Signalsammlung für ungewöhnliche Zugriffe, Rate-Limit-Ereignisse oder Adminanomalien.
- **Support Review:** Ursachen über API, DB, BC und Drittanbieter können nicht end-to-end verfolgt werden.
- **Risiken / Empfehlungen:** OpenTelemetry oder gleichwertigen Standard mit minimalen RED-/USE-Metriken und Trace-Propagation evaluieren.
- **Operatorfragen:** Betrieb: nein. Erkennung: unzureichend. Behebung: langsam. Reproduzierbar: nein. Rollback: nein. Ursache: systemübergreifend nein. Nachtruhe: nein.
- **Evidence:** PS Evidence/Enterprise; PB Observability als partielle Grundlage; Repo kein Metrics-/Tracing-SDK. Evidence Missing: Telemetriesystem.

### 17. Health Checks

- **Executive Summary:** Liveness und DB-Readiness sind vorhanden, aber zu schmal für die reale Servicebereitschaft.
- **Operations Review:** `/health` bestätigt Prozess, `/health/ready` prüft `SELECT 1`; Compose und Deploymentworkflow verwenden die Endpunkte unterschiedlich.
- **Quality Review:** Deploymenttests prüfen Readiness und Schema-Gate. Externe Abhängigkeiten, Migrationstand und Background-Job-Gesundheit sind nicht im Payload.
- **Security Operations Review:** Endpunkte geben Environment/Service preis, aber keine Secrets.
- **Support Review:** Gut für erste Triage, nicht für funktionale Bereitschaft.
- **Risiken / Empfehlungen:** Liveness, Readiness und Dependency Diagnostics klar trennen; Migration, Jobalter und kritische Abhängigkeiten kontrolliert abbilden.
- **Operatorfragen:** Betrieb: teilweise. Erkennung: Prozess/DB ja. Behebung: Hinweis begrenzt. Reproduzierbar: ja. Rollback: Health verifizierbar. Ursache: grob. Nachtruhe: nein.
- **Evidence:** PS Enterprise; PB `BACK-HEALTH-001`; Repo `main.py`, Compose, Workflow, Deploymenttests. Evidence Missing: vollständiger Readinessvertrag.

### 18. Alerting

- **Executive Summary:** Kein operatives Alarmierungssystem ist belegt.
- **Operations Review:** Fehlgeschlagene GitHub Actions sind sichtbar, aber Produktionsfehler, Health-Ausfälle, Jobstau, DB-Probleme und Ressourcenengpässe erzeugen keinen nachgewiesenen Pager-/Teamalarm.
- **Quality Review:** Keine Alert-Regeln, Tests oder Eskalationsziele.
- **Security Operations Review:** Keine Security Alerts.
- **Support Review:** Kundenmeldung kann der erste Alarm sein.
- **Risiken / Empfehlungen:** Alertkatalog mit Severity, Schwelle, Owner, Kanal, Runbook und Test für wenige harte Signale beginnen.
- **Operatorfragen:** Betrieb: nein. Erkennung: nicht schnell. Behebung: verspätet. Reproduzierbar: nein. Rollback: nein. Ursache: erst nach Analyse. Nachtruhe: nein.
- **Evidence:** PS Enterprise/Release; PB Operations Finding; Repo keine Alarmkonfiguration. Evidence Missing: vollständig.

### 19. Backup

- **Executive Summary:** Eine manuelle Mindestanleitung existiert, ein verlässlicher Backupdienst nicht.
- **Operations Review:** Täglicher `pg_dump` oder Volume-Backup wird empfohlen; Off-host, Verschlüsselung und sieben Tage Retention sind Soll, nicht belegter Zustand.
- **Quality Review:** Kein automatisierter Job, Monitoring, Erfolgstest, Katalog oder Immutable Storage.
- **Security Operations Review:** Schlüssel-/Secret-Backup wird erwähnt; Zugriff, Verschlüsselung und Löschung sind nicht nachgewiesen.
- **Support Review:** Im Incident ist unklar, welches letzte verwertbare Backup existiert.
- **Risiken / Empfehlungen:** Automatisierten, verschlüsselten Off-host-Backupjob mit Retention, Monitoring und täglicher Verifikation einführen.
- **Operatorfragen:** Betrieb: nein. Erkennung: Backupfehler nein. Behebung: unbewiesen. Reproduzierbar: Anleitung ja, Dienst nein. Rollback: abhängig. Ursache: kein Verlauf. Nachtruhe: nein.
- **Evidence:** PS zukünftige Operational Readiness; PB manual review; Repo `docs/ops/backup-restore.md`. Evidence Missing: Backupobjekte und Erfolgsprotokolle.

### 20. Restore

- **Executive Summary:** Restore ist beschrieben, aber nie als vollständiger Service-Recovery-Drill belegt.
- **Operations Review:** Fresh DB, Dump, Alembicstand, Health, Tenant- und Admincheck sind sinnvolle Schritte.
- **Quality Review:** Kein gemessener Restore, keine Konsistenzprüfung über Stichproben hinaus, kein automatisierter Drill.
- **Security Operations Review:** Sichere isolierte Restoreumgebung und Zugriffskontrolle sind nicht dokumentiert.
- **Support Review:** Dauer und Erfolgswahrscheinlichkeit sind unbekannt.
- **Risiken / Empfehlungen:** Quartalsweisen Restore-Drill mit RTO-Messung, Datenkonsistenz, Owner und Nachweis ausführen.
- **Operatorfragen:** Betrieb: nicht bewiesen. Erkennung: Restorefehler erst im Notfall. Behebung: Anleitung. Reproduzierbar: theoretisch. Rollback: Restore selbst. Ursache: begrenzt. Nachtruhe: nein.
- **Evidence:** PS Enterprise; PB manual review; Repo Backup/Restore-Dokumente und Checklisten. Evidence Missing: jeder erfolgreiche Drill.

### 21. Disaster Recovery

- **Executive Summary:** Kein Disaster-Recovery-Modell vorhanden.
- **Operations Review:** Single Host, lokale PostgreSQL-Volume und manuelle Backups bilden einen hohen gemeinsamen Failure Domain.
- **Quality Review:** Keine RTO/RPO, Region-/Hostverlustübung, Ersatzinfrastruktur oder DNS-/TLS-/Secret-Wiederherstellungsfolge.
- **Security Operations Review:** Kein DR-Zugriffs- oder Break-glass-Modell.
- **Support Review:** Kundenkommunikation und Priorisierung bei Totalverlust sind offen.
- **Risiken / Empfehlungen:** Business Impact, RTO/RPO, Abhängigkeiten, Ersatzhost, Daten-/Secret-/DNS-Recovery und jährlichen Disaster Drill definieren.
- **Operatorfragen:** Betrieb: nein. Erkennung: Totalausfall sichtbar, aber kein Alarm. Behebung: unklar. Reproduzierbar: nein. Rollback: nein. Ursache: sekundär. Nachtruhe: nein.
- **Evidence:** PS Operationsordner nur zukünftig; PB Gap/Finding; Repo kein DR-Plan. Evidence Missing: vollständig.

### 22. Incident Response

- **Executive Summary:** Ein Pilotablauf existiert, aber kein professionelles Incident-Management-System.
- **Operations Review:** Triage, Logsicherung, Kundenhinweis, Containment und Root Cause werden genannt.
- **Quality Review:** Severitydefinition, Rollen, On-call, Eskalationszeiten, Kommunikationsvorlagen, Statusseite, Postmortem und Übungen fehlen.
- **Security Operations Review:** Security Incidents sind nicht als eigener Playbook-/Notification-Pfad ausgearbeitet.
- **Support Review:** Ein kleines Team kann improvisieren; ein wachsendes Team kann den Prozess nicht verlässlich übernehmen.
- **Risiken / Empfehlungen:** Incident Commander, Severity, RACI, Kanäle, Zeiten, Playbooks, Kundenkommunikation und blameless Postmortem verbindlich machen und üben.
- **Operatorfragen:** Betrieb: nur founder-led. Erkennung: unzureichend. Behebung: ad hoc. Reproduzierbar: nein. Rollback: manuell. Ursache: RCA gefordert, nicht standardisiert. Nachtruhe: nein.
- **Evidence:** PS Enterprise/Traceability; PB Core Findings; Repo `docs/ops/pilot-runbook.md`, Pilot Go-Live Runbook. Evidence Missing: Incidentübung und On-call.

### 23. Supportfähigkeit

- **Executive Summary:** Für 1–3 handgeführte Pilotkunden plausibel, nicht für unbeaufsichtigten Enterprisebetrieb.
- **Operations Review:** Tenant ID, Run ID, Timestamp und Request-ID bilden eine gute Triagebasis; Supportkanal und Same-day-Ziel sind manuell.
- **Quality Review:** Keine Ticketplattform, SLA/SLO, Schichtmodell, Wissensbasis, Problem Management oder Supportmetriken.
- **Security Operations Review:** Keine Secrets per Chat anzufordern und Tokenkompromittierung zu behandeln ist positiv.
- **Support Review:** Founderwissen ist derzeit ein Single Point of Failure.
- **Risiken / Empfehlungen:** Support Intake, Severity, Ownership, Eskalation, KB, sichere Diagnosepakete und Übergabeprozesse etablieren.
- **Operatorfragen:** Betrieb: klein ja. Erkennung: oft kundenseitig. Behebung: Expertenabhängig. Reproduzierbar: IDs helfen. Rollback: manuell. Ursache: teilweise. Nachtruhe: nein.
- **Evidence:** PS zukünftige Support Handoff; PB Documentation/Admin; Repo Pilot Runbooks/Checklisten. Evidence Missing: Betriebshistorie und SLA-Erfüllung.

### 24. RBAC

- **Executive Summary:** BC besitzt fünf differenzierte Permission Sets; Backend-Operations hängen dagegen an einer einzelnen Basic-Adminidentität.
- **Operations Review:** Viewer, Scan, Setup, Admin und Scheduler trennen BC-Rechte. Adminportal besitzt kein rollenfeines Operator-/Support-/Auditor-Modell.
- **Quality Review:** Backend-Tenant-/Membershiptests und statische AL-Verträge existieren; native BC-Negativmatrix und Admin-RBAC-Tests fehlen.
- **Security Operations Review:** Least Privilege ist nicht end-to-end, gemeinsame Admincredentials sind für Enterprisebetrieb nicht akzeptabel.
- **Support Review:** Support benötigt entweder zu viele Rechte oder kann Aufgaben nicht sauber delegiert übernehmen.
- **Risiken / Empfehlungen:** Benannte Operatoridentitäten, Rollenmatrix, MFA/SSO-Ziel, Least Privilege, Break-glass und regelmäßige Access Reviews.
- **Operatorfragen:** Betrieb: begrenzt. Erkennung: Audit teilweise. Behebung: Rechte manuell. Reproduzierbar: BC-Definition ja. Rollback: Entzug manuell. Ursache: Adminakte teilweise. Nachtruhe: nein.
- **Evidence:** PS Enterprise Ready; PB Security/Admin; Repo Permission Sets, `require_admin`, Memberships/Audit. Evidence Missing: operative Rollen-/Access-Review-Evidenz.

### 25. Operational Security

- **Executive Summary:** Technische Schutzgrundlagen sind substantiell, Security Operations sind jedoch nicht institutionalisiert.
- **Operations Review:** HTTPS-Policy, CORS-Validierung, Security Headers, CSRF, Tokenhashing, Rate Limits und Audit Events sind vorhanden.
- **Quality Review:** Gute Tests für mehrere Controls; Penetrationstest, kontinuierliche Scans, Dependency-/Imageprüfung und Produktionsevidenz fehlen.
- **Security Operations Review:** Keine Vulnerability-Triage, Patch-SLA, SIEM, Secretrotation, Security-On-call oder Incident-Playbooks. In-process Rate Limits skalieren nicht verteilt.
- **Support Review:** Securityfälle würden founder-led bearbeitet.
- **Risiken / Empfehlungen:** Security Operations Programm mit Asset-/Vulnerability-Management, Patchrhythmus, Access Reviews, Detection und Incident Playbooks etablieren.
- **Operatorfragen:** Betrieb: nur kontrolliert. Erkennung: schwach. Behebung: manuell. Reproduzierbar: Controls teilweise. Rollback: unklar. Ursache: Audit/Logs teilweise. Nachtruhe: nein.
- **Evidence:** PS Trust/Enterprise; PB Security-Komponente/manual review; Repo Securitymodule/tests, Admin Audit. Evidence Missing: produktiver SecOps-Nachweis.

### 26. Performance Evidence

- **Executive Summary:** Keine belastbare Performance- oder Kapazitätsevidenz.
- **Operations Review:** Einzelne Requestdauern werden geloggt; es gibt keine Baseline, SLO, Lastprofile oder Ressourcenbudgets.
- **Quality Review:** PostgreSQL-Konkurrenztests prüfen Korrektheit, nicht Durchsatz, Latenz oder Sättigung. Keine Lastsuite.
- **Security Operations Review:** Verhalten unter missbräuchlicher Last und Rate-Limit-Wirkung über mehrere Instanzen ist unbekannt.
- **Support Review:** Langsamkeit kann nicht gegen Erwartungswerte diagnostiziert werden.
- **Risiken / Empfehlungen:** Kritische Journeys, Datenvolumen und Nutzerkonkurrenz definieren; Baseline-/Last-/Soaktests plus DB- und Ressourcenmessung ausführen.
- **Operatorfragen:** Betrieb: unbekannt. Erkennung: keine SLOs. Behebung: ohne Baseline langsam. Reproduzierbar: nein. Rollback: nein. Ursache: begrenzt. Nachtruhe: nein.
- **Evidence:** PS Evidence Before Opinion; PB Performance manual review; Repo keine Lasttests. Evidence Missing: vollständig.

### 27. Skalierbarkeit

- **Executive Summary:** Die aktuelle Topologie ist für einen kleinen, kontrollierten Pilot plausibel, nicht als Enterprise-SaaS-Skalierungsmodell.
- **Operations Review:** Ein Backendcontainer, eine PostgreSQL-Instanz, lokale Volumes, feste Containernamen und In-process Jobs/Rate Limits verhindern einfache horizontale Skalierung.
- **Quality Review:** Keine Mehrinstanz-, Failover-, Connection-Pool-, Queue- oder Capacity-Evidenz.
- **Security Operations Review:** Skalierung kann Rate Limits, Jobownership und Auditkonsistenz verändern.
- **Support Review:** Wachsende Kundenlast erhöht Blast Radius und manuelle Betreuung.
- **Risiken / Empfehlungen:** Erst Lastmodell und Single-Instance-Grenzen dokumentieren; dann stateless API, externe Jobownership, verteilte Limits und DB-HA schrittweise entscheiden.
- **Operatorfragen:** Betrieb: nur klein. Erkennung: keine Kapazitätsalarme. Behebung: vertikal/manuell. Reproduzierbar: nein. Rollback: nein. Ursache: unbekannt unter Last. Nachtruhe: nein.
- **Evidence:** PS Enterprise/Scale, Engineeringarchitektur zukünftig; PB Core/Operations Findings; Repo Compose und In-process-Komponenten. Evidence Missing: Mehrinstanz-/HA-Nachweis.

### 28. Wartbarkeit

- **Executive Summary:** Code- und Dokumentstruktur sind brauchbar, aber fehlende Automatisierung und Wissenskonzentration erhöhen langfristige Änderungskosten.
- **Operations Review:** Modularer FastAPI-Monolith, Services, Schemas, Migrationen und Runbooks sind positiv. Große Router/UI-Dateien, verteilte Konfiguration und manuelle Abläufe belasten.
- **Quality Review:** Tests und Product Master Book helfen; Inventarzahlen driften bereits: PB nennt 224 Tests/25 Migrationen, HEAD enthält 260/27.
- **Security Operations Review:** Manuelle Security-/Releaseprozesse sind fehleranfällig und personenabhängig.
- **Support Review:** Neue Operatoren können viel lesen, aber nicht alle Abläufe reproduzierbar ausführen.
- **Risiken / Empfehlungen:** Automatisierung vor Refactoring priorisieren; Ownership, ADRs, Runbooktests und synchronisierte Evidenz etablieren.
- **Operatorfragen:** Betrieb: durch Kernteam. Erkennung: teilweise. Behebung: expertise-heavy. Reproduzierbar: unvollständig. Rollback: unvollständig. Ursache: meist im Code/Log. Nachtruhe: bedingt nein.
- **Evidence:** PS Scalable Documentation/Traceability; PB Quality/Inventory; Repo Struktur, Tests, Audits und Driftvergleich. Evidence Missing: Bus-Factor-/Handover-Test.

### 29. Administrationsprozesse

- **Executive Summary:** Umfangreiche Adminfunktionen und Audit Events existieren, aber keine Enterprise Operations Governance.
- **Operations Review:** Tenants, Lizenzen, Credits, Pricing, Inhalte und Partner können administriert werden. Änderungen sind teilweise auditierbar.
- **Quality Review:** Admin-, Pricing- und Configurationtests sind breit; reale Bedien-, Fehler- und Rollbackabläufe fehlen.
- **Security Operations Review:** Eine Basic-Adminidentität, keine Rollen, kein Vier-Augen-Prinzip, keine zeitlich begrenzten Rechte und kein Break-glass-Audit.
- **Support Review:** Pilotinterventionen sind möglich, aber gefährlich zentralisiert.
- **Risiken / Empfehlungen:** SOPs und RACI pro kritischer Aktion, benannte Identitäten, Approval, Change Ticket, Vor-/Nachprüfung und Rücknahme definieren.
- **Operatorfragen:** Betrieb: kleines Team bedingt. Erkennung: Audit nach Aktion. Behebung: manuell. Reproduzierbar: nicht vollständig. Rollback: je Aktion uneinheitlich. Ursache: Audit teilweise. Nachtruhe: nein.
- **Evidence:** PS Product Architecture/Admin Portal und Enterprise Ready; PB `admin-backend.md`; Repo Adminroutes, Basic Auth, CSRF, Audit Service/Tests. Evidence Missing: operative Governance und Access Reviews.

## Cross-Capability Findings

1. Die Plattform besitzt technische Betriebsbausteine, aber kein geschlossenes Enterprise Operations System.
2. Deployment ist automatisiert, Release Safety nicht: Der Workflow deployt ungeprüften Branchstand direkt auf den Zielhost.
3. Observability endet weitgehend bei strukturierten Logs und Healthchecks; Metriken, Traces, Alerts und SLOs fehlen.
4. Recoverability ist dokumentiert, nicht bewiesen: Backup, Restore, Rollback und Disaster Recovery besitzen keine ausgeführten Drills.
5. Security Controls sind stärker als Security Operations; Detection, Rotation, Access Review und Incident Readiness fehlen.
6. Die Backend-Testbasis ist breit, aber ihre releaseblockierende Ausführung fehlt; AL und Performance bleiben ungetestete Betriebsgrenzen.
7. Single-Host/Single-Instance ist für einen handgeführten Pilot akzeptierbar, muss aber explizit als Grenze betrieben werden.
8. Product Master Book driftet gegen HEAD und kann ohne automatischen Abgleich nicht als aktueller Operationsindex dienen.

## Evidence Grenzen

- Keine Produktions-, GitHub-Environment-, Server-, Cloud-, DNS-, Registry-, Monitoring- oder Ticket-System-Zugriffe.
- Keine laufenden Tests, Deployments, Migrationen, Backups oder Restores wurden im Assessment ausgelöst.
- Keine nicht commitierte Änderung wurde als positive Evidenz verwendet.
- Keine Aussagen über tatsächliche Verfügbarkeit, Datenvolumen, Incidenthistorie oder Kunden-SLA.
- Landingpage, Dashboard UX, Scan-Produktfunktion, Executive Report, Pricing, Branding und Marketing sind ausgeschlossen.

`assessment_status=reviewed`; `assessment_owner=Chief Product Architect`; `last_assessed_at=2026-07-21`; `assessment_confidence=medium`. Die statische Evidenz ist breit, die Runtime- und Betriebsevidenz jedoch schwach.
