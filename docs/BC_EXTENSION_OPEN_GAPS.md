# BCSentinel Extension – Open Gaps and Follow-up Sprints

Stand: 16.07.2026  
Audit: GL-EXT-AUDIT-01  
Basisentscheidung: **NO-GO**

## Priorisierte Gap-Liste

### P0

| ID | Gap | Code-Evidenz | Auswirkung | Owner-Vorschlag |
|---|---|---|---|---|
| P0-01 | Produktions-API akzeptiert HTTP | `DHSetup.Table.al:383–396` | API-Token/Tenantdaten können im Klartext übertragen werden | AL/Security |
| P0-02 | Registrierung nicht idempotent und nicht an BC-Identität gebunden | `DHApiClient.Codeunit.al:135–163`, `backend/app/main.py:361` | Re-Registrierung/Reset kann Käufe, Portalzugang und Historie verwaisen | AL + Backend |
| P0-03 | Creditverbrauch nicht atomar/retry-sicher | `product_license_service.py:575–596`, `DHDeepScanMgt.Codeunit.al` | ein Credit kann parallele Runs zulassen; Antwortverlust kann doppelt verbrauchen | Backend + AL |
| P0-04 | Scanfehlerpfad nicht verdrahtet | direkter `DeepScanRunner.Run`; Failure-Codeunit ohne Call-Site | dauerhaft `Running`, verbrauchter Credit, keine Selbstheilung | AL |
| P0-05 | Findings lokal mit stale Lizenzgate geschützt | `DHIssueDrilldownMgt.Codeunit.al:38`, Findings-Pages prüfen `Premium Enabled` | Premiumdetails nach Ablauf weiterhin sichtbar | AL + Security |

### P1

| ID | Gap | Erforderliches Ergebnis |
|---|---|---|
| P1-01 | kein Install-/Upgradepfad | idempotente Install- und N-1-Upgrade-Codeunits mit Tests |
| P1-02 | kein aktueller AL-/Analyzer-Nachweis | CI-Compile plus CodeCop, AppSourceCop, PTECop grün |
| P1-03 | keine AL-Test-App | automatisierte Kernflow-, Permission-, Install- und Upgrade-Tests |
| P1-04 | Scan ist synchron, Monitor pollt nicht | echte Queue-Ausführung, Fortschritt, Timeout/Cancel/Retry |
| P1-05 | Schedulerrechte und Serviceidentität unklar | dedizierte minimale Rolle; Sandboxlauf ohne SUPER |
| P1-06 | Currency-Wert wird nur als LCY etikettiert | Umrechnung mit Kurs/Datum oder eindeutige EUR-Darstellung |
| P1-07 | Exception-Grund/Audit/Reaktivierung unvollständig | Pflichtgrund, Wer/Wann, klare Include/Exclude-Aktion, Cleanup |
| P1-08 | Lokalisierungschecker rot | Labels/XLF/UTF-8 bereinigt, EN/DE CAT grün |
| P1-09 | zwei Backendtests und Pricing-Consistency-Check rot | Assessment-Vertrag/Fallback in Pricing, Admin, Snapshot und Test angleichen; `Überblick`-Test aktualisieren |
| P1-10 | Tokenrotation/Recovery fehlt | Rotate/Revoke/Rebind ohne Tenant-/Kaufverlust |
| P1-11 | Portal-Resend/Recovery fehlt | kundenfähige Aktion mit Status und sicheren Fehlercodes |
| P1-12 | Page-OnOpen schreibt Sortfelder | Sortwerte bei Insert/Modify/Upgrade; Viewer bleibt read-only |
| P1-13 | API-Resilienz unzureichend | Timeouts, begrenzte Retries/Backoff, 429/Retry-After, Idempotency |
| P1-14 | Retention/Supportkorrelation nicht durchgängig | technische Löschfristen; Request-ID in AL und Runbook |
| P1-15 | Manifest-/Versionsdrift | eine Releaseversion, endgültige Metadaten und reproduzierbares Paket |

### P2

