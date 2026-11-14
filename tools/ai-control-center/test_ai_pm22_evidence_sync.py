"""AI-PM 2.2: dated observations never become release approvals or Excel ticks."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class CurrentEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "data" / "evidence-status.json").read_text(encoding="utf-8"))

    def test_original_excel_baseline_is_unchanged(self):
        meta = self.data["master_tracker"]
        self.assertEqual(meta["sha256"], "c1978141c8ee70f52be07ba64df765364a56cb16fe51dea4b084951ade60142a")
        self.assertEqual((meta["fiverr_tasks"], meta["saas_tasks"]), (61, 24))
        self.assertEqual((meta["checked_technical"], meta["checked_live"]), (2, 2))
        self.assertEqual(meta["verified_at"], "2026-11-11")
        # The immutable Excel baseline predates independently reviewed later evidence.\n        # New verified GitHub events must not be blocked by the first snapshot date.\n        self.assertGreaterEqual(self.data["reviewed_at"], meta["verified_at"])\n        self.assertEqual(self.data["observed_gates"]["fiverr"], "NO_GO")

    def test_evidence_is_precise_and_fail_closed(self):
        gates = self.data["observed_gates"]
        self.assertEqual(gates["fiverr"], "NO_GO")
        self.assertEqual(gates["tracker_checkbox_updates"], 0)
        self.assertEqual(gates["dashboard_agent_execution"], "disabled")
        host = gates["host_frontend"]
        self.assertEqual(host["port3000"], "verified_running_image_on_deploy_logs")
        self.assertEqual(host["port3001"], "isolated_full_v6_technical_pass")
        self.assertNotEqual(host["deployed_head"], host["ci_candidate_head"])
        self.assertEqual(host["public_routing"], "frontend_dev_smoke_success")
        self.assertEqual(host["backend_viewer_base_url"], "not_configured")
        self.assertEqual(host["real_paid_report_e2e"], "not_executed")

    def test_curated_task_inventory_is_not_inflated(self):
        items = self.data["work_items"]
        self.assertEqual(len(items), 15)
        self.assertEqual(len({x["id"] for x in items}), 15)
        by_id = {x["id"]: x for x in items}
        self.assertEqual(by_id["3.02"]["status"], "partial")
        self.assertIn("frontend/pull/13", " ".join(by_id["3.02"]["refs"]))
        self.assertIn("bcsentinel/pull/168", " ".join(by_id["1.03"]["refs"]))
        self.assertEqual(by_id["6.02"]["status"], "editorial_complete")
        self.assertEqual(by_id["7.03"]["status"], "editorial_complete")
        for item in items:
            self.assertNotIn(item["status"], ("approved", "go_live", "completed", "dev_accepted"))

    def test_new_dev_integration_evidence_never_promotes_to_runtime_approval(self):
        records = {x["title"]: x for x in self.data["cross_cutting"]}
        frontend = records["Frontend #14 · DEV-only Full-v6 viewer integration"]
        finding = records["Issues #30/#32 · Finding remediation and monitoring access display"]
        self.assertEqual(frontend["status"], "dev_frontend_deployed_technical_pass_e2e_open")
        self.assertEqual(finding["status"], "staging_merged_ci_pass_runtime_open")
        self.assertIn("Manual exact-SHA DEV deployment completed SUCCESS", frontend["detail"])
        self.assertIn("NOT accepted", finding["detail"])
        self.assertEqual(self.data["observed_gates"]["fiverr"], "NO_GO")
        dev = self.data["observed_gates"]["dev_runtime_release_20261114"]
        self.assertEqual(dev["frontend"]["state"], "deployed_dev")
        self.assertEqual(dev["frontend"]["sha"], "2af0ae555251600c0dccb29899104dbdf0ea818f")
        self.assertEqual(dev["backend"]["state"], "deployed_dev_operator_verified")
        self.assertEqual(dev["backend"]["alembic_current"], "0041_pilot_enrollment")
        self.assertEqual(dev["backend"]["deployment_result"], "DEV_0041_RELEASE_RESULT=PASS")
        self.assertEqual(dev["backend"]["pre_migration_backup"]["isolated_restore_test_of_this_exact_archive"], "NOT_EXECUTED")
        self.assertEqual(dev["backend"]["alembic_current"], "0041_pilot_enrollment")
        self.assertEqual(dev["go_live"], "NO_GO")
        self.assertEqual(dev["tracker_checkbox_updates"], 0)

    def test_dashboard_displays_review_timestamp_separately(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "executive.js").read_text(encoding="utf-8")
        self.assertIn('id="exec-evidence-asof"', html)
        self.assertIn('snapshot?.sprint_evidence?.reviewed_at', js)
        self.assertIn("kein aktueller Server-Snapshot", js)
        self.assertIn("Reviewstand nicht verfügbar", js)
        for forbidden in ("fetch(", "innerHTML", "/api/approve"):
            self.assertNotIn(forbidden, js)


if __name__ == "__main__":
    unittest.main()
