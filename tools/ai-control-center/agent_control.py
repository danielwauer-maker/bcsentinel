"""AI-PM 2.0: operator-only agent control plane, no automatic execution.

All mutations are intentional CLI operations on a separate SQLite store.
The service has NO network clients, no LLM integration, no GitHub write token,
and cannot dispatch, deploy or execute arbitrary code. "claimed" is a local
human-controlled work slot, NOT proof that an external agent was started.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path

STATE_PATH = Path(os.environ.get("AGENT_CONTROL_DB_PATH", "/state/agent-control.sqlite3"))
KEY_PATTERN = re.compile(r"^\d{1,2}\.\d{2}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MAX_CENTS = 100_000
PURPOSES = ("evidence_review", "code_review", "test_plan")
TERMINAL = ("completed", "rejected", "cancelled")
SCHEMA = """
CREATE TABLE IF NOT EXISTS control_settings (
  id INTEGER PRIMARY KEY CHECK(id = 1), monthly_budget_cents INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL, updated_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agent_job (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL, purpose TEXT NOT NULL,
  tracker_sha256 TEXT NOT NULL, request_sha256 TEXT NOT NULL,
  request_text TEXT NOT NULL, estimated_cost_cents INTEGER NOT NULL,
  cost_month TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN
    ('proposed','approved','claimed','completed','rejected','cancelled')),
  created_by TEXT NOT NULL, approved_by TEXT, claimed_by TEXT,
  finished_by TEXT, actual_cost_cents INTEGER,
  created_at TEXT NOT NULL, approved_at TEXT, claimed_at TEXT, finished_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS agent_one_claimed_job
  ON agent_job((1)) WHERE status='claimed';
CREATE TABLE IF NOT EXISTS agent_audit (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER, event TEXT NOT NULL, actor TEXT NOT NULL,
  detail TEXT NOT NULL, created_at TEXT NOT NULL
);
"""
def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def _connect(path):
    path=Path(path)
    connection=sqlite3.connect(path,timeout=15,isolation_level=None)
    connection.row_factory=sqlite3.Row
    connection.execute("PRAGMA busy_timeout=15000")
    return connection

def _require_db(path):
    if not Path(path).is_file():
        raise ValueError("Agent control database not initialized; run init explicitly")

def _actor(actor):
    if not isinstance(actor,str) or not re.fullmatch(r"[A-Za-z0-9_.@-]{3,80}",actor):
        raise ValueError("Explicit operator identity (3-80 safe characters) required")
    return actor

def _audit(con, job_id, event, actor, detail):
    con.execute("INSERT INTO agent_audit(job_id,event,actor,detail,created_at) VALUES(?,?,?,?,?)",
                (job_id,event,actor,json.dumps(detail,sort_keys=True),utc_now()))

def _transaction(path, fn):
    _require_db(path)
    con=_connect(path)
    try:
        con.execute("BEGIN IMMEDIATE")
        result=fn(con)
        con.commit()
        return result
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()

def init(path=STATE_PATH, *, actor, confirm=False):
    _actor(actor)
    if not confirm:
        raise ValueError("Explicit --confirm required")
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    con=_connect(path)
    try:
        con.executescript(SCHEMA)
        con.execute("BEGIN IMMEDIATE")
        if not con.execute("SELECT id FROM control_settings WHERE id=1").fetchone():
            con.execute("INSERT INTO control_settings VALUES(1,0,?,?)",(utc_now(),actor))
            _audit(con,None,"control.init",actor,{"monthly_budget_cents":0,"execution":"disabled"})
        con.commit()
        return {"state":"initialized","monthly_budget_cents":read_status(path)["budget"]["monthly_cap_cents"]}
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()

def set_budget(cents, *, path=STATE_PATH, actor, confirm=False):
    actor=_actor(actor)
    if not confirm or not isinstance(cents,int) or isinstance(cents,bool) or not 0<=cents<=MAX_CENTS:
        raise ValueError("Explicit confirmation and integer budget 0..100000 cents required")
    def operation(con):
        settings=con.execute("SELECT * FROM control_settings WHERE id=1").fetchone()
        if not settings:
            raise ValueError("Control store missing settings")
        months=[r[0] for r in con.execute("SELECT DISTINCT cost_month FROM agent_job WHERE status IN ('approved','claimed','completed')")]
        if any(_spend(con,month)>cents for month in months):
            raise ValueError("Budget reduction below existing reserved/actual costs denied")
        con.execute("UPDATE control_settings SET monthly_budget_cents=?,updated_at=?,updated_by=? WHERE id=1",
                    (cents,utc_now(),actor))
        _audit(con,None,"budget.set",actor,{"old_cents":settings["monthly_budget_cents"],"new_cents":cents})
        return {"monthly_budget_cents":cents}
    return _transaction(path,operation)

def propose(task_id, purpose, tracker_sha, request, estimated_cents, *,
            path=STATE_PATH, actor, confirm=False, current=None):
    actor=_actor(actor)
    if not confirm or not isinstance(task_id,str) or not KEY_PATTERN.fullmatch(task_id):
        raise ValueError("Must explicitly confirm a valid Fiverr task ID")
    if purpose not in PURPOSES or not SHA_PATTERN.fullmatch(str(tracker_sha)):
        raise ValueError("Purpose must be allowed and tracker SHA must be verified")
    if not isinstance(estimated_cents,int) or isinstance(estimated_cents,bool) or not 1<=estimated_cents<=MAX_CENTS:
        raise ValueError("Cost estimate must be explicit positive integer cents")
    if not isinstance(request,str) or not 40<=len(request)<=6000:
        raise ValueError("Bounded review request text required")
    forbidden=("deploy","release","publish","production","prod","merge","payments","credential")
    # Review prompts inevitably may use "no deploy" to state prohibitions;
    # vet actual execution rights instead of naïve keyword matching.
    now=current or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("UTC-aware date required")
    month=now.astimezone(dt.timezone.utc).strftime("%Y-%m")
    digest=hashlib.sha256(request.encode()).hexdigest()
    project_db=Path(os.environ.get('PROJECT_DB_PATH', '/state/projects.sqlite3'))
    if not project_db.is_file():
        raise ValueError('Verified project register unavailable')
    with sqlite3.connect('file:'+str(project_db)+'?mode=ro', uri=True, timeout=10) as project:
        imported=project.execute('SELECT sha256 FROM imports ORDER BY imported_at LIMIT 1').fetchone()
        target=project.execute("SELECT task_key FROM task WHERE area='fiverr' AND source_id=?",(task_id,)).fetchone()
        if not imported or imported[0]!=tracker_sha or not target:
            raise ValueError('Task or source SHA not present in verified project register')
    def operation(con):
        con.execute("""INSERT INTO agent_job(task_id,purpose,tracker_sha256,
                  request_sha256,request_text,estimated_cost_cents,cost_month,status,
                  created_by,created_at) VALUES(?,?,?,?,?, ?,?,'proposed',?,?)""",
                  (task_id,purpose,tracker_sha,digest,request,estimated_cents,month,actor,utc_now()))
        job_id=con.execute("SELECT last_insert_rowid()").fetchone()[0]
        _audit(con,job_id,"job.proposed",actor,{"task":task_id,"purpose":purpose,
                    "sha256":digest,"estimate_cents":estimated_cents,"month":month})
        return {"id":job_id,"state":"proposed","request_sha256":digest}
    return _transaction(path,operation)

def _job(con, job_id):
    row=con.execute("SELECT * FROM agent_job WHERE id=?",(job_id,)).fetchone()
    if not row:
        raise ValueError("Unknown job")
    return row

def _spend(con, month):
    # Actual costs from completed jobs plus reserved estimates for approved and
    # claimed jobs. Never double count a completed estimate.
    total=con.execute("""SELECT COALESCE(SUM(CASE WHEN status='completed'
                  THEN actual_cost_cents ELSE estimated_cost_cents END),0)
                  FROM agent_job WHERE cost_month=? AND status IN
                  ('approved','claimed','completed')""",(month,)).fetchone()[0]
    return int(total or 0)

def approve(job_id, request_sha, *, path=STATE_PATH, actor, confirm=False):
    actor=_actor(actor)
    if not confirm or not SHA_PATTERN.fullmatch(str(request_sha)):
        raise ValueError("Explicit confirmation and exact request SHA required")
    def operation(con):
        job=_job(con,job_id)
        if job["status"]!="proposed" or actor==job["created_by"]:
            raise ValueError("Only an independent approver can approve a proposed job")
        if request_sha!=job["request_sha256"]:
            raise ValueError("Approved request differs from proposed content")
        budget=con.execute("SELECT monthly_budget_cents FROM control_settings WHERE id=1").fetchone()
        if not budget or _spend(con,job["cost_month"])+job["estimated_cost_cents"]>budget[0]:
            raise ValueError("Hard monthly budget exceeded; approval denied")
        con.execute("UPDATE agent_job SET status='approved',approved_by=?,approved_at=? WHERE id=?",
                    (actor,utc_now(),job_id))
        _audit(con,job_id,"job.approved",actor,{"request_sha256":request_sha,
                "reserved_cents":job["estimated_cost_cents"],"execution":"disabled"})
        return {"id":job_id,"state":"approved","execution":"disabled"}
    return _transaction(path,operation)

def claim(job_id, *, path=STATE_PATH, actor, confirm=False):
    """Reserve the single human review slot. Never launches an agent/process."""
    actor=_actor(actor)
    if not confirm:
        raise ValueError("Explicit --confirm required")
    def operation(con):
        job=_job(con,job_id)
        if job["status"]!="approved" or actor==job["created_by"]:
            raise ValueError("Only separately approved jobs may be claimed by an operator")
        if con.execute("SELECT 1 FROM agent_job WHERE status='claimed'").fetchone():
            raise ValueError("One active human-controlled review slot already claimed")
        if _spend(con,job["cost_month"])>con.execute(
            "SELECT monthly_budget_cents FROM control_settings WHERE id=1").fetchone()[0]:
            raise ValueError("Current hard budget exceeded; claim denied")
        con.execute("UPDATE agent_job SET status='claimed',claimed_by=?,claimed_at=? WHERE id=?",
                    (actor,utc_now(),job_id))
        _audit(con,job_id,"job.claimed",actor,
               {"execution":"disabled","meaning":"human reservation only"})
        return {"id":job_id,"state":"claimed","execution":"disabled"}
    return _transaction(path,operation)

def close(job_id, outcome, actual_cost_cents=0, *, path=STATE_PATH, actor, confirm=False):
    actor=_actor(actor)
    if not confirm or outcome not in TERMINAL:
        raise ValueError("Explicit confirmation and terminal outcome required")
    if (not isinstance(actual_cost_cents,int) or isinstance(actual_cost_cents,bool)
        or actual_cost_cents<0 or actual_cost_cents>MAX_CENTS):
        raise ValueError("Invalid actual cost in integer cents")
    def operation(con):
        job=_job(con,job_id)
        if outcome=="completed":
            if job["status"]!="claimed":
                raise ValueError("Only claimed jobs may be marked completed")
            if actual_cost_cents>job["estimated_cost_cents"]:
                raise ValueError("Actual exceeds reserved estimate; manual budget review required")
        else:
            if job["status"] not in ("proposed","approved","claimed") or actual_cost_cents:
                raise ValueError("Rejected/cancelled jobs may not have automatic charge entries")
        con.execute("UPDATE agent_job SET status=?,actual_cost_cents=?,finished_by=?,finished_at=? WHERE id=?",
                    (outcome,actual_cost_cents,actor,utc_now(),job_id))
        _audit(con,job_id,"job."+outcome,actor,{"actual_cost_cents":actual_cost_cents,
                "external_execution_verified":False,"release_approved":False})
        return {"id":job_id,"state":outcome,"release":"NO_GO"}
    return _transaction(path,operation)

def read_status(path=STATE_PATH):
    path=Path(path)
    if not path.is_file():
        return {"state":"not_initialized","execution":"disabled","global_release":"NO_GO",
                "budget":{"monthly_cap_cents":0}}
    con=_connect(path)
    try:
        setting=con.execute("SELECT * FROM control_settings WHERE id=1").fetchone()
        if not setting:
            return {"state":"unavailable","execution":"disabled","global_release":"NO_GO"}
        jobs=[dict(r) for r in con.execute("""SELECT id,task_id,purpose,tracker_sha256,
             request_sha256,estimated_cost_cents,cost_month,status,created_by,
             approved_by,claimed_by,created_at,approved_at,claimed_at,finished_at,
             actual_cost_cents FROM agent_job ORDER BY id DESC LIMIT 50""")]
        months=[dict(r) for r in con.execute("""SELECT cost_month,
            SUM(CASE WHEN status='completed' THEN actual_cost_cents
                ELSE estimated_cost_cents END) AS reserved_or_actual_cents
            FROM agent_job WHERE status IN ('approved','claimed','completed')
            GROUP BY cost_month ORDER BY cost_month DESC LIMIT 12""")]
        logs=[dict(r) for r in con.execute("""SELECT seq,job_id,event,actor,created_at
            FROM agent_audit ORDER BY seq DESC LIMIT 15""")]
        claimed=sum(x["status"]=="claimed" for x in jobs)
        return {"state":"loaded","execution":"disabled","global_release":"NO_GO",
                "mode":"cli_only_human_review_no_runtime","max_claimed":1,
                "claimed_slots":claimed,
                "budget":{"monthly_cap_cents":setting["monthly_budget_cents"],
                           "monthly_reserved_and_actual":months,
                           "currency":"EUR","unit":"cents"},
                "jobs":jobs,"audit_recent":logs,
                "warning":"CLI-only human approval and slot reservation, never a running AI agent. "
                          "No provider configured. A completed entry is a MANUAL operator record "
                          "and is not automatically verified evidence."}
    except sqlite3.DatabaseError:
        return {"state":"unavailable","execution":"disabled","global_release":"NO_GO"}
    finally:
        con.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("init","status","budget","propose","approve","claim","complete","reject","cancel"))
    p.add_argument("--db",default=str(STATE_PATH))
    p.add_argument("--actor")
    p.add_argument("--confirm",action="store_true")
    p.add_argument("--cents",type=int)
    p.add_argument("--task-id")
    p.add_argument("--purpose",default="evidence_review")
    p.add_argument("--tracker-sha")
    p.add_argument("--request-file")
    p.add_argument("--job-id",type=int)
    p.add_argument("--request-sha")
    args=p.parse_args()
    if args.action=="status":
        result=read_status(args.db)
    elif args.action=="init":
        result=init(args.db,actor=args.actor,confirm=args.confirm)
    elif args.action=="budget":
        result=set_budget(args.cents,path=args.db,actor=args.actor,confirm=args.confirm)
    elif args.action=="propose":
        if not args.request_file:
            p.error("--request-file required")
        request=Path(args.request_file).read_text(encoding="utf-8")
        result=propose(args.task_id,args.purpose,args.tracker_sha,request,args.cents,
                       path=args.db,actor=args.actor,confirm=args.confirm)
    elif args.action=="approve":
        result=approve(args.job_id,args.request_sha,path=args.db,actor=args.actor,confirm=args.confirm)
    elif args.action=="claim":
        result=claim(args.job_id,path=args.db,actor=args.actor,confirm=args.confirm)
    else:
        result=close(args.job_id,{"complete":"completed","reject":"rejected","cancel":"cancelled"}[args.action],
                     0 if args.cents is None else args.cents,path=args.db,
                     actor=args.actor,confirm=args.confirm)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
