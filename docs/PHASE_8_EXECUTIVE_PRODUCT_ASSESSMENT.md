# Phase 8 — Executive Product Assessment

Stand: 2026-07-22

## Assessment Contract

Bewertet wird das fertige Produkt aus CTO-, CPO-, Investor-, Kunden-, Administrator-, Management-, Vertriebs-, Support-, Skalierungs-, Go-Live- und Enterprise-Sicht. Produktcode wurde nicht verändert. Nicht commitierte Arbeitsbaumänderungen wurden nicht als freigegebene positive Evidenz gewertet.

Baseline:

- Repository-HEAD: `ea5b597699790d3e0e9cea8384c8025c41f175b4`
- Product System: normative Produkt- und Enterprise-Prinzipien
- Product Master Book: deskriptiver Implementierungsstand
- bestehende Core-, Scan-, Customer-Experience-, Operations- und Executive-Assessments
- aktuelle GL-01A-2-/GL-01F-/Pilot-/Release-Audits

Die verlangten 0–10-Werte sind Phase-8-Executive-Einschätzungen. Sie ersetzen keine technischen Release-Gates. Skala: 0 = nicht vorhanden/nicht verantwortbar, 5 = für kontrollierten Pilot teilweise tragfähig, 8 = stark und weitgehend marktfähig, 10 = außergewöhnlich, vollständig bewiesen und ohne relevante Änderung freigabefähig.

## Executive Summary

BCSentinel ist heute ein substanzielles, differenziertes Produkt mit einem starken Kern: einheitlicher Business-Central-Deep-Scan, 199 produktive Checks, Findings, Score, Business Impact, Free-/Validation-/Monitoring-Kontexte, Executive Dashboard und PDF. Tenantbindung, atomare Credits, Access Snapshots, Lease/Heartbeat/Recovery und die breite Backend-Testbasis zeigen reifes Engineering.

Für einen zahlenden Design Partner ist das Produkt noch nicht „morgen ohne Vorbereitung“ freigabefähig. Die letzten Audits dokumentieren weiterhin offene reale BC-Sandbox-CATs, unbewiesene Betriebs- und Recoveryabläufe, fehlende native AL-Testautomation, eine nicht vollständig vertrauensstabile öffentliche Journey sowie fachliche Transparenzlücken bei Score und finanzieller Wirkung.

Die stärksten verkaufsfähigen Komponenten sind Executive PDF, Findings, Enterprise Check Catalog, Free Scan und Lizenzsystem. Die schwächsten produktweiten Bereiche sind Betriebsfähigkeit, Support, Deployment und Scheduler. Die richtige Executive-Entscheidung ist deshalb **B — erst noch einige Wochen investieren**, die P0-Gates schließen und danach mit genau einem eng betreuten Design Partner starten.

## Bewertungsdimensionen

| Kürzel | Dimension |
|---|---|
| PR | Produktreife |
| BV | Business Value |
| UX | Benutzerfreundlichkeit |
| TQ | Technische Qualität |
| ER | Enterprise Readiness |
| PI | Pilot Readiness |
| GL | Go-Live Readiness |
| SU | Supportfähigkeit |
| EX | Erweiterbarkeit |
| WA | Wartbarkeit |
| SK | Skalierbarkeit |
| VS | Verkaufsfähigkeit |
| DI | Differenzierung |
| MP | Marktpotenzial |

## Gesamtmatrix

