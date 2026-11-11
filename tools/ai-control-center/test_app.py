"""MVP contract tests: no silent success on missing evidence."""
import base64
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from openpyxl import Workbook
import app


class TrackerTests(unittest.TestCase):
    def test_missing_workbook_does_not_invent_progress(self):
        with mock.patch.object(app, "TRACKER", Path("/not-a-real-tracker-9173.xlsx")):
            result = app.tracker()
        self.assertEqual(result["state"], "missing")
        self.assertEqual(result["rows"], [])

    def test_workbook_reads_unmodified_raw_status(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tracker.xlsx"
            wb = Workbook()
            sheet = wb.active
            sheet.title = "Fiverr"
            sheet.append(["Sprint", "Titel", "Status"])
            sheet.append(["6.02", "Website-Inhalte", "IN PRÜFUNG"])
            wb.create_sheet("SaaS").append(["Nicht zugeordnet", "Info"])
            wb.save(path)
            with mock.patch.object(app, "TRACKER", path):
                result = app.tracker()
        self.assertEqual(result["state"], "loaded")
        self.assertEqual(result["mapped_rows"], 1)
        self.assertEqual(result["rows"][0]["status_raw"], "IN PRÜFUNG")
        self.assertFalse(result["sheets"][1]["mapped"])

    def test_github_token_missing_fails_closed(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            result = app.github("repos/danielwauer-maker/bcsentinel")
        self.assertEqual(result["state"], "unconfigured")

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
