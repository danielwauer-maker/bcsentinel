#!/usr/bin/env bash
# AI-PM 2.1: read-only status for local operator/monitoring integrations.
set -euo pipefail
state="/var/lib/bcsentinel-ai-backup"
success="$state/last-success"
failure="$state/last-failure"
max_age="${AI_PM_MAX_BACKUP_AGE_SEC:-93600}" # 26 hours
[[ "$max_age" =~ ^[0-9]+$ ]] || { echo "BACKUP_HEALTH_UNKNOWN invalid threshold"; exit 2; }
if [[ -e "$failure" ]]; then
  echo "BACKUP_HEALTH_FAIL: latest attempted backup failed. Inspect systemd journal."
  exit 1
fi
if [[ ! -r "$success" ]]; then
  echo "BACKUP_HEALTH_FAIL: no verified scheduled backup has completed"
  exit 1
fi
completed="$(sed -n 's/^completed_utc=//p' "$success" | head -1)"
[[ "$completed" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] ||
  { echo "BACKUP_HEALTH_FAIL: invalid success timestamp"; exit 1; }
then_sec="$(date -u -d "$completed" +%s)"
now_sec="$(date -u +%s)"
age="$((now_sec-then_sec))"
if ((age < 0 || age > max_age)); then
  echo "BACKUP_HEALTH_FAIL: stale or future backup; age_seconds=$age"
  exit 1
fi
echo "BACKUP_HEALTH_PASS: last_verified_utc=$completed age_seconds=$age"
