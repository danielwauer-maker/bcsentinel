#!/usr/bin/env bash
# AI-PM 2.1: operator-triggered encrypted *off-host* backup and restore verification.
# Not installed as a timer, does not touch live SQLite DBs, no repo init/prune.
set -euo pipefail
umask 077

die(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ "${EUID}" -eq 0 ]] || die "Run explicitly as root (sudo -E); never chown/chmod live SQLite state"
command -v restic >/dev/null || die "restic missing; install from your trusted OS package source first"
command -v python3 >/dev/null || die "python3 missing"
: "${RESTIC_REPOSITORY:?Configure a dedicated encrypted off-host restic repository}"
: "${RESTIC_PASSWORD_FILE:?Configure a root-only restic password file}"
# Rclone credentials must be a separate, root-owned config. Never silently
# fall back to root's default home or the unprivileged dashboard account.
if [[ "$RESTIC_REPOSITORY" == rclone:* ]]; then
  : "${RCLONE_CONFIG:?Set RCLONE_CONFIG to an explicit root-only config file}"
  [[ -f "$RCLONE_CONFIG" && ! -L "$RCLONE_CONFIG" ]] ||
    die "Rclone config missing or symlinked"
  [[ "$(stat -c %u "$RCLONE_CONFIG")" == 0 ]] ||
    die "Rclone config must be owned by root"
  [[ "$(stat -c %a "$RCLONE_CONFIG")" == 600 ||
     "$(stat -c %a "$RCLONE_CONFIG")" == 400 ]] ||
    die "Rclone config permissions must be 0600 or 0400"
  command -v rclone >/dev/null || die "rclone executable missing"
fi
case "$RESTIC_REPOSITORY" in
  sftp:*|s3:*|b2:*|rclone:*|rest:https://*) ;;
  *) die "Remote-only repository required: sftp:, s3:, b2:, rclone:, rest:https:// (no local/file/http)" ;;
esac
[[ -f "$RESTIC_PASSWORD_FILE" && ! -L "$RESTIC_PASSWORD_FILE" ]] ||
  die "Password file missing or symlinked"
[[ "$(stat -c %u "$RESTIC_PASSWORD_FILE")" == 0 ]] ||
  die "Password file must be owned by root"
[[ "$(stat -c %a "$RESTIC_PASSWORD_FILE")" == 600 ||
   "$(stat -c %a "$RESTIC_PASSWORD_FILE")" == 400 ]] ||
  die "Password file permissions must be 0600 or 0400"
# Explicitly require the operator to configure an existing repository.
restic cat config >/dev/null || die "Remote repo not initialized/reachable: init it separately and verify credentials"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${AI_PM_STATE_DIR:-$SCRIPT_DIR/state}"
[[ -d "$SOURCE_DIR" ]] || die "SQLite state directory missing"
TMP_PARENT="${AI_PM_BACKUP_TMP_PARENT:-/var/tmp}"
[[ -d "$TMP_PARENT" ]] || die "Temporary parent directory absent"
work="$(mktemp -d "$TMP_PARENT/ai-pm21-offsite.XXXXXXXX")"
chmod 700 "$work"
cleanup(){ rm -rf -- "$work"; }
trap cleanup EXIT
mkdir -m 700 "$work/staged" "$work/restore"
# Mandatory SQLite online backup; never cp a live WAL-enabled database.
python3 "$SCRIPT_DIR/backup_verify.py" backup \
  --source-dir "$SOURCE_DIR" --backup-dir "$work/staged/snapshot" --confirm >/dev/null
python3 "$SCRIPT_DIR/backup_verify.py" verify \
  --backup-dir "$work/staged/snapshot" >/dev/null
cd "$work/staged/snapshot"
printf 'Remote backup: encrypting verified temporary SQLite snapshots using restic.\n'
restic backup --tag ai-control-center projects.sqlite3 agent-control.sqlite3
# This dedicated restic repository must contain ONLY AI Control Center backups.
# 'latest' never refers to shared services because the repo is dedicated.
restic restore latest --target "$work/restore" --verify
python3 "$SCRIPT_DIR/backup_verify.py" verify --backup-dir "$work/restore" >/dev/null
restic check --read-data-subset=1/10
printf '%s\n' "OFFSITE_BACKUP_AND_RESTORE_PASS"
printf '%s\n' "Restic repository: dedicated remote (path deliberately not printed)"
printf '%s\n' "The local staging copies were deleted on exit; no schedule/retention/purge was activated."