| # | Komponente | PR | BV | UX | TQ | ER | PI | GL | SU | EX | WA | SK | VS | DI | MP | Gesamt |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Business Central Extension | 7 | 9 | 7 | 8 | 6 | 7 | 5 | 6 | 8 | 7 | 6 | 8 | 9 | 9 | 7,3 |
| 2 | Executive Dashboard | 7 | 8 | 7 | 7 | 6 | 7 | 5 | 6 | 7 | 6 | 6 | 8 | 7 | 8 | 6,8 |
| 3 | Executive PDF Report | 8 | 9 | 8 | 8 | 7 | 8 | 6 | 7 | 7 | 8 | 7 | 9 | 8 | 9 | 7,8 |
| 4 | Landingpage | 6 | 8 | 6 | 6 | 5 | 6 | 4 | 5 | 6 | 5 | 6 | 7 | 7 | 8 | 6,1 |
| 5 | Backend API | 8 | 9 | 6 | 8 | 7 | 8 | 6 | 7 | 8 | 7 | 6 | 7 | 7 | 8 | 7,3 |
| 6 | Admin Backend | 7 | 7 | 6 | 7 | 5 | 7 | 5 | 6 | 7 | 6 | 5 | 5 | 5 | 6 | 6,0 |
| 7 | Lizenzsystem | 8 | 9 | 7 | 8 | 7 | 8 | 6 | 7 | 8 | 7 | 7 | 8 | 8 | 9 | 7,6 |
| 8 | Registrierungsprozess | 7 | 8 | 7 | 8 | 6 | 7 | 5 | 6 | 7 | 7 | 6 | 7 | 7 | 8 | 6,9 |
| 9 | Monitoring | 6 | 8 | 6 | 7 | 5 | 6 | 4 | 5 | 7 | 6 | 5 | 7 | 7 | 8 | 6,2 |
| 10 | Validation Scan | 7 | 8 | 7 | 8 | 6 | 7 | 5 | 6 | 8 | 7 | 6 | 8 | 8 | 8 | 7,1 |
| 11 | Free Scan | 8 | 9 | 7 | 8 | 6 | 8 | 6 | 7 | 8 | 7 | 7 | 9 | 8 | 9 | 7,6 |
| 12 | Enterprise Check Catalog | 8 | 9 | 6 | 8 | 7 | 8 | 6 | 7 | 9 | 8 | 7 | 8 | 9 | 9 | 7,8 |
| 13 | Findings | 8 | 9 | 7 | 8 | 7 | 8 | 6 | 7 | 8 | 7 | 7 | 9 | 9 | 9 | 7,8 |
| 14 | Analytics | 7 | 8 | 7 | 7 | 6 | 7 | 5 | 6 | 8 | 6 | 6 | 8 | 7 | 8 | 6,9 |
| 15 | Scheduler | 6 | 7 | 6 | 7 | 5 | 6 | 4 | 5 | 7 | 6 | 5 | 6 | 6 | 7 | 5,9 |
| 16 | Produktarchitektur | 7 | 8 | 7 | 7 | 6 | 7 | 5 | 6 | 8 | 7 | 6 | 8 | 8 | 8 | 7,0 |
| 17 | Security | 7 | 9 | 6 | 8 | 6 | 7 | 5 | 6 | 8 | 7 | 6 | 7 | 7 | 8 | 6,9 |
| 18 | Deployment | 6 | 8 | 5 | 7 | 4 | 6 | 4 | 5 | 7 | 6 | 4 | 5 | 5 | 6 | 5,6 |
| 19 | Developer Experience | 7 | 7 | 6 | 7 | 5 | 7 | 5 | 6 | 7 | 6 | 6 | 5 | 6 | 7 | 6,2 |
| 20 | Supportfähigkeit | 6 | 8 | 6 | 6 | 4 | 6 | 4 | 5 | 6 | 6 | 5 | 6 | 6 | 7 | 5,8 |
| 21 | Betriebsfähigkeit | 5 | 9 | 5 | 6 | 3 | 6 | 3 | 4 | 6 | 5 | 4 | 4 | 5 | 7 | 5,1 |
| 22 | Dokumentation | 8 | 8 | 7 | 8 | 6 | 8 | 6 | 7 | 8 | 7 | 7 | 7 | 8 | 8 | 7,4 |
| 23 | Gesamtprodukt | 7 | 9 | 7 | 8 | 6 | 7 | 5 | 6 | 8 | 7 | 6 | 8 | 9 | 9 | 7,3 |

`Gesamt` ist der ungewichtete Mittelwert der 14 Dimensionen, auf eine Dezimalstelle gerundet. Er ist Orientierung, kein Releaseentscheid.

## Komponentenbewertungen

### 1. Business Central Extension — 7,3/10

**Begründung:** Produkt- und Business-Wert sind sehr hoch, weil die Extension den nativen Zugang zu BC, First Run, Deep Scan, Findings, Scheduler und Dashboard trägt. Technisch sind HTTPS, stabile Tenant-/Company-Bindung, Background Session und Recovery stark. Enterprise-, Go-Live- und Supportwerte bleiben niedriger, weil reale Post-Fix-CATs, negative Permissiontests und dauerhafte AL-Testautomation offen sind.

- **Stärken:** BC-native UX; einheitlicher Deep-Scan-Pfad; First-Run-Hinweise; fünf Permission Sets; Build und Quellverträge grün.
- **Schwächen:** Plattformverhalten wird überwiegend statisch/vertraglich statt nativ getestet; Setup bleibt funktionsreich.
- **Risiken:** Background-/Schedulerverhalten kann erst in BC abweichen; Upgrade-/Permissionfehler treffen den Kunden direkt.
- **Fehlende Features:** native AL-Test-App; belastbare Diagnose-/Telemetry-Oberfläche für Administratoren.
- **Quick Wins:** alle aktuellen Post-Fix-CATs in BC 28.3 ausführen; Pilotpackage sauber signieren/fixieren.
- **Spätere Features:** Role-Center-Cues, komfortable Recovery- und Supportdiagnose.
- **P0:** Sandbox-CAT, Permission-Negativtest, Releaseartefakt.
- **P1:** AL-Testautomation und Upgrade-Gate.
- **P2:** Telemetrie und Role-Center-Integration.
- **P3:** zusätzliche Komfort- und Partneradministration.

### 2. Executive Dashboard — 6,8/10

**Begründung:** Das Dashboard macht Health, Impact, Risiken, Findings, Actions und Reports gut sichtbar und unterstützt Free-/Paid-/Monitoring-Gates. UX und Verkaufsfähigkeit sind stark, aber nicht auf realen Browsern, mobilen Viewports, Accessibility-Setups und vollständigen Free-/Paid-Payloads abgenommen. Große JS-/CSS-Flächen und hohe Informationsdichte reduzieren Wartbarkeit.

- **Stärken:** Executive Overview; progressive Details; serverseitige Gates; Tenantwechsel; breite Seitenabdeckung.
- **Schwächen:** hohe Dichte; Navigation teilweise produkt- statt entscheidungsorientiert; technisches Portal wirkt schwächer.
- **Risiken:** sichtbare Zustände können mit realen Payloads abweichen; Accessibility ist Evidence Missing.
- **Fehlende Features:** persistierte Preferences/Notifications; vollständiger Action-/Owner-/Validation-Lifecycle.
- **Quick Wins:** reale Free-/Paid-/Monitoring-Screenshots und Browsermatrix; First View reduzieren.
- **Spätere Features:** rollenbasierte Views und konfigurierbare Executive Summary.
- **P0:** Pilotpayloads und Kernjourney visuell abnehmen.
- **P1:** Accessibility, Preferences und Action Workflow.
- **P2:** rollenbezogene Dashboards.
- **P3:** individuelle Executive Workspaces.

