#!/usr/bin/env python3
"""Regression cases for the fail-closed CI change classifier."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from ci_change_classification import CATEGORIES, classify


class ChangeClassificationTests(unittest.TestCase):
    def assert_categories(self, paths, expected, *, all_critical=False, full=False):
        result = classify(paths)
        enabled = {name for name, value in result["categories"].items() if value}
        self.assertEqual(enabled, set(expected))
        self.assertEqual(result["all_critical"], all_critical)
        self.assertEqual(result["requires_full_validation"], full)

    def test_documentation_and_evidence_only(self):
        self.assert_categories(
            ["docs/guide.md", "quality/release/evidence.json"],
            ["documentation_evidence"],
        )

    def test_dashboard_only(self):
        self.assert_categories(
            ["tools/ai-control-center/app.py"],
            ["dashboard"],
        )

    def test_backend_only(self):
        self.assert_categories(["backend/app/main.py"], ["backend"])

    def test_bc27_only(self):
        self.assert_categories(["bc-extension/app/src/Foo.al"], ["bc_al_bc27"])

    def test_security_migration_and_release_are_full_validation(self):
        self.assert_categories(
            ["backend/alembic/versions/0042_safe.py", ".github/workflows/deploy.yml"],
            ["backend", "migrations", "release_ci"],
            full=True,
        )
        self.assert_categories(
            ["backend/app/security/tenant.py"],
            ["backend", "security_auth_tenant"],
            full=True,
        )

    def test_mixed_change_set_preserves_all_relevant_categories(self):
        self.assert_categories(
            ["backend/app/main.py", "bc-extension/app/src/Foo.al",
             "backend/app/security/tenant.py"],
            ["backend", "security_auth_tenant", "bc_al_bc27"],
            full=True,
        )

    def test_deleted_security_and_workflow_paths_are_classified(self):
        self.assert_categories(["backend/app/security/tenant.py"], ["backend", "security_auth_tenant"], full=True)
        self.assert_categories([".github/workflows/deploy.yml"], ["release_ci"], full=True)

    def test_git_diff_and_critical_filter_contract_include_deletions(self):
        source = (ROOT / "scripts" / "ci_change_classification.py").read_text(encoding="utf-8")
        self.assertIn("--diff-filter=ACMRD", source)
        for name in ("bc-al-compile.yml", "ext-50-12b-bc27-runtime-gate.yml", "ext-50-12c-3-al.yml", "p0-04-postgres-migration-cycle.yml", "p0-05-postgres-backup-restore.yml", "core-pilot-50-readiness.yml"):
            workflow = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
            self.assertIn('".github/workflows/**"', workflow, name)
            self.assertIn('"scripts/ci_change_classification.py"', workflow, name)
        backend = (ROOT / ".github" / "workflows" / "ext-50-12c-3-backend.yml").read_text(encoding="utf-8")
        self.assertIn("paths-ignore:", backend)

    def test_unknown_and_empty_are_fail_closed(self):
        for paths in (["Makefile"], []):
            self.assert_categories(paths, CATEGORIES, all_critical=True, full=True)


if __name__ == "__main__":
    unittest.main()
