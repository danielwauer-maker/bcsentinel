# Core Platform Top Findings

Alle Findings sind Ableitungen aus [Core Platform Assessment](CORE_PLATFORM_ASSESSMENT.md). Die dort definierten Evidence Bundles enthalten jeweils Product-System-, Product-Book- und Repository-Referenzen. Individuelle Zuordnung:

- Strengths 1–10: `E-AUTHZ`, `E-REG`, `E-LIC`, `E-BILL`, `E-LIC`, `E-BACK`, `E-BACK`, `E-EXT`, `E-BACK/E-EXT`, Product Master Book.
- Risks 1–10: `E-BACK`, `E-EXT`, `E-BILL/E-SUB`, `E-AUTHZ`, `E-BILL/E-SUB`, `E-BACK`, `E-API`, `E-CONF`, `E-BACK`, Product Master Book plus Repository-HEAD.
- Quick Wins 1–10: `E-BACK`, Assessment Contract, `E-BILL/E-SUB`, `E-EXT/E-REG`, `E-AUTH/E-CONF`, `E-API`, `E-BACK`, `E-AUTH/E-REG`, `E-BILL/E-SUB`, Product Master Book plus Repository-HEAD.
- Go-Live Blockers 1–10: `E-BACK`, `E-EXT`, `E-AUTHZ`, `E-BILL/E-SUB`, `E-AUTHZ`, `E-BACK`, `E-BACK`, `E-API`, `E-CONF`, Assessment Contract.

## Top 10 Strengths

| # | Priorität | Stärke | Auswirkung und Begründung | Empfehlung |
|---:|---|---|---|---|
| 1 | P0 | Tenantgebundene Authentifizierung | Hashing, Header-/Pfad-/Payloadabgleich und Migration von Legacytokens schaffen eine starke Sicherheitsbasis. | Als unverhandelbaren Plattformvertrag erhalten und mit Rotation ergänzen. |
| 2 | P0 | Idempotente Tenantregistrierung | Stabile BC-Identität, Upsert und DB-Constraints reduzieren Doppel- und Fehlzuordnung. | Mit realem Sandbox-/Recovery-Test freigeben. |
| 3 | P0 | Atomare Creditverarbeitung | Transaktion, Row Locking, Request-Idempotenz und Ledger schützen kommerzielle Korrektheit. | PostgreSQL-Konkurrenzlauf als Release-Gate etablieren. |
| 4 | P0 | Stripe-Webhook-Idempotenz | Signaturprüfung und Eventreservierung adressieren zentrale Billingrisiken. | Um Reconciliation und Event-Recovery erweitern. |
| 5 | P1 | Produktentitlements und Ablauf | Frische Access Snapshots, Credits und Subscriptionperioden bilden ein differenziertes SaaS-Modell. | Taxonomie und Legacyaliases kontrolliert konsolidieren. |
| 6 | P1 | Health und Readiness | Separate Liveness-/DB-Readiness und Deploymentchecks verbessern Betriebsfähigkeit. | Um SLOs, Metrics und Alerting ergänzen. |
| 7 | P1 | Observability-Grundlagen | Request IDs, strukturierte Logs und Redaction erleichtern Diagnose und Datenschutz. | Externe Aggregation und Alertketten nachweisen. |
| 8 | P1 | Native BC-Lifecycle-Integration | Install-/Upgrade-Codeunits und Setupmodell respektieren die Zielplattform. | Native AL-Regression und Upgrade-Drill ergänzen. |
| 9 | P1 | Breite Python-Testbasis | Kritische Auth-, Billing-, Tenant- und Lifecyclepfade sind als Tests vorhanden. | Automatisch in CI und gegen PostgreSQL ausführen. |
| 10 | P2 | Evidenzorientiertes Product Master Book | Features, Workflows, Tests, Gaps und Unsicherheiten sind nachvollziehbar modelliert. | Bei jedem freigegebenen Commit synchronisieren. |

## Top 10 Risks

| # | Priorität | Risiko | Auswirkung und Begründung | Empfehlung |
|---:|---|---|---|---|
| 1 | P0 | Keine CI-Teststufe | Ungetesteter Code kann direkt deployt werden. | Deployment zwingend an Backend-, Contract- und Migrationstests koppeln. |
| 2 | P0 | Keine AL-Test-App | Kritische BC-Flows besitzen keine native Regression. | AL-Testprojekt für Setup, Registrierung, Auth, Install und Upgrade schaffen. |
| 3 | P0 | Keine reale Stripe-E2E-Evidenz | Zahlungs-, Abo- und Eventfehler bleiben bis zum Kunden verborgen. | Vollständige Testmode-Matrix ausführen und belegen. |
| 4 | P0 | Unvollständige Authorization Governance | Basic Admin und verteilte Guards skalieren nicht zu Enterprise-Rollen. | Zentrale Policy, RBAC und Negativtestmatrix definieren. |
| 5 | P0 | Fehlende Billing Reconciliation | Verlorene oder verspätete Events können Umsatz und Zugang entkoppeln. | Periodischen Abgleich und Exception Queue etablieren. |
| 6 | P0 | Kein Mehrinstanznachweis | In-Process-Jobs und lokale Mechanismen können bei Skalierung doppelt oder gar nicht laufen. | Skalierungsmodell entscheiden und unter Konkurrenz testen. |
| 7 | P1 | Kein API-Lifecycle-Vertrag | Clientverträge können durch Änderungen brechen. | Versionierung, Deprecation und Consumer Contracts einführen. |
| 8 | P1 | Konfigurations-Blast-Radius | Preis-, Gate- oder Sichtbarkeitsänderungen ohne Promotion/Rollback können alle Kunden treffen. | Vier-Augen-Freigabe, Audit und Rollback etablieren. |
| 9 | P1 | Migrations-/ORM-Testabweichung | Standardtests beweisen nicht durchgehend den realen Upgradepfad. | Release Candidate immer per Alembic gegen PostgreSQL prüfen. |
| 10 | P1 | Knowledge Drift | Master Book und HEAD unterscheiden sich bei Tests/Migrationen; Entscheidungen können auf veraltetem Ist beruhen. | Inventar an freigegebenen Commit binden und automatisch prüfen. |

