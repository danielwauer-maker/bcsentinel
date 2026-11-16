"""Operator time entries must stay auditable, exact-keyed and approval-independent."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sprint_effort as effort

class EffortTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"projects.sqlite3"
        with sqlite3.connect(self.path) as con:
            con.execute("CREATE TABLE approval (id INTEGER)")
        self.valid={("fiverr","3A.2 · BC Runtime"),("saas","S1 · Plattform")}

    def test_save_cumulative_minutes_and_update_without_losing_history(self):
        first=effort.save("fiverr","3A.2 · BC Runtime",80,0,self.valid,self.path)
        self.assertEqual(first["revision"],1)
        second=effort.save("fiverr","3A.2 · BC Runtime",120,1,self.valid,self.path)
        self.assertEqual(second["revision"],2)
        stored=effort.summary(self.path)
        self.assertEqual(stored["entries"][0]["minutes"],120)
        self.assertEqual([h["new_minutes"] for h in stored["history"]],[120,80])
        with sqlite3.connect(self.path) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM approval").fetchone()[0],0)

    def test_stale_editor_is_rejected(self):
        effort.save("fiverr","3A.2 · BC Runtime",60,0,self.valid,self.path)
        with self.assertRaises(effort.EffortConflict):
            effort.save("fiverr","3A.2 · BC Runtime",100,0,self.valid,self.path)
        self.assertEqual(effort.summary(self.path)["entries"][0]["minutes"],60)

    def test_invalid_values_and_sprints_rejected(self):
        for minutes in (-1,1.5,True,1000001,"120"):
            with self.subTest(minutes=minutes),self.assertRaises(effort.EffortError):
                effort.save("fiverr","3A.2 · BC Runtime",minutes,0,self.valid,self.path)
        with self.assertRaises(effort.EffortError):
            effort.save("fiverr","not in Excel",10,0,self.valid,self.path)

    def test_read_only_summary_does_not_create_schema(self):
        out=effort.summary(self.path)
        self.assertEqual(out["state"],"not_initialized")
        with sqlite3.connect(self.path) as con:
            self.assertEqual(con.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name='sprint_effort'").fetchone()[0],0)

    def test_sprint_and_project_budgets_compare_only_recorded_sprints(self):
        source={"sprints":[
            {"area":"fiverr","sprint":"3A.2 · BC Runtime","plan_hours":4,"actual_hours":None},
            {"area":"fiverr","sprint":"4 · Reports","plan_hours":10,"actual_hours":None},
            {"area":"saas","sprint":"S1","plan_hours":None,"actual_hours":None},
        ],"timeline":{"events":[],"planned_fiverr_hours":14}}
        logs={"state":"loaded","entries":[
            {"area":"fiverr","sprint":"3A.2 · BC Runtime","minutes":180,"revision":1},
            {"area":"saas","sprint":"S1","minutes":30,"revision":1}
        ],"history":[{"area":"fiverr","sprint":"3A.2 · BC Runtime",
                     "new_minutes":180,"recorded_at":"2026-11-16T12:00:00Z"}]}
        merged=effort.attach(source,logs)
        self.assertEqual(merged["effort"]["comparable_sprints"],1)
        self.assertEqual(merged["effort"]["budget_used_percent"],75)
        self.assertEqual(merged["timeline"]["actual_logged_hours"],3.5)
        self.assertEqual(merged["sprints"][1]["actual_minutes"],None)
        self.assertEqual(merged["timeline"]["events"][0]["kind"],"manual_minutes")

if __name__=="__main__":
    unittest.main()
