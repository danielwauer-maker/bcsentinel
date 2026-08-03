# BCSentinel Action Plan – 10 betreute Pilotkunden

**Ausgangslage:** Audit vom 2026-08-03, `staging@be29fd134465a0e05fdb5eca83c06ffc1e702b66`  
**Ziel:** schnellster sichere Weg zu einem und anschließend zehn betreuten Pilotkunden  
**Regel:** Kein Schritt gilt durch Code oder Dokumentation allein als abgeschlossen. Das jeweilige Exit-Kriterium und der verlangte Beweis müssen vorliegen.

## Verbindliche Reihenfolge und Gates

| Nr. | Sprint | Phase | Ziel/Ergebnis | Priorität | Codex | Daniel | Voraussetzung | Readiness-Gewinn |
| ---: | --- | --- | --- | --- | ---: | ---: | --- | ---: |
| 1 | RC-00A | 0 | Releasezweige konsolidiert, RC-SHA festgelegt | P0 | 2–4 h | 1 h | PR #20/#15 zugänglich | +4 % |
| 2 | RC-00B | 0 | reproduzierbares 1.0.2.17-Artefakt, AL/CodeCop/PTECop grün | P0 | 2–4 h | 1 h | RC-00A | +8 % |
| 3 | DB-00C | 0 | PostgreSQL Migration/Konkurrenz und U/D/U grün | P0 | 2–4 h | 1 h | isolierte Test-DB | +6 % |
| 4 | EXT-P0-01 | 1 | BC Install/Registrierung/Free Journey bestanden | P0 | 3–5 h | 2–3 h | RC-Artefakt, BC-27-Sandbox | +8 % |
| 5 | EXT-P0-02 | 1 | Assessment/Validation/Zugriffsablauf bestanden | P0 | 3–5 h | 2 h | EXT-P0-01 | +5 % |
| 6 | MON-P0-03 | 1 | manueller und geplanter Monitoringlauf inkl. Historie bestanden | P0 | 4–6 h | 3 h + 24 h Wartefenster | Monitoringgrant, Schedulerrolle | +10 % |
| 7 | REC-P0-04 | 1 | Abbruch/Lease/Retry/kein Doppelcredit real bestanden | P0 | 3–5 h | 2 h | MON-P0-03 | +5 % |
| 8 | OPS-P0-05 | 1/5 | Backup/Restore, Alarming, Rollback und Adminhärtung bewiesen | P0 | 1–2 d | 1 d | Stage/Backupziel/Alarmkanal | +10 % |
| 9 | COM-01 | 2 | kontrollierte manuelle Pilotfreischaltung und Reconciliation | P0 | 0.5–1 d | 2 h | Adminportal/Vertrag | +4 % |
| 10 | BILL-02 | 2 | Stripe Testmode E2E oder bewusst aus Pilotumfang ausgeschlossen | P1 | 1–2 d | 0.5–1 d | Stripe Testkonto | +3 % |
| 11 | MAIL-01 | 3 | Zugang, Fehlerwarnung und Pilotkommunikation zuverlässig | P0/P1 | 0.5–1 d | 2–3 h | SMTP oder sicherer Ersatzkanal | +4 % |
| 12 | DOC-01 | 4 | kundenfertiges Pilotpaket und Operatorhandbuch | P0 | 1–2 d | 0.5–1 d | stabiler RC/Prozess | +7 % |
| 13 | UX-01 | 4 | Pilotpfade ohne Legacycopy, Platzhalter und mobile Clippingfehler | P1 | 1–2 d | 2–3 h | kanonische Produktentscheidung | +3 % |
| 14 | OPS-10A | 5 | 10-Tenant Last-/Soak- und Kapazitätsgate | P0 für Kunde 10 | 1–2 d | 0.5 d | Stage, synthetische Tenants | +7 % |
| 15 | DRY-01 | 6 | vollständiger Pilot-Dry-Run inklusive Upgrade | P0 | 1 d | 1 d | Schritte 1–14 relevant grün | +8 % |
| 16 | GO-01 | 7 | Freigabe Kunde 1 | P0 | 1 h | 1 h | Gate A vollständig | +4 % |
| 17 | WAVE-02 | 7 | Pilotstaffel 2→3→5→10 mit Review je Welle | P0 | 2 h/Welle | 2–4 h/Welle | keine offenen P0, SLO stabil | +6 % |

Readiness-Gewinne sind Planungswerte, nicht additiv garantierte Messwerte.

## Phase 0 – Tatsächlichen Release-Stand festlegen

### Schritt 1 – RC-00A: Release Candidate definieren