### 3. Executive PDF Report — 7,8/10

**Begründung:** Der Report ist das stärkste verkaufsfähige Einzelartefakt. Management Summary, Score, Impact, Module und Severity sind professionell, lokal gerendert und in mehreren Formaten verfügbar. Er verliert Punkte durch unkalibrierte finanzielle Präzision, fehlende sichtbare Modellversion/Evidence Lineage und noch offene Produktions-PDF-Abnahme mit realen Extremdaten.

- **Stärken:** ruhiges Executive Design; JSON/HTML/PDF/Share; lokale Assets; gute Backendtests.
- **Schwächen:** zweite Seite teils vertriebs- statt actionorientiert; Methode und Confidence nicht prominent genug.
- **Risiken:** professionelle Darstellung kann höhere fachliche Sicherheit suggerieren als belegt.
- **Fehlende Features:** Calculation Snapshot, Confidence, Evidence Lineage und findingspezifische Top Actions.
- **Quick Wins:** „modellierte Schätzung“ sichtbar machen; reales Pilot-PDF freigeben.
- **Spätere Features:** Vorher-/Nachher-Report und kundenspezifische Benchmarks.
- **P0:** PDF-Visual-Gate und Finanzdisclaimer.
- **P1:** versionierter Reportvertrag und Action Report.
- **P2:** Outcome-/Benchmarkreporting.
- **P3:** erweiterte Board- und Partnerpakete.

### 4. Landingpage — 6,1/10

**Begründung:** Positionierung, Business Impact und Preise erzeugen Interesse, aber die öffentliche Experience bleibt inkonsistent. Zwei Sitebäume, Legal-/Support-Platzhalter, Sprachfehler und Pricing-CTAs mit unerwartetem Kontaktziel begrenzen Go-Live, Support und Enterprise-Vertrauen.

- **Stärken:** klare BC-Positionierung; finanzielle Story; strukturierte Produktangebote; DE/EN-Grundlage.
- **Schwächen:** kein klarer Free-Score-Einstieg; dunkle Markenwelt weicht vom Produkt ab; lange Seite.
- **Risiken:** Trust-Verlust in den ersten Minuten; Conversion endet im falschen Pfad.
- **Fehlende Features:** kanonischer Free-Score-Start; echter Checkout-/Activation-Pfad; finale Trust-/Legal-/Support-Inhalte.
- **Quick Wins:** CTA-Ziele korrigieren; Placeholder und Sprachfehler entfernen; kanonische Site deklarieren.
- **Spätere Features:** validierte Kundenbelege und interaktive Produktdemo.
- **P0:** Pilotpfad und öffentlich sichtbare Fehler bereinigen.
- **P1:** Self-Service-Conversion und Accessibility.
- **P2:** Social Proof und Partner-Cases.
- **P3:** segmentierte Kampagnen/Experimente.

### 5. Backend API — 7,3/10

**Begründung:** Die API trägt Registrierung, Scan, Lizenz, Dashboard, Reporting und Administration. Konfigurationsvalidierung, Migrationsgate, Tenantguards, Idempotenz und breite Tests sind stark. Skalierung, API-Lifecycle, externe Provider-E2E und in-process Background Work begrenzen Enterprise- und Go-Live-Werte.

- **Stärken:** klare Router/Services; transaktionale Core-Flows; Health/Readiness; strukturierte Fehler und Korrelation.
- **Schwächen:** breiter Monolith; synchroner DB-Zugriff; keine kanonische API-Versionierung.
- **Risiken:** Contract Breaks; single-process Jobownership; Provider-/DB-Abhängigkeit.
- **Fehlende Features:** Compatibility Policy, Consumer Contracts, zentrale Job-/Queue-Diagnose.
- **Quick Wins:** OpenAPI-Snapshot diffen; Release-Candidate-Suite gegen PostgreSQL.
- **Spätere Features:** explizites Worker-/Mehrinstanzmodell.
- **P0:** fixierten Release testen und Pilot-API-Vertrag einfrieren.
- **P1:** API Compatibility und Reconciliation.
- **P2:** Mehrinstanz/Worker und Capacity.
- **P3:** externe Partner-API-Governance.

### 6. Admin Backend — 6,0/10

**Begründung:** Das Admin Backend bietet bemerkenswert breite Steuerung und Auditierbarkeit für einen Pilot. Benutzerfreundlichkeit und Business Value sind ausreichend, aber eine einzige Basic-Adminidentität, fehlendes rollenfeines Operator-Modell, keine vollständige Bedienungsanleitung und uneinheitliche Rollbacks verhindern Enterprise-Reife.

