"""Canonical version and project status remain independent of immutable Excel titles."""
import unittest
from current_project import current_view

def source(version="1.0.2.60",acceptance="NOT_EXECUTED",backend_state="deployed_exact_staging_sha"):
    return {"reviewed_at":"2026-11-16","observed_gates":{
        "dev_runtime_release_20261116":{
            "backend":{"state":backend_state,"sha":"403709ca2dfdcbcc2ceb2e9dda4461f261d04aae","github_run":43837211210},
            "bc27":{"source_extension_version":version,"sandbox_runtime_acceptance":acceptance}}}}
class CurrentViewTests(unittest.TestCase):
    def test_current_bc27_version_and_gates(self):
        result=current_view(source(),{"github":{"state":"loaded"}})
        self.assertEqual(result["bc27_version"],"1.0.2.60")
        self.assertIn("1.0.2.60",result["current_titles"]["1.03"])
        self.assertIn("1.0.2.60",result["next"][0]["action"])
        self.assertEqual(result["next"][0]["gate"],"manual_not_executed")
        self.assertEqual(result["gate"],"NO_GO")
        self.assertEqual(len(result["areas"]),11)
        self.assertEqual(next(x for x in result["areas"] if x["name"]=="Backend / DEV")["stage"],"dev_verified")

    def test_unverified_version_must_not_be_projected(self):
        result=current_view(source(version="1.0.2.58"),{"github":{"state":"partial"}})
        self.assertIsNone(result["bc27_version"])
        self.assertNotIn("1.03",result["current_titles"])
        self.assertEqual(result["gate"],"NO_GO")

    def test_backend_missing_not_claimed_deployed(self):
        result=current_view(source(backend_state="unknown"),{})
        self.assertEqual(next(x for x in result["areas"] if x["name"]=="Backend / DEV")["stage"],"unverified")

if __name__=="__main__":
    unittest.main()