- **Ziel:** genau ein unveränderlicher Commit als Pilotbasis; Empfehlung: Inhalt von `origin/release/1.0.2.16@023f3a6` (Manifest 1.0.2.17) plus aktuell integriertes Sandbox-Evidence-Gate.
- **Begründung:** `staging` ist wegen doppelter AL-ID nicht releasefähig; parallele offene Release-PRs verhindern eindeutige Evidenz.
- **Aufgaben:** PR #20 diff/History prüfen; #17–#19 als durch #20 superseded schließen oder dokumentieren; PR #15 rebasen bzw. Evidence-Dateien konfliktfrei übernehmen; keine funktional unabhängigen Branches blind mergen; RC-Branch `codex/pilot-rc-1.0.2.17` oder freigegebene Alternative erstellen; Commit SHA protokollieren.
- **Komponenten:** Git, BC Extension, CI/Evidence.
- **Abhängigkeiten:** keine Produktivmutation; Daniel entscheidet Merge-/Branchstrategie.
- **Akzeptanzkriterien:** ein RC-SHA; saubere Working Tree Basis; alle enthaltenen/ausgeschlossenen PRs mit Grund; App-Version eindeutig 1.0.2.17; keine parallele „neueste“ Releasebasis.
- **Automatische Tests:** `git diff --check`; `scripts/validate_bc_extension.py`; Source-Uniqueness.
- **Manuelle Tests:** PR-Metadaten/Commitgraph/Files gegen Audit prüfen.
- **Codex-Anteil:** Analyse, Konfliktprüfung, Integrationspatch nach Freigabe.
- **Daniel-Anteil:** Merge-/Branchfreigabe, alte PRs ordnen.
- **Aufwand:** C 2–4 h; D 1 h.
- **Exit:** RC-SHA und Scope im Releaseprotokoll.
- **Gate:** **NO-GO**, solange zwei mögliche Releasebasen existieren.

### Schritt 2 – RC-00B: reproduzierbarer BC-Build

- **Ziel:** installierbares, reproduzierbares und analysiertes RC-Artefakt.
- **Begründung:** ein getracktes `.app` ersetzt keinen Build des RC-SHA.
- **Aufgaben:** Workspace mit `New-BCBuildWorkspace.ps1` unter `.build/bc-extension/ReleaseCloud`; BC 27 Compile; CodeCop/PTECop; Warnungen getrennt von bekannter AppSourceCop-Baseline ausgeben; `.app` und SHA-256 als CI-Artefakt; Manifest-/Objekt-ID-Report.
- **Komponenten:** AL, GitHub Actions, Buildartefakte.
- **Abhängigkeiten:** RC-00A; BC-Artifact/Runner.
- **Akzeptanzkriterien:** Compile Exit 0; Source-Uniqueness 0 Befunde; CodeCop/PTECop keine neuen Fehler/Warnungen gemäß Releasepolicy; Artefaktname/Version/SHA dokumentiert.
- **Automatische Tests:** `validate_bc_extension.py`, AL Contracts, XLIFF XML, Compile/Analyzer.
- **Manuelle Tests:** Artefaktmanifest und Download öffnen; SHA mit CI vergleichen.
- **Codex-Anteil:** Workflow/Diagnose, nur notwendige Fixes.
- **Daniel-Anteil:** Actions auslösen und Freigabelog verknüpfen.
- **Aufwand:** C 2–4 h; D 1 h.
- **Exit:** signiertes/attestiertes RC-Artefakt im Evidencepaket.
- **Gate:** **NO-GO** bei fehlendem/rotem Build.

### Schritt 3 – DB-00C: PostgreSQL- und Migrationsgate

- **Ziel:** reale PostgreSQL-Semantik und Upgradefähigkeit bestätigen.
- **Begründung:** sieben kritische Konkurrenztests wurden lokal übersprungen; SQLite darf sie nicht ersetzen.
- **Aufgaben:** isolierte PostgreSQL-16-Testinstanz; Alembic `upgrade head`; P0E-Suite; Bestandsfixture; Downgrade auf vorher vereinbarten sicheren Revisionpunkt; Zähl-/Constraintprüfung; erneutes `upgrade head`; App-Startup/Ready.
- **Komponenten:** PostgreSQL, Alembic, Backend.
- **Abhängigkeiten:** eindeutig als Test markierte DB; Backup der Fixture.
- **Akzeptanzkriterien:** 7/7 P0E PASS; ein Alembic Head; U/D/U ohne Daten-/Constraintverlust; `/health/ready` 200.
- **Automatische Tests:** `test_p0e_postgres_concurrency.py`, Deployment Readiness, SQL-Zählungen.
- **Manuelle Tests:** DB-/Umgebungsidentität vor jedem schreibenden Schritt bestätigen; Logs auf Secrets prüfen.
- **Codex-Anteil:** Befehle, Analyse, minimale Migrationfixes falls nötig.
- **Daniel-Anteil:** Testumgebung bereitstellen/freigeben.
- **Aufwand:** C 2–4 h; D 1 h.
- **Exit:** JUnit + Migrationlog + Vor/Nach-Zählung.
- **Gate:** **NO-GO** bei SKIP/FAIL.

