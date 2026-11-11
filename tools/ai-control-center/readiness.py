"""Fiverr-only release planning metrics: exact Excel semantics, no implied approval.

Planning ETA is capacity arithmetic, not a forecast of BC acceptance or a release promise.
"""
from __future__ import annotations

import datetime as dt
import math
from zoneinfo import ZoneInfo


def estimate_work_date(start: dt.date, workdays: int) -> dt.date:
    day = start
    count = 0
    while count < workdays:
        day += dt.timedelta(days=1)
        if day.weekday() < 5:
            count += 1
    return day


def fiverr_readiness(tracker_result: dict, *, as_of: dt.date | None = None):
    if tracker_result.get("state") != "loaded":
        return {"state": "unavailable",
                "reason": "Excel-Planbasis nicht geladen oder nicht verifiziert; keine Prozent- oder Terminprognose."}
    rows = [r for r in tracker_result.get("rows", []) if r.get("area") == "fiverr"]
    if len(rows) != 61:
        return {"state": "unavailable", "reason": "Fiverr-Gate-Anzahl abweichend – keine Projektion."}
    try:
        hours = [float(r["plan_hours"]) for r in rows]
        capacity = float(tracker_result["hours_per_week"])
        baseline = float(tracker_result["legacy_start_fraction"])
        if not 0 < capacity <= 80 or any(not math.isfinite(h) or h < 0 for h in hours):
            raise ValueError("invalid hours")
        if not math.isfinite(baseline) or not 0 <= baseline <= 1:
            raise ValueError("invalid legacy baseline")
        total = sum(hours)
        if total <= 0:
            raise ValueError("empty hours")
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"state": "unavailable", "reason": "Planstunden/Kapazität im Excel unvollständig oder ungültig."}

    tech_hours = sum(h for h, r in zip(hours, rows) if r.get("technical_checked"))
    gate_hours = sum(h for h, r in zip(hours, rows) if r.get("technical_checked") and r.get("live_checked"))
    tech_count = sum(bool(r.get("technical_checked")) for r in rows)
    gate_count = sum(bool(r.get("technical_checked") and r.get("live_checked")) for r in rows)
    remaining = max(0, total - gate_hours)
    hours_day = capacity / 5.0
    workdays = math.ceil(remaining / hours_day) if remaining else 0
    current = as_of or dt.datetime.now(ZoneInfo("Europe/Berlin")).date()
    eta = estimate_work_date(current, workdays)
    by_sprint = {}
    for r, hour in zip(rows, hours):
        name = r.get("sprint") or "Unbekannt"
        entry = by_sprint.setdefault(name, {"name": name, "plan_hours": 0, "gate_hours": 0, "tech_hours": 0, "total": 0, "approved": 0})
        entry["plan_hours"] += hour
        entry["total"] += 1
        if r.get("technical_checked"): entry["tech_hours"] += hour
        if r.get("technical_checked") and r.get("live_checked"):
            entry["gate_hours"] += hour
            entry["approved"] += 1

    result = {
        "state": "loaded",
        "source": "verified_excel_v2_readonly",
        "source_sha256": tracker_result.get("sha256"),
        "as_of_date": current.isoformat(),
        "technical_fraction": round(tech_hours / total, 6),
        "gate_fraction": round(gate_hours / total, 6),
        "technical_hours": round(tech_hours, 2),
        "accepted_hours": round(gate_hours, 2),
        "total_hours": round(total, 2),
        "remaining_hours": round(remaining, 2),
        "hours_per_week": capacity,
        "remaining_workdays": workdays,
        "remaining_weeks": round(remaining / capacity, 2),
        "capacity_scenario_date": eta.isoformat(),
        "capacity_scenario_note": "Reine Kapazitätsrechnung: 5 Arbeitstage/Woche, keine Feiertage, Risiken, Abhängigkeiten oder BC/Fiverr-Abnahmeverzögerung berücksichtigt.",
        "legacy_estimate_fraction": round(baseline + (1 - baseline) * gate_hours / total, 6),
        "legacy_start_fraction": baseline,
        "technical_count": tech_count,
        "gate_count": gate_count,
        "gate_total": len(rows),
        "go_live": "NO_GO" if gate_count < len(rows) or tech_count < len(rows) else "ALL_GATES_CHECKED_REVALIDATION_REQUIRED",
        "sprints": [{**v, "fraction": round(v["gate_hours"] / v["plan_hours"], 6) if v["plan_hours"] else 0.0} for v in by_sprint.values()],
        "warning": "Historische Excel-Häkchen; GitHub-PRs und SQLite-Status ändern diese Prozente nicht automatisch. SaaS/Stripe ist ausgeschlossen."
    }
    return result