## Top 10 Quick Wins

| # | Priorität | Quick Win | Auswirkung und Begründung | Empfehlung |
|---:|---|---|---|---|
| 1 | P0 | Tests vor Deployment ausführen | Nutzt vorhandene Tests und entfernt sofort ein großes Release-Risiko. | Separaten CI-Testjob als Pflichtcheck definieren. |
| 2 | P0 | Pilot-Commit einfrieren | Verhindert, dass uncommittete oder nachlaufende Änderungen in die Abnahme geraten. | Commit, Image Digest und Master-Book-Stichtag gemeinsam protokollieren. |
| 3 | P0 | Stripe-Testmode-Matrix abarbeiten | Vorhandene Flows können ohne Produktionszahlung real verifiziert werden. | Checkout, Webhook, Renewal, Failure, Cancel und Portal protokollieren. |
| 4 | P0 | BC-Sandbox-Smoke automatisierbar protokollieren | Schließt die größte Plattform-Evidenzlücke. | Installation, Registrierung, Lizenzabruf und Upgrade mit Belegen abnehmen. |
| 5 | P0 | Adminzugang begrenzen | Reduziert sofort Blast-Radius vor vollem RBAC. | Separate starke Credentials, Netzwerkgrenze und benannte Operatoren erzwingen. |
| 6 | P1 | API-Contract-Snapshot | Macht Breaking Changes sichtbar, bevor umfassende Versionierung existiert. | OpenAPI-Artefakt versionieren und diffen. |
| 7 | P1 | PostgreSQL-Migrationslauf | Nutzt vorhandene Migrationen und Tests für reale Schemaevidenz. | Leere und aktualisierte DB bis Head testen. |
| 8 | P1 | Token-Lifecycle-Runbook | Schließt sofort eine Support- und Securitylücke. | Rotation, Widerruf, Kompromittierung und Recovery dokumentieren/testen. |
| 9 | P1 | Billing Exception Report | Macht Provider-/DB-Differenzen früh sichtbar. | Täglichen manuellen Abgleich für den ersten Pilot definieren. |
| 10 | P2 | Master Book resynchronisieren | Stellt eine belastbare Ist-Quelle für Entscheidungen her. | Nach Freeze Counts, Migrationen und Evidenz neu validieren. |

## Top 10 Go-Live Blockers

| # | Priorität | Blocker | Auswirkung und Begründung | Empfehlung |
|---:|---|---|---|---|
| 1 | P0 | Deployment ohne Testgate | Ein fehlerhafter Commit kann trotz vorhandener Tests produktiv gehen. | Merge/Deploy bei fehlendem Testnachweis blockieren. |
| 2 | P0 | Fehlender nativer BC-Testnachweis | Kernclient ist in Zielruntime nicht reproduzierbar abgesichert. | AL-Tests und Sandboxabnahme verpflichtend machen. |
| 3 | P0 | Unbewiesener Tenant-Isolationsbetrieb | Potentieller Cross-Tenant-Zugriff ist nicht akzeptierbar. | Mehrtenant-Staging-Negativtests abschließen. |
| 4 | P0 | Unbewiesener produktiver Billing-Lifecycle | Finanzielle Fehler sind nicht verantwortbar. | Provider-E2E plus Reconciliation nachweisen. |
| 5 | P0 | Kein belastbares Admin-RBAC | Globaler Basic-Adminzugang erfüllt kein Enterprise-Least-Privilege. | Rollen, individuelle Identitäten und Audit einführen. |
| 6 | P0 | Kein Mehrinstanz-/Jobmodell | Skalierung kann Recovery und Jobs inkonsistent machen. | Single-/Multi-Instance-Entscheidung, Locks und Workerbetrieb belegen. |
| 7 | P0 | Fehlende Incident-/Recovery-Verantwortung | Ausfälle können nicht kontrolliert bearbeitet werden. | On-call, Eskalation, RTO/RPO und Drills definieren. |
| 8 | P1 | Kein API Compatibility Gate | Extension und Integrationen können ungeplant brechen. | Versionierungs- und Contract-Test-Gate etablieren. |
| 9 | P1 | Keine Konfigurationsfreigabe/Rollback | Fehlkonfiguration kann Preise und Zugänge systemweit verfälschen. | Promotion, Approval, Audit und Rollback nachweisen. |
| 10 | P1 | Nicht synchroner Assessment-Baseline | Freigabe wäre nicht reproduzierbar. | Repository, Inventar, Tests und Releaseartefakt auf einen Commit fixieren. |
