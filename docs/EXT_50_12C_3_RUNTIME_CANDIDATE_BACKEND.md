# EXT-50-12C.3-RUNTIME-01 — isolierter PR41-Candidate

## Ausführungsstatus am 19.09.2026

**DEPLOYMENT_SCRIPT_READY; SERVER_DEPLOYMENT_NOT_EXECUTED.**
Der read-only SSH-Test `daniel@bcsentinel-main` scheiterte an der Namensauflösung.
Es wurde kein Server-Checkout erstellt, kein Container gestartet und keine Datenbank
migriert. Server-Ressourcen, Ports und Proxy-Konfiguration sind hier nicht verifiziert.
Die folgende Vorbereitung ist ausdrücklich kein Deployment-Nachweis und keine
Freigabe für einen BC-SaaS-Test.

Remote PR41 stand vor diesen drei Operationsdateien exakt auf
`f483d78bf8bc9d00d0f6fd61a8247a05e3f955fb`, Basis PR40 `f312eaf`.
PR38 `89faeb7`, PR39 `00b7b4e`, PR40 und origin/staging `867b1f7` wurden nur gelesen.
Produkt-, Backend-, Migrations- und AL-Dateien werden in diesem Schritt nicht geändert.
Der Candidate baut weiterhin exakt **f483d78**, auch wenn der Repair-Branch danach
die drei neuen Deployment-/Test-/Dokumentationsdateien enthält. Andere Abweichungen
des Remote-Branches führen zum Abbruch; es wird nichts gemerged oder gepullt.

## Repository-Audit

- `docker-compose.dev.yml` enthält feste Namen `dhm-dev-backend`,
  `dhm-dev-postgres`, Port 8001 und `.env.dev`.
- `docker-compose.prod.yml` enthält feste DHM-Namen, Port 8000 und `.env.prod`.
  Beide werden **nicht** zum Start des Candidate verwendet.
- Wiederverwendet wird ausschließlich `backend/Dockerfile`, Target `production`,
  am gepinnten Produktcommit. Darin sind Uvicorn, Anwendung, Alembic, Übersetzungen
  und Chromium enthalten. Kein zusätzlicher Worker ist für diesen Test erforderlich.
- Startup wartet auf die DB und prüft den Alembic-Stand; es migriert nicht selbst.
  `/health/ready` führt `SELECT 1` aus. `/health` ist der reine API-Status.
- Pflichtkonfiguration: `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`,
  `DATABASE_URL`. Candidate erhält eigene Zufallswerte und einen Invite-Code.
- `ENV=dev`, `APP_ENV=dev`, Basis-URL und CORS zunächst ausschließlich Loopback.
  Es werden keine Sicherheitsregeln oder Produkt-Entitlements geändert.
- `/tenant/register` und `/scan/sync` erlauben einen synthetischen Free-Scan mit
  normaler Invite-/Token-Authentifizierung. SMTP und Stripe bleiben unkonfiguriert.
  Die erwartete fehlende Einladungsmail wird explizit geprüft; es wird keine Mail gesendet.
- Alembic: `0028_exception_count -> 0029_finding_identity`, ein einzelner Head.
  Die neue Identität ist `scan_issues.finding_id`, VARCHAR(128), NOT NULL;
  Unique Constraint/Index `(scan_id, finding_id)` ersetzt `(scan_id, code)`.

## Ein Befehl auf dem Server

Als **daniel** auf **bcsentinel-main**, ohne sudo ausführen. Voraussetzungen:
Python >=3.10, Bash, Git, `ss`, GitHub CLI mit vorhandenem Repository-Lesezugriff,
lokaler Linux-Docker-Zugriff und Docker Compose >=2.20. Fehlende Voraussetzungen
werden nicht automatisch installiert. Es werden keine bestehenden Credentials kopiert.

Der Download wird vor Ausführung per SHA256 geprüft. Bei später verändertem Skript
bricht der Befehl ab, statt ungeprüften neuen Code auszuführen.

