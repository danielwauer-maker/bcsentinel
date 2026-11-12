# AI-PM 2.1 — Sicherheits-, Restore- und DEV-Abnahmeplan

**Status: CI-tested / operator gates pending.** Diese Datei ist ein manueller, nichtdestruktiver Abnahmeplan; sie löst keine Deployments, GitHub-Merges, SaaS-Produktfreigaben oder Agentenstarts aus.

## Geltungsbereich und ausdrücklich nicht enthalten

- Nur das **standalone AI Control Center** und dessen separaten synchronisierenden Beobachter `ai-pm-sync`.
- Die BCSentinel-Anwendungsumgebungen `main/PROD`, `staging/DEV`, die BC-Extension sowie Stripe/Fiverr bleiben unverändert und außerhalb einer möglichen Kontrollcenter-Freigabe.
- Es gibt **keinen** ausführenden KI-/Codex-Agenten, keine echten Anbieterkostenmessungen und keine Laufzeitstatus-Provenienz. Acht Team-Rollen sind Konfiguration, nicht acht aktive Prozesse.
- Browser-Dashboard nutzt ausschließlich vorhandenes **Basic Auth hinter Loopback-Port und SSH-Tunnel**. Es ist keine öffentliche Multiuser-Anwendung. Keine neuen HTTP-Schreib-Endpunkte.
- Ein bestandenes CI-Unit-Test-Ergebnis ist **kein Live-Server-GO**, keine unabhängige BC27-Abnahme und kein Fiverr-Go-Live.

## Reproduzierbare CI-Evidence (ohne Produktionszugriff)

| Prüffeld | Technisches Verfahren | Erwartung |
| --- | --- | --- |
| Zwei SQLite-Backups | `test_backup_verify.py`: online Backup, Verifikation, Temp-Restore | 85 Aufgaben / 61 Fiverr / 24 SaaS, wiederhergestellte CLI-Daten, Integrität |
| WAL-Transaktionen | SQLite-WAL-Commit beim Backup | Committete Audit-Ereignisse im konsistenten Snapshot |
| Defekte Backups | Beschädigte/fehlende Quelle | Fail closed, Restore verweigert |
| Kein Überschreiben | `--confirm` nötig, Zielverzeichnis darf nicht existieren | Kein unbeabsichtigtes Datenüberschreiben |
| Login aller Seiten | `test_http_security.py`: echter lokaler HTTP-Testserver | 401 ohne Auth auf Dashboard, Team, CSS und API |
| Getrennte Rechte | POST/PUT/PATCH/DELETE und versteckte Dateipfade | Keine Mutation; unerlaubte GET-Routen 404 |
| Sicherheitsheader | Referrer-Policy, CSP, X-Frame-Options, nosniff, no-store | Auf Erfolg und Fehlern |
| Browser-Qualität | `test_light_theme.py`, Node-Syntaxprüfung | Beide Seiten, ausgewählte WCAG-AA-Farbpaare |
| Agenten-Budget | `test_agent_control.py` | Standard 0 Cent; Kostenlimit, zwei getrennte Operatornamen |
| Maximal eine Reservierung | Parallele lokale CLI-Versuche | Nur ein `claimed` und kein Agentenstart |
| Erkenntnisgrenzen | `test_team_roster.py` / `test_ai_pm_brief.py` | Keine erfundenen Ausführungen, Termine oder Freigaben |
| Compose-Isolation | Static contract checks | Kein Docker-Socket, kein Host-Netz, kein privileged, read-only rootfs |
| GitHub-Matching | Bestehende `pm_sync`-Tests | PR-Beobachtung löst kein Go-Live-Gate aus |

## Vor jedem Eingriff auf Hetzner

1. Verwende ausschließlich `~/bcsentinel-ai-control-center/repo` auf Branch `feature/ai-control-center-mvp`. Die gemeldete GitHub-CI-SHA und der lokal ausgecheckte SHA müssen identisch sein.
2. Halte `.env`, den Master-Tracker, das lokale `127.0.0.1:8092:8090`-Override und das bestehende `state/`-Volume unverändert. Vor dem Update die **alten** beiden SQLite-Datenbanken sichern; nicht die SQLite-Quelldateien bei laufenden Verbindungen per `cp` kopieren.
3. Stelle sicher, dass es **kein öffentliches Binding** an `0.0.0.0:8092` oder `:::8092` gibt; nur dein lokaler SSH-Tunnel `ssh -N -L 8092:127.0.0.1:8092 daniel@116.203.250.245` darf das Browserfenster öffnen. Keine öffentlichen Domain-Routen auf Dashboard/API.
4. Nimm **nur** den Control-Center-Dashboardcontainer im separaten Compose-Projekt neu in Betrieb; Poller `ai-pm-sync` und alle Produktcontainer unberührt. PR weiterhin Draft.

