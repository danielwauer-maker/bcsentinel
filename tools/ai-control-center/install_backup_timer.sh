#!/usr/bin/env bash
# AI-PM 2.1 systemd installer. Review-only by default; --activate is explicit.
set -euo pipefail
umask 077
die(){ echo "ERROR: $*" >&2; exit 1; }
[[ "$EUID" == 0 ]] || die "Run as root"
[[ "${1:-}" == "--prepare" || "${1:-}" == "--activate" ]] ||
  die "Usage: sudo bash install_backup_timer.sh --prepare|--activate"
action="$1"
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
destination="/usr/local/libexec/bcsentinel-ai-backup"
config="/etc/bcsentinel-ai-backup/backup.env"
unit="/etc/systemd/system/bcsentinel-ai-offsite-backup.service"
timer="/etc/systemd/system/bcsentinel-ai-offsite-backup.timer"

command -v systemctl >/dev/null || die "systemctl missing"
command -v flock >/dev/null || die "flock missing"
for f in offsite_backup.sh scheduled_backup.sh backup_verify.py; do
  [[ -f "$source_dir/$f" ]] || die "Missing $f"
done
[[ -f "$config" && ! -L "$config" ]] || die "Create root-only backup.env first (see guide)"
[[ "$(stat -c %u "$config")" == 0 ]] || die "backup.env must be root owned"
[[ "$(stat -c %a "$config")" == 600 || "$(stat -c %a "$config")" == 400 ]] ||
  die "backup.env must be 0600/0400"
# Do NOT source the config (avoid executing untrusted text). systemd will read it at runtime.
# No installation of unit files from an unverified runtime user home: all scripts copied
# to immutable root-owned directories, and only this controlled service is enabled.
install -d -o root -g root -m 0755 "$destination"
install -o root -g root -m 0700 "$source_dir/offsite_backup.sh" "$destination/offsite_backup.sh"
install -o root -g root -m 0700 "$source_dir/scheduled_backup.sh" "$destination/scheduled_backup.sh"
install -o root -g root -m 0600 "$source_dir/backup_verify.py" "$destination/backup_verify.py"

cat > "$unit" <<'UNIT'
[Unit]
Description=BCSentinel AI Control Center encrypted remote SQLite backup and restore verification
Wants=network-online.target
After=network-online.target
ConditionPathExists=/etc/bcsentinel-ai-backup/backup.env

[Service]
Type=oneshot
User=root
Group=root
EnvironmentFile=/etc/bcsentinel-ai-backup/backup.env
WorkingDirectory=/usr/local/libexec/bcsentinel-ai-backup
ExecStart=/usr/bin/flock -n /run/lock/bcsentinel-ai-offsite.lock /usr/bin/bash /usr/local/libexec/bcsentinel-ai-backup/scheduled_backup.sh
TimeoutStartSec=45min
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=read-only
ProtectSystem=strict
ReadWritePaths=/var/lib/bcsentinel-ai-backup /var/tmp /tmp /run/lock
StateDirectory=bcsentinel-ai-backup
UMask=0077
UNIT

cat > "$timer" <<'UNIT'
[Unit]
Description=Daily BCSentinel AI Control Center encrypted OneDrive backup

[Timer]
OnCalendar=*-*-* 03:20:00 UTC
RandomizedDelaySec=15min
Persistent=true
Unit=bcsentinel-ai-offsite-backup.service

[Install]
WantedBy=timers.target
UNIT
chmod 0644 "$unit" "$timer"
systemd-analyze verify "$unit" "$timer" || die "systemd unit validation failed"
systemctl daemon-reload
echo "FILES_PREPARED: root-owned execution copy, service and timer; no backup run."
if [[ "$action" == "--activate" ]]; then
  # Explicit action: schedules tomorrow and possibly immediate catch-up due to Persistent=true.
  systemctl enable --now bcsentinel-ai-offsite-backup.timer
  echo "TIMER_ACTIVATED: first run may occur soon due to Persistent=true"
else
  echo "TIMER_NOT_ACTIVE: operator must explicitly run --activate after reviewing configuration"
fi