## Phase 1 – Technische P0-Blocker schließen

### Schritt 4 – EXT-P0-01: Installation, Registrierung und Free Scan

- **Ziel:** erster Kundenpfad bis zum verwertbaren Free-Ergebnis.
- **Begründung:** dies ist der kleinste reale Wertstrom und Voraussetzung für alle Produkte.
- **Aufgaben:** frische BC-27-Sandbox; App installieren; Rollen zuweisen; Setup; Registrierung; simulierte verlorene Antwort + Retry; Free Scan; Status/History; Findings; Dashboard; Free HTML/PDF.
- **Komponenten:** BC, API, DB, Dashboard, Report.
- **Abhängigkeiten:** RC-00B, DB-00C, Stage API/HTTPS, Pilotmail.
- **Akzeptanzkriterien:** genau ein Tenant/User/Membership; Company-/Environmentbindung korrekt; ein abgeschlossener Run; keine Secrets in UI/Logs; Ergebnis dauerhaft erreichbar; Fremdtenant-Negativtest 401/403.
- **Automatische Tests:** vollständige Backend-Suite und Evidence-Validator.
- **Manuelle Tests:** Audit M02–M04.
- **Codex-Anteil:** begleiten, Logs korrelieren, nur reproduzierte Fehler minimal beheben.
- **Daniel-Anteil:** BC-Sandbox bedienen und Screenshots/Evidence ablegen.
- **Aufwand:** C 3–5 h; D 2–3 h.
- **Exit:** Installation-/Registration-/Free-Gates PASS.
- **Gate:** **NO-GO** bei jedem Fehler oder fehlender Evidence.

### Schritt 5 – EXT-P0-02: Assessment, Validation und Ablauf

- **Ziel:** mindestens ein kompletter bezahlbarer Produktfluss ohne Stripeabhängigkeit.
- **Begründung:** Pilotwert entsteht durch vollständige Findings/Report und kontrollierten Folgecheck.
- **Aufgaben:** Assessment via Admin grant; Snapshot refresh; vollständige Findings/Report; Ablauf testen; Validationcredit zuweisen; Start/Retry/Konkurrenz; Ledger prüfen; Rechte nach Abschluss/Ablauf prüfen.
- **Komponenten:** Admin, Entitlements, BC, Dashboard, Reports, Ledger.
- **Abhängigkeiten:** EXT-P0-01.
- **Akzeptanzkriterien:** Rechte sofort und tenantgebunden; Assessment erzeugt keinen unberechtigten neuen Scan; Validation verbraucht genau einen Credit; Retry verbraucht keinen zweiten; Ablauf fail-closed mit erlaubtem Free-Fallback.
- **Automatische Tests:** P0B/P0D/Product Licensing/Billing Regression.
- **Manuelle Tests:** Audit M05–M06.
- **Codex-Anteil:** Testdaten/Evidenceauswertung.
- **Daniel-Anteil:** Admin- und BC-Aktionen.
- **Aufwand:** C 3–5 h; D 2 h.
- **Exit:** Product Journey PASS.
- **Gate:** **NO-GO** bei Isolation-, Credit- oder Ablaufabweichung.

### Schritt 6 – MON-P0-03: Monitoring manuell und geplant

