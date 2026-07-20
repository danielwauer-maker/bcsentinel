# GL-EXT-P0E – Sandbox Release Gate, PostgreSQL Staging & Upgrade Evidence

Stand: 20.07.2026  
Geprüfter Basis-Commit: `bb551199832b8c1a6b90dbff55911e968bfd4b47` (`staging`)  
Release Candidate: BCSentinel `1.0.2.7`, Arbeitsbaum mit P0E-Änderungen  
Entscheidung: **NO-GO**

## Executive Summary

P0E hat die zuvor fehlende PostgreSQL-Evidenz praktisch erbracht: PostgreSQL 15, zwei gleichzeitig laufende Backendinstanzen, Fresh- und Legacy-Migration, echte Parallelität, Instanzausfall, PostgreSQL-Restart und persistentes Volume wurden ausgeführt. P0A–P0D bestanden 105/105 gegen PostgreSQL. Ein Produktionsimage wurde reproduzierbar gebaut. Der AL-Releasebuild 1.0.2.7 sowie N-1 aus Commit `630d896` kompilierten.

Ein Business-Central-Sandboxmandant ist in der verfügbaren Umgebung jedoch nicht angebunden. Fresh Install, echtes N-1-Upgrade, Rollen ohne `SUPER`, Scheduler-Servicebenutzer und die P0A–P0D-CATs wurden daher nicht ausgeführt. Sie sind `BLOCKED`, nicht bestanden. Diese fehlende Evidenz verhindert auch bei geschlossenen funktionalen P0 ein Pilot-Gate.

## Testumgebungen und Versionen

| Bereich | Tatsächliche Umgebung | Ergebnis |
|---|---|---|
| Git | Branch `staging`, Basis `bb55119`; P0A–P0D committed | sauberer Ausgangsstand; P0E danach bewusst uncommitted |
| PostgreSQL | offizielles Image `postgres:15`, eigenes Volume und Port 55432 | ausgeführt |
| Docker | Desktop 4.80.0, Engine 29.6.1, Linux/WSL2, Compose 5.1.4 | ausgeführt |
| Backend | Python 3.11 Produktionsimage, zwei Prozesse auf 18080/18081 | ausgeführt |
| AL | Compiler 17.0.34.45391, Runtime 16.0, BC Application/Platform 27.0 | Compile/Analyzer ausgeführt |
| BC Sandbox | keine authentisierte Sandboxverbindung vorhanden | `BLOCKED` |
| Signierung | kein Code-Signing-Zertifikat/Key-Vault verfügbar | `BLOCKED` |

Testkonfiguration verwendete ausschließlich anonyme `.invalid`-Kontakte und nichtproduktive Test-Credentials. Keine produktiven Tokens oder Kundendaten wurden verwendet.

## PostgreSQL-Staging

- Fresh Upgrade von leerer Datenbank bis `0024_scan_lifecycle_recovery`: PASS.
- Upgrade von `0021_dashboard_users` über 0022, 0023 und 0024: PASS.
- Legacy-Fixture: je ein Tenant, Kauf, Credit, Scan, Finding und `running` Run vor und nach Upgrade erhalten.
- Legacy-Identity blieb `NULL`; es wurde keine Tenantbindung geraten.
- Credit blieb `available`, historischer Run blieb nachvollziehbar `running`.
- 105/105 P0A–P0D-Tests liefen gegen echte PostgreSQL-Sessions.
- Zwei Backendinstanzen meldeten gleichzeitig `/health/ready = 200`.
- Acht parallele identische Registrierungen über beide Instanzen erzeugten exakt einen Tenant und einen Portaluser.
- PostgreSQL-Stop blockierte beide Readiness-Prüfungen; nach Restart waren beide wieder 200 und der Tenant blieb im Volume erhalten.
- Die neue `docker-compose.p0e.yml` wurde tatsächlich mit Migration, PostgreSQL und `--scale backend=2` gestartet; beide Backends und PostgreSQL meldeten `healthy`.

PostgreSQL verwendet das Standard-Isolation-Level `READ COMMITTED`. Creditclaim und Recovery verwenden zusätzlich Row Locks, `SKIP LOCKED`, bedingte Updates, Unique Constraints und Lifecycle-CAS.

## Concurrency- und Restart-Ergebnisse

Die P0A–P0D-Suiten sowie `test_p0e_postgres_concurrency.py` decken identische/unterschiedliche Registrierung, identische und konkurrierende Assessment-/Validationstarts, Monitoring ohne Creditverbrauch, Workerclaim, parallele Recovery, Heartbeat-vs-Recovery, Late Writer, Access-Snapshot-Refresh und Tokenausgabe nach Ablauf ab.

Der neue parallele Snapshot-Test fand eine Race Condition in der erstmaligen Default-Preisinitialisierung. Zwei Instanzen konnten gleichzeitig denselben Primärschlüssel einfügen. Der Initializer verwendet nun transaktionslokale Savepoints und behandelt ausschließlich den konkurrierenden `IntegrityError` als idempotenten Replay. P0E plus Pricing-Regression bestanden danach 21/21 gegen PostgreSQL.

