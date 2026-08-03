# BCSentinel Go-Live Feature Audit – 10 betreute Pilotkunden

**Auditdatum:** 2026-08-03  
**Entscheidung:** **NO-GO für den ersten externen Pilotkunden auf dem aktuell ausgecheckten Commit**  
**Zielbild:** schnellstmöglicher, kontrollierter Pilot mit maximal zehn aktiv betreuten Kunden; kein Self-Service- oder AppSource-Gate

## 1. Executive Summary

BCSentinel besitzt einen substanziellen, überwiegend automatisiert getesteten Produktkern. Zusätzlich liegt jetzt reale BC-Sandbox-Evidence vor: Extension `1.0.2.12` wurde installiert; `1.0.2.16` wurde nach mehreren Versuchen als Upgrade installiert. Setup, HTTPS zu `https://dev-api.bcsentinel.com`, Registrierung einschließlich Duplicate-Schutz, Tenant-/Company-/Membership-Zuordnung, Free Scan, Historie, Findings, Dashboard sowie HTML-/PDF-Report funktionierten. Auf `1.0.2.16` wurden außerdem Assessment, Validation Credit einschließlich Verbrauch, Zugriffslaufzeit, Monitoring-Freischaltung, manueller Monitoring-Scan, Data-Health-Ausnahmen und ein sauberer zweiseitiger A4-PDF-Render praktisch nachgewiesen.

Diese Nachweise gelten versionsgenau und attestieren **nicht automatisch den finalen Release Candidate**. Das Upgrade bleibt `IMPLEMENTED_NOT_E2E_VERIFIED`, weil Datenerhalt, Monitoring und Background Scan nach einem Upgrade auf den finalen RC noch nicht vollständig geprüft sind. Monitoring bleibt `PARTIAL`: In einem früheren Stand lief mindestens ein geplanter Scan erfolgreich; auf `1.0.2.16` trat später eine mögliche Regression ohne neuen Background-Scan beziehungsweise Historieneintrag auf. Der manuelle Monitoring-Scan lief, die Anzeige aktualisierte sich aber erst nach Refresh.

Weitere Pilotblocker sind: kein freigegebener, unveränderlicher finaler RC mit grünem AL-Build, eindeutigen AL-Objekt-IDs und grünem CodeCop/PTECop; kein aktueller PostgreSQL Upgrade/Downgrade/Upgrade- und Konkurrenznachweis; kein realer Recovery-, Backup-/Restore- oder Alerting-/Incident-Test; kein geschlossener Monitoring-Regressions- und 24-Stunden-Scheduler-Nachweis; sowie unvollständige Operator- und Pilotunterlagen. Für zehn Piloten fehlen zusätzlich 10-Tenant-Last-/Soak- und Betriebsevidence.

**Schnellster seriöser Weg:** finalen RC festlegen und bauen, danach nur einen kompakten Regressionstest der bereits bestandenen Grundfunktionen plus vollständige Upgrade-/Monitoring-/Recovery-Evidence ausführen. Parallel sind PostgreSQL-, Restore-, Alerting- und Operator-Gates zu schließen. Stripe Live, Refund und Chargeback sind für den ersten betreuten Pilot nicht P0; dokumentierte manuelle Pilotfreischaltung und Rechnungsstellung sind als Übergangslösung zulässig.

## 2. Geprüfter Branch, Commit und Release-Stand

| Gegenstand | Ergebnis | Bewertung |
| --- | --- | --- |
| Arbeitsbaum | vor Aktualisierung sauber; ausschließlich diese beiden Auditdokumente werden geändert | keine fremden Änderungen angetroffen |
| Aktueller Branch | `audit/release-1.0.2.16`, Tracking `origin/audit/release-1.0.2.16` | Auditbasis; nicht automatisch finaler RC |
| Aktueller Commit | `a5875cd1fd67572a092d0571f361bb3e874d4612`, 2026-08-03, `docs: add go-live audit and pilot action plan` | reiner Auditstand; RC-SHA weiterhin festzulegen |
| Tags | nur `pre-repo-01a-build-hygiene` | kein versionierter Release-Tag |
| Offene relevante PRs | #15, #17, #18, #19, #20 | mehrere übereinander aufbauende, noch nicht integrierte Releasezweige |
| Manuell getestete Extension-Versionen | Neuinstallation `1.0.2.12`; Upgradeziel `1.0.2.16` | reale Sandbox-Evidence, aber kein pauschaler Nachweis für den finalen RC |
| Finaler Release Candidate | noch nicht unveränderlich mit SHA, Artefakthash und Version attestiert | P0-Gate bleibt offen |
| CI-/Buildstatus finaler RC | in dieser Dokumentenaktualisierung nicht ausgeführt | **nicht verifiziert**; AL-/Objekt-ID-/CodeCop-/PTECop-Gate bleibt offen |
| PROD öffentlich | `/health` 200, `/health/ready` 200; OpenAPI 0.7.0 mit 102 Pfaden | erreichbar, Deploymentinhalt nicht commitgenau attestiert |
| DEV öffentlich | `/health` 200; OpenAPI 0.7.0 mit 120 Pfaden | sichtbare PROD/DEV-Drift |

**Empfohlene Pilotbasis:** ein explizit festgelegter, unveränderlicher finaler RC-SHA mit Extension-Version, Artefakthash und grünen Gates. Die reale `1.0.2.12`-/`1.0.2.16`-Evidence ist die Regression-Baseline, aber keine GO-Freigabe für diesen RC.

## 3. Auditumfang und Methode

Geprüft wurden alle getrackten Backend-, AL-, Landingpage-, Infrastruktur-, Workflow-, Migrations-, Test- und Dokumentationsdateien sowie lokale/Remote-Refs und offene PR-Metadaten. Frühere Statusdokumente dienten nur als Suchindex. Statusaussagen unten beruhen auf aktuellem Code, Migrationen, automatisierten Ergebnissen oder ausdrücklich benannten externen Gates.

Statusdefinitionen:

- `VERIFIED`: Code plus erfolgreicher relevanter Test.
- `IMPLEMENTED_NOT_E2E_VERIFIED`: implementiert, aber kein vollständiger realer End-to-End-Nachweis.
- `PARTIAL`: wesentliche Teile vorhanden, mindestens ein notwendiger Teil fehlt.
- `DOCUMENTED_ONLY`: nur Beschreibung/Plan/Runbook.
- `EXTERNAL_MANUAL_CHECK_REQUIRED`: außerhalb des Repositorys zu prüfen.
- `MISSING`: nicht vorhanden.
- `NOT_APPLICABLE`: für den betreuten Pilot nicht erforderlich.
- `BLOCKED`: Prüfung wegen fehlender Runtime/Umgebung nicht ausführbar.

Schätzungen verwenden `C` = Codex-Zeit und `D` = Daniel-Zeit. `h` = Stunden, `d` = Arbeitstage. Externe Wartezeiten sind nicht eingerechnet.

## 4. Architekturübersicht

```mermaid
flowchart LR
    BC["Business Central Extension\nAL / TaskScheduler / IsolatedStorage"] -->|"HTTPS + Tenant/API-Token"| API["FastAPI 0.7.0"]
    API --> DB["PostgreSQL + Alembic\n28 Migrationen"]
    API --> DASH["Dashboard / Analytics Embed"]
    API --> REP["Executive Report\nHTML + Chromium PDF"]
    API --> ADM["Adminportal\nHTTP Basic + CSRF"]
    API --> STRIPE["Stripe Checkout / Webhooks / Portal"]
    API --> SMTP["SMTP\nInvites/Partner"]
    WEB["statische Landingpage"] --> API
    CI["GitHub Actions"] --> API
    CI --> BC
```

Zentrale Verträge: `backend/app/core/product_model.py`, `backend/app/services/atomic_scan_start_service.py`, `backend/app/services/scan_status_service.py`, `backend/app/services/access_control_service.py`, `backend/app/routers/billing.py`, `backend/app/services/executive_report_service.py`, `bc-extension/app/src/codeunits/DHApiClient.Codeunit.al`, `DHDeepScanMgt.Codeunit.al`, `DHScanSchedulerMgt.Codeunit.al` und `DHAccessGuard.Codeunit.al`.

## 5. Vollständige Feature-Matrix

Die Bereichsangabe jedes Matrixeintrags ist die jeweilige Unterüberschrift A–J. Sie wird nicht in jeder Tabellenzeile wiederholt. Aufwand, Pilot-Relevanz, Risiko und empfohlene Maßnahme stehen je Eintrag in den entsprechend kombinierten Spalten.

