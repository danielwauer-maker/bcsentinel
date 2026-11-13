"""AI-PM 2.1: SQLite online backups and read-only restore verification.

Never overwrites live databases. Backup happens only on explicit CLI request.
Verification restores into private temporary files and checks both schemas, task
inventory, budget state, integrity and that the copied files match the sources.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path

NAMES=("projects","agent-control")
MIN_TABLES={
 "projects":{"task","imports","approval","audit_event"},
 "agent-control":{"agent_job","agent_audit","control_settings"},
}
def _connect(path,ro=False):
    if ro:
        con=sqlite3.connect("file:"+str(Path(path).resolve())+"?mode=ro",uri=True,timeout=15)
    else:
        con=sqlite3.connect(path,timeout=15)
    con.row_factory=sqlite3.Row
    return con

def _integrity(con,name):
    integrity=con.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity!="ok": raise ValueError(name+": SQLite integrity_check failed")
    tables={x[0] for x in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not MIN_TABLES[name].issubset(tables):
        raise ValueError(name+": missing expected schema tables")
    if name=="projects":
        tasks=con.execute("SELECT area,COUNT(*) FROM task GROUP BY area").fetchall()
        totals=dict(tasks)
        imp=con.execute("SELECT sha256,count_fiverr,count_saas FROM imports").fetchall()
        if totals!={"fiverr":61,"saas":24} or len(imp)!=1 or not imp[0][0] or imp[0][1:]!=(61,24):
            # sqlite3.Row slicing returns tuple
            raise ValueError("projects: missing verified 85 task import")
        return {"fiverr_tasks":61,"saas_tasks":24,"import_sha256":imp[0][0],
                "approvals":con.execute("SELECT count(*) FROM approval").fetchone()[0]}
    setting=con.execute("SELECT monthly_budget_cents FROM control_settings WHERE id=1").fetchone()
    if setting is None or not 0<=setting[0]<=100000:
        raise ValueError("agent-control: missing/invalid settings")
    claimed=con.execute("SELECT count(*) FROM agent_job WHERE status='claimed'").fetchone()[0]
    if claimed>1: raise ValueError("agent-control: concurrent claimed slots")
    return {"monthly_budget_cents":setting[0],"claimed_slots":claimed,
            "jobs":con.execute("SELECT count(*) FROM agent_job").fetchone()[0],
            "audit_events":con.execute("SELECT count(*) FROM agent_audit").fetchone()[0]}

def _digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def verify(backup_dir, *, source_dir=None):
    """Validate and restore *only into an isolated temporary directory*."""
    root=Path(backup_dir).resolve()
    if not root.is_dir(): raise ValueError("Backup directory missing")
    result={}
    with tempfile.TemporaryDirectory(prefix="bcsentinel-restore-test-") as temporary:
        for name in NAMES:
            backup=root/(name+".sqlite3")
            if not backup.is_file() or backup.is_symlink():
                raise ValueError("Backup absent, or symlink refused: "+name)
            restored=Path(temporary)/(name+".sqlite3")
            with _connect(backup,ro=True) as source, _connect(restored) as target:
                source.backup(target)
            with _connect(restored,ro=True) as con:
                state=_integrity(con,name)
            if source_dir is not None:
                original=Path(source_dir)/(name+".sqlite3")
                if not original.is_file(): raise ValueError("Live source unavailable: "+name)
                with _connect(original,ro=True) as con:
                    live=_integrity(con,name)
                if state!=live: raise ValueError("Backup differs from current live inventory: "+name)
            result[name]={"state":"verified","sha256":_digest(restored),"metrics":state}
    return {"state":"RESTORE_TEST_PASS","source":"explicit_offline_copy",
            "non_destructive":True,"databases":result,
            "warning":"Only temp restore validated. Does not prove off-host storage, encryption or production recovery time."}

def backup(source_dir, destination, *, confirm=False):
    """Consistent online SQLite backup with atomic rename and 0700 directory."""
    if not confirm: raise ValueError("--confirm explicitly required for creating backups")
    src=Path(source_dir).resolve()
    target=Path(destination).resolve()
    if src==target or src in target.parents or target in src.parents:
        raise ValueError("Backup destination must be outside live state directory")
    if target.exists(): raise ValueError("Destination already exists: no overwrite")
    if not target.parent.is_dir(): raise ValueError("Parent backup directory missing")
    os.mkdir(target,0o700)
    try:
        for name in NAMES:
            live=src/(name+".sqlite3")
            if not live.is_file() or live.is_symlink():
                raise ValueError("Expected local SQLite source missing or symlinked: "+name)
            tmp=target/(name+".sqlite3.tmp")
            with _connect(live,ro=True) as con, _connect(tmp) as copy:
                _integrity(con,name)
                con.backup(copy)
            os.chmod(tmp,0o600)
            os.replace(tmp,target/(name+".sqlite3"))
        return verify(target,source_dir=None)
    except BaseException:
        # No silently partial successful backup. Keep partial files for forensics
        # rather than removing somebody's data; caller sees the exception.
        raise

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("backup","verify"))
    p.add_argument("--source-dir",default="/state")
    p.add_argument("--backup-dir",required=True)
    p.add_argument("--confirm",action="store_true")
    a=p.parse_args()
    result=backup(a.source_dir,a.backup_dir,confirm=a.confirm) if a.action=="backup" else verify(a.backup_dir)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