- **Ziel:** bekannter Background-Monitoringfehler nachweislich geschlossen.
- **Begründung:** Monitoring ist Kernelement und der letzte reale Pilotversuch zeigte fehlende Historie.
- **Aufgaben:** 1.0.2.17 installieren; Monitoring grant; manuellen Start auslösen; Responsiveness/Historie/Backendstatus prüfen; TaskScheduler konfigurieren; Nutzer abmelden; geplanten Lauf abwarten; Erfolgs- und Failurefelder/Next Run prüfen; mindestens 24 Stunden Soak.
- **Komponenten:** BC Background Session, TaskScheduler, API Lifecycle, History.
- **Abhängigkeiten:** EXT-P0-02; Scheduler Permission Set.
- **Akzeptanzkriterien:** manueller Start kehrt sofort zurück; Run erscheint; queued→running→completed; geplanter Lauf ohne User Session; nächster Task geplant; Fehler schreibt Originaldiagnose statt Concurrencyfehler.
- **Automatische Tests:** GL01F Background Contract, Fix03–05, P0C.
- **Manuelle Tests:** Audit M07–M08.
- **Codex-Anteil:** Log-/Statuskorrelation, Fehlerreproduktion.
- **Daniel-Anteil:** BC-Aktionen und 24h-Kontrolle.
- **Aufwand:** C 4–6 h; D 3 h verteilt; 24 h Kalenderzeit.
- **Exit:** beide Monitoringpfade PASS mit Run-ID-Evidence.
- **Gate:** **NO-GO** bei fehlendem Historyeintrag oder stillem Exit.

### Schritt 7 – REC-P0-04: Fehler und Recovery

- **Ziel:** kein dauerhaft hängender Run und kein Doppelcredit.
- **Begründung:** bei zehn Kunden muss ein Abbruch beherrschbar sein.
- **Aufgaben:** Worker/BC-Session in Stage kontrolliert abbrechen; Heartbeat/Lease ablaufen; Recovery beobachten; alten Token wiederverwenden; Retry mit identischer Start-ID; Max-Attempt-Fall; Supportdiagnose durchführen.
- **Komponenten:** Scan Lifecycle, BC Failure Codeunits, Admindiagnose.
- **Abhängigkeiten:** MON-P0-03.
- **Akzeptanzkriterien:** terminaler oder kontrolliert requeued Status; alte Workerwrites abgewiesen; gleicher Run/kein zweiter Credit; verständliche Diagnose/Request ID; Recovery innerhalb definiertem Ziel.
- **Automatische Tests:** P0C/Fix04/Fix05.
- **Manuelle Tests:** Audit M09.
- **Codex-Anteil:** Testorchestrierung/Analyse.
- **Daniel-Anteil:** Störung autorisieren, Supportpfad ausführen.
- **Aufwand:** C 3–5 h; D 2 h.
- **Exit:** Recovery-Evidence PASS.
- **Gate:** **NO-GO** bei orphaned Run oder Doppelverbrauch.

### Schritt 8 – OPS-P0-05: Betriebs- und Sicherheitsfundament

- **Ziel:** Datenverlust, unbemerkte Ausfälle und ungeschützte Adminmutationen verhindern.
- **Begründung:** diese Risiken sind nicht durch betreute Bedienung kompensierbar.
- **Aufgaben:** verschlüsseltes DB-Backup; isolierter Restore; RPO/RTO; Image/DB-Rollback; externer `/health/ready` Monitor; Alarm für 5xx/Scan failures/stale runs/Backupfehler/Disk; Logrotation/Containerlimits; Admin nur VPN/IP-Allowlist; Secretrechte/Rotation; Incidentübung.
- **Komponenten:** Host, PostgreSQL, Docker, Nginx, Monitoring, Admin.
- **Abhängigkeiten:** Stage/Backupziel/Alarmkanal.
- **Akzeptanzkriterien:** Restore erfolgreich; Alarm innerhalb 5 min; Rollback ohne Datenverlust gemäß Runbook; Admin nicht aus offenem Internet erreichbar; Secrets nicht in Git/Logs; On-call-Verantwortung dokumentiert.
- **Automatische Tests:** Health/Readiness, Restore-SQL-Checks, Security Headers, optional pip-audit/image scan.
- **Manuelle Tests:** Audit M13–M14.
- **Codex-Anteil:** Scripts/Runbooks/Checks nach separater Umsetzungserlaubnis.
- **Daniel-Anteil:** Infrastruktur-/DNS-/Backupzugriff, Alarmempfang, Freigabe.
- **Aufwand:** C 1–2 d; D 1 d.
- **Exit:** Operations-Evidencepaket vollständig.
- **Gate:** **NO-GO** ohne Restore oder Alarm.

## Phase 2 – Kommerziellen End-to-End-Prozess absichern

### Schritt 9 – COM-01: manuelle Pilotfreischaltung

