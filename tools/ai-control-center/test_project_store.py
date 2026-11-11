"""Persistence contracts for the one-time Master-Tracker migration."""
import sqlite3
import tempfile
from pathlib import Path
import unittest

import project_store


def source():
    rows=[]
    for area,count in (("fiverr",61),("saas",24)):
        for i in range(count):
            rows.append({"id":f"{i+1}.01","area":area,"title":f"Task {i+1}",
                         "sprint":"S1","notes":"Note","technical_checked":i<2 and area=="fiverr",
                         "live_checked":i<2 and area=="fiverr"})
    return {"state":"loaded","sha256":"abc123","filename":"tracker.xlsx","rows":rows}


class ImportTests(unittest.TestCase):
    def test_one_time_import_and_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/"tasks.sqlite3"
            result=project_store.import_rows(source(),db)
            self.assertEqual(result["state"],"imported")
            state=project_store.read_summary(db)
            self.assertEqual(state["counts"],{"fiverr":61,"saas":24})
            self.assertEqual(sum(r["imported_technical"] for r in state["tasks"]),2)
            with sqlite3.connect(db) as c:
                c.execute("UPDATE task SET stage='in_progress', manually_edited=1 WHERE task_key='fiverr:1.01'")
            again=project_store.import_rows(source(),db)
            self.assertEqual(again["state"],"already_imported")
            state=project_store.read_summary(db)
            self.assertEqual(next(r["stage"] for r in state["tasks"] if r["task_key"]=="fiverr:1.01"),"in_progress")

    def test_mismatched_version_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/"tasks.sqlite3"
            project_store.import_rows(source(),db)
            changed=source()
            changed["sha256"]="different"
            with self.assertRaises(ValueError):
                project_store.import_rows(changed,db)

    def test_unverified_excel_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/"tasks.sqlite3"
            with self.assertRaises(ValueError):
                project_store.import_rows({"state":"snapshot_only","sha256":"abc123","rows":source()["rows"]},db)
            self.assertFalse(db.exists())

    def test_duplicate_identifiers_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/"tasks.sqlite3"
            s=source()
            s["rows"][2]["id"]=s["rows"][1]["id"]
            with self.assertRaises(ValueError):
                project_store.import_rows(s,db)

    def test_no_automatic_approvals(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/"tasks.sqlite3"
            project_store.import_rows(source(),db)
            state=project_store.read_summary(db)
            self.assertEqual(state["approvals"],[])
            self.assertEqual(len(state["recent_events"]),1)


if __name__=="__main__":
    unittest.main()
