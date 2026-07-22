# Phase 8 — Feature-Gap-Analyse

**Stand:** 2026-07-22  
**Produktbaseline:** `ea5b597699790d3e0e9cea8384c8025c41f175b4`  
**Zweck:** Die kleinste Menge fehlender Fähigkeiten und Nachweise bestimmen, mit denen BCSentinel zu den besten Executive-Data-Health-Produkten für Business Central gehören kann.

## Bewertungsmethode

Dies ist kein Ideen-Katalog. Ein Gap ist nur enthalten, wenn es vertrauenswürdige Executive-Entscheidungen, belegbaren Kundennutzen, sicheren Pilotbetrieb, Enterprise-Adoption oder wiederholbare kommerzielle Auslieferung substanziell verbessert.

- **Business Impact, Kundenmehrwert und Differenzierung:** 0–10; 10 ist der höchste Wert.
- **Aufwand:** S, M, L oder XL als relative Produktgröße, nicht als Terminversprechen.
- **ROI:** sehr hoch, hoch, mittel oder niedrig unter Berücksichtigung von Wirkung, Aufwand und Risikoreduktion.
- **P0:** Pilot Blocker; vor dem ersten zahlenden Design Partner zu schließen oder explizit zu mitigieren.
- **P1:** hoher Business Value; direkt nach einer stabilen Pilotbaseline.
- **P2:** mittlerer Business Value; stärkt Wiederholbarkeit und Enterprise-Skalierung.
- **P3:** später strategisch sinnvoll; nicht für den ersten Beweis der Produktthese erforderlich.

## P0 — Pilot Blocker

| Feature Gap | Erforderliches Ergebnis | Business Impact | Aufwand | Kundenmehrwert | Differenzierung | ROI |
|---|---|---:|:---:|---:|---:|:---:|
| Reale Post-Fix-BC-Abnahme | Registrierung, Free Scan, Background Completion, Findings, Dashboard, Reportzugriff und Scheduled Run vollständig in der Zielumgebung BC 28.3 ausführen und Tenant-Evidenz archivieren. | 10 | M | 10 | 5 | sehr hoch |
| Fixierter Pilot Release Candidate | Backend, Extension, Regeln, Konfiguration und Dokumentation auf eine reproduzierbare Baseline mit explizitem Go/No-Go-Record fixieren. | 10 | S | 8 | 4 | sehr hoch |
| Versionierte Finding-Evidenz | Regel-, Score-, Severity- und Impact-Modellversion, Quellkontext und Berechnungsherkunft je Ergebnis persistieren; historische Scans dürfen nicht still uminterpretiert werden. | 10 | L | 10 | 9 | sehr hoch |
| Vertrauensmodell für Finanzwerte | Annahmen, Konfidenz, Bandbreiten, Doppelzählungskontrollen und Evidenzlabels für Financial Impact und Savings transparent definieren. | 10 | M | 10 | 10 | sehr hoch |
| Golden Dataset und Expertenreview | High-/Critical-Findings, False Positives, Severity und Finanzwerte gegen repräsentative, freigegebene BC-Daten validieren. | 10 | L | 10 | 8 | sehr hoch |
| Produktive PDF-Evidenz | Deutsche und englische Reports mit Real- und Extremdaten rendern, jede Seite prüfen und Zahlen gegen Findings und Dashboard abstimmen. | 9 | M | 10 | 9 | sehr hoch |
| Minimaler Pilotbetrieb | Zentrale Health-/Fehlersignale, Alert Owner, Backup, getesteter Restore, Rollback, Incidentpfad und Kundenvorlage etablieren. | 10 | L | 9 | 5 | sehr hoch |
| Automatisches Release-Gate | Backend-, PostgreSQL-, Migrations- und kritische Licensing-/Scan-Contract-Tests je Release Candidate ausführen und fehlerhafte Auslieferung blockieren. | 9 | M | 8 | 4 | sehr hoch |
| Pilot-Billing-Vertrag | Einen kommerziellen Modus Ende-zu-Ende beweisen: kontrollierte manuelle Rechnung oder Stripe-Test-/Live-Flow inklusive Credit-Reconciliation und Recovery. | 9 | M | 8 | 5 | hoch |
| Kanonische Pilot-Customer-Journey | Einen konsistenten Startpfad anbieten, sichtbare Platzhalter entfernen oder kennzeichnen, Onboardingverantwortung und Supportkontakt eindeutig machen. | 9 | M | 10 | 6 | sehr hoch |
| Tenant-/Admin-Security-Gate | Tenant Isolation, Admin Authentication, Secrets, Permissions, Audit Trail und Least-Privilege-Deployment für den fixierten Candidate verifizieren. | 10 | M | 9 | 6 | sehr hoch |

