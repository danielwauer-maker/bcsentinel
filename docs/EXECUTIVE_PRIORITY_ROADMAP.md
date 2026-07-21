# Executive Priority Roadmap

Stand: 2026-07-21

## Roadmap-Prinzip

Die Roadmap konsolidiert ausschließlich Maßnahmen, die bereits in Core Platform, Scan Engine, Customer Experience oder Operations Assessment empfohlen wurden. Sie ist nach Unternehmenswert und Freigabegate geordnet, nicht nach Komponenten. Aufwand ist eine grobe Executive-T-Shirt-Schätzung und keine Lieferzusage.

## P0 — Vor Pilot zwingend

| # | Maßnahme | Business Impact | Customer Impact | Operational Impact | Aufwand | Abhängigkeiten |
|---:|---|---|---|---|---|---|
| 1 | Release Candidate einfrieren: Commit, Image-Digest, Alembic-Head, Konfiguration und Evidenzstichtag | Verhindert Investition in eine bewegliche Baseline | Kunde erhält genau den geprüften Stand | Macht Support und Rollback nachvollziehbar | S | Release Owner, Build, Master Book |
| 2 | Backend-/PostgreSQL-/Migrations-/Contract-Tests als Pflichtnachweis vor Pilotdeploy ausführen | Reduziert Ausfall- und Reputationsrisiko sofort | Verhindert bekannte Regressionen im Pilot | Schafft reproduzierbaren Go/No-Go-Beleg | M | Docker-Testtarget, Test-DB, CI/Releaseprozess |
| 3 | BC-Sandbox-Acceptance für Install, Registrierung, Permissions, Scan, Fehler/Retry und Upgrade durchführen | Schützt den primären Distributionskanal | Beweist den realen Kundeneinstieg | Reduziert plattformspezifische Supportüberraschungen | M | BC Sandbox, AL-Artefakt, Testtenant |
| 4 | Rule-/Score-/Severity-/Impact-Pilotbaseline versionieren | Schützt Produktvertrauen und zukünftiges IP | Ergebnis wird erklärbar und reproduzierbar | Erleichtert Diagnose und historische Vergleiche | M | Checkkatalog, Scoring, Reportreferenz |
| 5 | Finanzmodell transparent begrenzen und kundenseitig bestätigen | Verhindert Haftungs-/Reputationsschaden | Kunde erkennt Modell statt Versprechen | Senkt Eskalationen über falsche Erwartungen | S | Modellbaseline, Content, Pilotvertrag |
| 6 | Golden/Expected-Results-Lauf für Pilotmodule und High/Critical Findings abschließen | Beweist Kernwert statt nur Implementierung | Reduziert False Positives und Fehlpriorisierung | Liefert reproduzierbare Fehlerdiagnose | M | BC Sandbox, Golden Dataset, Fachowner |
| 7 | Tenantisolation, Adminzugang und Pilot-Secrets absichern | Schützt Existenz und Enterprise-Vertrauen | Verhindert fremden Datenzugriff | Begrenzter, nachvollziehbarer Operatorzugang | M | Mehrtenanttest, benannte Identitäten, Rotation |
| 8 | Zahlungsmodus festlegen und belegen | Ermöglicht verantwortbare erste Einnahmen | Klare Rechnung, Aktivierung und Support | Verhindert Billing-/Entitlement-Drift | M | Stripe-Testmode/Reconciliation oder manuelle Pilotabrechnung |
| 9 | Deployment-/Rollback- und Backup-/Restore-Drill ausführen | Begrenzt existenziellen Ausfall- und Datenverlust | Kunde erhält belastbare Recoveryzusage im Pilotscope | Beweist Wiederanlauf statt nur Runbook | M | Release Candidate, Testumgebung, Backupziel |
| 10 | Incident- und Supportmodell für den Pilot benennen | Schützt Reputation und Kundenbeziehung | Klarer Kanal, Reaktionsweg und Eskalation | Primary/Backup, Severity, Abbruchkriterien | S | Founder, Operations, Customer Success |
| 11 | Pilot-Customer-Journey kanonisieren und öffentliche Vertrauensfehler entfernen | Erhöht Conversion und schützt Marke | Klarer Einstieg ohne CTA-, Sprach- oder Placeholderbruch | Reduziert vermeidbare Supportfälle | M | Landingpage, Onboarding, Content Review |
| 12 | Tatsächlichen Pilotreport visuell und fachlich freigeben | Stärkt stärkstes Verkaufsartefakt | CEO/CFO erhalten belastbare Darstellung | Verhindert PDF-, Locale- und Extremwertfehler | S | Realscan, Modellbaseline, Fachreview |
| 13 | Pilotvertrag und Outcome-Messung festlegen | Verwandelt Pilotkosten in Unternehmenswissen | Erwartungen und Entscheidungsgrenzen sind klar | Definiert Feedback, Owner und Exit | S | Kunde, CPO, Legal/Commercial Review |