- P2-01: keine Role-Center-Erweiterung/Cues.
- P2-02: kein sauberer Cancel-/Partial-Success-Zustand.
- P2-03: Lizenzdaten in AL als Text statt DateTime.
- P2-04: Scheduler-DST-/Zeitzonen- und Orphan-Task-Härtung.
- P2-05: Dashboard-/Reporttoken zunächst in URL; Logredaction und Übergabe verbessern.
- P2-06: Historien-/Finding-Performance und Retention unter Volumen testen.
- P2-07: Starlette- und `datetime.utcnow()`-Deprecation-Warnungen bereinigen.
- P2-08: Setup versteckt technische Komplexität noch nicht ausreichend.

### P3

- P3-01: zusätzliche Telemetrie- und Supportdashboards.
- P3-02: Trend-/Delta-Benachrichtigungen und erweiterte Schedulerkomfortfunktionen.
- P3-03: erweiterte Filter, Export- und Accessibility-Politur.

## Empfohlene Folge-Sprints

### GL-EXT-FIX-01 – Identity, Transport and Access Enforcement

**Reihenfolge:** 1  
**Aufwand:** 8–12 Personentage  
**Abhängigkeiten:** Backend-/AL-Team, Security Review

Umfang: P0-01, P0-02, P0-05 sowie Token-/Invite-Recovery-Grundlage.

**Definition of Done**

- Produktion akzeptiert ausschließlich HTTPS und erwartete Hosts.
- Registrierung sendet verifizierbare Azure-/BC-Tenant-, Environment- und Company-Identität sowie korrekte App-Version.
- Wiederholung, Antwortverlust, Reinstall und Companywechsel liefern deterministisch denselben beziehungsweise bewusst getrennten Tenant.
- bestehende Entitlements können ohne manuellen DB-Eingriff wieder angebunden werden.
- jede lokale Premiumanzeige prüft einen frischen `Can View Issue Details`-Status; negative Tests nach Ablauf bestehen.
- Security Review und Cross-Tenant-Regression sind grün.

### GL-EXT-FIX-02 – Atomic Credits and Resilient Scan State Machine

**Reihenfolge:** 2  
**Aufwand:** 10–15 Personentage  
**Abhängigkeiten:** FIX-01-Identität; Datenbankmigration

Umfang: P0-03, P0-04, P1-04, P1-13.

**Definition of Done**

- Credit wird in einer atomaren Transaktion reserviert/verbraucht; DB-Constraint verhindert Doppelzuordnung.
- zehn parallele Starts mit einem Credit ergeben exakt einen akzeptierten Run.
- identische Run-ID und Antwortverlust sind idempotent; kein Doppelverbrauch.
- Zustandsautomat erlaubt nur definierte Übergänge und endet immer terminal oder wird durch Watchdog repariert.
- Manual und Scheduler nutzen dieselbe asynchrone Queue; Monitor pollt belastbar.
- Fehler-, Timeout-, Retry-, Cancel- und Recovery-Tests bestehen.

### GL-EXT-FIX-03 – Permissions, Scheduler and Data Correctness

**Reihenfolge:** 3  
**Aufwand:** 8–12 Personentage  
**Abhängigkeiten:** FIX-02 Queue-/State-Machine

Umfang: P1-05, P1-06, P1-07, P1-12.

**Definition of Done**

- dedizierte Scheduler-/Service-Rolle enthält genau benötigte Extension- und Standardtabellenrechte.
- VIEWER, SCAN, SETUP, ADMIN und Scheduler bestehen Positiv-/Negativtests ohne SUPER.
- Read-only-Pages schreiben beim Öffnen nicht.
- Currency-Vertrag ist fachlich freigegeben; Nicht-EUR-CAT besteht.
- Ausnahmen verlangen Grund, protokollieren Actor/Zeit und besitzen korrekte Deactivate/Reactivate-/Cleanup-Semantik.

### GL-EXT-QA-04 – AL Test App, Install and Upgrade

**Reihenfolge:** 4  
**Aufwand:** 12–18 Personentage  
**Abhängigkeiten:** FIX-01 bis FIX-03; BC-Sandbox/CI

Umfang: P1-01, P1-02, P1-03, P1-15.

**Definition of Done**

