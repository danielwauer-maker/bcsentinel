# Enterprise Risk Register

Stand: 2026-07-21

## Konsolidierungsregeln

Das Register führt ausschließlich Risiken zusammen, die bereits in den vier abgeschlossenen Assessment-Sets dokumentiert sind. Inhaltlich gleiche Risiken wurden zu einem Unternehmensrisiko verdichtet. Eintrittswahrscheinlichkeit und Auswirkung sind qualitative Konsolidierungen der vorhandenen Risiko-, Criticality- und Readiness-Aussagen, keine neue Gesamtbewertung.

Quellcodes:

- `CP`: Core Platform Assessment/Readiness/Top Findings/Executive Review
- `SE`: Scan Engine Assessment/Readiness/Top Findings/Executive Review
- `CX`: Customer Experience Assessment/Readiness/Top Findings/Executive Review
- `OP`: Operations Assessment/Readiness/Top Findings/Executive Review

## Dedupliziertes Risikoregister

| ID | Beschreibung | Quelle(n) | Kategorie | Eintritt | Auswirkung | Priorität | Pilotkritisch | Go-Live-kritisch | Skalierungskritisch | Empfohlene Maßnahme | Owner (empfohlen) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ER-01 | Deployment kann ohne releaseblockierenden Testnachweis erfolgen. | CP, OP | Release/Quality | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | CI vor CD; Backend-, PostgreSQL-/Migration-, Contract- und Securitytests als Required Gate. | CTO / QA Lead |
| ER-02 | Keine native AL-Test-App und keine automatisierte BC-Sandbox-Regression. | CP, SE, OP | Product Quality | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | AL-Testprojekt plus Sandboxpipeline für Install, Upgrade, Permissions, Scheduler, Scan und Fehlerpfade. | BC Engineering Lead |
| ER-03 | Tenantisolation, Adminautorisierung und rollenfeine IAM-Governance sind nicht end-to-end bewiesen. | CP, OP | Security/Governance | Mittel | Sehr hoch | P0 | Ja | Ja | Ja | Mehrtenant-Negativtests, benannte Identitäten, zentrale Rollenmatrix, MFA/SSO-Ziel und Access Reviews. | Security Owner / CTO |
| ER-04 | Billing-/Subscription-Lifecycle ist nicht real end-to-end validiert; Reconciliation und Exception Recovery fehlen. | CP, CX | Commercial/Operations | Mittel | Sehr hoch | P0 | Ja bei Zahlung | Ja | Ja | Stripe-Testmode-Matrix, täglicher Abgleich im Pilot, Exception Queue und auditierbarer Recoverypfad. | Finance Operations / CTO |
| ER-05 | Rule-, Score-, Severity- und Impactlogik ist nicht versioniert und historisch reproduzierbar. | SE, CX | Product Trust | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Pilotbaseline versionieren und je Report/Scan referenzieren. | Product Intelligence Owner |
| ER-06 | Centgenaue Verlustwerte und pauschaler Saving-Faktor suggerieren mehr Sicherheit als belegt. | SE, CX | Reputation/Commercial | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Werte als Modellschätzung kennzeichnen; Formel, Annahmen, Confidence, Doppelzählung und Kundenbestätigung zeigen. | CPO / Finance Domain Owner |
| ER-07 | Severity kann aus Ratio, statischem Risk Level und Impact-Eskalation unterschiedlich entstehen. | SE | Product Quality | Mittel | Hoch | P0 | Ja | Ja | Ja | Eine kanonische Severity-Semantik dokumentieren, versionieren und mit Expected Results prüfen. | Product Intelligence Owner |
| ER-08 | Findings fehlen vollständige Evidence Lineage, Modellversion, Confidence, Scope und Remediation Lifecycle. | SE, CX | Product Trust | Hoch | Hoch | P1 | Bedingt | Ja | Ja | Findings-/Report-Vertrag um nachvollziehbare Basis und Action-Lifecycle ergänzen. | CPO / Data Product Lead |
| ER-09 | Checkkatalog, ausgewiesene Checkanzahl und Kerndokumentation driften; Baseline nennt unterschiedliche Zahlen. | SE, CP | Knowledge/Quality | Hoch | Hoch | P0 | Ja | Ja | Ja | Katalog aus ausführbarer Registry generieren; leere Check-/Scoring-Dokumente füllen; Zahlen automatisch prüfen. | Product Architect / QA Lead |
| ER-10 | Laufzeit, Locking und Ressourcenverhalten auf großen realen BC-Datenbeständen sind unbekannt. | SE, OP | Performance | Hoch | Sehr hoch | P1 | Bedingt | Ja | Ja | Golden/Representative Dataset sowie Last-, Locking- und Soakprofil in BC messen und Grenzen publizieren. | Performance Owner / BC Lead |
| ER-11 | Produktions-PDF, Extremwerte, Seitenumbrüche, Fonts und DE/EN-Rendering sind nicht freigegeben. | SE, CX | Reporting/Quality | Mittel | Hoch | P0 | Ja | Ja | Bedingt | Reales Pilot-PDF visuell abnehmen; Golden Render, Extraktion, Overflow und Locale-Vertrag prüfen. | Product Design / QA Lead |
| ER-12 | Relevanz, False Positives, Zahlungsbereitschaft und realisierte Outcomes sind nicht kundenseitig belegt. | SE, CX | Market/Product | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Design-Partner-Pilot mit vorab definierten Outcome-, Relevanz- und Fortsetzungskriterien. | Founder / CPO |
| ER-13 | API besitzt keinen freigegebenen Versionierungs-, Deprecation- oder Compatibility-Vertrag. | CP | Architecture/Release | Mittel | Hoch | P1 | Bedingt | Ja | Ja | OpenAPI-Snapshot, Consumer Contracts, Versionierung und Deprecation Policy. | API Owner / CTO |
| ER-14 | Kritische Konfiguration kann ohne kontrollierte Promotion, Vier-Augen-Freigabe oder einheitlichen Rollback geändert werden. | CP, OP | Configuration/Governance | Mittel | Sehr hoch | P0 | Ja | Ja | Ja | Konfigurationskatalog, Approval, Environment-Promotion, Audit sowie Vor-/Nach- und Rollbackprüfung. | Operations Lead / Product Ops |
| ER-15 | Keine zentrale Monitoring-, Metrics-, Tracing- und Alertingkette; Kunden können erster Incident-Sensor sein. | CP, OP | Operations | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Uptime, 5xx, Latenz, Ressourcen, DB, Jobs und externe Abhängigkeiten mit Alarm, Owner und Runbook überwachen. | Head of Operations |
| ER-16 | Backup und Restore sind manuell beschrieben, aber weder automatisiert noch erfolgreich gedrillt. | CP, OP | Recoverability | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Verschlüsseltes Off-host-Backup automatisieren; Restore messen und regelmäßig protokollieren. | Database/Operations Owner |
| ER-17 | Kein Disaster-Recovery-/HA-Modell mit RTO/RPO; Single Host und lokale DB bilden gemeinsame Failure Domain. | CP, OP | Business Continuity | Mittel | Sehr hoch | P1 | Bedingt | Ja | Ja | RTO/RPO, Ersatzinfrastruktur, Daten-/Secret-/DNS-Recovery und Disaster Drill definieren. | CTO / Head of Operations |
| ER-18 | Incident Response und Support sind founder- und expertenabhängig; On-call, Severity, Statuskommunikation und Postmortem fehlen. | CP, CX, OP | Organization/Support | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Primary/Backup, Incident Commander, Severity, Eskalation, Kundenkommunikation, Tickets, Runbooks und Übungen. | Founder / Customer Success Lead |
| ER-19 | Secrets besitzen keinen nachgewiesenen zentralen Lifecycle für Inventar, Rotation, Widerruf und Leak Response. | CP, OP | Security Operations | Mittel | Sehr hoch | P0 | Ja | Ja | Ja | Secret-Inventar, Owner, Rotationstest, Notfallwiderruf; später zentraler Store/kurzlebige Identitäten. | Security Owner |
| ER-20 | Keine Performance-, Capacity- oder SLO-Baseline für Kunden-, Scan-, Report-, Job- und Datenwachstum. | CP, SE, OP | Scalability | Hoch | Sehr hoch | P1 | Bedingt | Ja | Ja | Kritische Lastprofile definieren, messen und mit Ressourcenbudgets/SLOs verknüpfen. | CTO / Performance Owner |
| ER-21 | In-process Jobs und Rate Limits sowie feste Single-Instance-Topologie besitzen kein belastbares Mehrinstanzmodell. | CP, OP | Architecture/Scalability | Mittel | Sehr hoch | P1 | Nein im begrenzten Single-Instance-Pilot | Ja | Ja | Single-Instance-Grenze festhalten; Jobownership, verteilte Limits, DB-HA und Mehrinstanztest entscheiden. | CTO / Platform Lead |
| ER-22 | Standardtests beweisen reale Alembic-Upgrades, Datenvolumen und sicheren Rollback nicht durchgehend. | CP, OP | Data/Release | Mittel | Sehr hoch | P0 | Ja | Ja | Ja | Leere und aktualisierte PostgreSQL-Kopie bis Head migrieren; Backup-ID, Vor-/Nachchecks und Downgradegrenzen dokumentieren. | Database Owner / QA Lead |
| ER-23 | Öffentliche CTA-, Pricing- und Checkout-Ziele sind widersprüchlich; erwarteter Kauf endet im Kontaktformular. | CX, CP | Commercial/CX | Hoch | Hoch | P0 für zahlenden Kunden | Bedingt | Ja | Ja | Einen wahrheitsgemäßen CTA pro Zustand und einen durchgängigen Kauf-/Aktivierungs-/Rückkehrpfad schaffen. | CPO / Growth Owner |
| ER-24 | Free Score, Onboarding, Registrierung und Upgrade bilden keine durchgängige erste Wertkette. | CX, CP | Customer Success | Hoch | Hoch | P0 | Ja | Ja | Ja | Kanonischen Free-to-Result-to-Upgrade-Pfad mit Scope, Fortschritt, Fehlern und nächster Aktion abnehmen. | CPO / Customer Success Lead |
| ER-25 | Sprachfehler, Placeholder-Keys sowie MVP-/Mockup-/Template-/vorläufige öffentliche Inhalte beschädigen Vertrauen. | CX | Reputation/Brand | Hoch | Sehr hoch | P0 | Ja | Ja | Ja | Customer-visible Fehler entfernen, DE/EN professionell lektorieren, unfertige Seiten finalisieren oder ausblenden. | CPO / Content Owner |
| ER-26 | Landingpage, Portal, Dashboard und Report besitzen inkonsistente Brand-, Design- und Informationsarchitektur; Browser-/Accessibility-Evidenz fehlt. | CX | Brand/CX Quality | Hoch | Hoch | P1 | Bedingt | Ja | Ja | Gemeinsame Tokens/Taxonomie; Desktop-, Mobile-, Keyboard-, Screenreader- und Payload-Abnahme. | Design Lead / QA Lead |
| ER-27 | Actions besitzen keinen vollständig belegten Owner-, Status-, Validierungs- und Outcome-Lifecycle. | SE, CX | Customer Value | Hoch | Hoch | P1 | Ja | Ja | Ja | Top Findings mit Why, Owner, Action, Status und Validation im Produkt/Report konsequent führen. | CPO / Customer Success Lead |
| ER-28 | Product Master Book, Assessment-Baselines und Repository-Stände driften; Freigabe kann auf veralteter Evidenz beruhen. | CP, SE, OP | Governance/Knowledge | Hoch | Hoch | P0 | Ja | Ja | Ja | Release auf Commit, Image, Migration, Konfiguration und Master-Book-Stichtag fixieren; Drift automatisch prüfen. | Product Architect / Release Owner |

