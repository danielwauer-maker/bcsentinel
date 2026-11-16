"""Sprint radar: source observations cannot silently promote human runtime gates."""
import unittest
from unittest import mock
import sprint_radar as radar

REPO="danielwauer-maker/bcsentinel"
def gh_pr(number, state="closed", merged=False):
    return {"number": number, "html_url": f"https://github.com/{REPO}/pull/{number}",
            "title": "sprint test", "state": state, "draft": False,
            "merged_at": "2026-11-16T11:00:00Z" if merged else None,
            "updated_at": "2026-11-16T11:00:00Z"}

def evidence():
    return {"reviewed_at":"2026-11-16",
            "observed_gates":{"admin_integration":{"nginx_admin_proxy":"operator_verified_live"},
                              "dev_runtime_release_20261116":{"backend":{"state":"deployed_exact_staging_sha"}}},
            "work_items":[
                {"id":"1.03","status":"manual_gate","detail":"BC27 runtime OPEN","refs":[]},
                {"id":"3.02","status":"partial","detail":"Full runtime open","refs":[f"https://github.com/{REPO}/pull/197"]},
                {"id":"6.02","status":"editorial_complete","detail":"Copy ready","refs":[f"https://github.com/{REPO}/pull/166"]},
            ]}

class RadarTests(unittest.TestCase):
    def setUp(self):
        radar._cache=None
        radar._cached_at=0.0

    def test_merge_is_evidence_not_approval(self):
        obs={"state":"loaded","observations":{f"{REPO}#197":{"number":197,"repo":REPO,
             "url":f"https://github.com/{REPO}/pull/197","state":"merged"}}}
        store={"state":"loaded","tasks":[{"source_id":"3.02","task_key":"fiverr:3.02",
              "title":"Full-Report","area":"fiverr","stage":"planned"}],"approvals":[]}
        result=radar.build_radar(evidence(),store,obs)
        by_id={r["id"]:r for r in result["items"]}
        self.assertEqual(result["go_live"],"NO_GO")
        self.assertEqual(by_id["3.02"]["category"],"waiting")
        self.assertEqual(by_id["3.02"]["manual_gates"],[])
        self.assertEqual(by_id["1.03"]["category"],"next")
        self.assertIn("1.0.2.60", by_id["1.03"]["next_action"])
        self.assertEqual(result["inventory"]["other_fiverr_unreviewed"],58)
        self.assertEqual(result["milestones"][0]["state"],"dev_verified")

    def test_unmerged_closed_is_never_merged(self):
        calls=[]
        def fetch(url):
            calls.append(url)
            return [gh_pr(165, "closed", False)] if url.startswith("repos/"+REPO+"/") else []
        result=radar.recent_prs(fetch,clock=lambda:100.0)
        self.assertEqual(result["observations"][f"{REPO}#165"]["state"],"closed_unmerged")
        radar.recent_prs(lambda url: self.fail("unexpected uncached query"),clock=lambda:101.0)
        self.assertEqual(len(calls),2)

    def test_partial_github_does_not_invent_success(self):
        result=radar.recent_prs(lambda url: {"state":"unavailable"})
        self.assertEqual(result["state"],"partial")
        self.assertEqual(result["observations"],{})
        board=radar.build_radar(evidence(),{"state":"not_initialized","tasks":[]},result)
        self.assertEqual(board["state"],"partial")
        self.assertEqual(board["go_live"],"NO_GO")

    def test_external_or_non_allowlisted_reference_is_rejected(self):
        self.assertIsNone(radar.reference_key("https://evil.test/pull/197"))
        self.assertIsNone(radar.reference_key("https://github.com/danielwauer-maker/other/pull/197"))

    def test_no_automatic_approvals_in_source(self):
        from pathlib import Path
        source=(Path(__file__).parent/"sprint_radar.py").read_text()
        for unsafe in ("UPDATE task", "INSERT INTO approval", "CREATE TABLE", "urllib.request"):
            self.assertNotIn(unsafe,source)

if __name__ == "__main__":
    unittest.main()
