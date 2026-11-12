"""AI-PM 1.6 must separate plan, stages, reviews and independently attested gates."""
import copy
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

import acceptance_review
import blocker_plan
import pm_insights
import progress_history
import project_store
import readiness
import task_coverage

class InsightsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"db.sqlite3"
        master=json.loads((Path(__file__).resolve().parent/"data/evidence-status.json").read_text())
        reviewed_ids=sorted(acceptance_review.PLAYBOOK)
        ids=reviewed_ids+[f"8.{i:02d}" for i in range(1,62-len(reviewed_ids))]
        hours=[2,3]+[4]*58+[50]
        rows=[]
        for i,identifier in enumerate(ids):
            rows.append({"area":"fiverr","id":identifier,"title":"Task "+identifier,
                         "sprint":"Sprint", "notes":"note","plan_hours":hours[i],
                         "technical_checked":i<2,"live_checked":i<2})
        rows += [{"area":"saas","id":f"S{i}","title":"SaaS", "sprint":"SaaS",
                  "technical_checked":False,"live_checked":False} for i in range(24)]
        self.tracker={"state":"loaded","sha256":"test-v16","filename":"fixture.xlsx",
                      "rows":rows,"planning_issue_date":"11.11.2026",
                      "hours_per_week":20,"legacy_start_fraction":0.65}
        project_store.import_rows(self.tracker,self.db)
        progress_history.init_baseline(self.tracker,self.db)
        self.master=master

    def parts(self,as_of=dt.date(2026,11,12)):
        review=acceptance_review.review(self.master,self.db,as_of=as_of)
        plan=blocker_plan.analyze(review)
        coverage=task_coverage.catalog(self.tracker,review,plan,self.db)
        history=progress_history.history(self.db)
        ready=progress_history.apply_to_readiness(readiness.fiverr_readiness(self.tracker,as_of=as_of),
                                                  history,as_of=as_of)
        return coverage,review,plan,ready,history

    def test_baseline_stage_counts_and_45_open_criteria(self):
        parts=self.parts()
        r=pm_insights.assess(*parts,as_of=dt.date(2026,11,12))
        self.assertEqual(r["state"],"loaded")
        self.assertEqual(r["work_status"]["total"],61)
        self.assertEqual(r["work_status"]["raw_stage_counts"]["planned"],61)
        self.assertEqual(r["work_status"]["historical_excel_technical"],2)
        self.assertEqual(r["work_status"]["independent_dev_attested"],0)
        self.assertEqual(r["evidence_quality"]["curated_review_tasks"],15)
        self.assertEqual(r["evidence_quality"]["unreviewed_tasks"],46)
        self.assertEqual(r["risk_summary"]["p0_review_tasks"],13)
        self.assertEqual(r["risk_summary"]["p0_open_criteria"],39)
        self.assertIsNone(r["schedule"]["delay_days"])
        self.assertEqual(r["schedule"]["interpretation"],"baseline_only")
        self.assertIn(r["next_action"]["task_id"],{"1.01","1.02","4.01"})
        self.assertEqual(r["global_release"],"NO_GO")

    def test_observed_pr_and_stage_do_not_create_acceptance(self):
        con=project_store.connect(self.db)
        with con:
            con.execute("UPDATE task SET stage='implementation_candidate' WHERE task_key='fiverr:8.01'")
            con.execute("""CREATE TABLE pr_task_link(repo TEXT,number INTEGER,task_key TEXT,
                         source TEXT,reason TEXT,observed_at TEXT)""")
            con.execute("""CREATE TABLE pr_observation(repo TEXT,number INTEGER,
                         url TEXT,pr_state TEXT,title TEXT,updated_at TEXT)""")
            repo="danielwauer-maker/bcsentinel"
            con.execute("INSERT INTO pr_task_link VALUES(?,?,?,?,?,?)",
                        (repo,99,"fiverr:8.01","explicit_sprint_marker","observation","2026-11-12T00:00:00Z"))
            con.execute("INSERT INTO pr_observation VALUES(?,?,?,?,?,?)",
                        (repo,99,f"https://github.com/{repo}/pull/99","draft","Observed PR","2026-11-12T00:00:00Z"))
        con.close()
        r=pm_insights.assess(*self.parts())
        self.assertEqual(r["work_status"]["raw_stage_counts"]["implementation_candidate"],1)
        self.assertEqual(r["evidence_quality"]["unreviewed_with_pr_observations"],1)
        self.assertEqual(r["evidence_quality"]["curated_review_tasks"],15)
        self.assertEqual(r["work_status"]["independent_dev_attested"],0)
        self.assertEqual(len(project_store.read_summary(self.db)["approvals"]),0)

    def test_age_of_review_is_not_age_of_pr(self):
        r=pm_insights.assess(*self.parts(dt.date(2027,1,12)),as_of=dt.date(2027,1,12))
        self.assertTrue(r["evidence_quality"]["review_source_stale"])
        self.assertEqual(r["evidence_quality"]["review_source_age_days"],62)
        self.assertIn("OLD_REVIEW_SOURCE",[x["code"] for x in r["risk_summary"]["risks"]])

    def test_refuse_mismatched_sources_and_missing_history(self):
        parts=list(self.parts())
        parts[0]=copy.deepcopy(parts[0])
        parts[0]["source_sha256"]="not-same"
        self.assertEqual(pm_insights.assess(*parts)["state"],"unavailable")
        parts=list(self.parts())
        parts[4]={"state":"not_initialized"}
        self.assertEqual(pm_insights.assess(*parts)["state"],"unavailable")

    def test_still_no_go_after_separately_attested_gates(self):
        progress_history.record("fiverr:8.01","technical","maker","reviewer",
            "https://github.com/danielwauer-maker/bcsentinel/pull/99",
            "Evidence independently inspected and documented",self.db,confirm=True)
        progress_history.record("fiverr:8.01","dev","maker","reviewer",
            "https://github.com/danielwauer-maker/bcsentinel/pull/99",
            "Sandbox execution independently inspected and documented",self.db,confirm=True)
        p=self.parts()
        r=pm_insights.assess(*p)
        self.assertEqual(r["work_status"]["independent_dev_attested"],1)
        self.assertEqual(r["global_release"],"NO_GO")
        self.assertEqual(r["schedule"]["forecast_reliability"],"not_established")
        self.assertEqual(r["schedule"]["interpretation"],"attested_history_but_incomplete")

    def test_read_only_against_sqlite(self):
        before=project_store.read_summary(self.db)
        pm_insights.assess(*self.parts())
        after=project_store.read_summary(self.db)
        self.assertEqual(before["approvals"],after["approvals"])
        self.assertEqual(before["tasks"],after["tasks"])
        self.assertEqual(before["recent_events"],after["recent_events"])

if __name__=="__main__":
    unittest.main()
