# AI-PM 2.1 – Offsite-Backup und Netzwerk-Restrisiken

**Einordnung:** Vorbereitung/Automatisierung **im Draft-PR**, aber keine echte externe Sicherung wurde ausgeführt und keine Firewall geändert. Die Wiederherstellung der beiden lokal gesicherten echten Hetzner-DBs wurde bereits bestätigt (`RESTORE_TEST_PASS`).

## Offsite-Ziel und Kosten

Wir empfehlen einen **eigenen, verschlüsselten restic-Backup-Repository-Speicher außerhalb desselben Hetzner-VPS und außerhalb dessen Backup-/Snapshot-Fehlerdomäne** (z. B. anderer Anbieter mit S3-kompatiblem Bucket oder ein vertrauenswürdiges, separates SFTP-Ziel). Ein zweiter Ordner auf demselben VPS ist **kein** Offsite-Backup. Ein weiterer Storage-Dienst kann unabhängig von KI-API-Nutzung Kosten verursachen. Keine Anbietergebühren ohne Benutzerentscheidung festlegen.

Restic verschlüsselt die gesicherten Inhalte clientseitig; Repository-Namen, Zugriffsmetadaten und Traffic-Informationen sind nicht vollständig geheim. Starke zufällige Repository-Passphrase **außerhalb** des Backups sicher verwahren. Backups sollten mit separaten, nur für das Ziel gültigen Zugriffsrechten erfolgen und gegen versehentliches Löschen durch Aufbewahrungsregeln / Object Lock geschützt werden, soweit die gewählte Gegenstelle dies erlaubt. Ein Angreifer mit vollen Schreib- und Löschrechten zum Repository kann trotz Verschlüsselung Snapshots entfernen.

## Bedienung (manuell, absichtlich kein Zeitplan)

Erst nach Auswahl des externen Ziels, Einrichtung der separat beschränkten Transport-Zugangsdaten und `restic` auf dem **Host**:

1. Ziel auf einem anderen System einrichten, Restic separat initialisieren (`restic init` nur nach dokumentierter Auswahl / explizitem Operatorauftrag) und wiederherstellbare Zugangsdaten getrennt vom VPS sichern.
2. Repository-Passwort unter einem privaten Pfad **außerhalb von Git und `state/`**, Eigentümer root und `0600` oder `0400`. Keinen Passwortinhalt im Chat/CI/Terminalprotokoll anzeigen oder in Docker-Umgebungsvariablen schreiben.
3. Root-Umgebung für `RESTIC_REPOSITORY`, `RESTIC_PASSWORD_FILE` und transportabhängige Credential-Variablen durch eine **root-only lokale Konfiguration außerhalb des Repos** bereitstellen. Bei `sudo` die tatsächliche Environment-Weitergabe prüfen. Keine Credentials in `.env` des Control Centers hinzufügen.
4. `offsite_backup.sh` kontrolliert explizit: Root, kein lokales Repository, Passwortdatei root-only 0600/0400, bereits initialisiertes Fern-Repository, vollständige zwei SQLite-Online-Backups, isolierter SQLite-Restore, Restic-Verschlüsselung und Upload, **Restore aus dem Fern-Repository**, erneute SQLite-Verifikation, Restic `check --read-data-subset=1/10`. Erfolgsmarker ist nur `OFFSITE_BACKUP_AND_RESTORE_PASS`.
5. Der Ziel-Repository muss **exklusiv für das AI Control Center** verwendet werden. Restic `restore latest` darf nicht versehentlich den neuesten Snapshot einer fremden Anwendung abrufen.
6. `offsite_backup.sh` läuft nur bei explizitem Operatorstart, hat kein `cron`, keine `systemd`-Timer-Installation, kein `prune`, kein `forget`, kein Credential-Renewal und keine Produktionsänderung.

Beispiel **ohne echte Zugangsdaten**:

```bash
# Referenz; nicht ohne eingerichtetes externes Repository starten.
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
sudo -E bash ./offsite_backup.sh
# Bei fertiger Konfiguration: OFFSITE_BACKUP_AND_RESTORE_PASS
```

