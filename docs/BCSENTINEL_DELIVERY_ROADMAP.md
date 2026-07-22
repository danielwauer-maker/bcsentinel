# BCSentinel Delivery Roadmap GL-01 bis GL-07

**Stand:** 22. Juli 2026

**Planungsbasis:** `staging@5177b8e969a0cc1e0d7fad1bec4fdcbe3dae8c55`
**Planungshorizont:** relative Phasen und Gates; keine erfundenen Kalendertermine

## 1. Aktueller Ausgangspunkt

BCSentinel besitzt einen belastbaren Produktkern aus BC Extension, Backend, Scan Engine, Produktzugriff, Analytics/Dashboard, Executive Report, Billing-/Partnergrundlagen und einem mehrsprachigen Enterprise Check Catalog. Der aktuelle Stand ist dennoch kein Public- oder Enterprise-Release:

- Pilot und erster zahlender Design-Partner: **GO unter Bedingungen**;
- Public Go-Live: **NO-GO**;
- Enterprise Rollout: **NO-GO**;
- zentrale offene Evidenz: fachliche Golden Results, Exceptions Contract, vollständige Sandbox Customer Journey, releaseblockierendes Testgate, Backup/Restore/Rollback, Operations- und Pilotvereinbarung.

Nach dem Executive Assessment wurden relevante First-Run-, Scan-Recovery- und Free-Access-Fixes ergänzt. Sie verbessern die Pilotfähigkeit, ersetzen aber keine reale Runtime- und Release-Abnahme.

## 2. Roadmap auf einen Blick

| Phase | Leitfrage | Kernresultat | Marktstatus nach Exit |
|---|---|---|---|
| GL-01 Product Completion | Ist das Produkt für einen betreuten Partner funktional konsistent? | Product-Completion RC | noch kein Pilotstart ohne GL-03/04 Gates |
| GL-02 Customer Experience Final | Ist die gesamte marktseitige Journey klar und vertrauenswürdig? | marktfähige Customer Journey | noch kein Public Go-Live |
| GL-03 Operational Excellence | Kann das SaaS sicher betrieben und wiederhergestellt werden? | nachgewiesene Release-/Ops-/Recovery-Fähigkeit | technische Pilotvoraussetzung |
| GL-04 Design Partner Readiness | Ist der Pilot vertraglich und organisatorisch kontrolliert? | signiertes Pilotpaket und Go/No-Go | Pilot darf starten |
| GL-05 First Design Partner | Erzeugt das Produkt mit echten Daten nachweisbaren Nutzen? | validierte oder falsifizierte Produktannahmen | Entscheidung über Skalierung |
| GL-06 Public Go-Live | Ist Self-Service öffentlich sicher und supportbar? | kontrollierter Marktstart | Public verfügbar |
| GL-07 Enterprise Scale | Ist das Produkt technisch und organisatorisch enterprisefähig? | skalierbarer Enterprise-Betrieb | Enterprise-Rollout möglich |

## 3. GL-01 – Product Completion

**Ziel:** funktional vollständiger und konsistenter Release Candidate für einen streng betreuten Design-Partner.

**Wichtigste Deliverables**

- DH-Ausnahmen Domain Contract, Persistenz/API, BC Flow, Scan-/Score- und Disclosure-Integration;
- reale Abnahme von Registrierung, Welcome/Invite, erstem Login, Tenant-Auswahl und Access Snapshot;
- verständliche Setup Experience und konsistente DE/EN-Texte;
- Pilot-UX-Polish und konsolidierte Pilotdokumentation;
- fixer Product-Completion RC.

**Entry Criteria**

- Executive Pilotentscheidung vorhanden;
- Repository-/Git-/Versionenbaseline bekannt;
- Product-Completion-Inventur priorisiert.

**Exit Criteria**

- GL-01A–J Definition of Done erfüllt;
- Exceptions Roh-/Adjusted-Score und Disclosure fachlich freigegeben;
- kanonische Pilot Journey in Sandbox bestanden;
- fixer Commit, Versions-/Migration-/Config-Matrix und Releaseakte;
- offene Public-/Enterprise-Themen klar abgegrenzt.

**Abhängigkeiten/Gates:** Founder-Entscheidungen zu Exceptions; Golden Dataset; Sandbox/SMTP/Browser; PostgreSQL- und AL-Testumgebung; Restore-/Rollback-Evidenz.

**Hauptrisiko:** UI-Fertigstellung wird mit fachlicher/operativer Freigabe verwechselt.

## 4. GL-02 – Customer Experience Final

**Ziel:** konsistente, vertrauenswürdige und marktfähige Customer Journey jenseits des betreuten Pilots.

**Deliverables**