- **Stärken:** Tenant-, Lizenz-, Credit-, Pricing-, Translation- und Auditsteuerung.
- **Schwächen:** technisch geprägte UI; schwache Delegation; große Blast-Radius-Aktionen.
- **Risiken:** Fehlkonfiguration oder zu weitreichender Zugriff wirkt systemweit.
- **Fehlende Features:** Admin-RBAC, benannte Identitäten, Approval, Change Ticket und sichere Rollbackpfade.
- **Quick Wins:** Pilotzugriff auf benannte Personen begrenzen; SOP für kritische Aktionen.
- **Spätere Features:** SSO/MFA, Vier-Augen-Freigabe und Break-glass.
- **P0:** Zugang begrenzen und Audit prüfen.
- **P1:** RBAC/Approval/Runbooks.
- **P2:** Enterprise Identity und Delegation.
- **P3:** automatisierte Compliance-/Operationsreports.

### 7. Lizenzsystem — 7,6/10

**Begründung:** Produktcodes, Credits, Entitlements, Access Snapshots und Free-/Paid-/Monitoring-Abgrenzung sind technisch und kommerziell stark. Die jüngsten Free-Access-Fixes schließen eine wichtige Customer-Value-Lücke. Abzüge entstehen durch offene reale Stripe-Läufe, Reconciliation, Token-/Entitlement-Lifecycle und manuelle Providerdiagnose.

- **Stärken:** atomare Credits; idempotente Webhooks; frische Access Snapshots; sieben Tage Free-Result-Access; klare Produktstufen.
- **Schwächen:** komplexes Modell; Legacyaliases; Providerzustand extern.
- **Risiken:** falsche Freischaltung, Credit- oder Subscriptiondrift wirkt direkt auf Umsatz und Vertrauen.
- **Fehlende Features:** automatisierte Reconciliation, Dunning/Exception Queue und Operatorübersicht.
- **Quick Wins:** Testmode-Matrix für verwendeten Pilotpfad; täglicher manueller Abgleich.
- **Spätere Features:** Self-Service-Lifecycle und Finance Operations Dashboard.
- **P0:** Zahlungsmodus und Accesspfad beweisen.
- **P1:** Reconciliation/Exception Recovery.
- **P2:** skalierbare Finance Operations.
- **P3:** erweiterte Packaging-/Partneroptionen.

### 8. Registrierungsprozess — 6,9/10

**Begründung:** Stabile Tenant-/Environment-/Company-Bindung, idempotente Registrierung und verbesserte First-Run-Hinweise sind gute Grundlagen. Der reale End-to-End-Retest nach Membership- und UX-Fixes bleibt jedoch offen. Customer Journey, Recovery und Support sind noch nicht vollständig self-service-fähig.

- **Stärken:** stabile Identität; Consent/E-Mail/API-Voraussetzungen; promoted Action; Mehrtenant-Memberships.
- **Schwächen:** mehrere Systeme und Zustände; Portal wirkt technisch; reale Retry-/Recovery-UX offen.
- **Risiken:** erster Kundeneindruck scheitert trotz technisch korrekter Grundlage.
- **Fehlende Features:** geführter Fortschritt, verständliche Recovery und sichere Einladung/Resend-Journey.
- **Quick Wins:** aktuellen Sandbox-CAT vollständig durchführen und dokumentieren.
- **Spätere Features:** rollen- und partnergeführtes Onboarding.
- **P0:** Registrierung und Tenantwechsel real beweisen.
- **P1:** Recovery-/Self-Service-Flow.
- **P2:** Partner-Onboarding.
- **P3:** skalierte Provisionierung.

### 9. Monitoring — 6,2/10

**Begründung:** Monitoring besitzt ein verständliches wiederkehrendes Wertversprechen und nutzt denselben Deep-Scan-Kern. Trends, Historie und Scheduler sind angelegt. Reale wiederholte Laufzeit, Alarme, Mailreports, Serviceberechtigungen und Supportbetrieb sind nicht vollständig bewiesen.

- **Stärken:** einheitlicher Checkumfang; Trends; Monitoring-Entitlement; Scheduled Trigger.
- **Schwächen:** Produkt-Monitoring und Plattform-Monitoring sind noch nicht vollständig operationalisiert.
- **Risiken:** wiederkehrender Wert wird verkauft, obwohl Automation oder Alarmierung ausfallen kann.
- **Fehlende Features:** zuverlässige Kundenalerts, Monitoring-Runbook, Failure-/Missed-Run-Übersicht.
- **Quick Wins:** mehrere Schedulerzyklen im Piloten protokollieren; Missed-Run-Check.
- **Spätere Features:** Delta-/Trendbenachrichtigung und SLA-nahe Statussicht.
- **P0:** ein realer geplanter Lauf nach manuellem Lauf.
- **P1:** Alerting und Supportdiagnose.
- **P2:** skalierbarer Monitoringbetrieb.
- **P3:** Benchmark-/Predictive Trends.

### 10. Validation Scan — 7,1/10

**Begründung:** Validation nutzt den einheitlichen Deep-Scan-Kern und hat ein klares Business-Narrativ: Wirkung einer Bereinigung bestätigen. Technisch ist der Pfad stark, aber spezifische Outcome-Deltas, klare Vergleichslogik und realer Kundennachweis sind noch schwächer als der allgemeine Scan.

