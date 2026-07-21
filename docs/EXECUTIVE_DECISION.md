# Executive Decision

Stand: 2026-07-21

## Entscheidungsgrundlage

Die Entscheidungen konsolidieren ausschließlich Core Platform, Scan Engine, Customer Experience und Operations Assessment. Sie erzeugen keine neue Capability-Bewertung.

## 1. Betreuter Pilot

# JA, UNTER BEDINGUNGEN

Alle vier Assessment-Sets unterstützen einen kleinen, kontrollierten Pilot, sofern ihre Pilot-Gates vor Kundenstart geschlossen sind.

Zwingende Bedingungen:

- ein fixierter Commit, ein getestetes Image, dokumentierte Konfiguration und synchroner Evidenzstichtag;
- grüner Backend-/PostgreSQL-Release-Candidate-Lauf und BC-Sandbox-Acceptance;
- versionierter Check-/Rule-/Score-/Severity-/Impact-Snapshot;
- transparente Kennzeichnung finanzieller Werte als Modellschätzung samt Annahmen;
- manuelle Fachreview aller High/Critical Findings und visuelle PDF-Freigabe;
- nachgewiesene Tenantisolation, streng begrenzter Adminzugang und rotierbare Secrets;
- dokumentierter Deployment-/Rollback- sowie Backup-/Restore-Drill;
- benannter Incident- und Support-Primary/Backup mit täglicher Betriebskontrolle;
- kuratierter Customer-Pfad ohne öffentliche MVP-/Placeholder-/Sprachfehler;
- klarer Pilotvertrag ohne autonome Compliance-, Audit-, Finanz- oder Enterprise-SLA-Zusage.

Die positive Entscheidung beruht auf dem realen BC-nativen Produktkern, robusten Plattformmechanismen, verständlichem Executive Value und der Möglichkeit, Risiken im kleinen Pilotumfang aktiv zu kontrollieren.

## 2. Erster zahlender Kunde

# JA, UNTER BEDINGUNGEN

Ein erster zahlender Kunde ist vertretbar, wenn er ausdrücklich als Design-Partner-Pilot aufgenommen wird und Zahlung, Leistungsumfang, Support und Grenzen transparent vertraglich geregelt sind.

Zusätzliche Bedingungen gegenüber dem betreuten Pilot:

- Stripe-Testmode-End-to-End für den tatsächlich genutzten Kaufpfad sowie Billing Reconciliation und Exception Handling; alternativ eine ausdrücklich manuelle Pilotabrechnung ohne unbewiesenen Self-Service-Checkout;
- wahrheitsgemäße Preis- und CTA-Kommunikation;
- eindeutige Produktstufe, Aktivierung, Entitlement und Rückkehr in das Produkt;
- belastbare Support- und Eskalationszusage für den vereinbarten Pilotzeitraum;
- kein Versprechen realisierter Einsparung, wenn nur modellierte Wirkung vorliegt;
- dokumentierte Abbruch- und Erstattungsentscheidung bei Tenant-, Billing-, Daten- oder Recoveryfehlern.

Die Zahlung darf Beweis für Zahlungsbereitschaft sein, nicht als Beweis allgemeiner Produkt- oder Betriebsreife interpretiert werden.

## 3. Öffentlicher Go-Live

# NEIN

Der öffentliche Go-Live ist in allen relevanten Readiness-Sichten blockiert. Die Gründe sind kumulativ:

- keine releaseblockierende CI-/AL-Evidenz;
- keine fachlich versionierte und kundenseitig kalibrierte Bewertungs- und Finanzlogik;
- gebrochene Free-/Onboarding-/Checkout-/Upgrade-Journey und unfertige öffentliche Inhalte;
- keine zentrale Monitoring-, Telemetry- und Alertingfähigkeit;
- Backup, Restore, Rollback und Disaster Recovery nicht bewiesen;
- Admin-RBAC, Secret Lifecycle, Incident und Support nicht allgemein skalierbar;
- keine Performance-, Capacity-, Mehrinstanz- oder BC-Großdatenevidenz.

Ein öffentlicher Launch würde mehr Nachfrage und Erwartung erzeugen, als Produkt, Journey und Betrieb heute zuverlässig tragen können.

## 4. Enterprise Rollout

# NEIN

Ein Enterprise-Rollout setzt wiederholbare fachliche Ergebnisse, Procurement-fähiges Vertrauen, kontrollierte Releases, professionelle Operations und belegte Skalierung voraus. Genau diese Beweiskette ist noch offen.

Besonders ausschließend sind:

- fehlende historische Reproduzierbarkeit von Regeln, Scores, Severity und Impact;
- fehlende Outcome-, False-Positive- und Benchmarkdaten;
- keine IAM-/RBAC-/Access-Review- und Configuration-Governance auf Enterprise-Niveau;
- keine SLO-, RTO/RPO-, HA-, DR- oder Capacity-Evidenz;
- founder-abhängiger Support und Incidentbetrieb;
- unbewiesene horizontale Skalierung von Jobs, Rate Limits und Datenbank.

Die vorhandenen Enterprise-Qualitäten einzelner Mechanismen sind wertvoll, ergeben aber noch keine Enterprise-Rollout-Freigabe.

## Konsolidierte Unternehmensentscheidung

BCSentinel sollte jetzt **kontrolliert in den Markt lernen**, nicht breit in den Markt skalieren. Der Design-Partner-Pilot ist der richtige nächste Unternehmensschritt, wenn die P0-Gates geschlossen sind. Öffentlicher Go-Live und Enterprise-Rollout bleiben bis zur belegten Schließung ihrer Blocker ausgeschlossen.

## Letzte Executive-Aussage

**Wenn ich BCSentinel in genau diesem Zustand übernehmen würde, würde ich das Unternehmen selbst weiterführen.**

Warum: Der schwer ersetzbare Teil ist bereits sichtbar — eine differenzierte, Business-Central-native Product-Intelligence-Kette, die technische Datenqualität in Executive-Entscheidungen übersetzt. Die offenen Risiken sind ernst, aber sie sind in den Assessments klar benannt und überwiegend durch Governance, Validierung, Automatisierung und Betriebsdisziplin reduzierbar. Ich würde deshalb weiter investieren, den Markt ausschließlich über einen kontrollierten Pilot betreten und jede breitere Freigabe an überprüfbare Evidenz statt an Zeitdruck binden.