### A. Business-Central-Extension

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Installation | PARTIAL | `DHInstall.Codeunit.al`, `app.json`; reale BC-Sandbox-Installation `1.0.2.12` PASS | AL-Vertragstests plus manueller `1.0.2.12`-Nachweis | frische Installation des finalen RC | Grundfunktion real belegt; RC-Kompatibilität offen | finalen RC kompakt installieren; C 30m, D 30m | P0 |
| Upgrade | IMPLEMENTED_NOT_E2E_VERIFIED | `DHUpgrade.Codeunit.al`, stabile App-ID; Upgrade auf `1.0.2.16` nach mehreren Versuchen PASS | Migrations-/AL-Contracts plus manueller `1.0.2.16`-Installationsnachweis | Datenerhalt, Monitoring und Background Scan nach Upgrade auf finalen RC | P0; Upgradeerfolg allein belegt keinen vollständigen Datenerhalt | fokussierte RC-Upgrade-Matrix; C 2h, D 2h | P0 |
| Uninstall/Reinstall | PARTIAL | keine Uninstall-Codeunit; Daten/IsolatedStorage-Verhalten nur Plattformstandard | keine | Uninstall mit/ohne Datenlöschung, Reinstall, Tokenzustand | P1; Support-/Datenschutzrisiko | Sandbox-Test und Anleitung; C 1h, D 1h | P1 |
| Manifest/Objektbestand | IMPLEMENTED_NOT_E2E_VERIFIED | Objektbestand und Validierungsskripte vorhanden | frühere Source-Uniqueness-Befunde/Fixes dokumentiert | Source-Uniqueness und Compile auf dem finalen RC grün | P0; finaler RC nicht attestiert | finalen RC-Guard ausführen; C 30m, D 15m | P0 |
| Setup-Seite/Guided Setup | VERIFIED | `DHSetup.Page.al`, `DHGuidedExperience.Codeunit.al`; reale Bedienung auf `1.0.2.12`/`1.0.2.16` PASS | automatisierte Contracts plus Sandbox-Nachweis | kompakte RC-Regressionsstichprobe | Grundfunktion belegt | im RC-Smoke wiederholen; C/D je 15m | P1 |
| Registrierung | VERIFIED | reale Registrierung auf `1.0.2.12`/`1.0.2.16` inklusive verhinderter Doppelregistrierung PASS | P0A-, Registration-, Multi-Tenant-Tests PASS | kompakte RC-Regressionsstichprobe und Responseverlustfall | P0-Grundfunktion real belegt | RC-Smoke + Retry-Negativfall; C/D je 30m | P0 |
| Tenant/Environment/Company-Zuordnung | VERIFIED | Tenant, Company und Membership im Backend auf `1.0.2.12`/`1.0.2.16` korrekt zugeordnet | P0A/Multi-Tenant PASS plus Sandbox-Nachweis | Mehrcompany-/Fremdtenant-Negativfall auf finalem RC | P0, hohe Isolation | RC-Isolationsstichprobe; C/D je 30m | P0 |
| sichere Token-Speicherung | IMPLEMENTED_NOT_E2E_VERIFIED | `DHSecretMgt`: `IsolatedStorage`, Scope Company; Backend speichert Hash | Token-/Registration-Tests PASS | BC-IsolatedStorage Upgrade/Reinstall/Permission | P0 | Sandbox-Negativtest; C 30m, D 45m | P0 |
| HTTPS-only API | VERIFIED | reale Verbindung von BC zu `https://dev-api.bcsentinel.com` auf `1.0.2.12`/`1.0.2.16` PASS | P0A Transporttests PASS plus Sandbox-Nachweis | Zertifikats-/Proxytest in endgültigem PROD | P0 | externes TLS-Gate; C 30m, D 30m | P0 |
| Permission Sets | IMPLEMENTED_NOT_E2E_VERIFIED | Viewer/Scan/Setup/Admin/Scheduler in `BCSentinelPermissionSets.al` | P0D Quellcontracts PASS | echte Positiv-/Negativtests je Rolle | P0/P1; über- oder unterprivilegierte Nutzer | Sandbox-Rollenmatrix; C 2h, D 2h | P0 |
| Deep Scan / manueller Scan | VERIFIED | `DHDeepScanMgt`, Runner, Dispatcher, Backend `/scan/start`/`sync` | Scan-, P0B/C-, Consolidation-Tests PASS | realer großer Tenant | P0 | Dry-Run; C 1h, D 1–2h | P0 |
| kostenloser Scan | VERIFIED | Free Scan auf `1.0.2.12`/`1.0.2.16` gestartet und abgeschlossen; neuer Historieneintrag vorhanden | GL01F Free, Product Licensing PASS plus Sandbox-Nachweis | kompakte RC-Regressionsstichprobe | P0-Grundfunktion real belegt | auf finalem RC einmal wiederholen; C/D je 30m | P0 |
| Assessment | VERIFIED | auf `1.0.2.16` erfolgreich freigeschaltet; Findings, Historie, Report und Zugriffslaufzeit praktisch angezeigt | Product Model/Licensing/Billing PASS plus Sandbox-Nachweis | kompakte RC-Regressionsstichprobe | vollständiger manueller Pilotpfad belegt | RC-Smoke; C/D je 30m | P1 |
| Validation Check | VERIFIED | Credit auf `1.0.2.16` zugewiesen und beim Validation Scan verbraucht; Findings, Historie und Report PASS | P0B, Licensing, Billing PASS plus Sandbox-Nachweis | Konkurrenz-/Retryfall auf PostgreSQL und finalem RC | Grundfunktion real belegt | fokussierte RC-/DB-Stichprobe | P1 |
| Monitoring-Entitlement | VERIFIED | Monitoring auf `1.0.2.16` erfolgreich freigeschaltet | Entitlement/Licensing PASS plus Sandbox-Nachweis | Ablauf und RC-Snapshot-Sync | P0 für Monitoring-Pilot | RC-Smoke; C/D je 30m | P0 |
| manueller Monitoring-Start | PARTIAL | manueller Scan auf `1.0.2.16` lief; Anzeige aktualisierte sich erst nach Refresh | Quellcontracts plus Sandbox-Nachweis | sofortige UI-/Historienaktualisierung auf finalem RC | P0; Refresh-Abhängigkeit und Regression offen | reproduzieren und RC-regressieren; C 2h, D 1h | P0 |
| geplanter Background Scan | IMPLEMENTED_NOT_E2E_VERIFIED | mindestens ein geplanter Lauf in früherem Stand PASS; auf `1.0.2.16` später kein neuer Background-Scan/Historieneintrag | GL01F Background Contracts PASS plus widersprüchliche Runtime-Evidence | Regression schließen; geplanter Lauf nach finalem Upgrade und 24h-Nachweis | P0 für Monitoring; frühere Evidence reicht nicht für RC | fokussierter 24h-RC-Lauf; C 2h, D 2h verteilt | P0 |
| Scan-Status/-Historie | VERIFIED | Free-, Validation- und manuelle Scans auf `1.0.2.16` in der Historie sichtbar; Monitoringanzeige teils erst nach Refresh | Scan Status, Fix05, History Contracts PASS | Refresh-/Background-Regressionsfall auf finalem RC | Grundfunktion real belegt, Monitoringteil offen | kompakte RC-Stichprobe | P0 |
| Findings / Drilldown / Open in BC | VERIFIED | Findings auf `1.0.2.12`/`1.0.2.16` angezeigt | P0D Direct-Page Guards, GL01C PASS plus Sandbox-Nachweis | Drilldown-Stichprobe auf finalem RC | Grundfunktion real belegt | RC-Smoke | P1 |
| Dashboard-Aufruf | VERIFIED | Dashboard auf `1.0.2.12`/`1.0.2.16` aus BC geöffnet | Analytics Security/P0D PASS plus Sandbox-Nachweis | kompakte RC-Regressionsstichprobe | P0-Grundfunktion real belegt | RC-Smoke | P1 |
| HTML-/PDF-Report-Aufruf | VERIFIED | HTML und PDF auf `1.0.2.12`/`1.0.2.16` aus dem Pilotpfad geöffnet | Report/P0D PASS plus Sandbox-Nachweis | kompakte RC-Regressionsstichprobe | P0-Grundfunktion real belegt | RC-Smoke | P1 |
| Produktzugriff/abgelaufener Zugriff | VERIFIED | Assessment-Zugriffslaufzeit auf `1.0.2.16` praktisch angezeigt | P0D/Entitlements PASS plus Sandbox-Nachweis | Ablauf nach finalem RC-Upgrade | P0 | fokussierter Upgrade-/Ablauftest | P0 |
| Scan Credits | VERIFIED | BC Snapshot + atomarer Backend-Ledger | P0B PASS | PostgreSQL Konkurrenz real lokal derzeit SKIP | P0 | PostgreSQL-Gate; C 1h, D 30m | P0 |
| Data-Health-Ausnahmen | VERIFIED | Ausnahmen auf `1.0.2.16` angelegt und erneuter Scan ausgelöst | GL01C/Exception Contract/Report PASS plus Sandbox-Nachweis | Ergebniswirkung über alle Entitätstypen auf finalem RC | P1 | RC-UAT-Stichprobe; C/D je 30m | P1 |
| DE/EN | PARTIAL | XLIFF 1519 Targets; direkte deutsche AL-Texte vorhanden | Target-Abdeckung; Localization-Script FAIL | BC Runtime DE/EN und globale Bereinigung | P1; sichtbare Sprachmischung | Pilotpfade bereinigen; C 1–2d, D 2h | P1 |
| Fehlermeldungen/Diagnose | PARTIAL | strukturierte Backendcodes, lokale Failure-Felder | Fix03/04/05, Observability PASS | Endnutzer-/Supportabnahme; Telemetrie fehlt | P0/P1 | Fehlerkatalog/Runbook; C 1d, D 2h | P1 |
| Idempotenz/Wiederholbarkeit | VERIFIED | Client Request ID, Run ID, Retry-Vertrag | P0A/B/C/Fix03/04 PASS | Netzwerkfehler real | P0 | Chaosfall im Dry-Run; C 1h, D 1h | P0 |
| Recovery abgebrochener Scans | IMPLEMENTED_NOT_E2E_VERIFIED | Lease/Heartbeat/periodische Recovery im Code vorhanden | P0C/Fix04/Fix05 PASS | echter BC-Sessionkill + Recovery auf finalem RC | P0; reale Recovery nicht belegt | Sandbox-Fehlerfall; C 1h, D 1h | P0 |
| Telemetrie | PARTIAL | Request IDs, Events, lokale Schedulerfelder | Observability PASS | zentraler Alert/Trace, BC-Telemetriesink | P1 bei 10 Kunden | zunächst täglicher manueller Check; C 1–2d, D 30m/Tag | P1 |
| AL Compile / CodeCop / PTECop | IMPLEMENTED_NOT_E2E_VERIFIED | Workflow und Buildskripte vorhanden | kein aktueller grüner finaler RC-Lauf belegt | finaler RC Compile + CodeCop-/PTECop-Logs | P0 | RC-Gate ausführen/belegen; C 1h, D 30m | P0 |
| AppSourceCop | PARTIAL | Konfiguration/Baseline vorhanden | nicht in aktuellem Lauf | bekannte Baseline + neue Warnungen | P3 Pilot, P0 AppSource | späteres Zertifizierungsgate; C 2–5d, D 1–2d | P3 |

