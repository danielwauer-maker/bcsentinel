"""AI-PM 2.1 disaster recovery: both SQLite databases, rollback and idempotence."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import backup_verify as b
import project_store
import agent_control

SHA="c1978141c8ee70f52be07ba64df765364a56cb16fe51dea4b084951ade60142a"

class BackupRestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.state=self.root/"state"
        self.state.mkdir()
        rows=[{"area":"fiverr","id":f"{i}.01","title":"Review","sprint":"Sprint",
               "technical_checked":False,"live_checked":False} for i in range(1,62)]
        rows.extend({"area":"saas","id":f"S{i}.01","title":"SaaS","sprint":"S",
                     "technical_checked":False,"live_checked":False} for i in range(1,25))
        project_store.import_rows({"state":"loaded","sha256":SHA,"filename":"fixture.xlsx",
                                   "rows":rows},self.state/"projects.sqlite3")
        agent_control.init(self.state/"agent-control.sqlite3",actor="operator",confirm=True)

    def test_fresh_online_backup_and_temp_restore_preserve_85_and_audit(self):
        destination=self.root/"backup"
        result=b.backup(self.state,destination,confirm=True)
        self.assertEqual(result["state"],"RESTORE_TEST_PASS")
        self.assertTrue(result["non_destructive"])
        self.assertEqual(result["databases"]["projects"]["metrics"]["fiverr_tasks"],61)
        self.assertEqual(result["databases"]["projects"]["metrics"]["saas_tasks"],24)
        self.assertEqual(result["databases"]["agent-control"]["metrics"]["monthly_budget_cents"],0)
        self.assertEqual(result["databases"]["agent-control"]["metrics"]["audit_events"],1)
        self.assertEqual(b.verify(destination)["state"],"RESTORE_TEST_PASS")
        self.assertEqual(project_store.read_summary(self.state/"projects.sqlite3")["counts"],
                         {"fiverr":61,"saas":24})
        self.assertEqual(agent_control.read_status(self.state/"agent-control.sqlite3")["state"],"loaded")

    def test_backup_requires_confirmation_and_never_overwrites(self):
        destination=self.root/"backup"
        with self.assertRaises(ValueError):
            b.backup(self.state,destination)
        b.backup(self.state,destination,confirm=True)
        with self.assertRaises(ValueError):
            b.backup(self.state,destination,confirm=True)
        with self.assertRaises(ValueError):
            b.backup(self.state,self.state/"subfolder",confirm=True)

    def test_missing_or_corrupt_backup_is_rejected(self):
        target=self.root/"backup"
        b.backup(self.state,target,confirm=True)
        (target/"agent-control.sqlite3").unlink()
        with self.assertRaises(ValueError):
            b.verify(target)
        with sqlite3.connect(target/"projects.sqlite3") as con:
            con.execute("DELETE FROM imports")
        with self.assertRaises(ValueError):
            b.verify(target)

    def test_backup_is_consistent_against_outstanding_wal_writes(self):
        # SQLite Online Backup API captures a coherent snapshot while a separate
        # source connection remains open with committed WAL contents.
        db=self.state/"agent-control.sqlite3"
        con=sqlite3.connect(db)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("INSERT INTO agent_audit(job_id,event,actor,detail,created_at) VALUES(NULL,'test','operator','{}','2026-11-12')")
        con.commit()
        result=b.backup(self.state,self.root/"backup",confirm=True)
        con.close()
        self.assertEqual(result["databases"]["agent-control"]["metrics"]["audit_events"],2)

    def test_verification_never_modifies_source_or_backup(self):
        destination=self.root/"backup"
        b.backup(self.state,destination,confirm=True)
        original=(self.state/"projects.sqlite3").read_bytes()
        archived=(destination/"projects.sqlite3").read_bytes()
        for _ in range(2):
            b.verify(destination)
        self.assertEqual(original,(self.state/"projects.sqlite3").read_bytes())
        self.assertEqual(archived,(destination/"projects.sqlite3").read_bytes())

if __name__=="__main__":unittest.main()