- **Ziel:** sicherer kommerzieller Pilot ohne Stripe-P0-Abhängigkeit.
- **Begründung:** zehn betreute Kunden lassen sich mit Auditlog und Checkliste kontrolliert manuell führen.
- **Aufgaben:** Pilotvereinbarung/Bestellbestätigung; Tenant-ID gegen Kunde prüfen; Assessment/Validation/Monitoring grant; Laufzeit/Credit festhalten; Adminaudit prüfen; Rechnung extern; tägliche Reconciliationliste; Vier-Augen-Check bei Revoke/Reset/Delete.
- **Komponenten:** Adminportal, CRM/Vertragsablage außerhalb Repo, Auditlog.
- **Abhängigkeiten:** EXT-P0-02, Rechts-/Datenschutzfreigabe.
- **Akzeptanzkriterien:** keine direkte DB-Manipulation; jede Freischaltung hat Ticket/Vertrag/Tenant-ID/Produkt/Zeitraum/Audit-Event; Rücknahme getestet.
- **Automatische Tests:** Admin Grant/Revoke/Credit/Audit.
- **Manuelle Tests:** Testkunde komplett freischalten und widerrufen.
- **Codex-Anteil:** Checkliste/Vorlagen.
- **Daniel-Anteil:** Vertrag, Rechnung, Freigabe.
- **Aufwand:** C 0.5–1 d; D 2 h Setup + 15 min/Kunde.
- **Exit:** Pilotfreischaltungsprotokoll freigegeben.
- **Gate:** **GO WITH CONDITIONS** möglich; Stripe bleibt out of scope.

### Schritt 10 – BILL-02: Stripe Testmode

- **Ziel:** optionaler Checkout verlässlich; nicht auf kritischen Pilotpfad setzen, bis grün.
- **Begründung:** Code ist mockgetestet, Provider-/Tax-/Fehlerfälle nicht.
- **Aufgaben:** vier Testprodukte/Prices; Beträge; Checkout success/cancel; Webhooksignatur; Duplicate/Delay; Test Clock renewal/cancel/failure; Portal; Tenantzuordnung; Refund/Dispute als manueller Runbookfall; keine echten Zahlungen.
- **Komponenten:** Stripe Testmode, API, Admin, Entitlements.
- **Abhängigkeiten:** Price-Signoff, Stripe-Zugang.
- **Akzeptanzkriterien:** alle Testmode-Fälle PASS; Idempotenz; korrekte Rechte; Events redigiert dokumentiert; Live bleibt deaktiviert bis Steuer/Recht grün.
- **Automatische Tests:** Billing/Product Licensing.
- **Manuelle Tests:** Audit M16.
- **Codex-Anteil:** E2E-Testbegleitung/Fixes.
- **Daniel-Anteil:** Stripe Dashboard/Test Clock.
- **Aufwand:** C 1–2 d; D 0.5–1 d.
- **Exit:** Stripe-Testmatrix signiert oder förmlich als „nicht im Pilot“ markiert.
- **Gate:** P1 Pilot, P0 vor Self-Service.

## Phase 3 – Statusmails und Kommunikation

### Schritt 11 – MAIL-01: minimale Pilotkommunikation

- **Ziel:** Kunde und Betreiber erhalten rechtzeitig alle notwendigen Informationen.
- **Begründung:** fehlende Automation darf Fehler nicht unsichtbar machen.
- **Aufgaben:** sicheren Invite testen; SPF/DKIM/DMARC; Vorlagen für Welcome, Aktivierung, Scanfehler, Monitoringfehler, Reportlink, Wartung/Incident; tägliche Cockpitprüfung mit Owner; deduplizierte manuelle Versandliste; keine sensiblen Findings per Mail.
- **Komponenten:** SMTP/DNS oder definierter Supportkanal, Runbook.
- **Abhängigkeiten:** echte Domain/Testinbox.
- **Akzeptanzkriterien:** Invite DE/EN zugestellt; Operatorwarnung bei Stagefehler; Vorlagen freigegeben; Reaktionszeit und Stellvertretung festgelegt.
- **Automatische Tests:** vorhandene Invite-/Template-Tests; später Mail-Outbox-Tests.
- **Manuelle Tests:** Audit M15 und Failure Drill.
- **Codex-Anteil:** Vorlagen/Outbox-Tests nach Umsetzungserlaubnis.
- **Daniel-Anteil:** DNS/Provider/Inbox/SLA.
- **Aufwand:** C 0.5–1 d; D 2–3 h.
- **Exit:** Kommunikationsmatrix mit Owner/Kanal/Frist.
- **Gate:** Zugang und Operatorfehlerwarnung P0; übrige Mails P1/P2.

## Phase 4 – Dokumentation und Onboarding

### Schritt 12 – DOC-01: Pilotpaket