Wenn die lokale Repository-Passphrase verloren geht, ist die verschlüsselte Sicherung nicht entschlüsselbar. Deshalb ist ein unabhängiges, geschütztes Secret-Recovery-Verfahren notwendig.

**Vor Automatisierung:** Erste erfolgreiche und protokollierte Offsite-Wiederherstellung; externe Rechte/Retention/immutable Schutz prüfen; erst anschließend tägliches Scheduling explizit freigeben. Empfohlene Startwerte: täglich, 14 tägliche + 8 wöchentliche + 12 monatliche Wiederherstellungspunkte. Diese Werte sind **nur Vorschläge**, noch keine aktivierte Löschstrategie.

## Netzwerkisolierung – Evidenz und Restrisiko

Erfolgreich am echten Hetzner-VPS geprüft:
- Die beiden AI-Control-Center-Container hängen ausschließlich an `ai-control-center_default`.
- DEV-Container hängen an `data-health-management-dev_default`, PROD-Container an `data-health-management_default`; keine gemeinsame Docker-Netzmitgliedschaft.
- Dashboard nur auf `127.0.0.1:8092` veröffentlicht, Auth-GET-401 und wichtige Sicherheitsheader geprüft.
- Keine privilegierten Containerrechte, Read-only-Root-Dateisysteme; `/data:ro`, `/state:rw`.

**Nicht nachgewiesen:**
- Docker-Bridge-Isolation unter Host-iptables/nftables-Policy inkl. Docker-FORWARD-Regeln, veröffentlichte Host-Ports und routbare Subnetze.
- Fehlende ungeplante Egress-Ziele (GitHub API und DEV-Health-Endpunkt sind **gewollt**, andere sollten eingeschränkt werden).
- Kein Zugriff vom Kontrollcenter auf andere Host-Dienste über das Host-Gateway oder veröffentlichte Reverse-Proxy-Domains.
- Least-privilege am Internet-Egress auf SNI/DNS-Ebene; reine IP-Limits für GitHub/CDN sind ohne Pflege fragil.

**Nur lesende nächste Prüfung auf Hetzner (keine persönlichen Daten/Token ausgeben):**

```bash
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
echo '===== Docker network names ====='
docker network inspect ai-control-center_default --format \
  'Name={{.Name}} Internal={{.Internal}}'
echo '===== Dashboard published ports ====='
docker port "$(docker compose -f compose.example.yml ps -q ai-control-center)"
echo '===== Produktnetze ====='
for net in data-health-management_default data-health-management-dev_default; do
  docker network inspect "$net" --format 'Name={{.Name}} Internal={{.Internal}}'
done
echo '===== Host public listening sockets (addresses only) ====='
sudo ss -lnt | sed -n '1,35p'
```

**Bewertung:** Docker-Netzwerkzuordnung ist **PASS**, eine **vollständige DEV/PROD-Netztrennung gegenüber Host-Routing und ausgehenden Verbindungen** noch nicht nachgewiesen. Vor hartem Egress-Blockieren müssen DNS, GitHub API, externe Login-Prozesse und die legitim konfigurierte DEV-Health-API berücksichtigt werden, damit das Control Center nicht ausfällt. Produkt-Akzeptanz und globales Go-Live bleiben NO_GO.

## Mindestabnahmeregel

Die finalen Operator-Gates werden erst geschlossen, wenn
- `OFFSITE_BACKUP_AND_RESTORE_PASS` anhand echter off-host Daten vorliegt,
- Remote-Rechte/Backup-Retention und Schlüsselwiederherstellung dokumentiert sind,
- die Docker-/Host-Netzpfade geprüft und Restrisiken ausdrücklich akzeptiert oder korrigiert wurden.

Die Abnahme betrifft nur das **standalone AI Control Center**. Alle Product-/Fiverr-Release-Gates bleiben unabhängig auf **NO_GO**.