### B. Backend und API

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| API-Struktur/Versionierung | PARTIAL | FastAPI 0.7.0; gemischte unversionierte und `/api`-Routen | OpenAPI erzeugbar, Routentests | formale v1-Kompatibilitätsstrategie | Pilot gering, Public mittel | bestehende Payloads einfrieren; C 0.5d, D 1h | P2 |
| Tenant-Authentifizierung | VERIFIED | Headerauth, Tokenhash, exakte Tenant-Prüfung | Registration, P0D, Reports PASS | Key-Rotation/Revoke E2E | P0 | manueller Token-Recoveryprozess; C 0.5d, D 1h | P1 |
| Dashboard-Authentifizierung | VERIFIED | PBKDF2-SHA256, JWT-Audience/Scope, HttpOnly/SameSite cookie | Multi-Tenant Dashboard PASS | Brute-force/Lockout, reale Sessionzeit | P0 | Login-Rate-Limit vor breitem Pilot; C 0.5d, D 30m | P1 |
| Tenant-/Company-Isolation | VERIFIED | DB-Abfragen/Tokenclaims gebunden | Multi-Tenant, P0E-Snapshot (lokal SKIP), Report PASS | echter PostgreSQL/Mehrcompany E2E | P0 | PostgreSQL + BC UAT; C 1h, D 1h | P0 |
| Rollen/Berechtigungen | PARTIAL | Dashboard Membership Role gespeichert; wenig serverseitige Rollendifferenzierung | Membershiptests | Owner/Viewer-Aktionsmatrix | P1 | Pilot nur definierte Userrolle; C 1d, D 1h | P1 |
| Registrierung | VERIFIED | idempotenter Upsert, Invite, Rate Limit | P0A/Registration PASS | Produktionsinvite/SMTP real | P0 | Stage-Test; C 30m, D 45m | P0 |
| Queue/Lifecycle | VERIFIED | Start, sync, status, events, reconcile | P0B/C/Fix04/05 PASS | echter BC Worker | P0 | Dry-Run; C 1h, D 1h | P0 |
| atomarer Credit-Verbrauch | VERIFIED | Transaktion, Unique Constraints, Ledger | P0B PASS | 7 PostgreSQL-Tests aktuell SKIP | P0 | CI/PostgreSQL-Gate belegen; C 1h, D 30m | P0 |
| Idempotenz | VERIFIED | Webhook-ID, Start Request, Scan-ID-Verträge | Billing/P0B/C PASS | Stripe CLI Wiederholung real | P0/P1 | Testmode-Replay; C 1h, D 1h | P1 |
| Heartbeat/Lease/Recovery | IMPLEMENTED_NOT_E2E_VERIFIED | `scan_status_service`, Startup + 60s Task | P0C/Fix04 PASS | realer Prozess-/BC-Sessionkill und Recovery | P0 | Chaos-Dry-Run; C 1h, D 1h | P0 |
| Deep-Scan-Verarbeitung | VERIFIED | `/scan/start`, `/scan/sync`, Scoring/Impact | Scan/Product Tests PASS | Last-/Volumentest | P0 | 10-Tenant synthetischer Test; C 1d, D 1h | P1 |
| Findings/Score/KPIs | VERIFIED | Scoring, impact, translation services | Scan, Pricing, Report PASS | fachliche Golden Dataset-Abnahme | P0 | 2–3 Golden Tenants; C 1d, D 1d | P1 |
| Produktmodell/Entitlements | VERIFIED | kanonischer Offer-/Entitlement-Vertrag plus Legacy-Aliase | ARCH-02A/B/C, Licensing PASS | reale Laufzeitmatrix | P0 | Dry-Run aller vier Produkte; C 1d, D 2h | P1 |
| Zugriffsablauf | VERIFIED | Access State/End Dates, frischer Recheck | P0D/Licensing PASS | laufende Sessions bei Ablauf | P0 | Stage-Test; C 1h, D 45m | P0 |
| Monitoring-Scheduler Backend | PARTIAL | Backend recovered Scan-Runs; eigentliche Zeitplanung liegt in BC | Lifecycle Tests | 10 aktive TaskScheduler, Zeit-/DST-Fälle | P0 für 10 | BC-Pilotmonitoring; C 1d, D 2h | P0 |
| Reports/Share Links | VERIFIED | JSON/HTML/PDF; Typ/Scan/Tenant/TTL-Bindung | 12 Reporttests PASS | URL-Leak/Proxylog in PROD | P0 | TTL/Logging manuell prüfen; C 1h, D 30m | P1 |
| Rate Limits | PARTIAL | Registrierung und Partnerauth limitiert | Registration/Partnertests | Dashboardlogin, Billing, Scan, Reports | P1; DoS/Bruteforce | Reverse-Proxy + app limits; C 1d, D 1h | P1 |
| Inputvalidierung | VERIFIED | Pydantic, stabile Registrationcodes, Produktvalidierung | breite API-Suite PASS | Fuzz/Max-Payload | P1 | Limits testen; C 0.5d, D 30m | P2 |
| Fehlerbehandlung/Logging | VERIFIED | strukturierte Handler, Request ID, Redaction | Observability PASS | zentraler Logsink/Alarm | P0/P1 | Betriebsintegration; C 1d, D 1h | P1 |
| Admin-Auditlog | VERIFIED | `admin_audit_events`, alle Kernmutationen loggen | Admin/Pricing/Landing PASS | Unveränderbarkeit/Exportvollständigkeit | P1 | tägliche Review; C 0.5d, D 30m | P1 |
| Health/Readiness | VERIFIED | `/health`, `/health/ready` mit DB-Check | Deployment/Billing PASS; PROD 200 | Alarm auf Readiness | P0 | externen Monitor konfigurieren; C 1h, D 1h | P0 |
| DB-Transaktionen | VERIFIED | Start/Webhook/Registration rollback und Constraints | P0A/B/C/Billing PASS | PostgreSQL E2E | P0 | PostgreSQL-Gate | P0 |
| Alembic-Migrationen | IMPLEMENTED_NOT_E2E_VERIFIED | 28 lineare Migrationen, Head `0028_exception_count` | Membership-/Deploymentmigration PASS | PostgreSQL Upgrade/Downgrade/Upgrade | P0 | isolierte Test-DB; C 2h, D 1h | P0 |
| Backup/Restore | DOCUMENTED_ONLY | `docs/ops/backup-restore.md`; keine Automation im Code/Workflow | keine | echter verschlüsselter Backup+Restore+RTO | P0 | Restore-Dry-Run; C 2h, D 2–3h | P0 |
| Datenschutz/Löschung | PARTIAL | Admin-Tenant-Delete, Scan-Delete; Privacy-Dokumente | Admin Delete PASS | Retention-Automation, Export, rechtliche Freigabe | P1/P0 vor echten Daten | manuelle Pilot-Retention + DPA; C 1d, D 1d | P1 |
| 10 parallele Kunden | BLOCKED | Architektur/Tests vorhanden | SQLite-Suite PASS, PostgreSQL-Konkurrenz SKIP | Lasttest mit PostgreSQL/10 Tenants | P0 für zehnten Kunden | Stage-Lasttest; C 1d, D 1h | P0 |

### C. Dashboard und Kundenportal

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Login/Logout/Sessionablauf | VERIFIED | `/dashboard/login`, logout, 60-min JWT cookie | Multi-Tenant Dashboard PASS | Browser-E2E/Idle UX | P0 | Pilotbrowser testen; C 1h, D 1h | P0 |
| Passwort-/Session-Sicherheit | PARTIAL | PBKDF2 210k, HttpOnly/Secure(prod)/Strict, Audience | Tests PASS | Login-Rate-Limit, Lockout, Rotation | P1 | Limit/Runbook; C 0.5d, D 30m | P1 |
| Passwort-Reset | MISSING | nur Invite-Aktivierung; Partner-Reset ist separates System | keine | vollständiger Dashboard-Reset | betreuter Pilot manuell ersetzbar | Admin-Reinvite-Prozess; C 0.5d, D 15m je Fall | P2 |
| Benutzer/Memberships/Rollen | VERIFIED | DashboardUser + Membership, Tenant Switch | Multi-Tenant PASS | Rollen-UX/Verwaltung durch Kunde | P0 | Pilot admin-geführt; C 1h, D 1h | P1 |
| Multi-Tenant-Trennung | VERIFIED | serverseitiger Membership-Recheck/Tokenrotation | Manipulationstests PASS | realer Mehrtenant-Browser | P0 | UAT; C 45m, D 45m | P0 |
| Onboarding/Empty State | PARTIAL | Inviteportal und Fallback/Demo-Guard | Analytics Security PASS | kompletter First-Run ohne Scan | P0 UX | Dry-Run; C 0.5d, D 1h | P1 |
| Health Score/KPIs/Findings | VERIFIED | Analytics Payload/Template/JS | Analytics, Licensing, Localization PASS | echte große Daten | P0 | UAT; C 1h, D 1h | P0 |
| Filter/Sortierung/Trends | PARTIAL | Dashboard JS und Trendpayload | API-/Contracttests | Browser-E2E aller Filter | P1 | Pilot-UAT; C 0.5d, D 1h | P1 |
| Scan-Historie | IMPLEMENTED_NOT_E2E_VERIFIED | API/BC Historie; Dashboard konzentriert auf aktuellen Kontext | History/Status PASS | Browser Journey | P1 | Journey testen; C 1h, D 1h | P1 |
| produktabhängige Sichtbarkeit/Ablauf | VERIFIED | Capability Claims + Backend-Recheck | P0D/Licensing PASS | offenes Browserfenster bei Ablauf | P0 | Stage-UAT; C 1h, D 45m | P0 |
| Report-Downloads | VERIFIED | Reportlinks/API | Reporttests PASS | Browserdownload | P0 | UAT; C 30m, D 30m | P0 |
| Fehlerzustände | PARTIAL | strukturierte API-Fehler, Fallback UI | Contracts | Netzwerk-/5xx-/expired Browser-E2E | P1 | UAT; C 0.5d, D 1h | P1 |
| Responsive | IMPLEMENTED_NOT_E2E_VERIFIED | Dashboard responsive Contract; lokale Landing bei 390 px teils clipping | Dashboard responsive Test | Portal auf realen Geräten | P1 | 390/768/1440 Abnahme; C 2h, D 1h | P1 |
| DE/EN | PARTIAL | JSON Übersetzungen; Legacy-/Premium-Schlüssel bleiben | Localization/ARCH tests PASS | redaktionelle Browserabnahme | P1 | Pilotpfade lektorieren; C 1d, D 2h | P1 |
| Barrierefreiheit | MISSING | keine Axe/WCAG-Suite, nur semantische Teilstruktur | keine | Keyboard/Screenreader/Contrast | P2 im betreuten Pilot | Basischeck; C 1d, D 2h | P2 |
| Support/Kontakt | PARTIAL | statische Supportseiten/Mailadresse | Linkcheck | bestätigter Kanal/SLA | P0 organisatorisch | Pilot-Supportkanal festlegen; C 1h, D 2h | P0 |
| Demo-/Platzhalterdaten | PARTIAL | Demo nur Dev-Flag fail-closed; Landing enthält sichtbare Mockup-/Placeholdertexte | Demo-mode Tests PASS | öffentlicher Content Sweep | Reputationsrisiko | Pilotlink kuratieren; C 1d, D 2h | P1 |