- **Ziel:** Kunde und Operator folgen einem einzigen aktuellen Satz von Anleitungen.
- **Begründung:** bestehende technische Audits sind kein kundenfähiges Onboarding.
- **Aufgaben:** Installation/Upgrade; QuickStart mit Registrierung/Free Scan; manuelle Assessmentfreischaltung; Validation; Monitoring/TaskScheduler; Dashboard/Findings/Reports; Exceptions; Rollen; Troubleshooting/Request ID; Deinstallation; Datenschutz/DPA; Known Limitations; Pilotcheckliste/-abnahme; Admin-/Backup-/Incident-/Release-/Rollbackhandbuch.
- **Komponenten:** `docs/`, Kundenpaket.
- **Abhängigkeiten:** stabile UI/RC und getestete Schritte.
- **Akzeptanzkriterien:** keine alten Versionen/Preise/Legacybegriffe/Platzhalter; Screenshot je kritischem Schritt; fremder Testnutzer schafft Journey ohne Zusatzwissen; Dokumentversion = RC.
- **Automatische Tests:** Linkcheck, Terminologie-/Placeholder-Scan.
- **Manuelle Tests:** Daniel liest und ein zweiter Tester führt QuickStart aus.
- **Codex-Anteil:** Entwurf/Konsolidierung/Prüfung.
- **Daniel-Anteil:** Screenshots, fachliche/rechtliche Freigabe.
- **Aufwand:** C 1–2 d; D 0.5–1 d.
- **Exit:** versioniertes Pilotpaket und Abnahmeprotokoll.
- **Gate:** **NO-GO** ohne QuickStart, Support und Known Limitations.

### Schritt 13 – UX-01: Pilotpfade bereinigen

- **Ziel:** keine sichtbare Produkt-/Preis-/Sprach- oder Platzhalterdrift.
- **Begründung:** verhindert Vertrauensverlust, ohne Landingpage komplett neu zu bauen.
- **Aufgaben:** „Assessment“ als Customer Copy; Storage-Alias `full_analysis` intern belassen; 79/49/149/1490 oder bewusst freigegebene Tiermatrix überall angleichen; `EUR-`, `[Telefonnummer]`, Mockup-/vorläufige Texte, unbewiesene 99.9%-Claims entfernen/ausblenden; 390px Clipping; Reportfallback; AL Pilotpfade DE/EN.
- **Komponenten:** Landing, Dashboard, AL Setup, Reports, Pricing.
- **Abhängigkeiten:** Daniels Preis-/Produktentscheidung.
- **Akzeptanzkriterien:** automatisierter Driftcheck grün; Browser 390/768/1440; DE/EN; keine sichtbaren Legacybegriffe im Pilotpfad; Stripe/DB/Copy konsistent.
- **Automatische Tests:** ARCH-02A Copy, Pricing Consistency, Localization, Linkcheck.
- **Manuelle Tests:** Browser-/Report-/BC-Screenshotreview.
- **Codex-Anteil:** gezielte Copy/CSS/Contracts nach Umsetzungserlaubnis.
- **Daniel-Anteil:** Preis-/Legal-/Brand-Signoff.
- **Aufwand:** C 1–2 d; D 2–3 h.
- **Exit:** Content-Signoff.
- **Gate:** P1 Pilot; P0 vor öffentlicher Akquise.

## Phase 5 – Betrieb für zehn Kunden

### Schritt 14 – OPS-10A: 10-Tenant Last-/Soak-/Supportgate

- **Ziel:** Kapazität und Betrieb für zehn parallele Kunden belegen.
- **Begründung:** Unit-Tests zeigen Korrektheit, nicht Laufzeit-/Operatorverhalten.
- **Aufgaben:** zehn synthetische Tenants, mindestens zwei Companies/Environments; versetzte und überlappende Starts; geplante Tasks; Reports; Login/Tenant switch; ein Worker-/DB-Fehler; CPU/RAM/DB-Conns/Disk/Latenz; tägliche Reconciliation; Supporttickets simulieren.
- **Komponenten:** Stage, BC Sandboxes, PostgreSQL, Monitoring, Support.
- **Abhängigkeiten:** OPS-P0-05, MON-P0-03, REC-P0-04.
- **Akzeptanzkriterien:** 0 Isolation-/Doppelcreditfehler; definierte p95-Zielwerte; keine hängenden Runs; Alarme/Recovery; Operatoraufwand ≤45 min/Tag ohne Onboarding; Backup läuft während Soak.
- **Automatische Tests:** P0E, Loadscript, Status-/Ledgerassertions.
- **Manuelle Tests:** Audit M19–M20.
- **Codex-Anteil:** Lastszenario/Auswertung.
- **Daniel-Anteil:** Infrastruktur beobachten, Supportrolle.
- **Aufwand:** C 1–2 d; D 0.5 d; mindestens 24 h Kalenderzeit.
- **Exit:** Kapazitätsbericht mit Grenzwerten.
- **Gate:** **NO-GO für Kunde 6–10** ohne PASS.

