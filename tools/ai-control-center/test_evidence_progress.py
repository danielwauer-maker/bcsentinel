"""Verify evidence-based phase metrics and non-fabricated labor estimates."""
import unittest
from evidence_progress import build_progress

REPO="danielwauer-maker/bcsentinel"
def item(id,area="Release & BC27",status="not_reviewed",prs=(),gates=()):
    return {"id":id, "title":id, "area":area, "source_status":status,
            "manual_gates":list(gates),"next_action":"Check safely","prs":list(prs)}
def merged(number=191):
    return {"number":number,"state":"merged",
            "url":f"https://github.com/{REPO}/pull/{number}",
            "merged_at":"2026-11-16T11:00:00Z",
            "created_at":"2026-11-13T11:00:00Z"}
def sample():
    tasks=[item("1.02",status="tracker_checked"),item("1.03",status="manual_gate"),
           item("3.02",area="Reports & Monitoring",status="partial",prs=[merged()])]
    track={"state":"loaded","sha256":"sha","rows":[
        {"area":"fiverr","id":"1.02","sprint":"3A.2 BC Runtime","title":"Backend","plan_hours":5},
        {"area":"fiverr","id":"1.03","sprint":"3A.2 BC Runtime","title":"BC27","plan_hours":17},
        {"area":"fiverr","id":"3.02","sprint":"4 Reports","title":"Full Report","plan_hours":12},
    ]}
    source={"reviewed_at":"2026-11-16","observed_gates":{
        "dev_runtime_release_20261116":{"backend":{"state":"deployed_exact_staging_sha",
            "sha":"403709ca2dfdcbcc2ceb2e9dda4461f261d04aae"}}}}
    radar={"state":"loaded","items":tasks}
    return track,radar,source

class ProgressTests(unittest.TestCase):
    def test_merged_pr_is_not_technical_or_accepted(self):
        track,radar,source=sample()
        board=build_progress(track,radar,source)
        report=next(g for g in board["sprints"] if g["sprint"]=="4 Reports")
        self.assertEqual(report["percent"]["integrated"],100.0)
        self.assertEqual(report["percent"]["technical"],0)
        self.assertEqual(report["percent"]["accepted"],0)
        self.assertEqual(report["percent"]["preview"],100.0)
        self.assertIsNone(report["actual_hours"])
        self.assertEqual(board["release"],"NO_GO")

    def test_plan_never_confused_with_work_hours(self):
        track,radar,source=sample()
        board=build_progress(track,radar,source)
        bc=next(g for g in board["sprints"] if g["sprint"]=="3A.2 BC Runtime")
        self.assertEqual(bc["plan_hours"],22)
        self.assertEqual(bc["actual_hours_state"],"missing_timesheets")
        self.assertIsNone(board["timeline"]["actual_logged_hours"])
        self.assertIsNone(board["timeline"]["planned_fiverr_hours"]) # Incomplete 61-task basis
        merged_events=[e for e in board["timeline"]["events"] if e["kind"]=="merge"]
        self.assertEqual(merged_events[0]["lead_calendar_days"],3)

    def test_no_hours_for_unverified_workbook(self):
        track,radar,source=sample()
        track["state"]="version_mismatch"
        board=build_progress(track,radar,source)
        self.assertEqual(board["state"],"partial")
        self.assertTrue(all(g["plan_hours"] is None for g in board["sprints"]))

    def test_human_gate_only_from_human_evidence(self):
        track,radar,source=sample()
        radar["items"][1]["manual_gates"]=["technical"]
        board=build_progress(track,radar,source)
        bc=next(g for g in board["sprints"] if g["sprint"]=="3A.2 BC Runtime")
        self.assertEqual(bc["counts"]["technical"],1)
        self.assertEqual(bc["counts"]["accepted"],0)

    def test_draft_not_equal_merged(self):
        track,radar,source=sample()
        radar["items"][2]["prs"]=[{"number":165,"state":"closed_unmerged",
            "url":f"https://github.com/{REPO}/pull/165"}]
        board=build_progress(track,radar,source)
        report=next(g for g in board["sprints"] if g["sprint"]=="4 Reports")
        self.assertEqual(report["counts"]["integrated"],0)

if __name__=="__main__":
    unittest.main()