Failure Injection:

| Fall | Ergebnis |
|---|---|
| eine Backendinstanz stoppt | zweite Instanz blieb 200 |
| gestoppte Instanz startet neu | Readiness 200; identischer Register-Retry `existing` |
| PostgreSQL stoppt | beide Instanzen lieferten keinen positiven Readiness-Entscheid |
| PostgreSQL startet neu | beide Instanzen reconnecteten; persistente Daten vorhanden |
| Compose Up | Migration beendet erfolgreich; PostgreSQL und zwei Backends healthy |
| Worker/Recovery/Late Writer | P0C-PostgreSQL-Tests grün |
| Antwortverlust/Retry | gleiche Registrierung beziehungsweise gleiche Request-ID bleibt idempotent |

Ein Gesamtlauf wurde während der bewussten PostgreSQL-Failure-Injection bei 251 bestandenen Tests und vier Setup-Errors unterbrochen. Die acht betroffenen Registrierungstests bestanden unmittelbar nach Restart. Dieser Lauf wird nicht als grüner Gesamtlauf gezählt; der unbeeinflusste Abschlusslauf ist die maßgebliche Evidenz.

Maßgeblicher Abschlusslauf: **261/261 Tests bestanden**, 40 Deprecation-Warnungen, 601,46 Sekunden. Die Warnungen betreffen bestehende Starlette-`TemplateResponse`-Aufrufe und sind P2.

## BC Sandbox, Installation und N-1-Upgrade

Der aktuelle Quellstand enthält jetzt:

- `DH Install` für idempotente Setup-Initialisierung pro Company;
- `DH Upgrade` für Setup-Erhalt und sichere Invalidation aller nicht nachweisbar frischen Access-Snapshots;
- Version 1.0.2.7 als echtes Upgradeziel;
- N-1-Paketquelle aus Commit `630d896`, Version 1.0.2.6;
- `BCSENTINEL SCHEDULER` als eigenständige Extension-Rolle.

N-1 und aktuelles Paket kompilieren. Installation, Sync, Upgradeausführung, Dauer, Uninstall/Reinstall und Datenintegrität in Business Central sind mangels Sandbox `BLOCKED`. Es gibt weiterhin keine Uninstall-Codeunit; deshalb wird keine automatische lokale oder Backend-Datenlöschung behauptet.

## Rollen, Scheduler und CATs

Die Soll-/Quellcodematrix steht in `BC_EXTENSION_ROLE_PERMISSION_MATRIX.md`. Kein Lauf ohne `SUPER` konnte in BC durchgeführt werden. Insbesondere die zusätzlich benötigten Leserechte auf BC-Basistabellen für den Scanner müssen in der Ziel-Sandbox ermittelt und als Standardrolle dokumentiert werden. Die Schedulerrolle allein verleiht bewusst keinen pauschalen Zugriff auf Kundendaten.

Alle 47 vorbereiteten P0A–P0D-Sandbox-CATs sind weiterhin `BLOCKED`. CAT-Passrate: **0/47 ausgeführt**, nicht 0/47 fachlich fehlgeschlagen.

## Releasepaket und Signierung

- AL-Paket 1.0.2.7 wurde erzeugt.
- Produktions-Dockerimage `bcsentinel-p0e:1.0.2.7-bb55119-dirty` wurde aus aktuellem Backendcode gebaut und mit `/health/ready = 200` gestartet; die Kennzeichnung `dirty` ist Absicht, weil P0E noch nicht committed ist.
- Paket- und SHA-256-Erzeugung sind dokumentiert.
- Das Release ist nicht signiert.
- Ein final reproduzierbares Paket aus einem sauberen P0E-Commit darf erst nach Commit und erneutem Build benannt werden.

## AppSourceCop

| Befund | Wirkung | Priorität/Entscheidung |
|---|---|---|
| EULA fehlt | AppSource und Customer-Legal-Gate | P1, URL nicht erfinden |
| Logo fehlt | AppSource | P1 |
| `contextSensitiveHelpUrl` fehlt | AppSource | P1, finale Help-Struktur erforderlich |
| ID-Range 53100–53199 | AppSource | P1/AppSource; keine unüberlegte ID-Änderung |
| Application Insights fehlt | AppSource-Warnung/Operations | P1 |
| Privacy/Produkt/Help | vorhanden | URL-Inhalt vor Customer Go extern verifizieren |

Normales Compile sowie CodeCop/PTECop haben keine Fehler. AppSourceCop bleibt rot und wird nicht als Pilot-Runtime-Fehler klassifiziert, verhindert aber `APPSOURCE READY`.

## Localization, Pricing und Telemetrie

Pricing ist grün. Source of Truth ist `PRODUCT_PRICING_DEFAULTS` beziehungsweise der öffentliche Pricing-Endpunkt; statischer Fallback: Full Analysis 79 EUR, Validation 49 EUR, Monitoring 149 EUR/Monat und 1.490 EUR/Jahr. Generator und Checker wurden daran angeglichen.

