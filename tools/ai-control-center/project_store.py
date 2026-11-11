"""Durable task store for BCSentinel Control Center.

Import is explicit, idempotent, and preserves approvals and human task edits.
No GitHub observation can promote an acceptance gate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3

DB_PATH = Path(os.getenv("PROJECT_DB_PATH", "/state/projects.sqlite3"))
SCHEMA = """
CREATE TABLE IF NOT EXISTS task (
    task_key TEXT PRIMARY KEY,
    area TEXT NOT NULL CHECK(area IN ('fiverr','saas')),
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    sprint TEXT NOT NULL DEFAULT '',
    source_note TEXT NOT NULL DEFAULT '',
    imported_technical INTEGER NOT NULL DEFAULT 0,
    imported_acceptance INTEGER NOT NULL DEFAULT 0,
    stage TEXT NOT NULL DEFAULT 'planned' CHECK(stage IN
      ('planned','in_progress','implementation_candidate','review','blocked','technical_complete','dev_accepted')),
    manually_edited INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence_link (
    task_key TEXT NOT NULL REFERENCES task(task_key),
    url TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'github',
    observed_at TEXT NOT NULL,
    PRIMARY KEY(task_key,url)
);
CREATE TABLE IF NOT EXISTS approval (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_key TEXT NOT NULL REFERENCES task(task_key),
    gate TEXT NOT NULL CHECK(gate IN ('technical','dev','go_live')),
    approved_by TEXT NOT NULL,
    evidence_uri TEXT NOT NULL,
    reason TEXT NOT NULL,
    approved_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    task_key TEXT,
    detail_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS imports (
    sha256 TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    count_fiverr INTEGER NOT NULL,
    count_saas INTEGER NOT NULL,
    imported_at TEXT NOT NULL
);
"""

def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def connect(db_path=None):
    path = Path(db_path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA)
    return con

def import_rows(source, db_path=None):
    """Only a validated SHA-matching workbook response is accepted."""
    if source.get("state") != "loaded" or not source.get("sha256"):
        raise ValueError("Only a SHA-verified live Excel workbook can initialize the database")
    rows = source.get("rows", [])
    keys = [(r["area"], str(r["id"])) for r in rows]
    if len(rows) != 85 or len(set(keys)) != 85 or keys.count(("fiverr","")):
        raise ValueError("Expected 85 distinct identifiers (61 Fiverr, 24 SaaS)")
    if sum(x[0] == "fiverr" for x in keys) != 61 or sum(x[0] == "saas" for x in keys) != 24:
        raise ValueError("Unexpected planning split")
    con = connect(db_path)
    now = timestamp()
    previous = con.execute("SELECT sha256 FROM imports LIMIT 1").fetchone()
    if previous:
        con.close()
        if previous["sha256"] != source["sha256"]:
            raise ValueError("Different workbook version: explicit reconciliation/migration required")
        return {"state": "already_imported", "tasks": 85, "sha256": source["sha256"]}
    with con:
        if con.execute("SELECT count(*) FROM task").fetchone()[0]:
            raise ValueError("Existing tasks: refusing implicit overwrite")
        for r in rows:
            con.execute("""INSERT INTO task(task_key,area,source_id,title,sprint,source_note,
                imported_technical,imported_acceptance,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (r["area"] + ":" + str(r["id"]), r["area"], str(r["id"]), r.get("title",""),
                 r.get("sprint",""), r.get("notes",""), int(bool(r.get("technical_checked"))),
                 int(bool(r.get("live_checked"))), now))
        con.execute("INSERT INTO imports VALUES(?,?,?,?,?)",
                    (source["sha256"], source.get("filename",""), 61, 24, now))
        con.execute("INSERT INTO audit_event(event_type,task_key,detail_json,created_at) VALUES(?,?,?,?)",
                    ("tracker.import", None, json.dumps({"sha256":source["sha256"],"tasks":85}), now))
    con.close()
    return {"state": "imported", "tasks": 85, "sha256": source["sha256"]}

def read_summary(db_path=None):
    if not Path(db_path or DB_PATH).exists():
        return {"state": "not_initialized", "tasks": [], "counts": {}}
    con = connect(db_path)
    task_rows = [dict(r) for r in con.execute(
        "SELECT task_key,area,source_id,title,sprint,stage,imported_technical,imported_acceptance FROM task ORDER BY area,source_id")]
    imported = con.execute("SELECT * FROM imports ORDER BY imported_at DESC LIMIT 1").fetchone()
    approvals = [dict(r) for r in con.execute(
        "SELECT task_key,gate,approved_by,evidence_uri,approved_at FROM approval ORDER BY id")]
    events = [dict(r) for r in con.execute(
        "SELECT event_type,task_key,created_at FROM audit_event ORDER BY id DESC LIMIT 20")]
    con.close()
    return {"state": "loaded" if imported else "not_initialized", "import": dict(imported) if imported else None,
            "tasks": task_rows, "counts": {"fiverr":sum(r["area"]=="fiverr" for r in task_rows),
                                          "saas":sum(r["area"]=="saas" for r in task_rows)},
            "approvals": approvals, "recent_events": events}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["import", "status"])
    parser.add_argument("--db", default=str(DB_PATH))
    args = parser.parse_args()
    if args.operation == "import":
        import app
        result = import_rows(app.tracker(), args.db)
    else:
        result = read_summary(args.db)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
