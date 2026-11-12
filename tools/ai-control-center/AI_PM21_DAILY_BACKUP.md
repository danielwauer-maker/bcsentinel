# AI-PM 2.1 – Täglicher verschlüsselter OneDrive-Backupbetrieb

**Geltung:** Ausschließlich die zwei lokalen SQLite-Datenbanken des standalone AI Control Centers. Keine BCSentinel-DEV/PROD-Datenbanken, keine Extension-, GitHub- oder Fiverr-Freigaben.

## Bestätigte Ausgangsbasis (Betreiber, 12.11.2026)

- OneDrive-Remote `bcs-onedrive`, Rclone-Konfiguration `/etc/bcsentinel-ai-backup/rclone.conf` root:root 0600.
- Separates Restic-Passwort `/etc/bcsentinel-ai-backup/restic-password` root:root 0600; Passwort unabhängig vom Server im Passwortmanager sichern.
- Eigenes verschlüsseltes Repository `rclone:bcs-onedrive:BCSentinel-AI-Backups/restic-repository`, ID-Präfix `69b7e0fa`.
- Betreiber führte `offsite_backup.sh` manuell aus; Snapshot `4d9c5dd3` 12.11.2026 12:03:32 UTC. Zwei Datenbanken wurden aus OneDrive in ein isoliertes Temp-Verzeichnis zurückgeladen und durch Restic sowie SQLite verifiziert. Erfolg `OFFSITE_BACKUP_AND_RESTORE_PASS`.
- **Ein einmaliger Erfolg beweist keinen automatischen Betrieb.** Keine Timer-Aktivierung oder Retention wurde bisher gemeldet.

## Sicherheitsmodell für wiederkehrende Backups

- `scheduled_backup.sh` startet die bereits bewährte `offsite_backup.sh`. Diese sichert beide Live-SQLite-Dateien mit der SQLite-Online-Backup-API und prüft anschließend einen echten Remote-Restore.
- Der Installer kopiert die drei benötigten Skriptdateien nach `/usr/local/libexec/bcsentinel-ai-backup`, root-owned, anstatt einen Dienst aus einem durch `daniel` bearbeitbaren Git-Checkout als root auszuführen.
- Root-only Env-Datei (enthält **nur Pfade**, niemals Passwort oder OAuth-Token); Restic- und Rclone-Geheimnisse bleiben in separaten root-only Dateien.
- `systemd` startet einen `Type=oneshot`-Dienst maximal einmal gleichzeitig (`flock`) mit `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateTmp`; Schreibbereiche sind gezielt freigegeben, damit Rclone OAuth-Refresh und lokale Cache-Dateien funktionieren.
- Timer: 03:20 UTC täglich, zufällige Verzögerung bis 15 Minuten, `Persistent=true` (nach verpassten Runs kann bei Aktivierung *sofort* ein Nachhol-Lauf erfolgen).
- Erfolgreiche Läufe aktualisieren `/var/lib/bcsentinel-ai-backup/last-success`; Fehlschläge schreiben `last-failure` und lassen `last-success` unangetastet. Die Details stehen im Systemjournal. `backup_health.sh` meldet fehlgeschlagene/fehlende/zu alte Sicherungen (Standard 26 Stunden) per Exit-Code; das ist **noch keine externe Benachrichtigung**.
- **Keine automatische Restic-Retention/Löschung**: `forget`, `prune` oder Cloud-Aufräumen sind ausgeschlossen. 14 täglich, 8 wöchentlich, 12 monatlich bleiben ein Vorschlag für ein eigenes, später nachgewiesen sicheres Retention-Gate. OneDrive kann serverseitig gelöschte/ersetzte Dateien wiederherstellen, ist aber kein garantierter Immutable-Storage.

## 1. Config einmalig auf dem Host erstellen

Voraussetzung: Das geprüfte Branch-Skript-Set (mindestens `offsite_backup.sh`, `scheduled_backup.sh`, `install_backup_timer.sh`, `backup_health.sh`, `backup_verify.py`) liegt vor Ort. **Kein pauschales `git pull`**, da lokale Compose-Port-Overrides erhalten bleiben sollen.

Folgende Kommandozeilen gelten für den bestätigten Standardcheckout unter dem Benutzer `daniel`. Den `AI_PM_STATE_DIR`-Pfad unbedingt vor Aktivierung gegen die tatsächlich laufenden Datenbanken prüfen. **Bestehende `backup.env` niemals versehentlich überschreiben:** Erst die Existenz prüfen und bei Bedarf die bestehende Datei bearbeiten.

