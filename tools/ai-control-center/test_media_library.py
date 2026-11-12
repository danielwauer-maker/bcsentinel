"""Media catalog and binary preview security: no writes, arbitrary GitHub refs or fabricated usage."""
import base64
import io
import json
import unittest
from unittest import mock

from openpyxl import Workbook
import media_library as m


CORE = "danielwauer-maker/bcsentinel"
FRONT = "danielwauer-maker/bcsentinel-frontend"
DRAFT = "fix/dev-v6-main-safe-integration-20261112"
SHA = "a" * 40


class MediaLibraryTests(unittest.TestCase):
    def tree(self):
        return {"tree_sha": "f"*40, "reviewed_at": "2026-11-12T18:00:00+00:00",
                "files": {
                    "src/assets/hero-mountains.jpg": {
                        "type": "blob", "sha": SHA, "size": 4
                    },
                    "docs/report.pdf": {"type": "blob", "sha": "b"*40, "size": 5},
                    "src/../../secrets.png": {"type": "blob", "sha": SHA, "size": 1},
                }}

    def test_catalog_separates_main_and_draft_and_usage(self):
        with mock.patch.object(m, "_tree", return_value=self.tree()):
            result = m.catalog()
        self.assertEqual(result["state"], "loaded")
        self.assertEqual(result["count"], 6)
        self.assertFalse(any("secrets" in x["path"] for x in result["assets"]))
        found = [x for x in result["assets"] if x["repo"] == FRONT and x["ref"] == DRAFT
                 and x["filename"] == "hero-mountains.jpg"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["usage_state"], "verified_source")
        self.assertEqual(len(found[0]["usage"]), 3)
        self.assertEqual(found[0]["version_state"], "branch_candidate")
        self.assertEqual(next(x for x in result["assets"] if x["repo"] == CORE)["usage_state"],
                         "not_verified")

    def test_partial_source_not_misrepresented_as_complete(self):
        original=m._tree
        def fake(repo, ref):
            if ref == DRAFT:
                raise m.MediaError(503, "not reachable")
            return self.tree()
        with mock.patch.object(m, "_tree", side_effect=fake):
            result=m.catalog()
        self.assertEqual(result["state"], "partial")
        self.assertEqual(len(result["errors"]), 1)

    def test_ref_whitelist_and_path_traversal(self):
        for repo, ref, path in (
            (CORE,"staging","docs/report.pdf"),
            ("someother/repository","main","docs/report.pdf"),
            (CORE,"main","../../secret.png"),
            (CORE,"main","config.env"),
            (CORE,"main","/etc/password.png"),
        ):
            with self.subTest(repo=repo,ref=ref,path=path):
                with self.assertRaises(m.MediaError):
                    m.get_asset(repo,ref,path)

    def test_blob_must_match_tree_size_and_sha(self):
        with mock.patch.object(m, "_tree", return_value=self.tree()), mock.patch.object(
            m, "_request", return_value={"encoding":"base64","content":base64.b64encode(b"DATA").decode()}
        ):
            data,ext=m.get_asset(CORE,"main","src/assets/hero-mountains.jpg")
            self.assertEqual((data,ext),(b"DATA",".jpg"))
        with mock.patch.object(m, "_tree", return_value=self.tree()), mock.patch.object(
            m, "_request", return_value={"encoding":"base64","content":base64.b64encode(b"INVALID").decode()}
        ):
            with self.assertRaises(m.MediaError):
                m.get_asset(CORE,"main","src/assets/hero-mountains.jpg")

    def test_limited_excel_preview(self):
        wb=Workbook()
        ws=wb.active
        ws.title="Tabelle"
        for n in range(20): ws.append([n,"Status", "Test"])
        f=io.BytesIO();wb.save(f)
        with mock.patch.object(m,"get_asset",return_value=(f.getvalue(),".xlsx")):
            result=m.preview_table(CORE,"main","report.xlsx")
        self.assertEqual(len(result["sheets"]),1)
        self.assertEqual(len(result["sheets"][0]["rows"]),8)
        self.assertTrue(result["truncated"])


if __name__=="__main__":
    unittest.main()
