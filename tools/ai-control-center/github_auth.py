"""Shared GitHub credential loading without exposing secrets."""

import os
from pathlib import Path


class GitHubTokenError(Exception):
    """Safe credential configuration error."""


def get_github_token():
    """Prefer a token file; retain legacy environment support."""
    token_file = os.environ.get("GITHUB_TOKEN_FILE", "").strip()

    if token_file:
        try:
            path = Path(token_file)
            if not path.is_absolute():
                raise GitHubTokenError("GitHub-Token-Datei ungueltig")

            with path.open("rb") as stream:
                raw = stream.read(8193)

            if len(raw) > 8192:
                raise GitHubTokenError("GitHub-Token-Datei ungueltig")

            token = raw.decode("ascii").strip()
        except (OSError, UnicodeError, ValueError):
            raise GitHubTokenError(
                "GitHub-Token-Datei nicht lesbar"
            ) from None

        if not token or any(ch.isspace() for ch in token):
            raise GitHubTokenError(
                "GitHub-Token-Datei ungueltig"
            )
        return token

    return os.environ.get("GITHUB_TOKEN", "").strip()