- **Stärken:** kein zweiter Scanmotor; separates Produkt-/Creditmodell; starke Wiederholungsstory.
- **Schwächen:** Vergleich und Erfolgskriterien werden nicht als eigenes Outcome prominent gemacht.
- **Risiken:** Kunde bezahlt für Wiederholung, ohne klaren messbaren Fortschritt zu sehen.
- **Fehlende Features:** Baseline-vs-Validation-Diff, resolved/new/unchanged Findings und Savings Validation.
- **Quick Wins:** Validation im Pilot mit definiertem Vorher/Nachher-Kriterium durchführen.
- **Spätere Features:** Improvement Score und Remediation Effectiveness.
- **P0:** Access/Credit/Resultat-Pfad testen.
- **P1:** Outcome-Diff.
- **P2:** Trend-/Benchmarkintegration.
- **P3:** Portfoliovergleich.

### 11. Free Scan — 7,6/10

**Begründung:** Der Free Scan ist kommerziell strategisch und technisch inzwischen klar auf den vollständigen Deep-Scan-Kern vereinheitlicht. Siebentägiger Zugriff auf Dashboard, Findings und Report schafft echten Wert, während Paid Actions geschützt bleiben. Der reale Sandbox-Retest und die öffentliche Einstiegskette bleiben die wichtigsten Grenzen.

- **Stärken:** echter Vollscan statt abgespeckter Quick Scan; atomarer Free Slot; resultatorientierter Zugang; hoher Upgrade-Hebel.
- **Schwächen:** Free-Einstieg auf Landingpage nicht dominant; Accessfix noch nicht real am Pilottenant abgenommen.
- **Risiken:** stärkster Conversionpfad scheitert im ersten realen Lauf oder zeigt falsche Gates.
- **Fehlende Features:** durchgängiger öffentlicher Free-to-Registration-to-Result Flow.
- **Quick Wins:** gemeldeten Pilottenant repariert verifizieren; 12-Schritt-CAT durchführen.
- **Spätere Features:** Benchmark-Preview und geführte Upgrade-Erklärung.
- **P0:** realer Free-Abschluss plus drei Accesspfade.
- **P1:** Self-Service-Free-Journey.
- **P2:** Conversion Analytics.
- **P3:** segmentierte Free Experiences.

### 12. Enterprise Check Catalog — 7,8/10

**Begründung:** 213 IDs mit 199 produktiven Deep Checks und 14 dokumentierten historischen Alias-IDs bilden einen starken Domänenmoat. Erweiterbarkeit und Differenzierung sind hoch. Enterprise-Reife wird durch fehlende formale Rule-Versionierung, vollständige fachliche Dokumentation, Golden Datasets und Outcome-Evidenz begrenzt.

- **Stärken:** breite BC-Domänenabdeckung; stabile IDs; Customer Overrides; Translation Layer.
- **Schwächen:** Katalog- und Ausführungswahrheit müssen automatisiert synchron bleiben; einige historische Dokumente driften.
- **Risiken:** Alias-/Count-Verwirrung, unklare Rule-Governance und False Positives.
- **Fehlende Features:** Version/Owner/Rationale/Expected Result/Confidence je produktivem Check.
- **Quick Wins:** generierten Katalog aus Registry publizieren; 199+14-Semantik überall einheitlich nennen.
- **Spätere Features:** Branchenprofile, Benchmark- und Outcome-Metadaten.
- **P0:** Pilotcheckscope einfrieren.
- **P1:** Rule Governance und Golden Dataset.
- **P2:** kalibrierte Branchenpakete.
- **P3:** Partner-/Marketplace-Erweiterungen.

### 13. Findings — 7,8/10

**Begründung:** Findings liefern den größten direkten Kundennutzen. Sie verbinden konkrete Probleme, affected counts, Severity, Impact und Empfehlungen. Persistenz und Deduplizierung sind stark. Die Lücke liegt in Evidence Lineage, Confidence, Owner, Status, Action und Validation.

- **Stärken:** konkret, priorisierbar, BC-spezifisch, reportfähig und tenantgebunden.
- **Schwächen:** Diagnose stärker als vollständige Remediation; Explainability variiert je Check.
- **Risiken:** False Positives oder generische Empfehlungen schwächen den gesamten Produktwert.
- **Fehlende Features:** Evidence Source, Calculation Snapshot, Owner/SLA, Action Status und Validation Outcome.
- **Quick Wins:** Top drei Pilotfindings manuell fachlich reviewen und actionorientiert darstellen.
- **Spätere Features:** Kollaboration, Exception Governance und Remediation Analytics.
- **P0:** High/Critical Review.
- **P1:** Evidence-/Action-Lifecycle.
- **P2:** Teamworkflow und Outcome-Messung.
- **P3:** Benchmark-/Recommendation Intelligence.

### 14. Analytics — 6,9/10

**Begründung:** Analytics bietet sinnvolle Vertiefung, Trends und Modulkontext und erhöht den wahrgenommenen Wert des Dashboards. Die dominante Managementfrage ist nicht immer klar; reale Daten-, Empty- und Fehlerzustände sowie langfristige Performance sind nicht umfassend abgenommen.

- **Stärken:** Trend-, Modul- und Verteilungssicht; Drilldown; Monitoringanschluss.
- **Schwächen:** Überschneidung mit Overview/Scans/Findings; hohe Informationsdichte.
- **Risiken:** wirkt wie zusätzliche Dashboardfläche statt klare Entscheidungshilfe.
- **Fehlende Features:** Benchmark, Periodenauswahl, erklärbare Vergleichsbasis.
- **Quick Wins:** jede Ansicht auf eine Nutzerfrage reduzieren und realen Payload testen.
- **Spätere Features:** Kohorten-/Benchmark- und Outcome-Analytics.
- **P0:** Pilotdaten visuell prüfen.
- **P1:** IA und Erklärbarkeit.
- **P2:** Benchmarks.
- **P3:** Advanced Analytics.

