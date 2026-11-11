"""Evidence matching must be conservative and must never approve a task."""
import sqlite3
import tempfile
from pathlib import Path
import unittest
import pm_sync
import project_store

class PMSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"pm.sqlite3"
        con=project_store.connect(self.db)
        with con:
            for key,area,source in [("fiverr:6.02","fiverr","6.02"),("fiverr:7.03","fiverr","7.03"),("saas:S1.01","saas","S1.01")]:
                con.execute("INSERT INTO task(task_key,area,source_id,title,updated_at) VALUES(?,?,?,?,?)",
                            (key,area,source,key,project_store.timestamp()))
            con.execute("INSERT INTO imports VALUES(?,?,?,?,?)",("hash","sample",61,24,project_store.timestamp()))
        con.close()

    def pr(self,title="docs: Sprint 6.02",number=166,body="",state="draft",repo="danielwauer-maker/bcsentinel"):
        return {"repo":repo,"number":number,"title":title,"body":body,
                "head_ref":"","state":state,"updated_at":"2026-11-11T20:00:00Z",
                "url":f"https://github.com/{repo}/pull/{number}"}

    def test_matching_requires_explicit_sprint_and_unique_task(self):
        tasks=[{"task_key":"fiverr:6.02","source_id":"6.02"},
               {"task_key":"fiverr:7.03","source_id":"7.03"}]
        self.assertEqual(pm_sync.match_tasks(self.pr(),tasks)["task_keys"],["fiverr:6.02"])
        self.assertEqual(pm_sync.match_tasks(self.pr("6.02 update"),tasks)["state"],"unmatched")
        self.assertEqual(pm_sync.match_tasks(self.pr("Sprint 6.02 and Sprint 7.03"),tasks)["state"],"ambiguous")
        self.assertEqual(pm_sync.match_tasks(self.pr("Sprint 6.02"),tasks+tasks[:1])["state"],"ambiguous")

    def test_repeated_same_evidence_is_noop_and_gates_untouched(self):
        p=self.pr()
        first=pm_sync.reconcile([p],[],self.db)
        self.assertEqual((first["matched"],first["changed"]),(1,0))
        second=pm_sync.reconcile([p],[],self.db)
        self.assertEqual(second["changed"],0)
        b=pm_sync.briefing(self.db)
        self.assertEqual(b["state"],"loaded")
        self.assertEqual(len(b["observations"]),1)
        state=project_store.read_summary(self.db)
        self.assertEqual(state["approvals"],[])
        self.assertTrue(all(row["stage"]=="planned" for row in state["tasks"]))

    def test_partial_source_preserves_prior_evidence(self):
        pm_sync.reconcile([self.pr()],[],self.db)
        r=pm_sync.reconcile([], [{"repo":"danielwauer-maker/bcsentinel-frontend","state":"unavailable"}],self.db)
        self.assertEqual(r["state"],"partial")
        self.assertEqual(len(pm_sync.briefing(self.db)["observations"]),1)

    def test_changed_state_logged_as_a_new_observation(self):
        pm_sync.reconcile([self.pr()],[],self.db)
        p=self.pr(state="closed")
        r=pm_sync.reconcile([p],[],self.db)
        self.assertEqual(r["changed"],1)
        b=pm_sync.briefing(self.db)
        self.assertEqual(b["observations"][0]["pr_state"],"closed")

    def test_invalid_url_rejected(self):
        p=self.pr()
        p["url"]="https://evil.test/pull/166"
        r=pm_sync.reconcile([p],[],self.db)
        self.assertEqual(r["changed"],0)

    def test_collect_failed_repo_does_not_forge_complete(self):
        def fetch(path):
            if "frontend" in path: return {"state":"unavailable","reason":"404"}
            return [{"number":166,"title":"Sprint 6.02","html_url":"https://github.com/danielwauer-maker/bcsentinel/pull/166",
                     "state":"open","head":{"ref":"feature/docs"},"updated_at":"2026-11-11T20:00:00Z"}]
        pulls,errors=pm_sync.collect(fetch)
        self.assertEqual(len(pulls),1)
        self.assertEqual(len(errors),1)

if __name__=="__main__":unittest.main()