### D. Admin-Backend/Adminportal

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Admin-Login | PARTIAL | HTTP Basic, constant-time compare, TLS-Proxy | Adminauth Tests | MFA, Rate Limit, IP-Allowlist | P0 bei kritischen Mutationen | Pilot: VPN/IP-Allowlist + starkes Secret; C 2h, D 1h | P0 |
| CSRF | VERIFIED | Middleware für `/admin/*` POST | negativer CSRF-Test PASS | Proxy/browser UAT | P0 | UAT; C 30m, D 30m | P0 |
| Tenant-/Kundenübersicht | VERIFIED | Admin Templates/Routes | Admin PASS | 10-Tenant UX | P0 Support | Seed/UAT; C 1h, D 1h | P1 |
| Benutzerverwaltung | PARTIAL | Membership/Invite indirekt; keine vollständige Dashboard-User-UI | Tests auf Invite/Membership | Admin CRUD/Disable UX | Pilot manuell/DB-frei eingeschränkt | Reinvite/disable Runbook; C 0.5d, D 1h | P1 |
| Produktzuweisung/Credits | VERIFIED | Grant/Revoke/Add/Remove/Reset | Admin PASS | echter Pilotflow | P0 als Stripe-Ersatz | UAT; C 45m, D 45m | P0 |
| Monitoring/Ablauf/Lizenzreset | VERIFIED | Enable/Disable/Extend/Reset | Admin PASS | BC Snapshot-Sync real | P0/P1 | Dry-Run; C 1h, D 1h | P0 |
| Invite/Registrierung | PARTIAL | Re-registration Reset dev-only; Invite send/resend | Registration/Admin Tests | PROD-Recovery ohne direkte DB | P0 Support | dokumentierter sicherer Recoverypfad; C 0.5d, D 1h | P0 |
| Scan-/Fehlerdiagnose | PARTIAL | Runs/Status im Tenant Detail, Request IDs | Status/Admin Tests | zentrale Suche/Alerting/Export | P0 Betrieb | tägliche Query/Checkliste; C 0.5d, D 30m/Tag | P0 |
| Payment/Stripe-Zuordnung | PARTIAL | Subscription/Invoice/Purchase-Daten sichtbar | Billing Tests | Testmode/Live UAT, Reconciliation UI | Pilot manuell möglich | manuelles Kontrollblatt; C 0.5d, D 1h | P1 |
| manuelle Korrekturen | VERIFIED | Produkt, Credits, Monitoring, Access, Reset | Admin Tests | Vier-Augen-/Freigabeprozess | hohes Missbrauchsrisiko | Pilot-Auditreview; C 1h, D 30m/Woche | P1 |
| Auditierbarkeit | VERIFIED | AdminAuditEvent bei Kernmutationen | Admin/Pricing PASS | unveränderbarer externer Logexport | P1 | wöchentlicher Export/Review; C 0.5d, D 30m | P1 |
| Schutz kritischer Aktionen | PARTIAL | CSRF/Basic/Bestätigungsmeldungen | Admin Tests | MFA, Step-up, IP-Allowlist aktiv | P0 Security | Proxy-Allowlist/VPN; C 2h, D 1h | P0 |
| Export/Supportinformationen | PARTIAL | Partner CSVs, kein vollständiges Tenant-Supportbundle | Tests partiell | Tenantdiagnoseexport | P2 | später; C 1d, D 1h | P2 |

### E. Executive Reports

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Free/Assessment/Validation/Monitoring Report | PARTIAL | Free-, Assessment- und Validation-Report auf `1.0.2.12`/`1.0.2.16` praktisch geöffnet; Monitoring-RC-Pfad offen | Report/Licensing PASS plus Sandbox-Nachweis | Monitoringvariante nach geschlossener Regression auf finalem RC | bezahlte Grundpfade belegt | kompakte RC-Variantenstichprobe; C/D je 45m | P1 |
| HTML | VERIFIED | HTML-Report auf `1.0.2.12`/`1.0.2.16` praktisch geöffnet | Reporttests PASS plus Sandbox-Nachweis | kompakte finale RC-Stichprobe | P0-Grundfunktion belegt | RC-Smoke | P1 |
| PDF | VERIFIED | PDF auf `1.0.2.12`/`1.0.2.16` praktisch geöffnet | Reporttests plus Sandbox-Nachweis | kompakte finale RC-Stichprobe | P0-Grundfunktion belegt | RC-Smoke | P1 |
| Dashboard-/HTML-/PDF-Datenkonsistenz | VERIFIED | gemeinsamer Reportbuilder/Scanmodell; Pilotpfade auf `1.0.2.16` sichtbar | JSON/HTML/PDF Test PASS plus Sandbox-Stichprobe | finaler RC-Screenshotvergleich | P0-Grundfunktion belegt | RC-Smoke | P1 |
| Score/KPI/Severity/finanzieller Impact | VERIFIED | Builder/Template, Score/Impact Services | Report/Scoring Tests PASS | fachliche Golden Results | P0 | Daniel fachliche Freigabe; C 1d, D 1d | P0 |
| Findings/Empfehlungen | IMPLEMENTED_NOT_E2E_VERIFIED | ReportFinding/Priority Items, Free-Redaktion | Tests | große/Sonderzeichen-Daten | P1 | Edge-Dataset; C 0.5d, D 1h | P1 |
| Branding/Layout/Druck | VERIFIED | sauberer zweiseitiger A4-PDF-Render auf dem mit `1.0.2.16` getesteten Pilotpfad | Chromium-Render visuell ohne Überlauf geprüft | finaler RC-Containerrender mit großen Zahlen | Grundlayout real belegt | finalen RC rendern; C 1h, D 30m | P1 |
| große Zahlen/Sonderzeichen | IMPLEMENTED_NOT_E2E_VERIFIED | `money-long`, UTF-8, Edge-Case Test | String-/CSS-Test PASS | echter Chromium-Render der >1 Mio.-Variante | P1 | Render/Screenshot; C 1h, D 30m | P1 |
| DE/EN | VERIFIED | Builder Labels/Template | German/English tests PASS | redaktionelle UAT | P1 | beide PDFs sign-off; C 1h, D 1h | P1 |
| sichere Links/TTL/Tenant-Schutz | VERIFIED | typ-/scan-/tenantgebundene Tokens + Recheck | Share/Expiry/Isolation PASS | Proxylogs/Referrer real | P0 | PROD-Logging prüfen; C 1h, D 30m | P0 |
| Erzeugung aus BC | VERIFIED | HTML/PDF auf `1.0.2.12`/`1.0.2.16` aus BC aufgerufen | Access Contracts plus Sandbox-Nachweis | kompakte finale RC-Stichprobe | P0-Grundfunktion belegt | RC-Smoke; C/D je 15m | P1 |
| E-Mail-Versand Report | MISSING | kein Reportmail-Event | keine | SMTP/PDF-Link-Flow | im betreuten Pilot manuell ersetzbar | Support sendet Link manuell; D 5m/Report | P2 |
| Terminologie | PARTIAL | getrackter PDF-Render und Fallback enthalten „Vollständige Analyse“, „Premium“, „Full Analysis“ | ARCH-Test deckt nur Teile | kompletter Output-Sweep | P1/Reputation | auf Assessment angleichen; C 0.5d, D 1h | P1 |

### F. Landingpage

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Start/Leistung/CTA | PARTIAL | `landingpage` und `landingpage_neu` parallel; Nginx zeigt `landingpage` | lokaler Link-/Browsercheck | kanonische deployte Quelle | P1 | eine Pilot-Landingquelle festlegen | P1 |
| Produktmodell/Preise | PARTIAL | 79/49/149/1490 sichtbar, aber „Full Analysis/Premium“ und Tierpreise im Backend | Pricing/ARCH Tests | End-to-End-Konsistenz mit Stripe/DB | P1 Pilot, P0 Self-Service | Copy/Preisvertrag schließen; C 1d, D 2h | P1 |
| Kauf/Registrierung | PARTIAL | CTAs, Checkout aus BC/Analytics; statische Seite führt teils Kontakt | Billing Tests | Browser→Kauf→Aktivierung | betreuter Pilot manuell möglich | Pilot-CTA auf Kontakt/Einladung | P2 |
| Dashboard-Login/Dokumentation/Kontakt | VERIFIED | lokale Seiten und Links vorhanden | lokaler Linkcheck: 0 fehlende Links/Assets | öffentlicher UAT | P1 | Smoke; C 1h, D 1h | P1 |
| Impressum/Datenschutz/Terms | PARTIAL | Seiten vorhanden; Datenschutz enthält `[Telefonnummer]`, vorläufige Rechtsformulierungen | Linkcheck | juristische Freigabe | P0 vor öffentlicher Akquise/zahlendem Self-Service | Daniel/Rechtsberatung; D 1–3d | P1 |
| Widerruf/B2B/Vertragsbedingungen | PARTIAL | Terms/EULA vorläufig | keine | Rechtsprüfung | regulär zahlender Kunde P0 | B2B-Vertrag/Pilotvereinbarung | P1 |
| Cookie/Tracking | PARTIAL | kein offensichtliches Tracking-SDK im Pilotpfad; externe Fonts/Forms in Content erwähnt | Quellscan | deployed Header/Requests/Consent | extern | Network-/Legal-Check; C 1h, D 2h | P1 |
| DE/EN | PARTIAL | Umschalter/JSON | i18n-Contract; Browser DE | redaktionelle Vollprüfung | P1 | Copy-Sweep | P1 |
| SEO | PARTIAL | Titel/Metadaten in statischen Seiten | keine Lighthouse-Suite | Canonical/OpenGraph/Sitemap/robots deployt | P3 Pilot | später; C 1d | P3 |
| Mobile | PARTIAL | global kein Horizontal-Scroll bei 390 px; interne Clipping-Befunde in Impact/Pricing | lokaler Browseraudit | Geräte-/Touchabnahme | P1 | CSS Pilotpfad korrigieren; C 0.5d, D 30m | P1 |
| Performance | BLOCKED | statische Assets klein; keine Lighthouse-/RUM-Evidenz | keine | öffentliches Lighthouse | P2 | später/Stage; C 2h | P2 |
| fehlerhafte Links | VERIFIED | beide Landing-Verzeichnisse: 0 fehlende lokale href/src-Ziele | lokaler statischer Check | externe Zielverfügbarkeit | P1 | externes Smoke; C 30m, D 30m | P1 |
| Platzhalter/Claims | PARTIAL | sichtbare `EUR-`, Mockup-Hinweise, `[Telefonnummer]`; `landingpage_neu` behauptet Verfügbarkeiten 99.98/99.99 % | Browser/Quellscan | Legal/Marketing-Signoff | Reputations-/Irreführungsrisiko | aus Pilotpfad entfernen; C 0.5–1d, D 2h | P1 |
| Deploymentkonsistenz | PARTIAL | PROD/DEV 200, aber unterschiedliche HTML/Path-Umfänge; Docker kopiert `landingpage`, Service referenziert auch `landingpage_neu` | öffentliche Health/OpenAPI-Checks | commitgenaue Deploy-Metadaten | P0 Betrieb | Release SHA exponieren/attestieren; C 0.5d, D 1h | P0 |