### 15. Scheduler — 5,9/10

**Begründung:** TaskScheduler, Failure Codeunit, Statusfelder und Background-Sessions sind vorhanden. Mehrere reale Fehler wurden verantwortungsvoll behoben. Der entscheidende Beweis — wiederholte fehlerfreie Ausführung in echter BC-Sandbox ohne `SUPER` und mit Recovery — bleibt offen.

- **Stärken:** native BC-Planung; eigenes Permission Set; Failure/Retry/Statusgrundlage.
- **Schwächen:** schwer lokal testbar; operative Sicht auf verpasste Jobs begrenzt.
- **Risiken:** still ausbleibende Monitoringläufe; doppelte/verwaiste Tasks; Serviceberechtigungen.
- **Fehlende Features:** Missed-Run-Alarm, zentrale Schedulerdiagnose und native Regression.
- **Quick Wins:** manuellen und folgenden geplanten Lauf als CAT beweisen.
- **Spätere Features:** Fleet-/Tenant-Schedulerübersicht.
- **P0:** Sandbox-E2E.
- **P1:** Alarmierung und AL-Test.
- **P2:** Multi-Tenant Operations.
- **P3:** adaptive Planung.

### 16. Produktarchitektur — 7,0/10

**Begründung:** Die Architektur trennt BC-Erhebung, Backendplattform, Dashboard/Admin, Reporting und Public Site sinnvoll. Einheitlicher Deep Scan reduziert Komplexität. Normative Verträge für API, IAM, Operations, Rule/Impact und Skalierung sind jedoch noch unvollständig; mehrere Systeme bleiben founder- und single-instance-orientiert.

- **Stärken:** klare Produktoberflächen; modularer Monolith; tenantgebundene Grenzen; einheitliche Scan Engine.
- **Schwächen:** Zielarchitektur für Multi-Instance, Worker, IAM und Operations fehlt.
- **Risiken:** lokale Entscheidungen skalieren später inkonsistent.
- **Fehlende Features:** freigegebene technische Zielverträge, nicht neue Produktfunktionen.
- **Quick Wins:** Single-Instance- und Pilotgrenzen explizit festhalten.
- **Spätere Features:** skalierbares Worker-/HA-/Integration-Modell.
- **P0:** Pilotarchitektur einfrieren.
- **P1:** API/IAM/Operations Contracts.
- **P2:** Scale Architecture.
- **P3:** Ecosystem Platform Architecture.

### 17. Security — 6,9/10

**Begründung:** HTTPS, URL-Policy, Tokenhashing, Tenantabgleich, CSRF, Security Headers, Access Snapshots und Audit sind starke technische Controls. Enterprise Readiness bleibt durch Basic Admin, fehlende MFA/SSO-/Access-Review-Evidenz, Secretrotation, Penetrationstest und Security Operations begrenzt.

- **Stärken:** fail-closed Zugriffe; tenant-/companygebundene Tokens; frische Capability Guards.
- **Schwächen:** heterogene Authmodelle; in-process Rate Limits; operative Governance fehlt.
- **Risiken:** privilegierter Zugriff, Secretkompromittierung oder unerkannte Anomalie.
- **Fehlende Features:** Admin-RBAC/MFA, Secret Lifecycle, Security Detection und Access Review.
- **Quick Wins:** Pilotoperatoren begrenzen; Secrets inventarisieren/rotieren; Tenant-Negativtest.
- **Spätere Features:** SSO, SIEM und formales Vulnerability Management.
- **P0:** Tenant/Admin/Secret-Gates.
- **P1:** RBAC/MFA/SecOps.
- **P2:** kontinuierliche Assurance.
- **P3:** Zertifizierungs-/Complianceprogramme.

### 18. Deployment — 5,6/10

**Begründung:** Docker, Compose, Migrationen, Nginx und Healthchecks bilden einen echten Deploymentpfad. Der Workflow deployt jedoch direkt per SSH aus Branchstand, führt keine Tests als Gate aus, baut auf dem Zielhost und besitzt keinen bewiesenen automatischen Rollback oder immutable Promotion.

- **Stärken:** dokumentierte DEV/PROD-Topologie; non-root Image; Migrations- und Health-Gates.
- **Schwächen:** CD ohne vollständiges CI; hostgebundene Pfade; kein signiertes Artefakt.
- **Risiken:** ungetesteter Commit, Migrationsfehler, unreproduzierbarer Kundenstand.
- **Fehlende Features:** Required Checks, Registry/Digest-Promotion, Environment Approval, Deployment History.
- **Quick Wins:** Testjob vor Deploy; Release Manifest; Concurrency Lock.
- **Spätere Features:** Blue/Green/Canary und IaC.
- **P0:** Pilotdeploy und Rollback beweisen.
- **P1:** immutable CI/CD.
- **P2:** HA-/IaC-Deployment.
- **P3:** progressive Delivery.

### 19. Developer Experience — 6,2/10

**Begründung:** Product Master Book, Audits, gepinnte Dependencies, Testtarget und klare Ordner helfen. Der leere/überholte Einstieg, zahlreiche historische Dokumente, fehlendes One-Command-Setup, keine vollständige CI und komplexe BC-Toolchain bremsen neue Entwickler.