## P1 — Vor allgemeinem Go-Live

| # | Maßnahme | Business Impact | Customer Impact | Operational Impact | Aufwand | Abhängigkeiten |
|---:|---|---|---|---|---|---|
| 1 | CI und CD trennen; immutable Image bauen, testen, scannen, signieren und promoten | Senkt Änderungsrisiko dauerhaft | Stabilere Releases | Approval, Provenance und sicherer Rollback | L | Registry, GitHub Environments, CI Gates |
| 2 | Native AL-Regression als dauerhaftes Release-Gate etablieren | Schützt Wachstum im BC-Ökosystem | Weniger Upgrade-/Permission-/Schedulerfehler | Automatisierte Sandboxevidenz | L | AL-Test-App, Toolchain, BC Sandbox |
| 3 | Zentrales Monitoring, Logging, Telemetry und Alerting operationalisieren | Reduziert Ausfallkosten und Reputationsverlust | Probleme werden vor Kundenmeldung erkannt | SLO-nahe Signale, Pager und Runbooks | L | Observability Backend, On-call, Signalmodell |
| 4 | Automatisiertes Off-host-Backup und regelmäßige Restore-/DR-Kadenz einführen | Schützt Unternehmensfortbestand | Belastbarere Daten- und Servicewiederherstellung | RTO/RPO werden messbar | L | Backup Storage, Verschlüsselung, Ersatzumgebung |
| 5 | IAM-/Admin-RBAC-, MFA/SSO-, Access-Review- und Secret-Lifecycle schließen | Erfüllt Procurement-Erwartungen | Höheres Sicherheitsvertrauen | Sichere Delegation an Team und Support | XL | Identity-Zielbild, Rollenmatrix, Secret Store |
| 6 | Billing Reconciliation, Exception Handling und vollständigen Subscription Lifecycle belegen | Schützt Umsatz und Unternehmensbewertung | Korrekte Belastung und Freischaltung | Fehler werden erkannt und repariert | L | Provider-E2E, Audit, Finance Operations |
| 7 | API Compatibility und Konfigurationspromotion kontrollieren | Verhindert Client- und Umsatzbrüche | Stabilere Extension und konsistente Angebote | Versionierung, Approval, Audit, Rollback | L | OpenAPI Snapshot, Config Catalog, Environments |
| 8 | Öffentliche Free-/Onboarding-/Checkout-/Upgrade-Journey end-to-end abnehmen | Ermöglicht skalierbare Akquisition | Verständlicher Self-Service-Pfad | Weniger manuelle Interventionen | L | Produktstufen, CTA, Billing, Activation |
| 9 | Findings- und Action-Lifecycle mit Evidence, Owner, Status und Validation schließen | Erhöht realisierten Kundennutzen | Diagnose führt messbar zur Verbesserung | Support und Outcome werden nachvollziehbar | L | Model Snapshot, Dashboard/Report, Customer Success |
| 10 | Gemeinsames Brand-/Design-/Content-System inklusive Accessibility-Gate anwenden | Erhöht Enterprise-Vertrauen | Konsistente und zugängliche Experience | Senkt UI-/Content-Drift | L | Design Tokens, Glossar, Browser-/Accessibility-QA |

## P2 — Vor Enterprise-Skalierung

