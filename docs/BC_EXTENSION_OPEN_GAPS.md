# BCSentinel Extension – Open Gaps and Follow-up Sprints

Stand: 16.07.2026  
Audit: GL-EXT-AUDIT-01  

## LIC-02 release gap

The simplified entitlement source is implemented in code. Remaining evidence is Alembic upgrade/backfill verification, full regression, regenerated DE-DE/EN-US XLIFF, AL compilation, Stripe sandbox fulfillment, and BC sandbox CAT. Go-live remains blocked until these are green.
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

## Status-Delta GL-EXT-P0E (20. Juli 2026)

| Gap | P0E-Evidenz | Status |
|---|---|---|
| PostgreSQL Migration/Concurrency/Restart | PostgreSQL 15, zwei Instanzen, Fresh/0021-Upgrade, Failure Injection | **geschlossen für lokale Stagingtopologie** |
| Install-/Upgrade-Codeunits | implementiert, AL Compile grün | **Code komplett; Sandbox offen** |
| N-1/Target-Version | 1.0.2.6 und 1.0.2.7 kompiliert | **Paketbasis vorhanden; Upgrade BLOCKED** |
| Rollen/Scheduler ohne SUPER | Schedulerrolle ergänzt, Sollmatrix erstellt | **BLOCKED – Sandbox** |
| P0A–P0D-CATs | 47 Fälle konsolidiert | **BLOCKED – 0/47 ausgeführt** |
| Pricing | Full Analysis 79, Validation 49, Monitoring 149/1490 EUR | **geschlossen** |
| Localization | Checker weiterhin rot | **P1 offen** |
| AppSource/Signing | EULA, Logo, Help URL, ID-Range, A.I., Zertifikat | **P1/AppSource offen** |

Verbleibender Gate-Sprint: **GL-EXT-P0F – BC Sandbox Execution & Signed Pilot Candidate**. Definition of Done: BC 27 Fresh Install und 1.0.2.6→1.0.2.7 Upgrade, Rollenmatrix und Scheduler ohne `SUPER`, 47/47 CATs, EN/DE-Lauf, Backup-/Rollbackprobe, P0E-Commit aus sauberem Checkout, signiertes Paket und keine kritischen P1.

## Status-Delta GL-EXT-UX01 (20. Juli 2026)

| Gap | UX01-Evidenz | Status |
|---|---|---|
| kundenorientierte Setup-Hierarchie | Status oben, Produktzugriff gebündelt, technische Werte separiert | **geschlossen auf Codeebene** |
| sichere Hauptaktionen | modusspezifischer Scanstart; Dashboard/Findings/Report mit bestehenden Guards | **geschlossen auf Codeebene** |
| destruktive Setup-Actions | Cache-Reset separat, konkrete Wirkung, Default Abbrechen | **geschlossen auf Codeebene** |
| Setup-Lokalisierung | alle finalen Setup-Units DE/EN synchron und gefüllt | **geschlossen für UX01-Texte** |
| Advanced-FastTab initial collapsed | `Expanded` im Zielkontext nicht unterstützt | **offen für Sandbox/Personalisierung, P2** |
| globale AL-Lokalisierung | 81 historische Checkerbefunde | **P1 offen** |
| UX01 Runtime/CAT | 20 Fälle, keine Sandbox | **BLOCKED** |

Empfohlener Carry-over in **GL-EXT-P0F**: 20 UX01-CATs gemeinsam mit den 47 P0A–P0D-Fällen ausführen. Definition of Done: 67/67 Sandboxfälle ohne `SUPER`, EN-US/DE-DE, Fresh Install/N-1-Upgrade, Screenshots, API-Call-/Performancebeobachtung und formelle Pilotfreigabe. Erst danach GL-EXT-UX02 beginnen oder parallel ausschließlich nicht-releasekritische Politur durchführen.

## Status-Delta GL-EXT-UX02 (20. Juli 2026)

| Gap | Evidenz | Status |
|---|---|---|
| ursprüngliche 81 Treffer | Labels/XLF, Checker 0 | **geschlossen** |
| XLF | 1.208 Source-/DE-Units, keine leeren Targets | **geschlossen strukturell** |
| Backend Top-Issues | 20 stabile Codes DE/EN, EN-Fallback, 3 Tests | **geschlossen** |
| AL-Issue-Katalog | 199 Codes; 6 als Labels, 193 EN-Fallback | **P1 offen** |
| direkte englische Kundenliterale | 155 in 23 Dateien | **P1 offen** |
| UX02 Runtime | 20 CATs ohne Sandbox | **BLOCKED** |

Nächster Sprint: **GL-EXT-UX02B**. DoD: 199/199 AL-Codes redaktionell DE/EN, 155 Kundenliterale als Labels, verschärfter Checker, große Finding-Liste performant und 20/20 UX02-CATs.

## Status-Delta REPO-01A (20. Juli 2026)