- Install-Codeunit und Upgrade-Codeunit mit Version-Tags sind idempotent.
- AL-Test-App deckt Setup, Registrierungsmocks, Lizenz, Credits, Scans, Scheduler, History, Currency, Findings, Exceptions und Permissions ab.
- N-1-Upgrade erhält Setup, Isolated-Storage-Token, History, Exceptions und geplante Tasks oder migriert sie dokumentiert.
- CI baut aus sauberem Checkout; Compiler, CodeCop, AppSourceCop und PTECop sind grün.
- Manifest-/Cloudversion, Paketname, Commit und SHA-256 stimmen überein.

### GL-EXT-REL-05 – Localization, CAT and Operational Readiness

**Reihenfolge:** 5  
**Aufwand:** 8–12 Personentage  
**Abhängigkeiten:** QA-04 Releasekandidat

Umfang: P1-08 bis P1-11, P1-14, CAT-01 bis CAT-23, relevante P2-Gaps.

**Definition of Done**

- AL-Lokalisierungscheck und komplette Backend-Suite sind grün.
- Pricing-Consistency-Check ist grün und der Assessment-Produktvertrag ist fachlich freigegeben.
- EN-US/DE-DE enthalten keine Mischtexte oder Encodingfehler.
- Retention, Löschung, Tokenrotation, Invite-Resend, Request-ID und Support-Runbook sind technisch und organisatorisch freigegeben.
- CAT-01 bis CAT-23 bestehen in frischer Sandbox und N-1-Upgradesandbox.
- Pilot-Runbook enthält Monitoring, Feature-Flag/Kill-Switch, Owner, Alarmgrenzen und Exit-Kriterien.
- formelle Neubewertung ergibt mindestens `PILOT GO`.

### GL-EXT-APP-06 – AppSource Submission Readiness

**Reihenfolge:** 6, nur nach erfolgreichem Pilot  
**Aufwand:** 5–8 Personentage  
**Abhängigkeiten:** REL-05 und Pilotabschluss

**Definition of Done**

- AppSource Technical Validation und alle Analyzer bestehen auf dem finalen Paket.
- EULA, Privacy, Terms, Support, Help, Logo, Screenshots und Listing sind final.
- Installation/Upgrade auf unterstützten BC-Versionen ist belegt.
- Customer-Go-Live-Betriebsdaten zeigen keine offenen P0/P1-Regressions.
- Freigabegremium entscheidet separat `APPSOURCE READY`.

## Abhängigkeitspfad

`FIX-01 Identity/Access` → `FIX-02 Credits/Scans` → `FIX-03 Permissions/Data` → `QA-04 Build/Upgrade/Tests` → `REL-05 CAT/Operations` → `APP-06 AppSource`.

Die ersten fünf Sprints sind keine optionalen Komfortpakete: Sie bilden zusammen die minimale Route von `NO-GO` zu einer belastbaren erneuten Pilotentscheidung.

## Status-Delta GL-EXT-P0A (16. Juli 2026)

Die ursprünglichen Gap-Zeilen bleiben als Audit-Historie erhalten.

| Gap | Ursprünglicher Status | Korrektur und Evidenz | Aktueller Status |
|---|---|---|---|
| P0-01 | offen: beliebiges HTTP möglich | zentrale URL-Policy in AL und Backend; produktive Transport-Middleware; Transport-Negativtests; AL-Build grün | **geschlossen** |
| P0-02 | offen: zufällige, nicht gebundene Registrierung | kanonische Entra-/Environment-/Company-Identität; Unique Constraint; transaktionaler Upsert; Parallel-/Retry-/Migrationstests | **geschlossen** |
| P1-10 | offen | nicht erweitert; deterministischer P0A-Registration-Retry ersetzt keine allgemeine Rotate/Revoke-Funktion | **offen** |
| P2-05 | offen | Dashboard-Kontextbindung gehärtet; initiale Tokenübergabe in URL unverändert | **offen** |

Verbleibende P0: P0-03 Credit-Atomizität, P0-04 Scanstatus-Lifecycle und P0-05 lokaler Findings-Zugriffsschutz. Gesamtentscheidung daher weiterhin **NO-GO**.

## Status-Delta GL-EXT-P0B (16. Juli 2026)