| # | Maßnahme | Business Impact | Customer Impact | Operational Impact | Aufwand | Abhängigkeiten |
|---:|---|---|---|---|---|---|
| 1 | Performance-, Load-, Soak- und Capacity-Baselines erstellen | Macht Wachstumsinvestitionen planbar | Verlässliche Laufzeiten und Grenzen | SLOs und Ressourcenbudgets werden steuerbar | L | Realdatenprofile, Telemetrie, Testumgebung |
| 2 | Mehrinstanz-, Jobownership-, Rate-Limit- und Worker-Modell belegen | Ermöglicht horizontales Wachstum | Reduziert Doppelverarbeitung und Ausfälle | Klare Failure Isolation und Konkurrenzkontrolle | XL | Capacity Baseline, DB Locks, Queue/Leader-Entscheidung |
| 3 | Datenbank-HA, Failover und vollständigen Disaster Drill nachweisen | Schützt größere Kundenbasis | Höhere Verfügbarkeit und Recoverability | Reduziert Single-Host-Blast-Radius | XL | RTO/RPO, Backup/Restore, Infrastrukturmodell |
| 4 | Enterprise Supportorganisation und Problem Management etablieren | Senkt Founderabhängigkeit und erhöht Marge | Wiederholbarer Support mit klaren SLAs | Schichten, Tickets, KB, Postmortems, Trends | L | On-call, RBAC, Telemetrie, Customer Success |
| 5 | Outcome-validierten BC Benchmark aufbauen | Schafft differenzierbares IP und Pricing Power | Belegt Relevanz, False Positives und Nutzen | Unterstützt Regression und Capacity Planning | XL | Mehrere Pilotdatensätze, Consent, Modellversionen |
| 6 | Partnerfähige, wiederholbare Delivery- und Governance-Pakete etablieren | Skaliert Vertrieb und Implementierung | Konsistente Kundenergebnisse | Reduziert individuelle Founderarbeit | L | Report/Action Contract, Support, Training, Evidenz |
| 7 | Normative Operations-, API-, IAM- und Reporting-Verträge im Product System verankern | Erhöht Due-Diligence- und Organisationsfähigkeit | Klare Qualitätszusagen | Entscheidungen bleiben bei Teamwachstum konsistent | M | Validierte P1/P2-Erkenntnisse, Owner, Reviewprozess |

## P3 — Langfristige Optimierung

| # | Maßnahme | Business Impact | Customer Impact | Operational Impact | Aufwand | Abhängigkeiten |
|---:|---|---|---|---|---|---|
| 1 | Product Master Book und Releaseevidenz automatisch aus Build/Test/Registry synchronisieren | Senkt Governancekosten und erhöht Unternehmenswert | Indirekt stabilere Releases | Entfernt Knowledge Drift | L | CI/CD, Release Manifest, Inventarvalidator |
| 2 | Kundenspezifische Impactkalibrierung und Benchmarks reifen lassen | Erhöht Differenzierung und Monetarisierung | Präzisere, glaubwürdigere Business Cases | Versionierbare Modelle und Vergleichsdaten | XL | Outcome Benchmark, Governance, Datenbasis |
| 3 | Design-, Content- und Reportregression über alle Locales automatisieren | Schützt Marke bei Wachstum | Konsistente internationale Experience | Weniger manuelle Release-QA | L | Design System, Golden Screens/PDFs, Browsermatrix |
| 4 | Betriebs- und Produktkosten je Tenant/Scan/Report messbar machen | Verbessert Unit Economics und Investitionsentscheidungen | Nachhaltige Servicequalität | Capacity- und Kostensteuerung | L | Telemetrie, Billing, Capacity Model |

## Freigabelogik

Eine Prioritätsstufe ist nicht durch Dokumentation allein abgeschlossen. Maßgeblich ist der in den Assessments geforderte Ausführungsnachweis. P0 schließt nur den definierten Pilotkontext. P1 ermöglicht eine erneute öffentliche Go-Live-Entscheidung. P2 ermöglicht eine erneute Enterprise-Rollout-Entscheidung. Keine Stufe ersetzt ein formales Go/No-Go.