- **Stärken:** umfangreiche Wissensbasis; automatisierte Backendtests; AL-Build-/Source-Guards.
- **Schwächen:** viele Wahrheiten und Stichtage; lokale Toolchainhürden; kein durchgehender Dev-Container.
- **Risiken:** Onboardingzeit, Knowledge Drift und foundergebundenes Wissen.
- **Fehlende Features:** aktueller Developer Guide, One-Command Bootstrap, Architecture Decision Index und Troubleshooting.
- **Quick Wins:** Root-README/Developer Start aktualisieren; kanonische Befehle und Baseline verlinken.
- **Spätere Features:** reproduzierbare Devcontainer/Ephemeral Environments.
- **P0:** Pilotbuild reproduzierbar dokumentieren.
- **P1:** Developer Guide/CI.
- **P2:** Devcontainer und Sandboxautomation.
- **P3:** SDK/Partner Development Experience.

### 20. Supportfähigkeit — 5,8/10

**Begründung:** Request-, Tenant- und Run-IDs, Adminfunktionen und Pilotrunbooks ermöglichen founder-led Support. Ticketing, SLA/SLO, Wissensbasis, sichere Diagnosepakete, Eskalationsmatrix und zweite operative Person fehlen oder sind nicht nachgewiesen.

- **Stärken:** gute technische Korrelationsdaten; bekannte Fehlerpfade dokumentiert; Admin Audit.
- **Schwächen:** Supportwissen verteilt; kein skalierbares Intake-/Ownership-Modell.
- **Risiken:** Kunde ist erster Monitor; Lösung hängt von Einzelpersonen ab.
- **Fehlende Features:** Support Guide, Troubleshooting Matrix, Ticketworkflow, Statuskommunikation und Problem Management.
- **Quick Wins:** Pilot Primary/Backup, Severity und sicheren Supportkanal definieren.
- **Spätere Features:** Customer Support Portal und Diagnosebundle.
- **P0:** Pilot-Supportvertrag.
- **P1:** Runbooks/KB/Tickets.
- **P2:** skalierbares Supportteam.
- **P3:** proaktiver Customer Success.

### 21. Betriebsfähigkeit — 5,1/10

**Begründung:** Logs, Healthchecks, Startupvalidierung und Runbooks sind Grundlagen. Kein zentrales Monitoring/Alerting, kein bewiesener Backup-/Restore-/DR-Prozess, kein On-call, keine SLOs und keine Capacity Evidence machen unbeaufsichtigten Betrieb unverantwortbar.

- **Stärken:** strukturierte Logs; Request IDs; DB-Readiness; Recoverymechanismen.
- **Schwächen:** reaktiv statt proaktiv; Single Host/DB; manuelle Operations.
- **Risiken:** unbemerkter Ausfall, Datenverlust, langer Recoveryweg und Founder-Burnout.
- **Fehlende Features:** Operational Monitoring, Alerting, Backupautomation, Restore/DR, Incident Management.
- **Quick Wins:** Uptime-/5xx-Alarm, tägliches Backup, Restore-Drill, Primary/Backup.
- **Spätere Features:** SLOs, HA, Capacity und Operations Automation.
- **P0:** kontrollierter Pilotbetrieb und Recoverybeweis.
- **P1:** Observability/Incident/Backup.
- **P2:** HA/DR/Capacity.
- **P3:** Cost/Performance Operations.

### 22. Dokumentation — 7,4/10

**Begründung:** Die Dokumentationsmenge, Audittiefe, Product Master Book und Knowledge Architecture sind außergewöhnlich stark. Wert geht durch historische Statusseiten, quantitative Drift, redundante Aussagen, fehlende zentrale Support-/Incident-/DR-/Developer-Guides und teilweise leere/veraltete Kerndokumente verloren.

- **Stärken:** evidenzbasiert; breite Architektur-/Audit-/Runbookabdeckung; Authority Model.
- **Schwächen:** schwer navigierbar; historische Prozentwerte wirken aktuell; Master Book hinkt einzelnen Sprints hinterher.
- **Risiken:** falsche Entscheidung auf veraltetem Dokument; hoher Pflegeaufwand.
- **Fehlende Features:** kanonischer Documentation Hub, aktuelle Product Baseline und fehlende Betriebs-/Supportguides.
- **Quick Wins:** Dokumente als current/historical markieren; Counts automatisch synchronisieren.
- **Spätere Features:** docs-as-code Releaseevidenz und rollenbezogene Portale.
- **P0:** Pilotdokumentenpaket fixieren.
- **P1:** fehlende Operations-/Support-/Developer-Guides.
- **P2:** automatische Evidenzgenerierung.
- **P3:** externe Enterprise Knowledge Base.

### 23. Gesamtprodukt — 7,3/10

**Begründung:** Business Value, Differenzierung und Marktpotenzial sind höher als aktuelle Go-Live-/Enterprise-Reife. Der Produktkern ist überzeugend genug für Investition und einen kontrollierten Design-Partner-Pilot. Er ist nicht ausreichend bewiesen, operationalisiert und journey-stabil für einen sofortigen öffentlichen oder unbeaufsichtigten Start.