| Gap | Ursprünglicher Status | Korrektur und Evidenz | Aktueller Status |
|---|---|---|---|
| P0-03 | offen: nicht atomarer Check-then-consume-Pfad | `scan_start_requests`, append-only Ledger, DB-Sperre/Conditional Update, Unique Constraints, stabile AL-GUID, Thread-/Rollback-/Migrationstests | **geschlossen** |
| P0-04 | offen | bewusst nicht bearbeitet | **offen** |
| P0-05 | offen | bewusst nicht bearbeitet | **offen** |

Verbleibende P0: P0-04 Scanstatus-Lifecycle und P0-05 lokaler Findings-Zugriffsschutz. Empfohlener nächster Sprint ist **GL-EXT-P0C – terminaler Scan-Lifecycle und kontrollierte Recovery**. Definition of Done: jeder angenommene Run erreicht terminal `Completed`, `Failed` oder `Cancelled`; Heartbeat/Stall-Detection und Restart-Recovery sind getestet; Refund bleibt explizit und ledgerbasiert; AL und Backend zeigen denselben Endstatus; Parallel-/Crash-/Timeouttests und BC-Sandbox-CAT sind grün. Danach folgt P0D für den Findings-Zugriffsschutz.

## Status-Delta GL-EXT-P0C (16. Juli 2026)

| Gap | Ursprünglicher Status | Korrektur und Evidenz | Aktueller Status |
|---|---|---|---|
| P0-04 | offen: Runs konnten unkontrolliert nichtterminal bleiben | State Machine, Lease/Heartbeat, atomarer Claim, Tokenrotation, Startup-/periodische Recovery, bounded Retry, Pflichtresultat-Gate, AL Failure Handler; automatisierte Parallel-/Recoverytests und AL-Compile | **geschlossen auf Codeebene** |
| P0-05 | offen | bewusst nicht bearbeitet | **offen** |
| P1 PostgreSQL/Sandbox-Evidenz | offen | Testfälle und Konfiguration vorbereitet | **offen / NOT_EXECUTED** |

Verbleibender P0 ist ausschließlich P0-05: lokale Findings müssen vor jeder Anzeige/Aktion mit einem frischen Access-Snapshot geschützt werden. Empfohlener Folgesprint ist **GL-EXT-P0D – Fresh Findings Access Enforcement**. Definition of Done: server- und AL-seitiger frischer Lizenzcheck auf Liste, Card, FactBox, Drilldown, direkte Page-URL und Aktionen; abgelaufener Zugriff wird ohne stale Cache blockiert; Offline-/Backendfehler fail-closed mit verständlichem Recoverypfad; Rollen-/Negativtests ohne SUPER; Sandbox-CAT grün. Produkt-Gate bleibt NO-GO.

## Status-Delta GL-EXT-P0D (20. Juli 2026)

| Gap | Ursprünglicher Status | Korrektur und Evidenz | Aktueller Status |
|---|---|---|---|
| P0-05 | stale lokale Booleans, ungeschützte Reportdownloads/Tokenausgabe | serverautoritärer Snapshot, zentraler AL Guard, Page-/Action-/Endpoint-Checks, kurze revalidierte Tokens, Least-Privilege-Viewer, 51 Szenarien | **geschlossen auf Codeebene** |
| P1 Sandbox/Permission-Evidenz | offen | 15 P0D-CATs detailliert vorbereitet | **offen / NOT_EXECUTED** |
| P1 Install/Upgrade/AL-Test-App | offen | außerhalb P0D unverändert | **offen** |
| P1 AL/Admin-Access-Telemetrie | implizit | Backendevents ergänzt; explizite Cache-/Page-/Revocation-Events noch zu vervollständigen | **offen, nicht autorisierungsblockierend** |

Alle fünf funktionalen P0-Gaps sind damit codebasiert geschlossen. Empfohlener Folgesprint: **GL-EXT-P0E – Sandbox Release Gate & Upgrade Evidence**. Definition of Done: Install und Upgrade N-1 in BC-Sandbox, alle P0A–P0D-CATs ohne SUPER, negative Rollenmatrix, Scheduler unter Servicebenutzer, PostgreSQL-Mehrinstanz/Restart, reproduzierbares signiertes Paket und vollständige Evidenz. Produkt-Gate bleibt bis dahin **NO-GO**.