```bash
bash -c 'set -euo pipefail; umask 077; t=$(mktemp); gh api "repos/danielwauer-maker/bcsentinel/contents/scripts/deploy_pr41_candidate.py?ref=sprint/ext-50-12c-3-lossless-findings" --jq .content | base64 --decode > "$t"; printf "%s  %s\n" "5753fae7bf85fd76ed8d7ef25e3f80b07ec8e8f45fa2d09c601432c2b38b64d7" "$t" | sha256sum --check --status; python3 "$t"'
```

Kein `sudo`, kein `git pull`, kein bestehendes Compose-Projekt verwenden.
Die temporäre Skriptdatei enthält keine Secrets. Das Skript selbst ist
`scripts/deploy_pr41_candidate.py`.

## Zielressourcen und Isolation

| Gegenstand | Festgelegter Candidate-Wert; erst nach erfolgreichem Serverlauf belegt |
|---|---|
| Checkout | `~/bcsentinel-pr41`, Branch `sprint/ext-50-12c-3-lossless-findings`, HEAD f483d78 |
| Compose-Projekt | `bcsentinel-pr41` |
| Konfiguration | `.candidate/docker-compose.pr41-candidate.yml` im neuen Checkout |
| Backend | `bcs-pr41-backend`, nur `127.0.0.1:8004 -> 8000` |
| PostgreSQL | `bcs-pr41-postgres`, eigener PostgreSQL-15-Container, kein Hostport |
| Einmalmigration | `bcs-pr41-migrate`, bleibt nach Erfolg beendet als Nachweis erhalten |
| DB / Benutzer | `bcs_pr41_candidate` / `bcs_pr41_user` |
| Datenvolume | `bcsentinel-pr41_postgres_data` |
| Netzwerk | `bcsentinel-pr41_network` |
| Backend-Image-Tag | `bcsentinel-backend:pr41-f483d78`; vorhandener Tag führt zum Abbruch |
| Tatsächliche Image-Nutzung | Nach Build per unveränderlicher lokaler Image-ID in Compose gepinnt |
| Secrets | `.env.pr41-candidate`, `.env.pr41-candidate-db`; gitignored, neu erzeugt, Modus 0600 |

Der neue Checkout und Nachweise sind privat (umask 077). Es gibt keine Bind-Mounts
des Backends. Nur PostgreSQL mountet das neu erstellte eigene Volume. Netzwerk und
Volume sind in Compose ausdrücklich `external`, werden vom Skript zuvor selbst
mit Projekt-/Source-Labels neu angelegt und anhand ihrer Identität kontrolliert.
Sie sind weder ein Verweis auf einen alten Stack noch eine Erlaubnis zur Adoption.

Vor jeder mutierenden Operation prüft das Skript den erhaltenen Ausgangsbestand
und die Identität/Labels seiner bereits angelegten Ressourcen. Port 8004 muss vor
Beginn und vor Containerstart frei sein; sonst Abbruch. Es gibt keinen automatischen
Ausweichport. Docker-/Compose-Overrides sowie entfernte Docker-Daemons werden abgelehnt.
Ein Prozess-Lock verhindert parallele Aufrufe dieses Skripts.

Bereits vorhandener Checkout ohne Abschlussnachweis, Candidate-Namen, Volume,
Netzwerk oder Image-Tag führen zum Abbruch. Teilweise fehlgeschlagene Läufe werden
nicht automatisch repariert, ersetzt oder bereinigt. Ein vollständiger Wiederaufruf
prüft nur lesend: kein neuer Smoke-Scan, keine Migration, kein Recreate, keine Rotation.

## BEFORE / AFTER und Provenance

`before.json` und `after.json` unter `.candidate/` enthalten alle vorherigen Container
mit IDs, Image-IDs/-Namen, Status, Startzeit, Restart-Zähler, Bindings und Mounts sowie
Volumes, Netzwerke und TCP-Listener. Environment-Inhalte werden nicht ausgegeben;
potenziell sensitive Driver-Optionen werden nur als Hash verglichen.