### G. Stripe und kommerzieller Prozess

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Test-/Live-Mode | EXTERNAL_MANUAL_CHECK_REQUIRED | Secret-/Price-ID-Settings vorhanden | Mocktests | Stripe Dashboard Test+Live-Konfiguration | Pilot manuell ersetzbar | Daniel prüft Konten/Keys getrennt | P1 |
| Produkte/Prices | PARTIAL | vier Produkte/Price IDs; DB-Tiermatrix weicht vom erwarteten Fixpreisbild ab | Pricing/Billing PASS | Stripe-Objekte und Beträge | Preis-/Vertragsrisiko | kanonischen Preisvertrag sign-off; C 1d, D 2h | P1 |
| Checkout/Success/Cancel | VERIFIED | sichere URLs, Payment vs Subscription | Billing PASS | Stripe Testmode Browser-E2E | Self-Service P0, Pilot P2 | Testmode-Dry-Run; C 2h, D 1h | P2 |
| Webhook-Signatur | VERIFIED | `stripe.Webhook.construct_event`, in PROD Pflicht | valid/invalid Tests PASS | Stripe CLI/Testmode | P1 | Replay-Test | P1 |
| Webhook-Idempotenz/Mehrfachzustellung | VERIFIED | unique event record/processed flag | Billing PASS | verzögerte Reihenfolge Testmode | P1 | Stripe CLI Matrix | P1 |
| Purchase/Credit/Productaktivierung | VERIFIED | Purchase/Entitlement/Credit Services | Billing/Product Licensing PASS | realer Kauf→BC Snapshot | Pilot manuell alternativ | Testmode oder Admin-Grant | P1 |
| Verlängerung/Kündigung/Zahlungsfehler | IMPLEMENTED_NOT_E2E_VERIFIED | Subscription + invoice events, Portal | Billing-Unitfälle teilweise | Testclock/Dunning/Grace-Period E2E | zahlender Kunde P0 | Stripe Test Clock; C 1d, D 2h | P1 |
| Refund/Chargeback/Dispute | MISSING | keine `charge.refunded`/`refund`/`dispute` Handler | keine | gesamter Prozess | zahlender Kunde P0, Pilot manuell | Runbook + später Handler; C 1–2d, D 2h | P2 |
| Statussynchronisierung/Recovery | PARTIAL | Session Status Sync, Webhooklog, Adminsicht | Billing PASS | periodische Reconciliation/Retry UI | P1 | tägliche manuelle Reconciliation | P1 |
| Stripe Customer↔Tenant | IMPLEMENTED_NOT_E2E_VERIFIED | Metadata/Subscription lookup | Billing PASS | echte Kunden-/Mergefälle | P1 | Testmode | P1 |
| Rechnungen/Steuer/USt | EXTERNAL_MANUAL_CHECK_REQUIRED | Invoice-Datenspeicher; keine Tax-Logik | Mocktests | Stripe Tax, Rechnungsangaben, USt-ID | zahlender Kunde P0 | Steuerberater/Stripe-Konfiguration | P1 |
| Logging ohne Zahlungsdaten | PARTIAL | strukturierte Events; Roh-Webhook-Payload wird gespeichert | Redaction allgemein | Datenschutz-/Retentionreview des Payloads | P1 Datenschutz | Payload minimieren/Retention festlegen | P1 |
| Kauf-bis-Nutzung E2E | BLOCKED | Komponenten vorhanden | Mocktests | Stripe Testmode + BC Runtime | nicht P0 bei manueller Freischaltung | vor Self-Service schließen | P2 |

**Reifegradtrennung Stripe:** Code vorhanden und mockgetestet; Stripe-Testumgebung, Live-Vorbereitung und Produktion sind im Audit nicht verifiziert. Für den betreuten Pilot wird Stripe durch dokumentierte Admin-Freischaltung und manuelle Rechnung ersetzt.

### H. E-Mail-Versand

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Einladung/Dashboardzugang | IMPLEMENTED_NOT_E2E_VERIFIED | SMTP, DE/EN Templates, resend | Registration/Invite Tests | echter Provider/Inbox/Retry | P0, manuell ersetzbar | SMTP-Test oder Link sicher über Pilotkanal | P0 |
| Registrierung/Welcome | MISSING | keine separaten Events | keine | Mailflow | manuell | Pilot-Welcome-Vorlage; C 1h, D 5m/Kunde | P1 |
| Kaufbestätigung/Aktivierung | MISSING | Stripe aktiviert DB, keine Mail | keine | Mailflow | manuell | Supportvorlage; C 1h, D 5m/Kauf | P1 |
| Scan gestartet/abgeschlossen/fehlgeschlagen | MISSING | keine Mailaufrufe in Scanpfaden | keine | Mailflow | fehlgeschlagen ist P0-Kommunikation, automatisiert nicht P0 | täglicher Monitor + manuelle Mail | P1 |
| Report verfügbar | MISSING | kein Versand | keine | Mailflow | manuell | Link aus Supportkanal | P2 |
| Monitoring-Ergebnis/Adminwarnung | MISSING | keine Notification Pipeline | keine | Mailflow | P0 Betrieb bei 10 Kunden | zentrale tägliche Kontrolle, Fehlalarm manuell | P0 |
| Zahlungsfehler/Kündigung/Ablauf | MISSING | keine Billingmails | keine | Mailflow | zahlender Self-Service P0 | vor Self-Service implementieren | P2 |
| Provider/SPF/DKIM/DMARC | EXTERNAL_MANUAL_CHECK_REQUIRED | generisches SMTP konfigurierbar | keine | DNS/Providerzustellung | Einladung P0 | Daniel DNS/Inbox-Test | P0 |
| Templates/Branding/DE/EN | PARTIAL | Invite/Partner/Admin-Testtemplates | Template Tests indirekt | alle Transaktionsarten | P1 | Pilotvorlagen finalisieren | P1 |
| Retry/Bounce/Dedupe/Logging/Opt-out | MISSING | synchrones SMTP, kein Queue-/Bounce-System | keine | Zustellbetrieb | Pilot manuell tragbar, Public P0 | Supportlog; später Provider-Webhooks | P2 |

**Für den Pilot unverzichtbar:** sichere Zugangseinladung, Scanfehler-/Monitoring-Fehler-Warnung an den Betreiber und klare Onboarding-/Supportkommunikation. Diese dürfen für zehn betreute Kunden zunächst manuell erfolgen, müssen aber mit Checkliste, Verantwortlichem und täglicher Kontrolle belegt sein.