### P0-Exit-Regel

Der erste zahlende Design Partner startet erst, wenn jede P0-Zeile objektive Evidenz oder eine benannte, terminierte und vom Verantwortlichen akzeptierte Mitigation besitzt. Unit Tests allein schließen kein Realumgebungs- oder Betriebsmodell-Gap.

## P1 — Hoher Business Value

| Feature Gap | Erforderliches Ergebnis | Business Impact | Aufwand | Kundenmehrwert | Differenzierung | ROI |
|---|---|---:|:---:|---:|---:|:---:|
| Finding Action Lifecycle | Owner, Status, Fälligkeit, Begründung, Accepted Risk und Post-Remediation Validation ergänzen; Findings werden zum gesteuerten Verbesserungsprozess. | 10 | L | 10 | 8 | sehr hoch |
| Validation Outcome Delta | Neue, gelöste, regressierte und unveränderte Findings sowie Scorebewegungen zwischen Assessment und Validation erklären. | 9 | M | 10 | 9 | sehr hoch |
| Monitoring Notifications | Verantwortliche über neue Critical-/High-Findings, fehlgeschlagene/verpasste Runs und wesentliche Verschlechterung mit Deduplizierung und Eskalation informieren. | 9 | L | 9 | 7 | hoch |
| Einheitlicher Self-Service-Funnel | Landingpage, Registrierung, Lizenzwahl, Extension-Setup, First Scan und Ergebniszugriff zu einer messbaren, recoverbaren Journey verbinden. | 10 | L | 10 | 7 | hoch |
| Outcome Measurement | Remediationaufwand, vermiedenes Risiko und validierte Verbesserung erfassen; Customer Success und Renewal Value belegbar machen. | 10 | L | 9 | 10 | sehr hoch |
| Enterprise Administration | Basic-only-Administration durch RBAC, stärkere Identity, begrenzte Aktionen, unveränderbare Auditevidenz und Secret Lifecycle ersetzen. | 9 | L | 7 | 6 | hoch |
| Support-Evidence-Paket | Diagnostic Export, Correlation IDs, Run History, Known-Error-Verfahren, Severity-/SLA-Modell und kundensicheres Troubleshooting bereitstellen. | 9 | M | 9 | 6 | sehr hoch |
| Daten-/Modell-Reconciliation | Katalog, ausführbare Regeln, API, Dashboard, Findings und Report je Release und Scan automatisch abstimmen. | 9 | M | 9 | 8 | sehr hoch |
| Konfigurationspromotion und Kompatibilität | Konfiguration und API-Verträge umgebungsübergreifend versionieren; Upgrade, Rollback und Rückwärtskompatibilität beweisen. | 8 | L | 7 | 5 | mittel |
| Native Extension-Testabdeckung | Kritische AL-Szenarien für Setup, Registrierung, Trigger, Scheduler, Permissions, Upgrade und Recovery automatisieren. | 8 | L | 8 | 5 | hoch |

## P2 — Mittlerer Business Value

