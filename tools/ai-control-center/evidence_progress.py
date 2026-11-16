"""Evidence-qualified project progress. No PR lead-time is counted as work hours.

The source workbook is immutable, status metrics use a known denominator and
unknown never becomes completed. This module is read-only.
"""
from __future__ import annotations
import datetime as dt
import math
from collections import defaultdict

EVIDENCE_LEVELS = ("draft", "integrated", "preview", "technical", "accepted")
DATE_ANCHOR = "2026-11-11"
def _valid_hours(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0

def _iso_day(value):
    if not isinstance(value, str):
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None

def build_progress(tracker, radar, source, *, approvals=None):
    """Produce independently attributable phase coverage, not subjective percent complete."""
    approved = approvals if isinstance(approvals, dict) else {}
    rows = tracker.get("rows", []) if tracker.get("state") == "loaded" else []
    excel = {(r.get("area"), str(r.get("id"))): r for r in rows
             if r.get("area") in ("fiverr", "saas")}
    accurate_excel = (len([x for x in excel if x[0]=="fiverr"]) == 61 and
                      len([x for x in excel if x[0]=="saas"]) == 24)
    items = radar.get("items", []) if radar.get("state") in ("loaded", "partial") else []
    gates = source.get("observed_gates", {})
    release = gates.get("dev_runtime_release_20261116", {})
    known_release = (release.get("backend", {}).get("state") == "deployed_exact_staging_sha"
                     and release.get("backend", {}).get("sha") ==
                     "403709ca2dfdcbcc2ceb2e9dda4461f261d04aae")
    groups = defaultdict(list)
    timeline = []
    for item in items:
        # source_id may be shared across areas; preserve the task's own area.
        task_area = "saas" if item.get("area") == "SaaS & Stripe" else "fiverr"
        key = (task_area, str(item.get("id")))
        reference = excel.get(key, {})
        sprint = str(reference.get("sprint") or item.get("area") or "Nicht zugeordnet")
        title = str(reference.get("title") or item.get("title") or item.get("id"))
        prs = item.get("prs") or []
        merged = [p for p in prs if p.get("state") == "merged"]
        draft = [p for p in prs if p.get("state") in ("open","draft")]
        source_status = item.get("source_status")
        # Source review demonstrates candidate state, not CI or acceptance.
        has_draft = bool(draft) or source_status in (
            "implementation_draft", "code_candidate", "audit_draft",
            "partial", "editorial_complete")
        has_integrated = bool(merged)
        has_preview = False
        # Exactly scoped operator evidence; do not promote unrelated infrastructure.
        if task_area == "fiverr" and known_release and key[1] in ("1.02", "3.02"):
            has_preview = True
        # Explicit approved task gate only; historical checkmarks are NOT current approvals.
        manual = set(item.get("manual_gates") or [])
        has_tech = "technical" in manual or "dev" in manual or "go_live" in manual
        has_accepted = "dev" in manual or "go_live" in manual
        observed = {"draft":has_draft, "integrated":has_integrated,
                    "preview":has_preview, "technical":has_tech,
                    "accepted":has_accepted}
        hours = reference.get("plan_hours")
        # A source row is fully accounted for only when its original numeric plan hours are present.
        hours = float(hours) if task_area == "fiverr" and _valid_hours(hours) else None
        result = {"id": key[1], "area": task_area, "sprint": sprint,
                  "title": title, "plan_hours":hours, "actual_hours":None,
                  "actual_hours_state":"not_recorded",
                  "evidence":observed, "review_status":source_status,
                  "next_action":item.get("next_action"),
                  "prs":prs, "evidence_coverage":"curated" if source_status != "not_reviewed" else "unreviewed"}
        groups[(task_area,sprint)].append(result)
        for pr in merged:
            day = _iso_day(pr.get("merged_at"))
            if day:
                created = _iso_day(pr.get("created_at"))
                lead_days = (dt.date.fromisoformat(day)-dt.date.fromisoformat(created)).days if created else None
                timeline.append({"date":day, "kind":"merge",
                                 "label":f"PR #{pr['number']} · {key[1]} · Code integriert",
                                 "area":sprint,"url":pr.get("url"),
                                 "lead_calendar_days":lead_days if lead_days is not None and lead_days >= 0 else None})
        for pr in draft:
            day = _iso_day(pr.get("created_at"))
            if day:
                timeline.append({"date":day, "kind":"draft",
                                 "label":f"PR #{pr['number']} · {key[1]} · Entwurf",
                                 "area":sprint,"url":pr.get("url")})
    # Exact operator-verified milestone dates, without fabricated hours.
    if known_release:
        timeline.append({"date":"2026-11-16","kind":"preview",
                         "label":"DEV Backend · SHA 403709ca · Release-Nachweis",
                         "area":"Release & BC27","url":None})
    radar_gate=gates.get("ai_pm24_sprint_radar",{})
    if radar_gate.get("state") == "operator_verified_DEV_8092_cutover_pass":
        timeline.append({"date":"2026-11-16","kind":"preview",
                         "label":"AI Control Center 2.4 · DEV Port 8092 abgenommen",
                         "area":"AI Control Center","url":None})
    summary = []
    for (area,sprint), tasks in sorted(groups.items(),key=lambda kv:(kv[0][0],kv[0][1])):
        total = len(tasks)
        counters = {phase:sum(bool(t["evidence"][phase]) for t in tasks) for phase in EVIDENCE_LEVELS}
        # These are phase-coverage rates of evidenced tasks, NOT % of development complete.
        phase_pct = {name:round(100 * count / total,1) for name,count in counters.items()}
        plan_known = area == "fiverr" and all(t["plan_hours"] is not None for t in tasks)
        summary.append({
            "area":area,"sprint":sprint,"tasks":total,
            "plan_hours":round(sum(t["plan_hours"] for t in tasks),2) if plan_known else None,
            "plan_hours_state":"verified_excel" if plan_known and accurate_excel else "unavailable",
            "actual_hours":None,"actual_hours_state":"missing_timesheets",
            "counts":counters,"percent":phase_pct,
            "reviewed":sum(t["evidence_coverage"]=="curated" for t in tasks),
            "unreviewed":sum(t["evidence_coverage"]=="unreviewed" for t in tasks),
            "tasks_detail":tasks,
        })
    totals = {name:sum(item["counts"][name] for item in summary) for name in EVIDENCE_LEVELS}
    fiverr = [g for g in summary if g["area"]=="fiverr"]
    coverage = {name:round(100*sum(g["counts"][name] for g in fiverr)/
                          sum(g["tasks"] for g in fiverr),1) if fiverr else None
                for name in EVIDENCE_LEVELS}
    unique_events = {(e["date"],e["kind"],e["label"]):e for e in timeline}
    events = sorted(unique_events.values(),key=lambda e:(e["date"],e["kind"],e["label"]))
    return {
        "state":"loaded" if accurate_excel and radar.get("state")=="loaded" else "partial",
        "source_reviewed_at":source.get("reviewed_at"),
        "workbook_state":tracker.get("state"),
        "workbook_sha256":tracker.get("sha256") if accurate_excel else None,
        "method":"Task-denominator phase evidence, independent axes; no arbitrary phase weighting",
        "metrics":{"fiverr_tasks":sum(g["tasks"] for g in fiverr),
                   "saas_tasks":sum(g["tasks"] for g in summary if g["area"]=="saas"),
                   "phase_coverage_fiverr_percent":coverage,
                   "phase_counts":totals},
        "sprints":summary,
        "timeline":{"events":events[-150:],"event_count":len(events),
                    "duration_basis":"PR milestone dates only; no active work duration",
                    "actual_logged_hours":None,
                    "actual_hours_state":"No task-level timesheets or verified worklogs available",
                    "planned_fiverr_hours":round(sum(g["plan_hours"] for g in fiverr),2)
                       if fiverr and all(g["plan_hours"] is not None for g in fiverr) and accurate_excel else None,
                    "planned_basis":"verified Excel plan, not actual spent hours",
                    "start_baseline":DATE_ANCHOR},
        "warning":"Die Prozentwerte sind je Phase der Anteil belegter Aufgaben, keine Schätzung des Gesamtfertigstellungsgrades. 0 % heißt kein zugeordneter Nachweis, nicht 0 % Entwicklungsarbeit. PR-Erstellungs-/Mergezeiten sind Kalenderereignisse, keine Arbeitsstunden.",
        "release":"NO_GO"}