### I. Dokumentation und Pilot-Onboarding

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Installation/Upgrade | PARTIAL | `BC_EXTENSION_RELEASE_PACKAGE.md`, `BC_EXTENSION_RELEASE_CHECKLIST.md`, `BC_EXTENSION_UPGRADE_TEST_REPORT.md`, CAT und Runbooks | reale Nutzerprobe für `1.0.2.12`→`1.0.2.16` | finaler RC, Datenerhalt und aktuelle Screenshots | P0 | versionsgenau konsolidieren | P0 |
| QuickStart/Free Scan | PARTIAL | `PILOT_E2E_01A_MANUAL_RUNBOOK_DE.md`, `PILOT_GO_LIVE_RUNBOOK.md`, CAT und Go-Live-Checkliste enthalten die Schritte | manueller Free-Pfad auf `1.0.2.12`/`1.0.2.16` PASS | kompakter kundenlesbarer RC-QuickStart/Nutzerprobe | P0 | vorhandene Inhalte konsolidieren; C 0.5d, D 1h | P0 |
| Registrierung | IMPLEMENTED_NOT_E2E_VERIFIED | CAT und deutsche Pilot-Runbooks; realer Ablauf auf `1.0.2.12`/`1.0.2.16` PASS | Contracttests plus Sandbox-Nachweis | finaler RC-Screenshot und Fehler-/Recoverypfad | P0 | QuickStart aktualisieren | P0 |
| Assessment kaufen/verwenden | DOCUMENTED_ONLY | Billing-/Produktmatrix, CAT und Pilot-Runbooks beschreiben Adminfreischaltung; `1.0.2.16` praktisch freigeschaltet | manuelle Produktsicht belegt | kundenfertiger Ablauf einschließlich manueller Rechnung | zulässige Pilotübergangslösung | bestehende Inhalte konsolidieren | P1 |
| Validation Check | IMPLEMENTED_NOT_E2E_VERIFIED | CAT/Billingmatrix; Creditverbrauch auf `1.0.2.16` praktisch belegt | automatisierte Tests plus Sandbox-Nachweis | kundenfertige RC-Kurzschritte | P1 | Kurzguide aktualisieren | P1 |
| Monitoring/TaskScheduler | PARTIAL | CAT, `GL_EXT_P0E_SANDBOX_RELEASE_GATE.md` und Pilot-Runbooks | früher geplanter Lauf PASS; `1.0.2.16` mit späterer Regression | finaler RC-Screenshot, Regression und 24h-Lauf | P0 | Guide nach Regression finalisieren | P0 |
| Dashboard/Findings/Reports | IMPLEMENTED_NOT_E2E_VERIFIED | CAT, Pilot-Runbooks und Exceptions Guide; auf `1.0.2.12`/`1.0.2.16` praktisch belegt | Linkchecks plus Sandbox-Nachweis | finaler RC-Screenshotsatz/Nutzerprobe | P1 | vorhandenes QuickStart-Kapitel aktualisieren | P1 |
| Data-Health-Ausnahmen | VERIFIED | `DH_EXCEPTIONS_USER_ADMIN_GUIDE.md` | GL01C Tests | Nutzerprobe | P1 | UAT | P1 |
| Benutzer/Berechtigungen | PARTIAL | Rollenmatrix | Source Contracts | Sandboxrolle | P0 | Pilot-Rollenblatt | P0 |
| Deinstallation | PARTIAL | CAT erwähnt Verhalten | keine | echte Durchführung | P1 | Runbook | P1 |
| Troubleshooting/FAQ | PARTIAL | mehrere technische Audits, kein kompakter Pilot-Troubleshooter | keine | Supportprobe | P0 | Top-10 Fehler + Request ID | P0 |
| Datenschutz/Datenverarbeitung | PARTIAL | Processing/Retention/DPA-Checkliste | keine | Rechts-/Kundenfreigabe | P0 vor echten Daten | Daniel finalisiert DPA | P0 |
| Supportprozess | PARTIAL | Pilot Runbook | keine Übung | Kontakt, SLA, Eskalation | P0 | verbindlich festlegen | P0 |
| Pilot-Onboarding-Checkliste | PARTIAL | Pilot-/Go-Live-Runbooks | keine | vollständiger Dry-Run | P0 | konsolidieren | P0 |
| Pilot-Abnahmeprotokoll | DOCUMENTED_ONLY | `BC_EXTENSION_CUSTOMER_ACCEPTANCE_TEST.md`, `MANUAL_GO_LIVE_CHECKLIST.md` und `GL_PILOT_01_SANDBOX_VALIDATION.md` vorhanden | Struktur vorhanden | konsolidiertes signierbares RC-Protokoll | P0 | vorhandene Vorlagen konsolidieren | P0 |
| Admin-Betriebshandbuch | PARTIAL | `docs/ops/pilot-runbook.md`, `PILOT_GO_LIVE_RUNBOOK.md` und technische Operationsdokumente vorhanden | keine Operatorprobe | konsolidierter 10-Kunden-Betrieb und Vertretung | P0 | vorhandene Inhalte konsolidieren | P0 |
| Backup/Restore | DOCUMENTED_ONLY | `docs/ops/backup-restore.md` | keine | echter Restore | P0 | testen und Werte eintragen | P0 |
| Incident/Release/Rollback | PARTIAL | Deployment/Release/Pilot-Runbooks | keine Übung | Drill und letzte Version | P0 | Dry-Run | P0 |
| bekannte Einschränkungen | DOCUMENTED_ONLY | Einschränkungen in Audit-, Release- und Pilotdokumenten verteilt vorhanden | keine | kompakte kundenlesbare RC-Fassung und Signoff | P0 Transparenz | vorhandene Inhalte konsolidieren | P0 |

### J. Betrieb, Sicherheit und Support

| Feature | Status | Evidenz | Vorhandene Tests | Fehlender Test | Pilot-Relevanz / Risiko | Maßnahme / Aufwand | Prio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DEV/STAGING/PROD | PARTIAL | DEV/PROD Compose; kein klar separates Staging-Deployment | öffentliche DEV/PROD Health 200 | commitgenaue Umgebungsinventur | P0 | RC→Stage→Prod-Prozess | P0 |
| Secret Management | PARTIAL | Env-Settings/GitHub Secrets; `.env.dev` ignoriert | keine Secrets getrackt nach Dateinamen | Serverrechte/Rotation/Vault | P0 | Daniel prüft Rechte/Rotation | P0 |
| HTTPS/Sicherheitsheader | VERIFIED | Nginx TLS, App CSP/HSTS/XFO | Header/Transporttests PASS | öffentliches TLS/Header-Scan | P0 | extern prüfen | P0 |
| Backups/Restore | DOCUMENTED_ONLY | Runbook, Volume | keine | Restoretest/RPO/RTO | P0 | vor Kunde | P0 |
| Monitoring/Alerting/Errortracking | MISSING | Health und Logs, aber kein externer Monitor/Sentry/Prometheus/Alarmworkflow | Healthtests | Alarmzustellung | P0 | Uptime+Readiness+Logalarm | P0 |
| Logrotation/Speicherplatz | MISSING | kein Compose-/Host-Nachweis | keine | Hostprüfung | P1 bei 10 | Docker/Host Limits dokumentieren | P1 |
| Container-Restart | IMPLEMENTED_NOT_E2E_VERIFIED | `restart: unless-stopped`, healthcheck | Compose config dev/P0E PASS | Kill-/Reboot-Test | P0/P1 | Stage-Test | P1 |
| Deployment | PARTIAL | GitHub Action deployt main/staging via SSH und destruktivem clean auf Server | YAML/Healthpfad | aktuelle Actions-Evidenz, Schutzregeln | P0 | manuelles RC-Gate vor Push | P0 |
| Rollback | DOCUMENTED_ONLY | Runbooks, kein automatisierter DB/App Rollback | keine | Restore/previous image | P0 | Drill | P0 |
| Migrationen | IMPLEMENTED_NOT_E2E_VERIFIED | Deploy führt upgrade head aus | Tests/Head PASS | PostgreSQL U/D/U | P0 | Test-DB-Gate | P0 |
| Releaseartefakt/BC-Download | PARTIAL | installierte Artefakte `1.0.2.12`/`1.0.2.16` praktisch belegt; kein attestiertes finales RC-Artefakt | kein aktueller finaler RC-Compile | reproduzierbares finales RC-Artefakt/Hash | P0 | CI-Artefakt erzeugen | P0 |
| Verfügbarkeit/Performance | BLOCKED | Health online; keine SLO-/Lastdaten | keine | 10-Tenant Last/SLA | P0 für zehnten Kunden | Last-/Soaktest | P0 |
| Dependency Security | BLOCKED | gepinnte Requirements; `pip check` PASS; kein lokaler pip-audit/trivy | Konsistenz PASS | CVE/SBOM/Image Scan | P1 | CI pip-audit + image scan | P1 |
| Datenschutz/DPA/Retention | PARTIAL | DPA-/Processing-/Retentiondocs | Delete Test | Rechtsfreigabe + technische Retention | P0/P1 | Pilotvereinbarung/manuelle Retention | P0 |
| Support/SLA/Incidentkommunikation | PARTIAL | statische Supportangaben und Runbooks | keine Übung | bestätigte Erreichbarkeit/Vertretung | P0 | Daniel legt Kanal/Zeiten/Eskalation fest | P0 |
| manuelle 10-Kunden-Abläufe | PARTIAL | Adminfunktionen ermöglichen Freischaltung/Korrektur | Admin Tests | Kapazitätsprobe/Checkliste | P0 | tägliches Cockpit + Wochenreview | P0 |

## 6. Testübersicht

| Kommando/Prüfung | Ergebnis | Einordnung |
| --- | --- | --- |
| `backend\.venv\Scripts\python.exe -m pytest --collect-only -q` | PASS: 394 Tests gesammelt | Inventar |
| `backend\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q` | PASS: 387; SKIP: 7; 89 Warnungen; 196,49 s | breite Unit/API/Contract-Suite |
| `... pytest -q -rs tests\test_p0e_postgres_concurrency.py` | SKIP: 7, explizit „requires real PostgreSQL locking semantics“ | kein PostgreSQL-Nachweis |
| `alembic heads` | PASS: ein Head `0028_exception_count` | Graph konsistent |
| Alembic Upgrade/Downgrade/Upgrade | BLOCKED: kein PostgreSQL/psql; Docker Engine nicht aktiv | P0 offen |
| `docker compose -f docker-compose.dev.yml config --quiet` | PASS mit Env-Warnungen | Syntax |
| `docker compose -f docker-compose.p0e.yml config --quiet` mit Audit-Platzhaltern | PASS | Syntax |
| PROD Compose Config | BLOCKED: `.env.prod` absichtlich nicht lokal vorhanden | externes Gate |
| Docker Build/Compose Runtime | BLOCKED: Docker Engine nicht aktiv | kein Image-/Postgreslauf |
| `Test-ALSourceUniqueness.ps1` | historischer FAIL-Befund dokumentiert; für finalen RC in diesem Dokumentensprint nicht ausgeführt | P0 offen, bis finaler RC grün |
| `Test-GL01CDHExceptions.ps1` | PASS: 7 Contracts | AL-Ausnahmen |
| `Test-GL01FFirstRunUX.ps1` | PASS | Setup/First Run Contracts |
| `scripts/validate_bc_extension.py` | FAIL: doppelte AL-ID | Releaseblocker |
| `scripts/check_al_localization.py` | FAIL: 24 Befunde in `DHSalesLineIssueWorklist.Page.al` | P1 Pilot-UX |
| XLIFF XML/Targets | PASS: 1519 DE-Targets für 1519 DE-Units | formale Targetabdeckung, keine Sprachqualität |
| `scripts/check_pricing_consistency.py` mit isolierter Testkonfiguration | PASS: Landing-Snapshot und Backend-Fallbacks stimmen überein | beweist keine DB-Tier-/Stripe-Live-Konsistenz |
| `pip check` | PASS | keine gebrochenen Python-Abhängigkeiten |
| CVE/Image Scan | BLOCKED: kein lokales Audittool/Docker | P1 offen |
| lokaler Landing-Link-/Assetcheck | PASS: 0 fehlende lokale Ziele in beiden Landing-Verzeichnissen | keine externen/inhaltlichen Aussagen |
| lokaler Chromium-Browseraudit | PASS Konsole/Globaloverflow; FAIL sichtbare `EUR-`, Legacycopy und interne 390px-Clipping-Befunde | P1 |
| getrackter Report-PDF-Render | PASS: 2 A4-Seiten, Footer 01/02, visuell kein Überlauf; Terminologie veraltet | aktueller RC-Render noch offen |
| öffentliche PROD/DEV Health | PASS: HTTP 200; PROD ready DB ok | Erreichbarkeit, keine Business-E2E-Evidenz |
| `git diff --check` | PASS nach Dokumenterstellung | keine Whitespacefehler |