## Live-Betreibertest 1: Online-Backup beider Datenbanken

`backup_verify.py` gehört zum 2.1-Branch und verwendet nur die Python-Standardbibliothek. Auf dem **Host** (nicht im laufenden Container, damit die Sicherung nicht im 16-MB-tmpfs liegt):

```bash
set -euo pipefail
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
umask 077
mkdir -p "$HOME/bcsentinel-ai-control-center/backups"
stamp="$(date -u +%Y%m%d-%H%M%S)"
dest="$HOME/bcsentinel-ai-control-center/backups/ai-pm21-$stamp"

python3 backup_verify.py backup --source-dir ./state \
  --backup-dir "$dest" --confirm

python3 backup_verify.py verify --backup-dir "$dest"
```

Erwartet: `RESTORE_TEST_PASS`, beide Datenbanken `verified`, 85 Aufgaben, Tracker-SHA vorhanden, Agenten-Steuerdaten konsistent. Die Verifikation stellt Dateien **nur in einem temporären Verzeichnis** wieder her, niemals in das Live-`state/`. Backups erhalten private Verzeichnis- und Dateiberechtigungen (0700/0600). Zusätzlich eine **verschlüsselte Kopie außerhalb des VPS** und einen dokumentierten, getrennten Restore-Prozess einrichten. **Weder die Datei `dest` löschen noch den Originalzustand überschreiben.**

**Begrenzung:** Die Restore-Daten werden semantisch und mit `integrity_check` geprüft; dieses Werkzeug beweist keine anbieterübergreifende Recovery Time, Ausfalltests, Offsite-Retention oder Wiederherstellung eines kompletten Containers.

## Live-Betreibertest 2: sichere Runtime (nur lesende Abfragen)

Auf dem Server im Compose-Verzeichnis:

```bash
docker compose -f compose.example.yml ps
docker compose -f compose.example.yml config --quiet
docker inspect "$(docker compose -f compose.example.yml ps -q ai-control-center)" \
  --format 'Privileged={{.HostConfig.Privileged}} ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} Network={{.HostConfig.NetworkMode}}'
ss -lnt | grep ':8092'
```

Erwartet: `Privileged=false`, `ReadonlyRootfs=true` und für den privaten Dashboard-Zugang nur `127.0.0.1:8092`. Exakt diese Eigenschaften am **laufenden Container** nachprüfen; Compose-Datei allein reicht nicht.

Vom VPS ohne Auth:

```bash
for route in index.html team.html light-theme.css api/snapshot; do
  status="$(curl -sS -o /dev/null -w '%{http_code}' "http://127.0.0.1:8092/$route")"
  printf '%-22s %s\n' "$route" "$status"
  test "$status" = 401
done
```

Mit bestehender Anmeldung über deinen SSH-Tunnel den Browser prüfen. **Kein** Passwort, Github-Token oder Cookie im öffentlichen Prüfprotokoll protokollieren. Erneut Snapshot prüfen: `project_store.tasks=85`, `agent_queue.execution=disabled`, `team.active_agents=0`, globale Produktfreigabe `NO_GO`, keine neu genehmigten Projekt-Gates.

## Live-Betreibertest 3: Isolation und keine unbeabsichtigten Mutationen

- Prüfe mit `docker compose ps` und `docker inspect`, dass weder BCSentinel-DEV-/PROD-Container noch Netzwerk-/Volume-Mounts der Produktdatenbanken zum Control Center gehören.
- `ai-pm-sync` darf nur PR-Metadaten mit lokalen Beobachtungsprotokollen synchronisieren, aber keine `approval`-Gates setzen. GitHub-Token-Berechtigungen separat in GitHub prüfen: **read-only**, keine Workflow-/Contents-Schreibrechte.
- Kontrolliere vor/nach passiver Dashboardnutzung Projektfreigaben, Agentenbudget, `claimed`-Slots und Aufgabenanzahl. Es darf durch bloßes Öffnen oder Aktualisieren nichts freigegeben werden.
- Prüfe, dass die Produktionsseite `bcsentinel.com` und produktive BC-Daten NICHT zur Dashboard-Route weitergeleitet werden.

