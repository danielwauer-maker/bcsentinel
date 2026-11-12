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
        with mock.patch.object(m, "_tree", return_value=self.tree()), mock.patch.object(
            m, "_scan_references", return_value={
                "usages": {"src/assets/hero-mountains.jpg": [
                    "src/components/landing-preview.tsx",
                    "src/components/bc/shell.tsx",
                    "src/components/bc/assessment-overview.tsx"
                ]},
                "coverage": {"source_candidates": 3, "source_scanned": 3,
                             "source_failed": 0, "limited": False}
            }
        ):
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
        self.assertEqual(next(x for x in result["assets"] if x["repo"] == CORE and x["filename"] == "report.pdf")["usage_state"],
                         "not_detected")

    def test_partial_source_not_misrepresented_as_complete(self):
        original=m._tree
        def fake(repo, ref):
            if ref == DRAFT:
                raise m.MediaError(503, "not reachable")
            return self.tree()
        with mock.patch.object(m, "_tree", side_effect=fake), mock.patch.object(
            m, "_scan_references", return_value={
                "usages": {}, "coverage": {"source_candidates": 0, "source_scanned": 0,
                                            "source_failed": 0, "limited": False}
            }
        ):
            result=m.catalog()
        self.assertEqual(result["state"], "partial")
        self.assertEqual(len(result["errors"]), 1)

    def test_static_reference_scan_matches_exact_paths_only(self):
        assets={"src/assets/logo.png", "src/assets/hero-mountains.jpg",
                "public/logo.png", "docs/report.pdf"}
        self.assertEqual(
            m._resolve_literal("src/components/header.tsx", "@/assets/logo.png", assets),
            "src/assets/logo.png")
        self.assertEqual(
            m._resolve_literal("src/components/header.tsx", "../assets/hero-mountains.jpg", assets),
            "src/assets/hero-mountains.jpg")
        self.assertEqual(
            m._resolve_literal("src/components/header.tsx", "/logo.png", assets),
            "public/logo.png")
        self.assertIsNone(m._resolve_literal("src/x.tsx", "logo.png", assets))
        self.assertIsNone(m._resolve_literal("src/x.tsx", "https://evil.example/logo.png", assets))

    def test_scan_records_coverage_and_failed_reads(self):
        import time
        images={"src/assets/logo.png": {"size": 4, "sha": SHA},
                "src/components/header.tsx": {"size": 37, "sha": "c"*40},
                "src/components/other.tsx": {"size": 21, "sha": "d"*40}}
        content=b'import logo from "@/assets/logo.png";'
        images["src/components/header.tsx"]["size"]=len(content)
        tree={"tree_sha": "f"*40,"files": images}
        def fetch(url):
            if url.endswith("c"*40):
                return {"encoding":"base64","content":base64.b64encode(content).decode()[:12]+"\\n"+base64.b64encode(content).decode()[12:]}
            raise m.MediaError(503,"source unavailable")
        with mock.patch.object(m,"_request",side_effect=fetch), mock.patch.object(m,"MAX_SOURCE_FILES",3):
            result=m._scan_references(CORE,"main",tree)
        self.assertEqual(result["usages"]["src/assets/logo.png"],["src/components/header.tsx"])
        self.assertEqual(result["coverage"]["source_candidates"],2)
        self.assertEqual(result["coverage"]["source_scanned"],1)
        self.assertEqual(result["coverage"]["source_failed"],1)
        self.assertTrue(result["coverage"]["limited"])

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