Warnungen der Vollsuite: Starlette `TemplateResponse`-Deprecations und python-jose `datetime.utcnow()`-Deprecations. Kein Pilotblocker, aber P2-Technikschuld.

## 7–16. Bereichsbewertungen

### 7. BC-Extension

Codekern und Zugriffsschutz sind stark. Die reale BC-Sandbox-Journey belegt die Grundfunktionen auf `1.0.2.12` und `1.0.2.16`; sie muss nicht vollständig neu erfunden werden. Offen bleiben der grüne Build samt Objekt-ID-Eindeutigkeit und CodeCop/PTECop des finalen RC, ein kompakter RC-Regressionstest, vollständiger Datenerhalt nach Upgrade sowie die Monitoring-Regression einschließlich 24-Stunden-TaskScheduler- und Recovery-Nachweis.

### 8. Backend/API

Der Backendkern hat die höchste nachweisbare Reife. Tenant-Isolation, Starttransaktionen, Lifecycle und Access-Rechecks sind gut getestet. P0 bleiben reale PostgreSQL-Semantik, Upgrade-/Restore-Beweis, Last-/Soaktest und produktiver Alertingbetrieb.

### 9. Dashboard/Portal

Login, Multi-Tenant-Membership und Capability-Schutz sind implementiert und getestet. Für den Pilot fehlen Browser-E2E, Login-Bruteforce-Schutz und ein manueller Passwort-Recoveryprozess. Ein vollwertiges kundenseitiges User-Management ist nicht nötig, solange Daniel Onboarding und Reinvites übernimmt.

### 10. Adminportal

Die notwendigen manuellen Pilotoperationen sind vorhanden. HTTP Basic allein ist für einen öffentlich erreichbaren Adminbereich zu schwach. Vor echten Kunden muss mindestens eine Netzwerkbeschränkung/VPN/IP-Allowlist zusätzlich zu TLS und starkem Secret aktiv sein.

### 11. Reports

HTML/PDF, Tenant-Schutz, TTL, DE/EN und Kennzahlen sind gut getestet. Auf dem `1.0.2.16`-Pilotpfad funktionierten HTML und PDF; das Ergebnis war ein sauberer zweiseitiger A4-Render. P1 bleiben Terminologie, fachliche Golden Results und ein kompakter finaler RC-Render mit großen Zahlen und vielen Findings.

### 12. Landingpage

Für einen eingeladenen, begleiteten Pilot ist keine öffentliche Kaufstrecke erforderlich. Der sichtbare Content ist jedoch nicht durchgehend pilotreif: parallele Landing-Systeme, Legacycopy, `EUR-`, Platzhalter, unbestätigte Verfügbarkeitsclaims und mobile Clipping-Befunde. Pilotkunden sollten bis zur Bereinigung einen kuratierten Onboardinglink erhalten.

### 13. Stripe/Billing

Der Code deckt Checkout, Signatur, Idempotenz, Subscription-/Invoice-Events, Portal und Aktivierung gut ab. Reale Test-/Live-Konfiguration, Tax, Invoice Compliance, Refund/Dispute und E2E sind offen. Stripe ist für den betreuten Pilot nicht zwingend: Admin-Grant, manuelle Rechnung und Auditlog sind eine sichere Übergangslösung.

### 14. E-Mail

Nur Dashboard-/Partner-Einladungen und Admin-Testmails sind als produktive SMTP-Pfade erkennbar. Für Pilot zehn werden keine automatischen Marketingmails benötigt. Notwendig sind ein verifizierter Zugangskanal und eine garantierte Betreiberwarnung bei Scan-/Monitoringfehlern; beides kann anfangs manuell über tägliche Checks und Vorlagen erfolgen.

### 15. Dokumentation

Viele deutsche technische, Pilot- und Abnahmedokumente existieren bereits. Das Defizit ist überwiegend Konsolidierung, Versionsaktualität und praktische Operatorabnahme, nicht pauschales Fehlen. Vor Kunde 1 sind die vorhandenen Inhalte zu Installation/Upgrade, QuickStart/Registrierung/Free Scan, Monitoring/TaskScheduler, Dashboard/Findings/Report, Rollen, Troubleshooting, Datenschutz/DPA, Support, Abnahme, Known Limitations und Operator-/Backup-/Incidentbetrieb auf den finalen RC zu bündeln.

### 16. Operations, Security, Datenschutz

Healthchecks, TLS, Sicherheitsheader und Deployworkflow sind vorhanden. Fehlend oder nicht belegt sind externer Monitor/Alarm, Backup-Restore, Log-/Disk-Grenzen, Rollback-Drill, SBOM/CVE-Scan, commitgenaue Deploymentattestierung, Retentionbetrieb und Supportbereitschaft. Diese Punkte dürfen nicht hinter UI-Polish zurückgestellt werden.

## 17–21. Gesonderte Go-Live-Bewertungen

| Ziel | Readiness | Entscheidung | P0-Blocker | wichtigste P1-Risiken | manuelle Prozesse | realistische Restdauer* |
| --- | ---: | --- | --- | --- | --- | --- |
| 1 betreuter Pilotkunde | 78 % | **NO-GO heute** | finaler RC mit AL-/Objekt-ID-/CodeCop-/PTECop-Gate; kompakte RC-Regression und vollständiger Upgrade-Datenerhalt; Monitoring-Regression/24h-Scheduler; PostgreSQL U/D/U/Konkurrenz; realer Recovery-, Restore- und Alerting-/Incident-Test; minimales Operator-/Pilotpaket | Copy/Localization, Loginlimit, Golden Results | Admin-Grant und Auditlog, manuelle Rechnung, Statusmails, tägliche Kontrolle | 2–4 fokussierte Arbeitstage plus 24h Schedulerfenster |
| 10 betreute Pilotkunden | 63 % | **NO-GO** | alle obigen plus 10-Tenant Last-/Soaktest, Operatorcockpit, Backup-/Rollbackbetrieb und Supportkapazität | Admin-Härtung, Retention, Runbookkonsolidierung | tägliches Scan-/Billing-/Backup-Cockpit, wöchentliche Review | 5–8 Arbeitstage plus Pilotstaffelung |
| erster regulär zahlender Kunde | 43 % | **NO-GO** | Stripe Live/Tax/Invoice/E2E oder rechtskonforme manuelle Bestellung; Rechtsseiten/Vertrag; Zahlungsfehler/Kündigung/Refundprozess | E-Mail-Automation, Passwortreset, SLA | nur mit individuell unterschriebenem B2B-Vertrag und manueller Rechnung vertretbar | 2–4 Wochen |
| Public Go-Live | 28 % | **NO-GO** | Self-Service, Rechts-/Cookiefreigabe, Security/Load/DR, automatisierte Kommunikation, öffentliche Supportfähigkeit | SEO/A11y, Reconciliation, Content | manuelle Prozesse skalieren nicht | 4–8 Wochen |
| AppSource | 18 % | **NO-GO** | AppSourceCop/Metadaten/ID-Range/Signierung, vollständige BC Runtime-/Upgrade-/Permission-Evidence, Listing/Support | Telemetrie/Localization/Marketplace Docs | nicht sinnvoll manuell ersetzbar | 6–12+ Wochen |

\* Ab Verfügbarkeit einer BC-27-Sandbox, PostgreSQL-Testumgebung und Daniels Zeit; keine Provider-/Rechtswartezeiten.

## 22. P0–P3-Gap-Liste

### P0 – vor erstem bzw. zehntem Pilotkunden

1. Finalen RC mit SHA, Extension-Version, Artefakt und Hash einfrieren.
2. Finalen RC mit eindeutigen AL-Objekt-IDs grün bauen; Source-Uniqueness, CodeCop und PTECop ohne neue Releasebefunde.
3. Kompakte BC-Sandbox-Regression auf dem finalen RC: Installation/Setup/Registrierung/Duplicate-Schutz/Free/History/Findings/Dashboard/HTML/PDF sowie Assessment/Validation stichprobenartig wiederholen; die bestandenen `1.0.2.12`-/`1.0.2.16`-Nachweise bleiben Baseline.
4. Upgrade auf den finalen RC mit Datenerhalt, Setup/Token/Rechten, Historie, erneutem Scan, Monitoring und Background Scan vollständig belegen.
5. Monitoring-Regression schließen und manuellen sowie geplanten Lauf einschließlich Historie und 24-Stunden-Schedulerfenster auf dem finalen RC nachweisen.
6. Echten BC-Recoverytest durchführen; kein orphaned Run und kein Doppelcredit.
7. Reale PostgreSQL-Konkurrenztests und Alembic Upgrade/Downgrade/Upgrade auf isolierter Test-DB.
8. Backup/Restore, externes Alerting und Incident-/Rollback-Probe erfolgreich ausführen; Adminzugang und tägliche Betreiberchecks absichern.
9. Vor Kunde 1: vorhandene Operator-/Pilot-/Abnahme-/Datenschutzunterlagen auf den finalen RC konsolidieren und praktisch abnehmen. Vor Kunde 10 zusätzlich 10-Tenant-Last-/Soaktest und belastbaren Operatorbetrieb nachweisen.

Stripe Live, Refund und Chargeback gehören **nicht** zu diesen P0-Punkten für den ersten betreuten Pilotkunden. Zulässige Übergangslösung sind protokollierte Adminfreischaltung, Auditlog, externe manuelle Rechnung und tägliche Reconciliation.

### P1 – im Onboarding bzw. vor mehreren aktiven Kunden

