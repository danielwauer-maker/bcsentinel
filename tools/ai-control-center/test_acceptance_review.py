"""Acceptance review must remain a proposal, never a runtime approval."""
import datetime as dt
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import acceptance_review
import project_store

class AcceptanceReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"projects.sqlite3"
        con=project_store.connect(self.db)
        with con:
            known=sorted(acceptance_review.PLAYBOOK)
            ids=known+["X."+str(i) for i in range(61-len(known))]
            for i,identifier in enumerate(ids):
                con.execute("""INSERT INTO task(task_key,area,source_id,title,imported_technical,
                               imported_acceptance,updated_at) VALUES(?,?,?,?,?,?,?)""",
                    ("fiverr:"+identifier,"fiverr",identifier,"Test "+identifier,
                     int(identifier in ("1.01","1.02")),int(identifier in ("1.01","1.02")),
                     project_store.timestamp()))
            con.execute("INSERT INTO imports VALUES(?,?,?,?,?)",
                        ("fixed","tracker",61,24,project_store.timestamp()))
            con.execute("""CREATE TABLE pr_task_link(repo TEXT,number INTEGER,task_key TEXT,
                           source TEXT,reason TEXT,observed_at TEXT)""")
            con.execute("""CREATE TABLE pr_observation(repo TEXT,number INTEGER,url TEXT,
                           pr_state TEXT,title TEXT,updated_at TEXT)""")
            con.execute("INSERT INTO pr_task_link VALUES(?,?,?,?,?,?)",
                ("danielwauer-maker/bcsentinel",165,"fiverr:7.03","reviewed_reference","verified mapping",project_store.timestamp()))
            con.execute("INSERT INTO pr_observation VALUES(?,?,?,?,?,?)",
                ("danielwauer-maker/bcsentinel",165,
                 "https://github.com/danielwauer-maker/bcsentinel/pull/165",
                 "draft","Buyer Kit",project_store.timestamp()))
        con.close()
        path=Path(__file__).resolve().parent/"data/evidence-status.json"
        self.source=json.loads(path.read_text(encoding="utf-8"))

    def test_review_priority_and_no_mutations(self):
        before=project_store.read_summary(self.db)
        review=acceptance_review.review(self.source,self.db,as_of=dt.date(2026,11,12))
        after=project_store.read_summary(self.db)
        self.assertEqual(review["state"],"loaded")
        self.assertEqual(review["covered"],15)
        self.assertEqual(review["unreviewed"],46)
        self.assertEqual(review["global_release"],"NO_GO")
        self.assertEqual(after["approvals"],before["approvals"])
        self.assertEqual([r["stage"] for r in after["tasks"]],
                         [r["stage"] for r in before["tasks"]])
        self.assertTrue(all(c["state"]=="open" for r in review["items"] for c in r["criteria"]))
        self.assertEqual(review["items"][0]["priority"],"P0")

    def test_editorial_is_not_technical_or_release_ready(self):
        r=acceptance_review.review(self.source,self.db)
        items={x["id"]:x for x in r["items"]}
        self.assertEqual(items["7.03"]["review_state"],"editorial")
        self.assertEqual(items["6.02"]["review_state"],"editorial")
        self.assertEqual(items["4.01"]["review_state"],"blocked")
        self.assertEqual(items["1.01"]["review_state"],"revalidation")
        self.assertEqual(items["7.03"]["pr_links"][0]["state"],"draft")

    def test_old_or_bad_source_fails_closed(self):
        invalid=dict(self.source,schema_version=99)
        self.assertEqual(acceptance_review.review(invalid,self.db)["state"],"unavailable")
        duplicated=dict(self.source,work_items=self.source["work_items"]*2)
        self.assertEqual(acceptance_review.review(duplicated,self.db)["state"],"unavailable")

    def test_no_db_or_no_fiverr_register(self):
        self.assertEqual(acceptance_review.review(self.source,Path(self.tmp.name)/"absent.sqlite3")["state"],"not_initialized")
        with sqlite3.connect(self.db) as con:
            con.execute("DELETE FROM task WHERE task_key='fiverr:7.03'")
        self.assertEqual(acceptance_review.review(self.source,self.db)["state"],"unavailable")

if __name__=="__main__":
    unittest.main()
