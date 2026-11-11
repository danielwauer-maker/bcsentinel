"""Contract tests for DEV-first master tracker and evidence isolation."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from openpyxl import Workbook
import app


class TrackerTests(unittest.TestCase):
    def test_missing_workbook_does_not_invent_progress(self):
        with mock.patch.object(app, "TRACKER", Path("/not-a-real-tracker-9173.xlsx")), \
             mock.patch.object(app, "evidence", return_value={}):
            result = app.tracker()
        self.assertEqual(result["state"], "missing")
        self.assertEqual(result["rows"], [])

    def test_verified_snapshot_without_mount_is_not_live(self):
        with mock.patch.object(app, "TRACKER", Path("/not-a-real-tracker-9173.xlsx")), \
             mock.patch.object(app, "evidence", return_value={"master_tracker": {
                 "filename": "tracker.xlsx", "sha256": "knownhash",
                 "fiverr_tasks": 61, "saas_tasks": 24,
                 "checked_technical": 2, "checked_live": 2
             }}):
            result = app.tracker()
        self.assertEqual(result["state"], "snapshot_only")
        self.assertEqual(result["fiverr_count"], 61)
        self.assertEqual(result["rows"], [])

    def test_exact_workbook_layout_separates_fiverr_and_saas(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "master-tracker.xlsx"
            wb = Workbook()
            sprint = wb.active
            sprint.title = "Sprint-Tracker"
            sprint.append(["Title"])
            sprint.append(["ID"])
            for i in range(61):
                row = [""] * 24
                row[0] = f"{i + 1}.01"
                row[1] = "Sprints"
                row[3] = "Aufgabe"
                row[20] = "✓" if i < 2 else "☐"
                row[21] = "✓" if i < 2 else "☐"
                sprint.append(row)
            saas = wb.create_sheet("SaaS-Stripe Roadmap")
            for _ in range(8):
                saas.append(["Title"])
            for i in range(24):
                row = [""] * 13
                row[0] = f"S{i + 1}.01"
                row[2] = "SaaS Aufgabe"
                row[9] = row[10] = "☐"
                saas.append(row)
            dashboard = wb.create_sheet("Dashboard")
            dashboard["A3"] = "Stand 11.11.2026"
            dashboard["B5"] = 0.65
            dashboard["B7"] = 20
            wb.save(path)
            import hashlib
            actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
            with mock.patch.object(app, "TRACKER", path), mock.patch.object(
                app, "evidence", return_value={"master_tracker": {"sha256": actual_sha}}
            ):
                result = app.tracker()
                self.assertEqual(result["state"], "loaded")
                self.assertEqual(result["mapped_rows"], 85)
                self.assertEqual((result["fiverr_count"], result["saas_count"]), (61, 24))
                self.assertEqual((result["fiverr_technical"], result["fiverr_live"]), (2, 2))
                self.assertEqual(result["saas_live"], 0)
                self.assertEqual(result["rows"][0]["source"], "excel")
            with mock.patch.object(app, "TRACKER", path), mock.patch.object(
                app, "evidence", return_value={"master_tracker": {"sha256": "bad"}}
            ):
                self.assertEqual(app.tracker()["state"], "version_mismatch")

    def test_github_token_missing_fails_closed(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(app.github("repos/danielwauer-maker/bcsentinel")["state"], "unconfigured")

    def test_snapshot_never_assumes_approvals(self):
        with mock.patch.object(app, "github", return_value={"state": "unavailable"}), \
             mock.patch.object(app, "tracker", return_value={"state": "missing", "rows": []}), \
             mock.patch.object(app, "dev_health", return_value={"state": "unconfigured"}):
            result = app.snapshot()
        self.assertEqual(result["go_live"], "NO_GO_UNTIL_EXPLICIT_ACCEPTANCE")
        self.assertTrue(all(v == "not_verified" for v in result["gates"].values()))
        self.assertIsNone(result["ai_cost"]["amount"])


if __name__ == "__main__":
    unittest.main()
