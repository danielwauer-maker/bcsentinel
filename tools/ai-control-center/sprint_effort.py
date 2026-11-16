"""Operator-entered sprint effort minutes, separate from Excel plan and gate approvals.

One current cumulative minutes value per exact (area, sprint), with append-only
revision history. No automatic time guessing. Works on existing /state mount.
"""
from __future__ import annotations
import datetime as dt
import sqlite3
from pathlib import Path
import os

DB_PATH = Path(os.getenv("PROJECT_DB_PATH", "/state/projects.sqlite3"))
SCHEMA = """
CREATE TABLE IF NOT EXISTS sprint_effort (
 area TEXT NOT NULL CHECK(area IN ('fiverr','saas')),
 sprint TEXT NOT NULL,
 minutes INTEGER NOT NULL CHECK(minutes BETWEEN 0 AND 1000000),
 revision INTEGER NOT NULL DEFAULT 1 CHECK(revision >= 1),
 modified_at TEXT NOT NULL,
 PRIMARY KEY(area,sprint)
);
CREATE TABLE IF NOT EXISTS sprint_effort_audit (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 area TEXT NOT NULL, sprint TEXT NOT NULL,
 old_minutes INTEGER, new_minutes INTEGER NOT NULL,
 revision INTEGER NOT NULL,
 recorded_at TEXT NOT NULL
);
"""

class EffortError(ValueError):
    pass

class EffortConflict(EffortError):
    pass

def _database(path=None, *, write=False):
    p=Path(path or DB_PATH)
    if not p.is_file():
        raise EffortError("Projekt-Datenbank fehlt")
    if write:
        con=sqlite3.connect(str(p),timeout=10)
    else:
        con=sqlite3.connect(p.as_uri()+"?mode=ro",uri=True,timeout=10)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA busy_timeout=10000")
    return con

def _tables(con):
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def summary(path=None):
    try:
        with _database(path) as con:
            if "sprint_effort" not in _tables(con):
                return {"state":"not_initialized","entries":[],"history":[]}
            entries=[dict(r) for r in con.execute(
                "SELECT area,sprint,minutes,revision,modified_at FROM sprint_effort ORDER BY area,sprint")]
            audit=[dict(r) for r in con.execute(
                "SELECT area,sprint,old_minutes,new_minutes,revision,recorded_at "
                "FROM sprint_effort_audit ORDER BY id DESC LIMIT 100")] if "sprint_effort_audit" in _tables(con) else []
        return {"state":"loaded","entries":entries,"history":audit}
    except (sqlite3.Error,EffortError):
        return {"state":"unavailable","entries":[],"history":[]}

def save(area,sprint,minutes,revision,valid_sprints,path=None):
    if area not in ("fiverr","saas") or not isinstance(sprint,str) or not 0<len(sprint)<=200:
        raise EffortError("Ungültige Sprintkennung")
    if (area,sprint) not in valid_sprints:
        raise EffortError("Sprint nicht im verifizierten Excel-Tracker")
    if isinstance(minutes,bool) or not isinstance(minutes,int) or not 0<=minutes<=1000000:
        raise EffortError("Minuten müssen eine ganze Zahl von 0 bis 1000000 sein")
    if isinstance(revision,bool) or not isinstance(revision,int) or revision<0:
        raise EffortError("Ungültige Revision")
    with _database(path,write=True) as con:
        con.executescript(SCHEMA)
        con.execute("BEGIN IMMEDIATE")
        old=con.execute("SELECT minutes,revision FROM sprint_effort WHERE area=? AND sprint=?",
                        (area,sprint)).fetchone()
        existing_revision=old["revision"] if old else 0
        if existing_revision != revision:
            raise EffortConflict("Die Zeit wurde inzwischen geändert. Bitte neu laden.")
        if old and old["minutes"]==minutes:
            return {"state":"unchanged","area":area,"sprint":sprint,
                    "minutes":minutes,"revision":revision}
        new_revision=revision+1
        stamp=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        con.execute("INSERT INTO sprint_effort(area,sprint,minutes,revision,modified_at) "
                    "VALUES(?,?,?,?,?) ON CONFLICT(area,sprint) DO UPDATE SET "
                    "minutes=excluded.minutes,revision=excluded.revision,modified_at=excluded.modified_at",
                    (area,sprint,minutes,new_revision,stamp))
        con.execute("INSERT INTO sprint_effort_audit(area,sprint,old_minutes,new_minutes,revision,recorded_at) "
                    "VALUES(?,?,?,?,?,?)",
                    (area,sprint,old["minutes"] if old else None,minutes,new_revision,stamp))
        con.commit()
    return {"state":"saved","area":area,"sprint":sprint,"minutes":minutes,
            "revision":new_revision,"modified_at":stamp}

def attach(progress,effort):
    """Annotate only matching existing sprint rows, no source evidence mutation."""
    known={(e["area"],e["sprint"]):e for e in effort.get("entries", [])}
    logged=[]
    for group in progress.get("sprints",[]):
        key=(group["area"],group["sprint"])
        e=known.get(key)
        group["actual_minutes"]=e["minutes"] if e else None
        group["time_revision"]=e["revision"] if e else 0
        group["actual_hours"]=round(e["minutes"]/60,2) if e else None
        group["actual_hours_state"]="manually_recorded" if e else "not_recorded"
        group["budget_used_percent"]=round(e["minutes"]/(group["plan_hours"]*60)*100,1) if
            e and isinstance(group.get("plan_hours"),(int,float)) and group["plan_hours"]>0 else None
        if e and isinstance(group.get("plan_hours"),(int,float)):
            logged.append(group)
    plan=sum(g["plan_hours"] for g in logged)
    actual=sum(g["actual_minutes"] for g in logged)
    progress["effort"]={
        "state":effort.get("state"),"recorded_sprints":len(known),
        "comparable_sprints":len(logged),
        "comparable_plan_minutes":round(plan*60),
        "comparable_actual_minutes":actual,
        "budget_used_percent":round(actual/(plan*60)*100,1) if plan>0 else None,
        "all_project_plan_minutes":progress.get("timeline",{}).get("planned_fiverr_hours",0)*60
           if isinstance(progress.get("timeline",{}).get("planned_fiverr_hours"),(int,float)) else None,
        "disclaimer":"Erfasste Ist-Minuten sind kumulierte manuelle Eingaben. "
                     "Unter Budget ist nicht automatisch im Terminplan: unfertige Aufgaben haben Restaufwand."
    }
    dated=[]
    for entry in effort.get("history",[]):
        dated.append({"date":entry["recorded_at"][:10],"kind":"manual_minutes",
                      "label":f"{entry['sprint']} · Ist-Zeit auf {entry['new_minutes']} Minuten gesetzt",
                      "area":entry["sprint"],"url":None})
    timeline=progress.get("timeline",{})
    events=timeline.get("events",[])+dated
    timeline["events"]=sorted(events,key=lambda x:(x["date"],x["kind"],x["label"]))[-150:]
    timeline["event_count"]=len(events)
    timeline["actual_logged_hours"]=round(sum(x["minutes"] for x in known.values())/60,2) if known else None
    timeline["actual_hours_state"]="manually_recorded" if known else "not_recorded"
    return progress
