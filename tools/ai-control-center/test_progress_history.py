"""AI-PM 1.2: historical baseline and independent gate attestations."""
import datetime as dt
import tempfile
from pathlib import Path
import sqlite3
import unittest
import project_store
import progress_history
import readiness
from test_project_store import source as fixture

def plan():
    s=fixture()
    planned_hours=[2,3]+[4]*58+[50]
    for i,r in enumerate(x for x in s["rows"] if x["area"]=="fiverr"):
        r["plan_hours"]=planned_hours[i]
    s["planning_issue_date"]="Stand 11.11.2026"
    s["legacy_start_fraction"]=0.65
    s["hours_per_week"]=20
    return s

class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"projects.sqlite3"
        self.s=plan()
        project_store.import_rows(self.s,self.db)

    def initialize(self):
        return progress_history.init_baseline(self.s,self.db)

    def attest(self,gate,task="fiverr:3.01",**kwargs):
        return progress_history.record(
            task,gate,"implementer","independent-reviewer",
            "https://github.com/danielwauer-maker/bcsentinel/pull/165",
            "Reviewed explicit evidence and documented DEV behavior",self.db,confirm=True,**kwargs)

    def test_baseline_idempotent_and_historic_flags_not_duplicated(self):
        self.assertEqual(self.initialize()["tasks"],61)
        self.assertEqual(self.initialize()["state"],"already_initialized")
        h=progress_history.history(self.db)
        self.assertEqual(h["count_events"],0)
        self.assertEqual(h["counts"]["technical"],2)
        self.assertEqual(h["counts"]["go_live"],2)
        self.assertEqual(len(h["points"]),1)
        self.assertEqual(project_store.read_summary(self.db)["approvals"],[])

    def test_pr_activity_does_not_change_readiness(self):
        self.initialize()
        initial=readiness.fiverr_readiness(self.s,as_of=dt.date(2026,11,12))
        overlay=progress_history.apply_to_readiness(initial,progress_history.history(self.db),
                                                    as_of=dt.date(2026,11,12))
        self.assertEqual(overlay["legacy_estimate_fraction"],initial["legacy_estimate_fraction"])
        self.assertEqual(overlay["gate_count"],2)
        self.assertEqual(overlay["history_event_count"],0)

    def test_gate_order_and_independent_reviewer(self):
        self.initialize()
        with self.assertRaises(ValueError):
            progress_history.record("fiverr:3.01","technical","same","same",
                "https://github.com/danielwauer-maker/bcsentinel/pull/165",
                "Enough evidence documentation",self.db,confirm=True)
        with self.assertRaises(ValueError):self.attest("go_live")
        with self.assertRaises(ValueError):self.attest("dev")
        with self.assertRaises(ValueError):
            progress_history.record("fiverr:3.01","technical","actor","reviewer",
                "https://github.com/danielwauer-maker/bcsentinel/pull/165",
                "Enough evidence documentation",self.db,confirm=False)
        self.attest("implementation")
        self.attest("technical")
        self.attest("dev")
        self.attest("go_live")
        with self.assertRaises(sqlite3.IntegrityError): self.attest("go_live")
        h=progress_history.history(self.db)
        self.assertEqual(h["count_events"],4)
        self.assertEqual(h["counts"]["technical"],3)
        self.assertEqual(h["counts"]["dev"],1)
        self.assertEqual(h["counts"]["go_live"],3)
        self.assertEqual(h["global_release"],"NO_GO")
        self.assertEqual(len(project_store.read_summary(self.db)["approvals"]),3)
        self.assertEqual(project_store.read_summary(self.db)["tasks"][2]["stage"],"planned")

    def test_history_growth_and_no_double_count(self):
        self.initialize()
        before=readiness.fiverr_readiness(self.s,as_of=dt.date(2026,11,12))
        self.attest("technical")
        self.attest("dev")
        self.attest("go_live")
        after=progress_history.apply_to_readiness(before,progress_history.history(self.db),
                                                  as_of=dt.date(2026,11,12))
        self.assertEqual(after["gate_count"],3)
        self.assertEqual(after["technical_count"],3)
        self.assertGreater(after["legacy_estimate_fraction"],before["legacy_estimate_fraction"])
        self.assertLess(after["remaining_hours"],before["remaining_hours"])
        self.assertEqual(after["go_live"],"NO_GO")
        self.assertEqual(after["history_event_count"],3)
        self.assertTrue(after["timeline"]["actual_series"])

    def test_reject_changed_workbook_and_historic_duplicates(self):
        self.initialize()
        changed=plan()
        changed["sha256"]="different"
        with self.assertRaises(ValueError):progress_history.init_baseline(changed,self.db)
        with self.assertRaises(ValueError):self.attest("technical","fiverr:1.01")
        with self.assertRaises(ValueError):self.attest("go_live","fiverr:1.01")
        with self.assertRaises(ValueError):self.attest("technical","saas:3.01")
        self.assertEqual(len(project_store.read_summary(self.db)["approvals"]),0)

    def test_overlay_refuses_mismatched_master(self):
        self.initialize()
        h=progress_history.history(self.db)
        r=readiness.fiverr_readiness(self.s,as_of=dt.date(2026,11,12))
        r["source_sha256"]="changed"
        result=progress_history.apply_to_readiness(r,h,as_of=dt.date(2026,11,12))
        self.assertNotEqual(result["history_status"],"loaded")
        self.assertNotIn("history_event_count",result)

if __name__=="__main__":unittest.main()