## Konzentrationsanalyse

Die höchste Priorität erhalten Risiken, die in mindestens zwei Assessments übereinstimmend auftreten oder als Pilot-/Go-Live-Gate dokumentiert sind. Besonders starke Konvergenz besteht bei:

- CI/AL-/Releaseevidenz (`CP`, `SE`, `OP`);
- fachlicher Erklärbarkeit finanzieller Aussagen (`SE`, `CX`);
- IAM/RBAC, Konfiguration und Secrets (`CP`, `OP`);
- Monitoring, Recovery, Incident und Skalierung (`CP`, `OP`);
- Customer Journey und kommerziellem Vertrauen (`CX`, unterstützt durch `CP`);
- reproduzierbarer Baseline und Knowledge Drift (`CP`, `SE`, `OP`).

## Akzeptanzgrenze

P0-Risiken dürfen vor dem jeweiligen Pilot- oder Zahlungskontext nur dann offen bleiben, wenn das zugrunde liegende Assessment ausdrücklich eine kontrollierende Ersatzmaßnahme erlaubt. Nicht akzeptiert werden Cross-Tenant-Risiko, unbelegte echte Zahlung, Deployment ohne Testnachweis, fehlender verwertbarer Restore, unkontrollierte Secrets oder finanzielle Aussagen ohne transparente Modellgrenze.
