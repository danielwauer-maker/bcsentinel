"""AI-PM 1.4 dependency planning is read-only and fail-closed."""
import copy
import json
import tempfile
from pathlib import Path
import unittest

import acceptance_review
import blocker_plan
import project_store

class BlockerPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"db.sqlite3"
        con=project_store.connect(self.db)
        known=sorted(acceptance_review.PLAYBOOK)
        identifiers=known+["X."+str(i) for i in range(61-len(known))]
        with con:
            for id in identifiers:
                con.execute("INSERT INTO task(task_key,area,source_id,title,updated_at) VALUES(?,?,?,?,?)",
                            ("fiverr:"+id,"fiverr",id,"Task "+id,project_store.timestamp()))
            con.execute("INSERT INTO imports VALUES(?,?,?,?,?)",
                        ("fixture","test",61,24,project_store.timestamp()))
        con.close()
        source=json.loads((Path(__file__).resolve().parent/"data/evidence-status.json").read_text())
        self.review=acceptance_review.review(source,self.db)
        assert self.review["state"]=="loaded"

    def test_expected_roots_and_critical_downstream_reach(self):
        result=blocker_plan.analyze(self.review)
        self.assertEqual(result["state"],"loaded")
        self.assertEqual(result["modeled_tasks"],15)
        self.assertEqual(result["unmodeled_fiverr_tasks"],46)
        self.assertEqual(result["edge_count"],len(blocker_plan.EDGES))
        roots={v["id"] for v in result["upstream_p0_reviews"]}
        self.assertEqual(roots,{"1.01","1.02","4.01"})
        items={x["id"]:x for x in result["items"]}
        self.assertIn("7.03",items["4.01"]["downstream_tasks"])
        self.assertIn("3.04",items["1.03"]["downstream_tasks"])
        self.assertIn("4.01",items["7.03"]["unverified_prerequisites"])
        self.assertEqual(items["7.03"]["review_phase"],"review_with_prerequisites")
        self.assertEqual(result["global_release"],"NO_GO")

    def test_historic_checkbox_does_not_clear_dependency(self):
        r=copy.deepcopy(self.review)
        for x in r["items"]:
            if x["id"]=="1.01":
                x["technical_checked_historic"]=True
                x["go_live_checked_historic"]=True
        plan=blocker_plan.analyze(r)
        item=next(x for x in plan["items"] if x["id"]=="1.03")
        self.assertIn("1.01",item["unverified_prerequisites"])

    def test_independent_attestations_are_only_signals_not_release(self):
        r=copy.deepcopy(self.review)
        next(x for x in r["items"] if x["id"]=="4.01")["attested_gates"]=["technical","dev"]
        p=blocker_plan.analyze(r)
        full=next(x for x in p["items"] if x["id"]=="4.02")
        self.assertEqual(full["unverified_prerequisites"],[])
        self.assertEqual(full["review_phase"],"review_prerequisites_attested")
        self.assertEqual(p["global_release"],"NO_GO")
        self.assertIn("keine Vertrags",full["gate_caution"])

    def test_fail_closed_missing_or_cyclic_model(self):
        self.assertEqual(blocker_plan.analyze({"state":"missing"})["state"],"unavailable")
        changed=copy.deepcopy(self.review)
        changed["items"].pop()
        self.assertEqual(blocker_plan.analyze(changed)["state"],"unavailable")
        original=blocker_plan.EDGES
        try:
            blocker_plan.EDGES=original+(("7.03","4.01","introduce cycle"),)
            self.assertEqual(blocker_plan.analyze(self.review)["state"],"unavailable")
        finally:
            blocker_plan.EDGES=original

    def test_never_writes_to_database(self):
        before=project_store.read_summary(self.db)
        blocker_plan.analyze(self.review)
        after=project_store.read_summary(self.db)
        self.assertEqual(after["approvals"],before["approvals"])
        self.assertEqual(after["recent_events"],before["recent_events"])

if __name__=="__main__":
    unittest.main()