Localization bleibt P1: der Checker meldet 82 Treffer (47 Umlaut-/Kommentarindikatoren und 35 deutsch lokalisierte Zeilen), darunter harte deutsche Texte, `LocalizeText`-Doppelpfade, Übersetzungskommentare und echte UI-Mischungen. Die Treffer wurden nicht pauschal unterdrückt. EN/DE-Sandbox-CAT bleibt erforderlich.

Backendevents decken Registrierung, Access, Scanstart/-lifecycle, Credit und Recovery weitgehend ab. Neu sind AL-Telemetrie für Installation und Upgrade. Explizite AL-Events für `access_cache_expired`, `protected_page_blocked`, Schedulerausfall und ein produktives Application-Insights-Ziel bleiben offen.

## Readiness-Neubewertung

| Kategorie | Gewicht | Score | Evidenz/Risiko |
|---|---:|---:|---|
| Security | 7 | 90 % | HTTPS/Fresh Access grün; Signing offen |
| Tenant Isolation | 6 | 90 % | PostgreSQL parallel grün; BC-CAT offen |
| Registration | 5 | 95 % | Mehrinstanz/idempotent grün |
| Licensing | 5 | 90 % | PostgreSQL-Regression grün |
| Billing/Credits | 5 | 90 % | Locks/Ledger grün |
| Scan Reliability | 8 | 88 % | Recovery/Restart grün; echter BC-Worker offen |
| Access Control | 7 | 90 % | P0D grün; BC-Runtime offen |
| BC Installation | 6 | 35 % | Install-Code vorhanden/Compile; Sandbox blockiert |
| BC Upgrade | 6 | 30 % | N-1/Target gebaut; Sandbox blockiert |
| Permissions | 5 | 45 % | statisch verbessert; Negativtests blockiert |
| Scheduler | 5 | 35 % | Rolle vorhanden; Serviceuser-CAT blockiert |
| PostgreSQL | 7 | 88 % | Migration/Parallelität/Restart real grün |
| Deployment | 4 | 65 % | Image/Health grün; Proxy/Backup/Signing offen |
| Observability | 3 | 55 % | Kernevents vorhanden; A.I./AL-Gaps offen |
| Localization | 4 | 45 % | Checker rot; Sandboxsprachen offen |
| Pricing | 3 | 100 % | Backend/Snapshot/Checker konsistent |
| AppSource | 4 | 25 % | vier Fehlerklassen plus Telemetriewarnung |
| Customer Acceptance | 6 | 20 % | CATs vorbereitet, nicht ausgeführt |
| Documentation | 2 | 90 % | P0A–P0E und Betriebsreports vorhanden |
| Rollback | 2 | 70 % | Verfahren dokumentiert; Restore-Drill offen |
| **Gesamt** | **100** | **67 %** | Gate überschreibt Prozentwert |

- Gesamtreadiness: **67 %**
- Pilot-Readiness: **58 %**
- Customer-Readiness: **47 %**
- AppSource-Readiness: **28 %**

## Offene Fehler und Restrestrisiken

- P1: BC-Sandbox Fresh Install und N-1-Upgrade.
- P1: negative Rollenmatrix und Scheduler ohne `SUPER`.
- P1: 47 P0A–P0D-CATs.
- P1: Localization-Gate.
- P1: Signierung, EULA, Logo, Help-URL, ID-Range und Application Insights.
- P1: produktive Reverse-Proxy-, Backup-/Restore- und Monitoring-Evidenz.
- P2: AL-Test-App, Telemetrievervollständigung und Analyzer-Warnungsabbau.
- P3: automatisierte Releaseprovenienz/SBOM und erweiterte Betriebsdashboards.

## Rollback

Vor Deployment PostgreSQL-Backup und exportierte Extension-/Company-Evidenz sichern. Backend und AL-Paket gemeinsam versionieren. Bei Fehlern zuerst Traffic stoppen, Backendimage zurückrollen und bei bereits ausgeführtem AL-Upgrade bevorzugt vorwärts korrigieren. Migration 0022–0024 nur mit geprüftem Backup downgraden. Access bleibt bei Versionsmismatch fail-closed. Bereits angelegte Backend-Tenants werden nicht automatisch gelöscht.

## Finale Entscheidung

**NO-GO.** Keine funktionalen P0 sind offen, aber die Freigabelogik erlaubt nicht einmal `CONDITIONAL PILOT GO`, solange Fresh Install, Upgrade, Rollen/Scheduler und zentrale CATs in einer echten BC-Sandbox nicht ausgeführt wurden.

Nächster Gate-Wechsel: P0E-Sandbox-Execution mit BC 27, DE/EN-Companies, vier Rollen ohne `SUPER`, Install 1.0.2.7, Upgrade 1.0.2.6→1.0.2.7, 47 CATs, Schedulerlauf, signiertem Paketkandidaten und dokumentierter Backup-/Rollbackprobe.