- kanonische Landingpage und Produkt-/Preispositionierung;
- Dashboard/Analytics UX, responsive Verhalten und Accessibility-Baseline;
- Free vs Full, Upgrade, Checkout und Billing-Kommunikation;
- durchgängiges Branding, Trust Elements, Fehler-/Empty-/Loading States;
- Self-Service-nahe Journey-Spezifikation, noch ohne Public-Freigabe.

**Entry Criteria:** stabiler GL-01 RC und Terminologie/Capabilities eingefroren.

**Exit Criteria:** Journey-Tests DE/EN, responsive/accessibility smoke, konsistente Pricing-/Checkout-Aussage, keine Customer-Sackgassen.

**Abhängigkeiten:** Product Pricing, Legal/Privacy, Billing-Konfiguration, GL-01 Access Snapshot.

**Entscheidungspunkt:** Reicht die Experience für kontrollierte externe Akquise oder bleibt sie design-partnergeführt?
**Risiken:** Marketing verspricht mehr als getestete Produkt-/Operationsfähigkeit.

## 5. GL-03 – Operational Excellence

**Ziel:** sicherer, messbarer und wiederherstellbarer SaaS-Betrieb.

**Deliverables**

- releaseblockierendes Backend-/Migration-/AL-Testgate vor Deployment;
- Monitoring, Telemetry, Alerting und verständliche Runbooks;
- Backup, Restore, Rollback und Disaster-Recovery-Drills;
- Secret Lifecycle, Backend-RBAC und MFA-/SSO-Nachweis für privilegierte Zugänge;
- AL-Testautomation, PostgreSQL-Integrationstests und Artefaktprovenienz;
- Performance/Capacity/Multiinstance-Verhalten, Incident Management, Support, SLO, RTO/RPO.

**Entry Criteria:** bekannte Architektur und RC-Buildpfad.

**Exit Criteria:** Tests blockieren Deployment; Restore/Rollback unter dokumentierten Zielen nachgewiesen; Alerts/On-call/Incidentweg getestet; Capacity-Grenze bekannt.

**Abhängigkeiten:** produktionsnahe Infrastruktur und verantwortliche Operatoren.

**Entscheidungspunkt:** Ist der Pilotbetrieb innerhalb der vereinbarten Daten-/Ausfallgrenzen verantwortbar?
**Risiken:** Health Check ohne fachliche Tests; Single-Founder-Betrieb; Recovery nur dokumentiert.

## 6. GL-04 – Design Partner Readiness

**Ziel:** Pilot vertraglich, organisatorisch und technisch kontrollierbar machen.

**Deliverables**

- Design-Partner-Kriterien und ausgewählter Partner;
- Pilotvertrag, Datenschutz/DPA, Datenumfang und Grenzen;
- messbare Success-/Abort-Kriterien;
- Support-, Incident-, Kommunikations- und Feedbackprozess;
- freigegebener RC, Pilot Runbook und formales Go/No-Go.

**Entry Criteria:** GL-01 RC; pilotrelevante GL-03 Gates bestanden; fachlicher Golden-Result-Nachweis.

**Exit Criteria:** beidseitig signierter Scope; Verantwortliche und Eskalation benannt; Daten-/Recovery-/Supportgrenzen akzeptiert; Startfreigabe protokolliert.

**Abhängigkeiten:** Founder, Partner, Datenschutz/Legal, Operations.

**Entscheidungspunkt:** Start, begrenzte Nacharbeit oder Abbruch.
**Risiken:** unbegrenzte Erfolgserwartung, fehlende Datenfreigabe oder unklare Incident-Verantwortung.

## 7. GL-05 – First Design Partner

**Ziel:** mit echten Kundendaten Produktnutzen und fachliche Annahmen validieren.

**Deliverables**

- kontrolliertes Onboarding/Installation/erster Scan;
- Validierung von Score, Findings, Severity und Financial Impact;
- Review von Ausnahmen und Executive Report;
- Nutzungsbeobachtung, Interviews, Fehler-/Incident-Auswertung;
- Pilotabschlussbericht und Entscheidung über nächsten Kunden.

**Entry Criteria:** GL-04 GO und unveränderter RC.

**Exit Criteria:** vordefinierte Success-/Abort-Metriken ausgewertet; fachliche Abweichungen klassifiziert; Incidents geschlossen; Folgeentscheidung signiert.

**Abhängigkeiten:** Partnerverfügbarkeit, Datenqualität, Support-/Incidentteam.

**Entscheidungspunkt:** iterieren, zweiten Design-Partner zulassen oder stoppen.
**Risiken:** Einzelkunde wird als Marktbeweis überinterpretiert; Workarounds werden Produktstandard.

## 8. GL-06 – Public Go-Live

**Ziel:** kontrollierter öffentlicher Marktstart.

