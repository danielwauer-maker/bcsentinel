"""AI-PM 1.1: reviewed references, safe multi-link attribution and no gate promotion."""
import tempfile
from pathlib import Path
import unittest

import pm_mapping
import pm_sync
import project_store

REPO="danielwauer-maker/bcsentinel"

def pr(number=165,title="Buyer kit",repo=REPO):
    return {"repo":repo,"number":number,"title":title,"body":"",
            "head_ref":"","state":"draft","updated_at":"2026-11-11T20:00:00Z",
            "url":f"https://github.com/{repo}/pull/{number}"}

TASKS=[{"task_key":f"fiverr:{id}","source_id":id} for id in
       ["2.02","3.02","4.01","4.02","4.03","4.04","4.06","6.02","7.03"]]

class MappingTests(unittest.TestCase):
    def test_curated_multi_task_reference(self):
        reviewed=pm_mapping.curated_map({"work_items":[
            {"id":"4.02","refs":[f"https://github.com/{REPO}/pull/154"]},
            {"id":"4.03","refs":[f"https://github.com/{REPO}/pull/154"]},
            {"id":"4.04","refs":[f"https://github.com/{REPO}/pull/154"]}]})
        found=pm_mapping.match_evidence(pr(154,"Access-v2"),TASKS,reviewed)
        self.assertEqual(found["state"],"reviewed")
        self.assertEqual({v["task_key"] for v in found["links"]},
                         {"fiverr:4.02","fiverr:4.03","fiverr:4.04"})

    def test_curated_ignores_unreviewed_domains_and_cross_cutting(self):
        reviewed=pm_mapping.curated_map({"work_items":[
            {"id":"6.02","refs":["https://evil.example/pull/166"]}],
            "cross_cutting":[{"refs":[f"https://github.com/{REPO}/pull/166"]}]})
        self.assertEqual(reviewed,{})

    def test_direct_marker_only_and_multiple_markers_go_review(self):
        self.assertEqual(pm_mapping.match_evidence(pr(200,"Sprint 7.03"),TASKS,{})["state"],"matched")
        self.assertEqual(pm_mapping.match_evidence(pr(200,"Sprint 7.03 and Sprint 6.02"),TASKS,{})["state"],"review")
        self.assertEqual(pm_mapping.match_evidence(pr(200,"7.03"),TASKS,{})["state"],"unmatched")
        p=pr(200,"unrelated")
        p["body"]="Sprint 7.03"
        self.assertEqual(pm_mapping.match_evidence(p,TASKS,{})["state"],"unmatched")

    def test_curated_missing_task_blocks_all_links(self):
        reviewed={(REPO,154):{"4.03","not-a-task"}}
        self.assertEqual(pm_mapping.match_evidence(pr(154),TASKS,reviewed)["state"],"review")

    def test_reconcile_persists_multilinks_without_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            db=Path(folder)/"project.sqlite3"
            con=project_store.connect(db)
            with con:
                for t in TASKS:
                    con.execute("INSERT INTO task(task_key,area,source_id,title,updated_at) VALUES(?,?,?,?,?)",
                        (t["task_key"],"fiverr",t["source_id"],t["source_id"],project_store.timestamp()))
                con.execute("INSERT INTO imports VALUES(?,?,?,?,?)",("fixture","test",61,24,project_store.timestamp()))
            con.close()
            original=pm_mapping.evidence_source
            try:
                pm_mapping.evidence_source=lambda root=None:{(REPO,154):{"4.02","4.03"}}
                first=pm_sync.reconcile([pr(154)],[],db)
                self.assertEqual((first["matched"],first["links"]),(1,2))
                again=pm_sync.reconcile([pr(154)],[],db)
                self.assertEqual(again["changed"],0)
                data=pm_sync.briefing(db)
                self.assertEqual(len(data["observations"][0]["links"]),2)
                self.assertEqual(data["curated_count"],1)
                self.assertEqual(project_store.read_summary(db)["approvals"],[])
                self.assertTrue(all(t["stage"]=="planned" for t in project_store.read_summary(db)["tasks"]))
            finally:
                pm_mapping.evidence_source=original

if __name__=="__main__":unittest.main()
