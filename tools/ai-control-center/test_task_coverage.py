"""Full 61-task Fiverr inventory must not claim 61 evidence reviews."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import acceptance_review
import blocker_plan
import project_store
import task_coverage


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"db.sqlite3"
        self.source=json.loads((Path(__file__).resolve().parent/"data/evidence-status.json").read_text(encoding="utf-8"))
        known=sorted(acceptance_review.PLAYBOOK)
        ids=known+[f"8.{i:02d}" for i in range(1,62-len(known))]
        self.assertEqual(len(ids),61)
        rows=[]
        for i,identifier in enumerate(ids):
            rows.append({"id":identifier,"title":"Fiverr Task "+identifier,"area":"fiverr",
                         "sprint":"Test","notes":"","technical_checked":i<2,"live_checked":i<2,
                         "plan_hours":i+1})
        for i in range(24):
            rows.append({"id":f"S.{i:02d}","title":"SaaS", "area":"saas","sprint":"SaaS",
                         "technical_checked":False,"live_checked":False})
        self.tracker={"state":"loaded","sha256":"verified-fixture","filename":"test.xlsx","rows":rows}
        project_store.import_rows(self.tracker,self.db)
        self.acceptance=acceptance_review.review(self.source,self.db)
        self.plan=blocker_plan.analyze(self.acceptance)

    def result(self):
        return task_coverage.catalog(self.tracker,self.acceptance,self.plan,self.db)

    def test_all_61_inventory_but_only_15_evidence_reviewed(self):
        result=self.result()
        self.assertEqual(result["state"],"loaded")
        self.assertEqual((result["total"],result["reviewed"],result["needs_review"]),(61,15,46))
        self.assertEqual((result["dependency_modeled"],result["dependency_unknown"]),(15,46))
        self.assertEqual(result["unassigned_priority"],46)
        self.assertEqual(result["global_release"],"NO_GO")
        self.assertEqual(len({r["task_key"] for r in result["items"]}),61)
        unknown=next(r for r in result["items"] if r["id"]=="8.01")
        self.assertIsNone(unknown["priority"])
        self.assertEqual(unknown["review_state"],"unknown")
        self.assertEqual(unknown["dependency_coverage"],"unmodeled")
        self.assertEqual(unknown["direct_prerequisites"],[])
        self.assertEqual(unknown["acceptance_criteria"],[])
        self.assertEqual(unknown["observed_prs"],[])
        known=next(r for r in result["items"] if r["id"]=="7.03")
        self.assertEqual(known["priority"],"P1")
        self.assertIn("4.01",known["direct_prerequisites"])
        self.assertEqual(known["review_coverage"],"curated")

    def test_uncurated_pr_link_does_not_count_as_review(self):
        con=project_store.connect(self.db)
        with con:
            con.execute("""CREATE TABLE pr_task_link(repo TEXT,number INTEGER,task_key TEXT,
                         source TEXT,reason TEXT,observed_at TEXT)""")
            con.execute("""CREATE TABLE pr_observation(repo TEXT,number INTEGER,
                         url TEXT,pr_state TEXT,updated_at TEXT)""")
            repo="danielwauer-maker/bcsentinel"
            url=f"https://github.com/{repo}/pull/123"
            con.execute("INSERT INTO pr_observation VALUES(?,?,?,?,?)",
                (repo,123,url,"draft","2026-11-12T00:00:00Z"))
            con.execute("INSERT INTO pr_task_link VALUES(?,?,?,?,?,?)",
                (repo,123,"fiverr:8.01","explicit_sprint_marker","Observed PR","2026-11-12T00:00:00Z"))
        con.close()
        state=self.result()
        candidate=next(r for r in state["items"] if r["id"]=="8.01")
        self.assertEqual(candidate["review_coverage"],"unreviewed")
        self.assertEqual(candidate["priority"],None)
        self.assertEqual(len(candidate["observed_prs"]),1)
        self.assertEqual(state["reviewed"],15)

    def test_source_version_and_metadata_mismatch_fail_closed(self):
        t=copy.deepcopy(self.tracker)
        t["sha256"]="different"
        self.assertEqual(task_coverage.catalog(t,self.acceptance,self.plan,self.db)["state"],"unavailable")
        t=copy.deepcopy(self.tracker)
        t["rows"][0]["title"]="changed"
        self.assertEqual(task_coverage.catalog(t,self.acceptance,self.plan,self.db)["state"],"unavailable")
        t=copy.deepcopy(self.tracker)
        t["rows"][0]["technical_checked"]=False
        self.assertEqual(task_coverage.catalog(t,self.acceptance,self.plan,self.db)["state"],"unavailable")
        t=copy.deepcopy(self.tracker)
        t["rows"][0]["id"]=t["rows"][1]["id"]
        self.assertEqual(task_coverage.catalog(t,self.acceptance,self.plan,self.db)["state"],"unavailable")
        t=copy.deepcopy(self.tracker)
        t["state"]="snapshot_only"
        self.assertEqual(task_coverage.catalog(t,self.acceptance,self.plan,self.db)["state"],"unavailable")

    def test_never_writes_approval_or_stage(self):
        before=project_store.read_summary(self.db)
        task_coverage.catalog(self.tracker,self.acceptance,self.plan,self.db)
        after=project_store.read_summary(self.db)
        self.assertEqual(before["approvals"],after["approvals"])
        self.assertEqual(before["tasks"],after["tasks"])
        self.assertEqual(before["recent_events"],after["recent_events"])


if __name__=="__main__":
    unittest.main()