- **Stärken:** klarer BC-Markt; End-to-End-Wertkette; Executive Story; starke transaktionale Grundlagen.
- **Schwächen:** Trust-/Outcome-Evidenz, Public Journey und Operations hinken der Kernfunktion hinterher.
- **Risiken:** zu früher Launch macht Reportpräzision, Support und Betrieb zu Reputationsschäden.
- **Fehlende Features:** keine zusätzliche Breite als P0; fehlend sind Trust Layer, Outcome Loop und Operationsfähigkeit.
- **Quick Wins:** P0-Gates in einer fixierten Pilotbaseline schließen.
- **Spätere Features:** Benchmarking, Partnerdelivery, skalierbare Operations und internationale Expansion.
- **P0:** Design-Partner-Release Candidate beweisen.
- **P1:** öffentlicher Go-Live-Vertrag.
- **P2:** Enterprise Scale.
- **P3:** Plattform-/Ökosystemwachstum.

## Interne Konkurrenzanalyse

### Welches Modul ist bereits 10/10 und sollte nicht mehr verändert werden?

**Keines ist evidenzbasiert 10/10.** Das wäre angesichts offener Sandbox-, Operations- und Customer-Evidence nicht seriös. Am nächsten an einem „nicht leichtfertig verändern“-Kern liegen die transaktionalen Mechanismen hinter Tenantbindung, atomarem Creditverbrauch, Start-Idempotenz und Scan-Lease/Recovery. Unter den sichtbaren Komponenten ist der Executive PDF Report mit 7,8/10 am stärksten. Er sollte gezielt um Trust/Evidence erweitert, nicht grundsätzlich neu gestaltet werden.

### Welches Modul bringt aktuell den größten Kundennutzen?

**Findings.** Sie übersetzen 199 produktive Deep Checks in konkrete, priorisierbare Probleme und verbinden technische Realität mit Handlung. Der Report verkauft den Wert; Findings erzeugen ihn.

### Welches Modul wirkt im Vergleich zum Rest noch unfertig?

**Betriebsfähigkeit**, gefolgt von Scheduler und Supportfähigkeit. Der Produktkern ist deutlich weiter als das System, das ihn dauerhaft überwachen, wiederherstellen und betreuen muss.

### Wo passt die UX noch nicht zum Qualitätsniveau der übrigen Anwendung?

**Landingpage, technisches Registrierungsportal und Admin Backend.** Dashboard und PDF wirken wie ein Executive-Produkt; die öffentlichen und administrativen Übergänge wirken teilweise wie MVP- oder Engineering-Oberflächen.

### Welche drei Komponenten erhöhen den wahrgenommenen Produktwert am stärksten?

1. Executive PDF Report
2. Findings
3. Free Scan mit siebentägigem Result Access

Der Enterprise Check Catalog ist der fachliche Substanzträger hinter diesen sichtbaren Wertbeweisen.

### Welche drei Komponenten bergen aktuell das größte Risiko für einen Pilotkunden?

1. Betriebsfähigkeit — Detection, Backup/Restore und Incidentbetrieb sind nicht bewiesen.
2. Business Central Extension/Scheduler — reale Post-Fix-Sandbox-CATs sind offen.
3. Lizenz-/Registrierungs-/Free-Access-Kette — technisch stark verbessert, aber der aktuelle reale End-to-End-Pilotnachweis fehlt.

## Founder-Priorisierung

### Ohne Änderungen live bringen

Keine der 23 Komponenten sollte isoliert als „ohne Änderungen und ohne Gate“ freigegeben werden. Als stabil zu erhaltende Grundlagen gelten Tenantbindung, atomare Credits, Idempotenz, Lease/Recovery und der bestehende Executive-Report-Look.

### Vor dem Pilot verbessern beziehungsweise beweisen

Business Central Extension, Registrierung, Free Scan, Lizenzsystem, Scheduler, PDF, Security, Deployment, Support und Betriebsfähigkeit. Der Schwerpunkt liegt auf Ausführungsevidenz und Trust, nicht auf neuer Featurebreite.

### Erst nach dem Pilot verbessern

Advanced Analytics, persistierte Dashboardpreferences, Validation-Deltas, Monitoringbenachrichtigungen, Supportportal und rollenbasierte Executive Views.

### Erst für AppSource verbessern

AppSourceCop-/Manifest-/Signing-/Listing-Gates, vollständige Marketplace-Dokumente, zusätzliche AL-Negativ-/Upgradeautomation, Partnerassets und externe Support-/Legal-Reife.

### Komplett neu denken

Keine Kernkomponente muss komplett neu gedacht werden. Neu geordnet werden müssen die öffentliche Customer Journey und das Operationsmodell. Der technische Kern sollte evolutiv gehärtet, nicht ersetzt werden.

## Quellenbasis

Die Bewertungen konsolidieren insbesondere `CORE_PLATFORM_*`, `SCAN_ENGINE_*`, `CUSTOMER_EXPERIENCE_*`, `OPERATIONS_*`, `EXECUTIVE_*`, Product-Master-Book-Komponenten sowie `GL_01A_2_UNIFIED_SCAN_START_AUDIT.md`, `GL_01F_REGISTRATION_FIRST_RUN_UX_AUDIT.md`, `GL_01F_FIX01_BACKGROUND_SCAN_RECOVERY_AUDIT.md`, `GL_01F_FIX02_FREE_SCAN_ACCESS_AUDIT.md`, `GL_PILOT_01_SANDBOX_VALIDATION.md` und die BC-Extension-Release-Dokumente.