| Feature Gap | Erforderliches Ergebnis | Business Impact | Aufwand | Kundenmehrwert | Differenzierung | ROI |
|---|---|---:|:---:|---:|---:|:---:|
| Branchen- und Größenprofile | Schwellwerte, Empfehlungen und Executive Narrative nach Unternehmensprofil kontextualisieren, ohne den gemeinsamen Scorevertrag zu verdecken. | 8 | XL | 9 | 9 | mittel |
| Capacity-/Performance-Envelope | Gemessene Tenant-, Scan-, Daten- und Reportlimits sowie Graceful Degradation veröffentlichen. | 8 | L | 7 | 5 | mittel |
| High-Availability-Betriebsmodell | Multi-Instance-/Job-Koordination, Datenbankresilienz und geprobtes Disaster Recovery für breitere Enterprise-Ausrollung ergänzen. | 8 | XL | 7 | 5 | mittel |
| Rollenbasierte Produkterfahrung | Views und Aktionen für Executive, Data Owner, Administrator, Partner und Support differenzieren, bei einer gemeinsamen Wahrheit. | 8 | L | 8 | 7 | hoch |
| Accessibility-/Browser-Evidenz | Accessibility-Kriterien sowie wiederholbare Browser-/Viewport-Tests für öffentliche und Executive Journeys etablieren. | 7 | M | 7 | 5 | hoch |
| Partner Delivery Kit | Discovery, Onboarding, Konfiguration, Ergebnisworkshop, Remediation-Handoff und Renewal-Evidenz für BC-Partner standardisieren. | 8 | L | 8 | 8 | hoch |
| Kundenfähige Knowledge Base | Aktuelle Setup-, Interpretations-, Privacy-, Support- und Remediation-Guides mit Versionsverantwortung und Suche veröffentlichen. | 7 | M | 8 | 5 | hoch |
| Produkttelemetrie/Funnel Analytics | Aktivierung, Scanabschluss, Reportnutzung, Remediation und Renewal-Signale ohne tenantübergreifende Datenmischung messen. | 8 | L | 7 | 7 | hoch |

## P3 — Später sinnvoll

| Feature Gap | Erforderliches Ergebnis | Business Impact | Aufwand | Kundenmehrwert | Differenzierung | ROI |
|---|---|---:|:---:|---:|---:|:---:|
| Privacy-sichere Benchmark Intelligence | Trends und Reife gegen belastbare anonymisierte Peer Cohorts vergleichen, sobald ausreichend consented Daten vorliegen. | 8 | XL | 8 | 10 | mittel |
| Predictive Risk Trends | Verschlechterung und Remediation-Priorität aus bewiesenen historischen Signalen mit Konfidenz und Erklärung prognostizieren. | 7 | XL | 7 | 9 | anfangs niedrig |
| Personalisierte Executive Workspaces | Gespeicherte Views, Board Packs und rollenbezogene Briefings ermöglichen, nachdem die Standardstory stabil ist. | 6 | L | 7 | 6 | mittel |
| Erweiterbares Regelökosystem | Governed Partner-/Customer-Rule-Packs mit Validierung, Versionierung, Provenance und Kompatibilitätsverträgen anbieten. | 8 | XL | 8 | 9 | mittel |
| Cross-Company-Portfolio | Explizit autorisierte Gesellschaften für Gruppen/Partner streng isoliert aggregieren und evidenzbasiert aufschlüsseln. | 8 | XL | 8 | 8 | mittel |

## Was jetzt nicht gebaut werden sollte

- Mehr Checks nur zur Erhöhung der Katalogzahl. Die 199 ausführbaren Checks brauchen zuerst Outcome-Evidenz und Modell-Provenance.
- KI-Empfehlungen ohne Quellenherkunft, deterministischen Fallback und Human-Review-Grenzen.
- Breite Dashboard-Anpassbarkeit vor Validierung der Standard-Executive-Story und des Action Loops.
- Komplexes Usage Billing vor Beweis von Zahlungsbereitschaft und einfachstem kommerziellem Vertrag.
- Benchmarkversprechen vor einer repräsentativen, consented und statistisch belastbaren Kohorte.

## Priorisierungslogik

BCSentinel verliert aktuell nicht wegen fehlender Featurebreite. Das größere Risiko ist, dass der starke analytische Kern noch nicht von gleich starker Trust-, Operations- und Customer-Outcome-Evidenz umgeben ist. P0 beweist deshalb das bestehende Produkt. P1 macht aus einmaliger Erkenntnis einen wiederholbaren Verbesserungs- und Renewal-Prozess. P2 skaliert Delivery über Rollen, Partner und Enterprises. P3 erweitert erst danach den verteidigbaren Datenvorsprung.