- Terminologie-/Preisdrift und sichtbare Pilot-Contentfehler beseitigen.
- Dashboardlogin limitieren, Passwort-Recovery dokumentieren.
- Rollenmatrix real testen; DE/EN-Pilotpfade lektorieren.
- Golden-Dataset-Freigabe für Score, Impact und Empfehlungen.
- Logrotation/Diskgrenzen, CVE-/Image-Scan, Auditreview und Retentionbetrieb.
- Stripe Testmode vollständig testen, falls während des Piloten genutzt.

### P2 – während des betreuten Piloten

- automatische Welcome-, Scan-, Report- und Billingmails;
- Dashboard-Passwortreset, Tenant-Supportbundle, Barrierefreiheitsbasis;
- Refund/Dispute-Automation, periodische Stripe-Reconciliation;
- Performance-/Lighthouse-Verbesserungen.

### P3 – Public/Enterprise/AppSource

- AppSource-Zertifizierung, Listing, Signierung und Marketplace-Material;
- vollständiger Self-Service, Enterprise-Skalierung und Partnerausbau;
- umfassende Telemetrie/SLOs, A11y-Zertifizierung, SEO/RUM.

## 23. Manuell durch Daniel auszuführende Prüfungen

| ID | Voraussetzungen/Testdaten | Schritte | Erwartetes Ergebnis | PASS/FAIL | Beweis |
| --- | --- | --- | --- | --- | --- |
| M01 RC/CI | finaler RC-SHA, Actionszugriff | AL, Objekt-ID-Eindeutigkeit, CodeCop, PTECop, Backend und PostgreSQL-Gates ausführen; Logs archivieren | alle Pflichtjobs grün, SHA und Extension-Version identisch | ☐ | Actions-URLs + Artefakthash |
| M02 Install | reale BC-Sandbox; Baseline `1.0.2.12` PASS | finalen RC kompakt installieren; Rollen/Setup stichprobenartig prüfen | keine Fehler, Setup vorhanden; Baseline bleibt erhalten | ☐ | Screenshots + BC-/Extension-Version |
| M03 Registrierung/Free | Baseline `1.0.2.12`/`1.0.2.16` PASS | auf finalem RC Registrierung/Duplicate-Schutz/Free/History/Findings/Dashboard/HTML/PDF kompakt regressieren | genau ein Tenant/Membership; ein abgeschlossener Scan; Ausgaben erreichbar | ☐ | Screenshots + redigierte Request IDs/DB-Zählung |
| M04 Isolation | zwei Tenants, zwei Companies, zwei User | Tokens/URLs/Sessionkontext kreuzweise verwenden | jeder Fremdzugriff 401/403, keine Datenanzeige | ☐ | Screenshots + Logs ohne Secrets |
| M05 Assessment manuell | `1.0.2.16` Baseline PASS | Grant, Zugriffslaufzeit, Findings und Report auf finalem RC stichprobenartig wiederholen; Ablauf prüfen | Rechte sofort aktiv; nach Ablauf nur erlaubte Free-Sicht | ☐ | Adminaudit + BC/Dashboard Screenshots |
| M06 Validation | `1.0.2.16` Baseline PASS, 1 Credit | Validation auf finalem RC starten; Retry und konkurrierenden Start prüfen | genau ein Credit/Scan; Findings/History/Report aktualisiert | ☐ | Ledger/Run/History-Screenshots |
| M07 Monitoring manuell | finaler RC, Monitoring aktiv; `1.0.2.16` nur PARTIAL | „Start Monitoring Scan“; Client weiter bedienen; Historie ohne manuellen Refresh beobachten | sofortige Rückkehr; Run queued→running→completed; Historie selbstständig aktuell | ☐ | Zeitstempelvideo/Screenshots + Request ID |
| M08 Monitoring geplant | TaskSchedulerrechte, kurzer Testzeitpunkt | täglichen Task planen; Benutzer abmelden; Ausführung abwarten | Task läuft ohne Session; nächster Termin/Status korrekt | ☐ | Task-/History-/Backendlogs |
| M09 Fehler/Recovery | aktiver Scan | BC-Session oder Backendworker kontrolliert stoppen; Lease ablaufen/retry; wiederherstellen | kein ewiges Running; gleicher Run kontrolliert recovered/failed; kein Doppelcredit | ☐ | Eventfolge + Ledger |
| M10 Reports | `1.0.2.16`-Baseline: sauberes zweiseitiges A4-PDF | finalen RC mit DE/EN, Sonderzeichen, großen Werten/vielen Findings kompakt rendern | erwartete Seiten, keine Überläufe, Footer/Seitenzahlen, Daten identisch | ☐ | PDFs + Screenshots |
| M11 Upgrade | installierte `1.0.2.12` mit Setup/Token/History/Rechten; Upgrade auf `1.0.2.16` bereits grundsätzlich PASS | Upgrade auf finalen RC; Datenerhalt zählen; manuellen und Background Scan ausführen | Setup/Token/History/Rechte erhalten; Monitoring und neuer Scan funktionieren | ☐ | Upgradeprotokoll + Vor/Nach-Zählungen |
| M12 PostgreSQL | isolierte PostgreSQL-Test-DB | Migration head; P0E-Tests; downgrade auf letzten sicheren Schritt; wieder head | alle Tests grün, Datenzählungen stabil | ☐ | Logs/JUnit/Schema-Version |
| M13 Backup/Restore | Stage-DB + Objectstorageziel | Backup; Prüfsumme; isolierte DB restaurieren; Ready + Stichproben | Restore verwendbar innerhalb RTO; keine PROD-Veränderung | ☐ | Backup-ID/Hash/Restorelog/RTO |
| M14 Betrieb | externer Monitor/Alarmkanal | Backend/DB testweise in Stage stören; Alarm empfangen; Incident/Recovery ausführen | Alarm innerhalb Zielzeit, Runbook funktioniert | ☐ | Alarm + Incidenttimeline |
| M15 SMTP/DNS | produktive Absenderdomain/Testinbox | SPF/DKIM/DMARC prüfen; DE/EN Invite senden; Spam/Links testen | authentifiziert zugestellt, Link einmalig/TTL | ☐ | DNS-Report + Header/Screenshot |
| M16 Stripe Testmode | Testprodukte/Prices/Webhook/Testclock | je Produkt Checkout; Duplicate/Delayed Webhook; Renewal/Cancel/Failure | korrekte Purchase/Credit/Rechte; idempotent; kein Fremdtenant | ☐ | Stripe Event IDs + redigierte DB-Snapshots |
| M17 Stripe Live/Tax | Steuerberaterfreigabe/Live Dashboard | Produkte/Prices, Tax, Invoice, Portal, Refund/Dispute-Runbook prüfen | rechts-/preisvertragskonform | ☐ | signierte Checkliste, keine Secrets |
| M18 Recht/Datenschutz | reale Anbieter-/Firmendaten | Impressum, Datenschutz, DPA, Terms/B2B, Retention freigeben | keine Platzhalter/vorläufige Texte; Pilotvereinbarung signierbar | ☐ | Freigabedatum/Version |
| M19 10-Tenant Soak | 10 synthetische Tenants | registrieren; versetzte manuelle/geplante Scans; Reports; Fehlerfall | keine Isolation-/Creditfehler, definierte Laufzeit, Alarme funktionieren | ☐ | JUnit/Logs/Metriken/Tabelle |
| M20 Supportprobe | Operator + Testkunde | Zugang verloren, Scan hängt, Report fehlt, Upgrade scheitert simulieren | Diagnose/Recovery innerhalb SLA | ☐ | Ticket-/Zeitprotokoll |

## 24. Empfohlener Pilotumfang

Enthalten: BC Cloud 27, ein klar definierter Company-Kontext je Pilottenant, Free Scan, manuell freigeschaltetes Assessment, optional Validation, Monitoring Monthly/Annual als Berechtigung ohne zwingenden Stripe-Kauf, Dashboard, Findings, HTML/PDF, Data-Health-Ausnahmen, DE/EN und betreuter Support.

Zunächst manuell: Kundenanlage, Einladung, Produktgrant, Rechnung, Monitoringkontrolle, Status-/Fehlermails, Reconciliation und Support. Bei zehn Kunden ist dies tragbar, wenn Daniel täglich etwa 30–45 Minuten für Cockpit/Alarme plus Onboardingzeit reserviert und ein Stellvertreter/Notfallkontakt definiert ist.

Ausgeschlossen: öffentlicher Self-Service, AppSource, automatische Refunds/Chargebacks, garantierte Enterprise-SLAs, unbegrenzte Kundenbenutzerverwaltung und Marketingautomation.

## 25. Bekannte Einschränkungen

- der finale RC ist noch nicht mit grünem AL-Build, Objekt-ID-Eindeutigkeit, CodeCop/PTECop und Artefakthash attestiert;
- reale BC-Evidence liegt für `1.0.2.12` und `1.0.2.16` vor, gilt aber nicht automatisch für den finalen RC;
- PostgreSQL-, SMTP-, Restore-, Alerting-/Incident- und Last-/Soak-Evidence fehlt;
- parallele Produkt-/Landingmodelle und Legacybegriffe bestehen;
- Monitoring ist widersprüchlich belegt: früher geplanter Lauf erfolgreich, auf `1.0.2.16` später mögliche Regression; 24h-RC-Nachweis fehlt;
- Dashboard-Passwortreset, umfangreiche Benutzerselbstverwaltung und automatische Statusmails fehlen;
- Operations/Alerting/DR sind nicht ausreichend belegt;
- öffentliche Rechts-/Contentseiten benötigen Freigabe und Bereinigung.

## 26. Finale GO/NO-GO-Entscheidung

**NO-GO heute.** Die Entscheidung gilt für den aktuellen Repository- und Umgebungsstand und ist keine Bewertung des Produktpotenzials. Nach Schließen der P0-Gates kann ein einzelner betreuter Pilot als **GO WITH CONDITIONS** starten; zehn Kunden erst nach zusätzlichem Last-/Soak-, Alerting-, Restore- und Supportkapazitätsnachweis. Stripe darf dabei vorübergehend manuell ersetzt werden. Sicherheit, Tenant-Isolation, Datenintegrität, funktionierende manuelle/geplante Scans, Reports, Backup/Restore und kontrollierter Support bleiben unverhandelbare Gates.