### Tägliche Pilotkontrolle (Daniel, 30–45 Minuten)

1. `/health/ready`, Alarmkanal und Backupstatus prüfen.
2. Runs `queued/running` älter als Schwellenwert, `failed/expired/recovery_required` prüfen.
3. geplante Scans und „Next Scheduled Scan“ je Monitoringtenant prüfen.
4. Credit Ledger, Admin-Audit und manuelle Freischaltungen abgleichen.
5. offene Invites, Supporttickets, Reportzugriffe und Kundenkommunikation prüfen.
6. Incident oder Abweichung mit Request ID, Tenant-ID, Run-ID und Zeit dokumentieren; keine Tokens kopieren.

### Wöchentliche Pilotkontrolle

- Restore-Stichprobe/Backup-Prüfsumme; Disk/Logrotation; Dependency-/Imagealerts;
- Tenant-/Membership-/Produkt-/Stripe-Reconciliation;
- Fehlertrend, Supportaufwand, Scanlaufzeiten, PDF-Fehler;
- Entscheidung, ob nächste Kundenwelle aufgenommen wird.

## Phase 6 – Pilot-Dry-Run

### Schritt 15 – DRY-01: vollständige Simulation

Der Dry-Run wird mit synthetischen Daten, nicht in PROD und ohne echte Zahlung/Mail an Kunden ausgeführt.

| # | Aktion | erwartetes Ergebnis / Evidence |
| ---: | --- | --- |
| 1 | Pilotkunde anlegen | Ticket/Pilot-ID/Tenant-Ziel eindeutig |
| 2 | Extension und Anleitung bereitstellen | RC-Artefakt-SHA stimmt |
| 3 | Extension installieren | Install PASS, Rollen korrekt |
| 4 | Registrierung abschließen | ein Tenant/User/Membership, Invite zugestellt |
| 5 | Produkt manuell zuweisen oder Testmode kaufen | Adminaudit/Purchase/Entitlement korrekt |
| 6 | erster Scan starten | queued mit Run-/Request-/Execution-Identität |
| 7 | Scan verarbeiten | running/heartbeat/completed, Pflichtresultat gespeichert |
| 8 | Findings prüfen | lokal/backend/dashboard konsistent, Drilldowns korrekt |
| 9 | Dashboard öffnen | Login/BC Embed, Tenant korrekt, keine Demo-Daten |
| 10 | HTML/PDF öffnen | Daten identisch, Layout/Footer/DE/EN korrekt |
| 11 | Statuskommunikation | Invite/Welcome/Result/Fehler via automatischem oder protokolliert manuellem Kanal |
| 12 | Monitoring einrichten | Entitlement, Frequenz, Next Run, Schedulerrolle |
| 13 | Background Scan abwarten | Historie + Backendrun + nächster Task |
| 14 | Fehler simulieren | Alarm, Recovery/terminaler Status, kein Doppelcredit |
| 15 | Support/Recovery testen | Diagnose/Antwort innerhalb Pilot-SLA |
| 16 | Upgrade installieren | Setup/Token/History/Rechte erhalten; neuer Scan erfolgreich |

- **Akzeptanzkriterien:** 16/16 PASS; Beweise im Evidencepaket; keine offene P0-Abweichung.
- **Automatische Tests:** vollständige Suite, PostgreSQL, Compile/Analyzer, Evidence-Validator.
- **Manuelle Tests:** Audit M01–M20 soweit pilotrelevant.
- **Codex-Anteil:** Evidenceprüfung/Fehleranalyse, Abschlussbericht.
- **Daniel-Anteil:** reale BC-/Provider-/Operationshandlungen und Signoff.
- **Aufwand:** C 1 d; D 1 d plus Wartefenster.
- **Exit:** signiertes Dry-Run-Protokoll.
- **Gate:** **NO-GO**, sobald ein Pflichtfeld leer, SKIP oder FAIL ist.

## Phase 7 – Pilot-Go-Live-Gates

### Schritt 16 – GO-01: Gate A vor erstem Pilotkunden

Alle Kästchen müssen erfüllt sein:

- [ ] RC-SHA und `.app`-SHA festgelegt; AL/CodeCop/PTECop grün.
- [ ] vollständige Backend-Suite PASS; PostgreSQL 7/7 PASS; Alembic U/D/U PASS.
- [ ] Install/Registration/Free/Assessment/Scan/Findings/Dashboard/HTML/PDF PASS.
- [ ] manueller und geplanter Monitoringlauf inkl. Historie PASS.
- [ ] Failure/Recovery/kein Doppelcredit PASS.
- [ ] Upgrade von repräsentativer Vorversion PASS.
- [ ] Backup/Restore und Rollback PASS; Alerts empfangen.
- [ ] Adminbereich gehärtet; Secrets/HTTPS/Headers geprüft.
- [ ] QuickStart, Support, DPA/Pilotvertrag, Known Limitations, Abnahmeprotokoll fertig.
- [ ] Betreiber und Stellvertreter, SLA, tägliche Kontrolle und Eskalation bestätigt.
- [ ] keine echten Kundenmails/Zahlungen im Dry-Run ausgelöst.

**Entscheidungsregel:** Nur `GO WITH CONDITIONS`, wenn ausschließlich dokumentierte P1/P2-Punkte offen sind und ihre manuelle Kompensation Owner, Frist und Beweis besitzt. Sonst `NO-GO`.

### Schritt 17 – WAVE-02: Gate B vor dem zehnten Pilotkunden

Zusätzlich zu Gate A:

- [ ] mindestens erster Kunde und zwei weitere Piloten ohne offene P0-Incidents stabil.
- [ ] 10-Tenant Last-/24h-Soak PASS; p95-/Ressourcengrenzen dokumentiert.
- [ ] Backups für Pilotdaten laufen; mindestens ein periodischer Restore erneut geprüft.
- [ ] alle Monitoringtenants täglich sichtbar; kein ungeklärter fehlender Historieneintrag.
- [ ] täglicher Operatoraufwand ≤45 min ohne Onboarding; Supportkapazität bestätigt.
- [ ] Logrotation/Disk/DB-Verbindungen/Alerts stabil.
- [ ] Produkt-/Credit-/Zugriffs-/Rechnungs-Reconciliation ohne Differenz.
- [ ] P1-Lokalisierungs-/Contentfehler auf dem tatsächlichen Pilotpfad geschlossen.
- [ ] Incidentkommunikation und Vertretung einmal geübt.

Aufnahme in Wellen: Kunde 1 → Review nach erstem vollständigem Monitoringlauf → Kunden 2–3 → Review → Kunden 4–5 → OPS-10A erneut bewerten → Kunden 6–10. Nach jedem P0-Incident wird die nächste Welle gestoppt, Ursache behoben und das betroffene Gate wiederholt.

## Was Codex direkt umsetzen kann – erst nach separater Freigabe

- Branch-/RC-Konsolidierung, CI-/Evidence-Gates und Builddiagnose;
- minimale AL-Fixes und Regressionstests;
- Login-Rate-Limit, Betriebschecks, Test-/Lastskripte und Alerting-Integration im Repository;
- Terminologie-/Preisdrift, Landing-/Report-/Localization-Fixes;
- konsolidierte Kunden-/Operator-Dokumentation und Abnahmevorlagen;
- Statusmail-Outbox/Events und Stripe-Sonderfälle in späteren Sprints.

## Was Daniel persönlich bzw. extern erledigen muss

- BC-Sandboxhandlungen und visuelle Evidence;
- GitHub-Merge-/Releasefreigabe;
- Hosting, DNS, TLS, Nginx, Backupziel, Monitoring-/Alarmkanal und Secretrotation;
- Stripe Test-/Live-Dashboard, Tax/Invoice/Refund-Konfiguration;
- SMTP-Provider und SPF/DKIM/DMARC;
- Preis-/Produkt-/Brand-Entscheidung;
- Rechts-, Datenschutz-, DPA-, Pilotvertrags- und Steuerfreigabe;
- Pilotkundenkommunikation, Rechnung, Supportbereitschaft und finale GO-Entscheidung.

## Finale Planentscheidung

Heute bleibt das Gate **NO-GO**. Der früheste seriöse Start für einen betreuten Einzelpiloten ist nach den Schritten 1–9, 11–12 und 15–16 realistisch in **3–5 fokussierten Arbeitstagen plus mindestens 24 Stunden Monitoring-/Soakzeit**, sofern die Umgebungen sofort verfügbar sind und kein neuer Defekt auftritt. Zehn Piloten erfordern zusätzlich OPS-10A und eine gestaffelte Aufnahme; realistisch **7–10 Arbeitstage** bis zum ersten Zehner-Gate, nicht zwingend bis alle zehn gleichzeitig gestartet sind.
