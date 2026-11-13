#!/usr/bin/env bash
# Dedicated, root-only systemd helper. No retention/prune/deletion.
set -euo pipefail
umask 077

die(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ "$EUID" == 0 ]] || die "Run as root only"
: "${AI_PM_STATE_DIR:?Specify the absolute live AI Control Center state directory}"
[[ "$AI_PM_STATE_DIR" == /* && -d "$AI_PM_STATE_DIR" ]] || die "Invalid AI_PM_STATE_DIR"
: "${RESTIC_REPOSITORY:?Set remote Restic repository}"
: "${RCLONE_CONFIG:?Set root-owned rclone configuration path}"
: "${RESTIC_PASSWORD_FILE:?Set root-owned restic password path}"

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
status_dir="/var/lib/bcsentinel-ai-backup"
install -d -o root -g root -m 0700 "$status_dir"
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

on_exit(){
    code=$?
    if [[ $code -eq 0 ]]; then
        printf 'state=PASS\ncompleted_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$status_dir/last-success.tmp"
        mv -f "$status_dir/last-success.tmp" "$status_dir/last-success"
        rm -f "$status_dir/last-failure"
        printf 'AI_PM_OFFSITE_DAILY_PASS at %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    else
        printf 'state=FAIL\nstarted_utc=%s\nexit_code=%s\n' "$started" "$code" > "$status_dir/last-failure.tmp"
        mv -f "$status_dir/last-failure.tmp" "$status_dir/last-failure"
        printf 'AI_PM_OFFSITE_DAILY_FAIL code=%s; inspect journal; last-success preserved\n' "$code" >&2
    fi
}
trap on_exit EXIT
bash "$ROOT/offsite_backup.sh"