**Deliverables**

- echter Self-Service von Akquise bis Nutzung/Kündigung;
- Stripe Live, Billing-Reconciliation und öffentlich korrekte Preise;
- Supportkapazität, Betriebsnachweise und Release Management;
- finale rechtliche Dokumente, Privacy/Retention, Marketing/Sales Funnel;
- Public Go-Live Checkliste und Rollback-/Kommunikationsplan.

**Entry Criteria:** erfolgreicher Design-Partner-Lernzyklus; GL-02/03 abgeschlossen; Produkt-/Preisfit ausreichend belegt.

**Exit Criteria:** Self-Service E2E, Legal, Billing, Support, Security, Recovery und Observability freigegeben; Public Go/No-Go signiert.

**Abhängigkeiten:** echte Payment-/Mail-/Domain-/Supportsysteme.

**Entscheidungspunkt:** schrittweiser Launch, Warteliste oder No-Go.
**Risiken:** Volumen überholt Support/Capacity; Live Billing und Vertragstexte divergieren.

## 9. GL-07 – Enterprise Scale

**Ziel:** Enterprise-Rollout und nachhaltige Skalierung.

**Deliverables**

- AppSource-/Partner-Distribution;
- Hochverfügbarkeit, Multi-Host, Failure Domains und Capacity Automation;
- Enterprise Identity/RBAC, Audit/Compliance und SLA-Fähigkeit;
- Datenbank-HA, skalierbarer Worker-/Schedulerbetrieb und belastbare Benchmarks;
- Supportorganisation und organisatorische Entkopplung vom Founder.

**Entry Criteria:** stabiler Public-Betrieb oder explizit finanzierter Enterprise-Track; reale Last-/Supportdaten.

**Exit Criteria:** HA/DR/Scale getestet; Enterprise Security/Identity/Audit belegt; SLAs operationalisierbar; Delivery/Support nicht foundergebunden.

**Abhängigkeiten:** Team, Budget, Kundenanforderungen, Hosting-/Compliance-Ziel.

**Entscheidungspunkt:** AppSource/Enterprise Segment freigeben oder weiter begrenzen.
**Risiken:** vorzeitige Plattformkomplexität ohne validierten Markt; Compliance nur als Dokument.

## 10. Meilensteine und Gates

| Meilenstein | Nachweis | Freigabe |
|---|---|---|
| M1 Delivery Baseline | GL-01A Artefakte, sauberer Scope | Start Domain Contract |
| M2 Exceptions Contract | signierte Decision Matrix und Golden Vectors | Backend/BC Implementierung |
| M3 Product-Complete Candidate | reconciliertes Exceptions E2E, Onboarding-/Setup-CAT | RC-Erstellung |
| M4 Fixed RC | Commit/Version/Migration/Config/Testakte | Pilot Readiness |
| M5 Operational Gate | CI/Test, Restore/Rollback, Alerts/Incident | Pilot Go/No-Go |
| M6 Pilot Contract Gate | Scope, Datenschutz, Success/Abort, Support signiert | echter Kundendatenstart |
| M7 Pilot Evidence | fachliche/technische Outcome-Auswertung | nächster Partner/Public-Entscheid |
| M8 Public Gate | Self-Service, Live Billing, Legal, Support, Ops | Public Launch |
| M9 Enterprise Gate | HA/Scale/Identity/Compliance/SLA/Organisation | Enterprise Rollout |

## 11. Kritischer Pfad und Parallelisierung

Kritischer Pfad: **Exceptions Contract → Persistence/API → BC Flow → Score/Disclosure → Journey/Setup → Dokumentation → RC → Operational/Pilot Gates → echter Pilot**.

Sinnvoll parallel, ohne Scopevermischung:

- Golden Dataset und fachliche Reviewvorbereitung während GL-01B/C;
- SMTP-/Sandbox-Testvorbereitung während Exceptions-Implementierung;
- GL-03 CI-/Restore-Arbeit nach stabiler Buildmatrix, bevor GL-04 freigibt;
- Pilotvertrag/Datenschutzentwurf während GL-01, finale Signatur erst mit fixem RC und bekannten Grenzen.

Nicht parallel als unabhängige Wahrheit: Score-/Exception-Implementierung vor Domain Contract, Report vor Result Contract oder Public-Marketing vor getesteter Produkt-/Operationsfähigkeit.

## 12. Nächste konkrete Codex-Etappe

**GL-01B – DH-Ausnahmen Domain Contract & Safety Freeze.** Codex soll im nächsten Sprint keine breite Funktion implementieren, sondern die Founder-Entscheidungen in einen versionierten Domain-/API-/Scorevertrag und ausführbare Golden-Testvektoren übersetzen. Erst die signierte Entscheidung öffnet GL-01C.
