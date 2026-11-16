"""Regression tests for secure GitHub token loading."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from github_auth import GitHubTokenError, get_github_token


class GitHubAuthTests(unittest.TestCase):

    def test_token_file_has_priority(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "token"
            path.write_text("file_token\n", encoding="ascii")
            with mock.patch.dict(os.environ, {
                "GITHUB_TOKEN_FILE": str(path),
                "GITHUB_TOKEN": "legacy_token",
            }):
                self.assertEqual(get_github_token(), "file_token")

    def test_legacy_token_still_supported(self):
        with mock.patch.dict(os.environ, {
            "GITHUB_TOKEN_FILE": "",
            "GITHUB_TOKEN": "legacy_token",
        }):
            self.assertEqual(get_github_token(), "legacy_token")

    def test_missing_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(os.environ, {
                "GITHUB_TOKEN_FILE": str(Path(directory) / "missing"),
                "GITHUB_TOKEN": "legacy_token",
            }):
                with self.assertRaises(GitHubTokenError):
                    get_github_token()

    def test_invalid_token_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "token"
            path.write_text("invalid token with spaces", encoding="ascii")
            with mock.patch.dict(os.environ, {
                "GITHUB_TOKEN_FILE": str(path),
                "GITHUB_TOKEN": "legacy_token",
            }):
                with self.assertRaises(GitHubTokenError):
                    get_github_token()

    def test_invalid_encoding_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "token"
            path.write_bytes(b"\xff\xfe")
            with mock.patch.dict(os.environ, {
                "GITHUB_TOKEN_FILE": str(path),
                "GITHUB_TOKEN": "",
            }):
                with self.assertRaises(GitHubTokenError):
                    get_github_token()

    def test_oversized_token_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "token"
            path.write_bytes(b"x" * 8193)
            with mock.patch.dict(os.environ, {
                "GITHUB_TOKEN_FILE": str(path),
                "GITHUB_TOKEN": "legacy_token",
            }):
                with self.assertRaises(GitHubTokenError):
                    get_github_token()


if __name__ == "__main__":
    unittest.main()