Jede Änderung oder Entfernung einer vorhandenen Ressource bzw. eines vorhandenen
Listeners stoppt den Lauf. Vor Start müssen die vier erwarteten DHM-Container laufen
und die bekannten Backend-Bindings 127.0.0.1:8000/8001 stimmen. Abweichungen brauchen
zuerst eine manuelle Bestandsprüfung. Das Skript stoppt auch bei unabhängigen
gleichzeitigen Änderungen; es beansprucht keine atomare Kontrolle über andere Betreiber.

`complete.json` wird ausschließlich nach allen erfolgreichen Gates neu geschrieben.
Es enthält Repository, Branch, SHA, Server, IDs, Startzeiten, Image-ID/ggf. RepoDigest,
DB, Volume, Binding, Migrationsstand, Smoke-Ergebnisse, Logklassifikation und den
BEFORE/AFTER-Status. Lokal gebaute Images können keinen Registry-RepoDigest haben;
die lokale sha256-Image-ID wird trotzdem eindeutig aufgezeichnet. Keine Tokens oder
Passwörter werden in diese Nachweise aufgenommen.

## Migration, Health und Smoke

1. Unveränderten Produktstand bauen; erst danach neue Secrets erzeugen.
2. Eigenes Volume/Netzwerk und PostgreSQL starten; `pg_isready`-Health prüfen.
3. Nur in der identifizierten Candidate-DB lesend prüfen, dass `public` leer ist.
4. Alembic-Chain prüfen, regulär `upgrade head` ausführen. Kein Stamp, kein
   manuelles Schema-SQL und kein Kaschieren eines Migrationsfehlers.
5. Backend starten; Container-Health und HTTP 200 auf `/health/ready` prüfen.
6. `alembic current`, `alembic heads`, DB-Name, Revision, Spaltentyp/NOT NULL,
   neuen Unique Constraint/Index und Wegfall des alten Constraints prüfen.
7. Über reguläre API eine **synthetische**, nicht mit BC verbundene Testregistrierung
   erzeugen. Zwei Gruppen derselben Check-ID mit Counts 2/3 synchronisieren.
   Erwartet: zwei gespeicherte Identitäten, fünf Prüftreffer und 72/108 EUR Impact
   für `CUSTOMERS_DUPLICATE_EMAIL` bei unveränderten Standardparametern.
8. Reihenfolge umdrehen, denselben Scan erneut senden; zwei Zeilen, gleiche DB-IDs,
   Counts und Impacts prüfen. DB-Abgleich verwendet ausschließlich SELECT.
9. Candidate-Logs auf Fehler prüfen; unbekannte Warnungen stoppen den Lauf.
   PostgreSQL-initdb-Hinweis zu lokalem Socket-Trust wird getrennt klassifiziert.
   Fehlende SMTP-Konfiguration ist im synthetischen Registrierungsergebnis erwartet.
10. Bestandsvergleich und Abschlussnachweis schreiben. Keine Testdaten bereinigen.

Die synthetische Registrierung verbraucht nur ihren eigenen Free-Scan. Sie ist keine
BC-SaaS-Registrierung und greift weder BCS-PERF-DEV noch BCS-FINDING-QA an.
Die vorhandene pytest-DB-Fixture mit `drop_all/create_all` wird ausdrücklich **nicht**
gegen diese Candidate-DB ausgeführt. Auth-, Lizenz- und Validierungsregeln bleiben aktiv.

## Prüfungen dieser Vorbereitung

- **39 PASS / 0 FAIL / 0 SKIP / 0 XFAIL**: neue Deployment-Safety-/API-Smoke-Tests
  sowie bestehende Finding-Identity- und Deployment-Readiness-Regressionen.
  Zwei bestehende python-jose-Datetime-DeprecationWarnings; kein neuer Produktfehler.