```bash
sudo install -d -o root -g root -m 0700 /etc/bcsentinel-ai-backup

if sudo test -e /etc/bcsentinel-ai-backup/backup.env; then
  echo 'backup.env existiert bereits: bitte vor Änderung manuell prüfen'
  exit 1
fi
sudo install -o root -g root -m 0600 /dev/null /etc/bcsentinel-ai-backup/backup.env
sudo tee /etc/bcsentinel-ai-backup/backup.env >/dev/null <<'EOF'
AI_PM_STATE_DIR=/home/daniel/bcsentinel-ai-control-center/repo/tools/ai-control-center/state
RESTIC_REPOSITORY=rclone:bcs-onedrive:BCSentinel-AI-Backups/restic-repository
RESTIC_PASSWORD_FILE=/etc/bcsentinel-ai-backup/restic-password
RCLONE_CONFIG=/etc/bcsentinel-ai-backup/rclone.conf
EOF
sudo chmod 600 /etc/bcsentinel-ai-backup/backup.env
sudo stat -c '%U:%G %a %n' /etc/bcsentinel-ai-backup/backup.env
```

**ACHTUNG:** Die `tee`-Variante oben schreibt nur vier öffentliche Pfade/Identifier, **keine Secrets**. Sie darf nicht verwendet werden, um Tokens/Passwörter in die Shell-Historie zu kopieren. `EnvironmentFile` wird von systemd **nicht** als Shell-Skript ausgewertet. Beim ersten Mal die vorhandene `backup.env` nur erstellen, wenn sie noch nicht existiert; bei vorhandener Datei gezielt prüfen statt blind überschreiben.

## 2. Einmalig installieren, zuerst nur vorbereiten

```bash
cd ~/bcsentinel-ai-control-center/repo/tools/ai-control-center
# Nur nach dem gezielten Import der neuen Skripte aus dem geprüften Draft-Branch.
sudo bash ./install_backup_timer.sh --prepare
sudo systemctl cat bcsentinel-ai-offsite-backup.service
sudo systemctl cat bcsentinel-ai-offsite-backup.timer
systemctl is-enabled bcsentinel-ai-offsite-backup.timer || true
```

Hier wird der Timer **nicht gestartet**. Die systemd-Einheiten werden nur vorbereitet und mit `systemd-analyze verify` überprüft.

## 3. Erst nach Konfigurations-Review aktivieren

```bash
sudo bash ./install_backup_timer.sh --activate
systemctl list-timers bcsentinel-ai-offsite-backup.timer --all
```

Wegen `Persistent=true` kann ein Backup direkt nach Aktivierung anlaufen. Kein eigenständiger Erstlauf starten, solange der Timer denselben Backupjob ausführt.

## 4. Erfolg und Fehler beobachten

```bash
sudo systemctl status bcsentinel-ai-offsite-backup.service --no-pager
sudo journalctl -u bcsentinel-ai-offsite-backup.service -n 50 --no-pager
sudo bash /usr/local/libexec/bcsentinel-ai-backup/backup_health.sh
```

Der Installer kopiert `backup_health.sh` ebenfalls in das root-owned Verzeichnis; der Checker ist rein lesend. Ein erfolgreicher Journal-Marker lautet `AI_PM_OFFSITE_DAILY_PASS`; in OneDrive entsteht ein weiterer Restic-Snapshot. Fehler erscheinen als `AI_PM_OFFSITE_DAILY_FAIL`, der systemd-Dienst wird nicht als dauerhaft laufend erwartet (`Type=oneshot`).

Prüfung des Repositorys anhand aktueller Credentials:
```bash
sudo bash -c 'export RCLONE_CONFIG=/etc/bcsentinel-ai-backup/rclone.conf RESTIC_PASSWORD_FILE=/etc/bcsentinel-ai-backup/restic-password RESTIC_REPOSITORY=rclone:bcs-onedrive:BCSentinel-AI-Backups/restic-repository; restic snapshots --tag ai-control-center'
```

## 5. Retention, Monitoring und Recovery bewusst getrennt freigeben

- Retention (`restic forget --prune`) **nicht** aktiv, bevor Recovery mindestens zwei getrennte Backup-Tage nachweisbar abdeckt, und Löschrechte/Snapshot-Anzahl vorher in `--dry-run` geprüft wurden.
- Kein externer Alarmdienst, E-Mail-Provider, API-Budget oder GitHub-Workflow-Write-Recht ist aktiviert. Fehlerüberwachung lokal über Journald/Exit-Code/Statusdatei; echte Benachrichtigung erfordert einen separaten Operatorauftrag.
- Für Totalverlust-Szenarien muss das Passwort, die OneDrive-Authentisierung und die Runbook-Anleitung unabhängig von Hetzner verfügbar bleiben. Ein echter Restore auf einem unabhängigen anderen System ist gesondert zu testen.
- Network-Restrisiko (nicht blockiertes Docker-Egress/Host-Routing) bleibt dokumentiert, ohne ungetestete Firewall-Änderungen.

**Go/No-Go:** CI-/Host-/Remote-Restore-Gates erfolgreich. Ein **täglicher Betrieb ist erst nach aktivierter Timer-Unit und mindestens einem erfolgreichen Timer-Lauf** bestätigt. Es gibt keinerlei Auswirkung auf BCSentinel-/Fiverr-Produkt-`NO_GO`.