| Gap | Evidenz | Status |
|---|---|---|
| generierte AL-Quellen im Projektstamm | 246 Dateien/3 Source-Kopien entfernt; danach Guard PASS | **geschlossen** |
| rekursiver P0E-N-1-Baum | kein eingecheckter N-1-Erzeuger; Workspace-/Releasepfade extern und Allow-List | **geschlossen auf Skriptebene** |
| erneute Source-Duplikation | OutputPath-Hard-Guard und `Test-ALSourceUniqueness.ps1`; Negativtest Exit 1 | **geschlossen** |
| BC Publish/Install | keine Sandbox in diesem Lauf | **BLOCKED, unverändert** |
| AppSource-Metadaten/ID-Range/Telemetrie/Signierung | Baseline weiterhin rot | **offen, außerhalb REPO-01A** |

REPO-01A führt keine neuen Produktgaps ein. REPO-01B kann auf einem eindeutigen AL-Quellbaum aufsetzen; Sandbox-, UX02B- und AppSource-Gaps bleiben unabhängig davon offen.

## Status-Delta GL-PILOT-01-FIX01 (20. Juli 2026)

| Gap | Evidenz | Status |
|---|---|---|
| gleiche Dashboard-E-Mail in mehreren Tenants | normalisierter Benutzer + relationale Memberships, Race-/Idempotenztests | **geschlossen auf Code-/DB-Ebene** |
| Tenant-Liste und Wechsel | Session-JWT mit aktivem Tenant; serverseitige Membership-Revalidierung | **geschlossen auf Codeebene** |
| IDOR/Fremd-Tenant | direkter Pfad, Switch und manipulierter Claim jeweils 403 | **geschlossen automatisiert** |
| AL-Busy-State/Fehlertexte | TryFunction-Recovery, stabile Codes, vollständige DE/EN-Labels | **geschlossen auf Codeebene** |
| bestehende Produktionsdaten migrieren | Backup/Zählprüfung vorbereitet, keine Produktivmigration autorisiert | **offen vor Deployment** |
| Post-Fix-CAT BC 28.3 | kein Sandboxzugriff in diesem Lauf | **BLOCKED** |

Nächster zwingender Schritt ist kein weiterer Refactor, sondern der dokumentierte Wiederholungstest in `BCSentinel-Pilot` mit Migration 0025, Extension-Upgrade, Multi-Tenant-Login und Datenisolationsnachweis.

## Status-Delta GL-PILOT-01-FIX03 (20. Juli 2026)

| Gap | Evidenz | Status |
|---|---|---|
| lokal kollidierende Scan-ID | Tageszähler um 29 GUID-Hexzeichen erweitert; AL Compile PASS | **geschlossen auf Codeebene** |
| ungebundener Same-Tenant-Pending-Scan | Recovery verlangt leeren Scan, keinen Ledger/Request, identischen Tenant/Company-Kontext | **geschlossen auf Codeebene** |
| Fremd-Tenant-/Fremd-Request-Adoption | strukturierte 409-Codes; Auth/Tenant-Match unverändert | **geschlossen auf Codeebene** |
| lokaler Run bleibt nach 409 queued | `Rejected/Failed`, `Finished At`, leerer Heartbeat | **geschlossen auf Codeebene** |
| Dashboard-Busy bleibt nach Access-Denied | TryFunction, genau eine Meldung, normaler Action-Exit | **geschlossen auf Codeebene** |
| FIX03 Backend-Verhaltenstests | Tests erstellt; Docker-Nutzungslimit verhindert Ausführung | **BLOCKED** |
| Post-Fix BC-28.3-CAT | kein Sandboxzugriff in diesem Lauf | **BLOCKED** |

Keine Alembic-Migration. Vor Pilot-GO sind Backendtests und beide CATs zwingend nachzuholen.

## Status-Delta GL-PILOT-01-FIX04 (21. Juli 2026)

| Gap | Evidenz | Status |
|---|---|---|
| Lease rotiert während legitimem BC-Scan | gültige Lease ist autoritativ; 4h Lease/Stale, 6h Hard Runtime | **geschlossen auf Codeebene** |
| erster Statuswechsel invalidiert Start-Identität | Worker/Lease bereits beim akzeptierten Start gebunden; GUIDs kanonisiert; Token-Hash und Worker vor/nach Update 1 identisch | **geschlossen automatisiert** |
| unstrukturierte Lease-Konflikte | vier stabile Codes, DE-/EN-Mapping | **geschlossen automatisiert** |
| Tenantwechsel über Statuspfad | Besitzprüfung vor jeder Mutation, Negativtest mit gültigem fremdem Token | **geschlossen automatisiert** |
| wiederholte Statuscalls nach Lease-409 | terminaler Syncstatus stoppt weitere Calls | **geschlossen auf AL-Codeebene** |
| Completed im Monitor, Failed in Historie | lokaler Status und Backend-Sync-Status getrennt | **geschlossen auf AL-Codeebene** |
| autoritative Pilot-DB-Untersuchung | lokale DB ist Revision 0021 und enthält den Run nicht | **BLOCKED** |
| Post-Fix BC-28.3-CAT | neuer Run, vollständiger Sync und Dashboardöffnung erforderlich | **BLOCKED** |

Keine Alembic-Migration. Extension-Upgrade auf 1.0.2.10 erforderlich. Automatisierte Regression: 298 PASS, 7 SKIP, 0 FAIL. Pilot bleibt **NO-GO** bis der reale CAT PASS ist.