- Darin 19 neue Prüfungen: Ressourcenkollisionen, gelöschte/ersetzte Bestandsressourcen,
  verlorener Listener, fremde Ownership vor Mutation, Teilcheckout, belegter Port,
  Compose-Isolation, Secret-Redaktion, echter API-Smoke und eingebettete Python-Skripte.
- Docker Compose CLI: tatsächliches JSON/YAML-Rendering und isolierte Bindings geprüft,
  ohne Container zu starten. Ergebnis PASS.
- Nachweise lokal: `.build/candidate-regression-final.xml`,
  `.build/candidate-compose-check/`. API-Test hier nutzt die normale isolierte lokale
  Testsuite; er ersetzt weder PostgreSQL- noch Server-Runtime-Evidence.
- Pinned f483d78: [BC-CI](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35315763714)
  Fresh/Upgrade SUCCESS. [Backend-CI](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35315763713)
  518 PASS / 1 unveränderter Billing-Baseline-FAIL / 8 SKIP / 2 XFAIL;
  separate Migrationsprüfung 2 PASS und PostgreSQL-Gate 23 PASS.
- **NICHT AUSGEFÜHRT:** Linux-Server-Deployment, dortige Docker-Builds, Migration,
  HTTP-Smoke, BEFORE/AFTER-Abgleich und öffentliche HTTPS-Erreichbarkeit.

## HTTPS-Stop-Gate und nächster BC-Schritt

Die bestehenden Deployment-Workflows referenzieren `api.bcsentinel.com` (8000) und
`dev-api.bcsentinel.com` (8001). Das belegt keine freie Candidate-Route. Diese
Endpunkte werden nicht übernommen oder umkonfiguriert. Das Skript listet auf dem
Server lediglich lesbare Proxy-Konfigurations-Dateinamen; es liest keine TLS-Secrets
und verändert weder Reverse Proxy, Firewall, DNS noch TLS.

Nach erfolgreichem Serverlauf ist maximal **READY_FOR_SECURE_BC_SAAS_EXPOSURE**
zulässig. Zuerst `complete.json`, `before.json` und `after.json` ohne Env-Dateien
zur Prüfung bereitstellen. Anschließend eine ausdrücklich freigegebene separate
HTTPS-Candidate-Route mit dem Betreiber festlegen. Dabei Candidate-Basis-URL/CORS
und produktgerechte HTTPS-Einstellungen prüfen; Loopback-DEV-Konfiguration darf
nicht ungeprüft öffentlich geschaltet werden. Kein Hostname wird hier erfunden.

Erst nach real verifizierter HTTPS-Erreichbarkeit ist
`READY_FOR_BC_SAAS_RUNTIME_RETEST` zulässig. BC-App-Installation, echte Registrierung
und Scan erfolgen in einem separaten Schritt. LARGE bleibt blockiert.

## Späterer Teardown — jetzt nicht ausführen

Zuerst Evidence sichern und anhand `complete.json` aktuelle Container-IDs,
Compose-Project-/Source-Labels sowie die unveränderte generierte Compose-Datei
prüfen. Bei Abweichungen stoppen. Dann ausschließlich den Candidate entfernen:

```bash
docker compose --project-directory "$HOME/bcsentinel-pr41" -p bcsentinel-pr41 --env-file "$HOME/bcsentinel-pr41/.env.pr41-candidate" -f "$HOME/bcsentinel-pr41/.candidate/docker-compose.pr41-candidate.yml" --profile tools down
```

Kein `-v`, kein `--remove-orphans`, kein globales prune. Das explizit externe
Candidate-Volume und -Netzwerk bleiben erhalten, ebenso alle bisherigen DHM-Ressourcen.
Die Datenbank bleibt so für Evidence erhalten. Auch Image, Checkout und Secrets
werden nicht automatisch gelöscht. Nach Teardown wird das Deployment-Skript den
alten Bestand nicht automatisch wiederverwenden; erneute Freigabe/Prüfung erforderlich.