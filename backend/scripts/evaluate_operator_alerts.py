from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Alert:
    code: str
    severity: str
    title: str
    detail: str
    runbook: str


def evaluate(snapshot: dict[str, Any]) -> list[Alert]:
    alerts: list[Alert] = []

    def add(code: str, severity: str, title: str, detail: str, runbook: str) -> None:
        alerts.append(Alert(code, severity, title, detail, runbook))

    if not snapshot.get("api_ready", False):
        add("API_NOT_READY", "P0", "API nicht bereit", "Der Readiness-Check ist fehlgeschlagen.", "RB-API-01")
    if not snapshot.get("database_ready", False):
        add("DATABASE_NOT_READY", "P0", "PostgreSQL nicht bereit", "Die Datenbankverbindung ist nicht verfügbar.", "RB-DB-01")
    if not snapshot.get("worker_ready", False):
        add("WORKER_NOT_READY", "P0", "Worker nicht bereit", "Der Scan-Worker verarbeitet keine Aufgaben.", "RB-WORKER-01")
    if not snapshot.get("scheduler_ready", False):
        add("SCHEDULER_NOT_READY", "P0", "Scheduler nicht bereit", "Geplante Monitoring-Läufe sind gefährdet.", "RB-SCHED-01")

    failed_scans = int(snapshot.get("failed_scans_15m", 0))
    if failed_scans >= 3:
        add("SCAN_FAILURE_SPIKE", "P0", "Mehrere Scans fehlgeschlagen", f"{failed_scans} Scans sind in 15 Minuten fehlgeschlagen.", "RB-SCAN-02")
    elif failed_scans > 0:
        add("SCAN_FAILURE", "P1", "Scan fehlgeschlagen", f"{failed_scans} Scan(s) sind in 15 Minuten fehlgeschlagen.", "RB-SCAN-01")

    stuck_scans = int(snapshot.get("stuck_scans", 0))
    if stuck_scans > 0:
        add("STUCK_SCAN", "P0", "Scan hängt", f"{stuck_scans} Scan(s) überschreiten Heartbeat/Lease-Grenzen.", "RB-RECOVERY-01")

    recovery_failures = int(snapshot.get("recovery_failures_1h", 0))
    if recovery_failures > 0:
        add("RECOVERY_FAILURE", "P0", "Recovery fehlgeschlagen", f"{recovery_failures} Recovery-Versuch(e) sind fehlgeschlagen.", "RB-RECOVERY-02")

    queue_age = int(snapshot.get("oldest_queue_age_seconds", 0))
    if queue_age >= 900:
        add("QUEUE_BACKLOG", "P0", "Queue-Rückstau", f"Ältester Queue-Eintrag ist {queue_age} Sekunden alt.", "RB-QUEUE-01")
    elif queue_age >= 300:
        add("QUEUE_DELAY", "P1", "Queue verzögert", f"Ältester Queue-Eintrag ist {queue_age} Sekunden alt.", "RB-QUEUE-01")

    disk_percent = float(snapshot.get("disk_used_percent", 0))
    if disk_percent >= 90:
        add("DISK_CRITICAL", "P0", "Datenträger fast voll", f"Datenträgerauslastung {disk_percent:.1f}%.", "RB-DISK-01")
    elif disk_percent >= 80:
        add("DISK_WARNING", "P1", "Datenträgerauslastung hoch", f"Datenträgerauslastung {disk_percent:.1f}%.", "RB-DISK-01")

    backup_age = float(snapshot.get("backup_age_hours", 0))
    if backup_age >= 48:
        add("BACKUP_TOO_OLD", "P0", "Backup veraltet", f"Letztes erfolgreiches Backup ist {backup_age:.1f} Stunden alt.", "RB-BACKUP-01")
    elif backup_age >= 24:
        add("BACKUP_OLD", "P1", "Backup älter als Zielwert", f"Letztes erfolgreiches Backup ist {backup_age:.1f} Stunden alt.", "RB-BACKUP-01")

    smtp_failures = int(snapshot.get("smtp_failures_1h", 0))
    if smtp_failures >= 5:
        add("SMTP_FAILURE_SPIKE", "P0", "E-Mail-Versand gestört", f"{smtp_failures} SMTP-Fehler in einer Stunde.", "RB-SMTP-01")
    elif smtp_failures > 0:
        add("SMTP_FAILURE", "P1", "E-Mail-Versandfehler", f"{smtp_failures} SMTP-Fehler in einer Stunde.", "RB-SMTP-01")

    cert_days = int(snapshot.get("certificate_days_remaining", 999))
    if cert_days <= 7:
        add("CERTIFICATE_CRITICAL", "P0", "TLS-Zertifikat läuft ab", f"Nur noch {cert_days} Tag(e) Restlaufzeit.", "RB-TLS-01")
    elif cert_days <= 30:
        add("CERTIFICATE_WARNING", "P1", "TLS-Zertifikat bald fällig", f"Noch {cert_days} Tag(e) Restlaufzeit.", "RB-TLS-01")

    restarts = int(snapshot.get("container_restarts_1h", 0))
    if restarts >= 3:
        add("CONTAINER_RESTART_LOOP", "P0", "Container-Restartschleife", f"{restarts} Restarts in einer Stunde.", "RB-CONTAINER-01")
    elif restarts > 0:
        add("CONTAINER_RESTART", "P1", "Container neu gestartet", f"{restarts} Restart(s) in einer Stunde.", "RB-CONTAINER-01")

    return sorted(alerts, key=lambda item: (item.severity, item.code))


def write_report(snapshot: dict[str, Any], alerts: list[Alert], json_out: Path, markdown_out: Path) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not any(alert.severity == "P0" for alert in alerts) else "FAIL",
        "alert_count": len(alerts),
        "p0_count": sum(alert.severity == "P0" for alert in alerts),
        "p1_count": sum(alert.severity == "P1" for alert in alerts),
        "alerts": [asdict(alert) for alert in alerts],
        "snapshot": snapshot,
    }
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# P0-06 Operator Alert Evaluation", "", f"- **Status:** {payload['status']}", f"- **P0:** {payload['p0_count']}", f"- **P1:** {payload['p1_count']}", "", "## Alerts", ""]
    if not alerts:
        lines.append("Keine Alerts.")
    else:
        lines.extend(f"- **{a.severity} {a.code}:** {a.title} — {a.detail} (`{a.runbook}`)" for a in alerts)
    markdown_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--fail-on-p0", action="store_true")
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    alerts = evaluate(snapshot)
    write_report(snapshot, alerts, args.json_out, args.markdown_out)
    if args.fail_on_p0 and any(alert.severity == "P0" for alert in alerts):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