## Zusätzliche Betreiber-Evidence (12.11.2026)

Vom Betreiber am Hetzner-Server bereits nachgewiesen:
- Wiederherstellung beider echten SQLite-Backups: `RESTORE_TEST_PASS`, 61 Fiverr + 24 SaaS-Aufgaben, 0 formelle Projektfreigaben, Agentenbudget 0 Cent, 0 Jobs, 0 claimed Slots.
- Dashboard und Poller: unprivileged, read-only root, ohne Container-Neustarts; `/data` nur lesbar, `/state` beschreibbar; Dashboardbindung `127.0.0.1:8092`.
- HTTP GET ohne Login liefert auf Dashboard, Team, CSS und API jeweils `401`; Header enthalten CSP, `no-store`, `nosniff`, `DENY`, `Referrer-Policy` und `Permissions-Policy`.
- Fine-Grained-GitHub-PAT-Berechtigungen vom Betreiber auf notwendige Read-only-Rechte reduziert; `Workflows` (nur Read-and-write verfügbar) entfernt; Repositoryauswahl auf beide BCSentinel-Repos beschränkt. Authentifizierter Dashboard-GitHub-GET und Poller nach Änderung funktionsfähig: `loaded`, `errors=[]`, Poller zuletzt `2026-11-12T10:58:01+00:00` mit 171 PR-Einträgen, 9 Matches.
- Docker-Netzmitgliedschaften des Control Centers separat von DEV und PROD bestätigt.

Noch offen:
- **Echter verschlüsselter Offsite-Upload und isolierter Restore von einem externen Standort:** nur lokale Wiederherstellung bestanden; eine operationelle Restic-Lösung wurde in `offsite_backup.sh` vorbereitet, aber **nicht** aktiviert oder ausgeführt. Details: [AI_PM21_OFFSITE_NETWORK.md](AI_PM21_OFFSITE_NETWORK.md).
- **Host-Netzwerk-/Egress-Restrisiko:** getrennte Docker-Netze sind nachgewiesen, vollständige Host-Firewall- und Routing-Sperren dagegen nicht; siehe dieselbe Risk-Matrix.

**Entscheidung:** `AI_PM21_CODE_CI_PASS + HOST_CORE_PASS / FINAL_GATES_PENDING`. Keine globale BCSentinel-Produkt-/Fiverr-Freigabe, kein Merge und keine Agentenaktivierung.

## Ergebnis- und Freigabematrix

| Gate | CI-Ergebnis | Operator-Evidence erforderlich |
| --- | --- | --- |
| Python/JS/Lighttheme | GitHub Actions nach letztem Commit | Browser Desktop & Mobil bestätigen |
| HTTP-Auth und CSP | Lokaler CI-Server | 401 live, Laufzeitheader und lokale Bindings |
| SQLite-Restore | Isolierter CI-Restore | **Echte Kopien der beiden Hostdatenbanken**, Wiederherstellungsnachweis |
| Rechte/Isolation | Compose-Vertragsprüfung | Docker-Inspect + SSH-Firewall + Token-Scopes |
| Agentensteuerung | Budget-/Concurrency-Unit-Tests | 0-Cent-Limit, keine ausführbaren Jobs/Provider |
| Projektgates | Code trennt Status und Evidence | 0 unautorisierte Approvals, global `NO_GO` |

**Abnahmeentscheidung:** Bis die Betreiberbelege zu jedem Live-Gate vorliegen, bleibt AI-PM 2.1 `CI_PASS / OPERATOR_ACCEPTANCE_PENDING`. Selbst dann betrifft eine technische Control-Center-Abnahme **nicht** die Fiverr-/BCSentinel-Produktfreigabe. Reale LLM-Agentenausführung ist als getrenntes, explizit genehmigungspflichtiges Vorhaben einzustufen.

## Rollback

Wenn das neue Dashboard nicht startet, **nicht** die Live-Datenbanken überschreiben. Prüfe zuerst Container-Logs und sichere den aktuellen Datenzustand zusätzlich. Stelle lediglich den vorherigen Dashboard-Code/Docker-Image-Stand wieder her, ohne `git reset --hard`, ohne Datenbanken zurückzukopieren, ohne `docker compose down -v`. Ein produktiver Restore ist ein gesonderter, dokumentierter Notfallvorgang mit Freigabe und Betreiberaufsicht.
