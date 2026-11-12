"""Read-only, authenticated asset inventory for two allowlisted GitHub repositories.

GitHub trees are ref-resolved; images/PDFs are served from matching verified blobs only.
No uploads, external URLs, writes, speculative deployment claims, or GitHub token exposure.
"""
from __future__ import annotations

import base64
import datetime as dt
import io
import json
import mimetypes
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import PurePosixPath

from openpyxl import load_workbook

ROOTS = (
    ("danielwauer-maker/bcsentinel", "main", "Core · main"),
    ("danielwauer-maker/bcsentinel-frontend", "main", "Frontend · main"),
    ("danielwauer-maker/bcsentinel-frontend", "fix/dev-v6-main-safe-integration-20261112",
     "Frontend · Draft #13"),
)
EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
                        ".pdf", ".xlsx", ".xls", ".csv", ".docx", ".pptx"})
IMAGE_EXT = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"})
PREVIEW_EXT = IMAGE_EXT | {".pdf", ".xlsx", ".csv"}
MAX_BLOB = 6_000_000
CACHE_SECONDS = 600
_lock = threading.Lock()
_cache = {}

# Verified source imports; no inferred release or deployed usage.
VERIFIED_USAGES = {
    ("danielwauer-maker/bcsentinel-frontend",
     "fix/dev-v6-main-safe-integration-20261112", "src/assets/hero-mountains.jpg"): [
        "src/components/landing-preview.tsx",
        "src/components/bc/shell.tsx",
        "src/components/bc/assessment-overview.tsx",
    ],
}


class MediaError(Exception):
    def __init__(self, status, message):
        self.status = status
        super().__init__(message)


def _request(url):
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise MediaError(503, "GitHub-Lesetoken nicht konfiguriert")
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "BCSentinel-ReadOnly-Media",
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = response.read(9_000_000)
        return json.loads(raw)
    except (urllib.error.URLError, ValueError, TimeoutError) as e:
        raise MediaError(503, "GitHub-Quelle vorübergehend nicht erreichbar") from e


def _tree(repo, ref):
    if (repo, ref) not in {(r, b) for r, b, _ in ROOTS}:
        raise MediaError(404, "Unzulässiges Repository oder Ref")
    key = (repo, ref)
    now = time.monotonic()
    with _lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < CACHE_SECONDS:
            return cached[1]
    url = "https://api.github.com/repos/" + repo + "/git/trees/" + urllib.parse.quote(ref, safe="") + "?recursive=1"
    obj = _request(url)
    if obj.get("truncated") or not isinstance(obj.get("tree"), list):
        raise MediaError(503, "GitHub-Dateibaum unvollständig; Ergebnisse nicht belastbar")
    if not re.fullmatch(r"[0-9a-f]{40}", str(obj.get("sha", ""))):
        raise MediaError(503, "GitHub-Quelle ohne nachvollziehbare Tree-SHA")
    tree = {x["path"]: x for x in obj["tree"]
            if x.get("type") == "blob" and isinstance(x.get("path"), str)}
    result = {"tree_sha": obj["sha"], "files": tree, "reviewed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    with _lock:
        _cache[key] = (now, result)
    return result


def _allow_path(path):
    if not path or len(path) > 350 or "\\" in path or "\x00" in path:
        return False
    p = PurePosixPath(path)
    return not p.is_absolute() and all(part not in (".", "..") for part in p.parts) and p.suffix.lower() in EXTENSIONS


def _url(repo, ref, path):
    return ("https://github.com/" + repo + "/blob/"
            + urllib.parse.quote(ref, safe="") + "/"
            + urllib.parse.quote(path, safe="/"))


def _type(path):
    ext = PurePosixPath(path).suffix.lower()
    if ext in IMAGE_EXT:
        return "Grafik"
    if ext == ".pdf":
        return "PDF"
    if ext in (".xlsx", ".xls", ".csv"):
        return "Tabelle"
    return "Dokument"


def catalog():
    items, sources = [], []
    errors = []
    for repo, ref, label in ROOTS:
        try:
            tree = _tree(repo, ref)
        except MediaError as exc:
            errors.append({"source": label, "reason": str(exc)})
            continue
        sources.append({"source": label, "repo": repo, "ref": ref,
                        "tree_sha": tree["tree_sha"], "observed_at": tree["reviewed_at"]})
        for path, node in tree["files"].items():
            if not _allow_path(path):
                continue
            uses = VERIFIED_USAGES.get((repo, ref, path), ())
            # A usage reference is a source-code location, not proof of a live deployment.
            usage = [{"path": p, "url": _url(repo, ref, p),
                      "scope": "Quellcode-Import (nicht Deployment)"} for p in uses]
            items.append({
                "repo": repo, "ref": ref, "source": label,
                "path": path, "filename": PurePosixPath(path).name,
                "category": _type(path), "extension": PurePosixPath(path).suffix.lower(),
                "size": node.get("size"), "sha": node.get("sha"),
                "url": _url(repo, ref, path), "usage": usage,
                "usage_state": "verified_source" if usage else "not_verified",
                "version_state": "branch_candidate" if ref != "main" else "repository_main",
                "preview": "image" if PurePosixPath(path).suffix.lower() in IMAGE_EXT else
                           ("pdf" if path.lower().endswith(".pdf") else
                            ("table" if path.lower().endswith((".xlsx", ".csv")) else "external")),
            })
    items.sort(key=lambda x: (x["filename"].casefold(), x["source"], x["path"]))
    return {"state": "partial" if errors else "loaded", "assets": items,
            "sources": sources, "errors": errors, "count": len(items),
            "message": "Dateiinventar aus GitHub-Refs; nur belegte Code-Imports gelten als Verwendungsnachweis. Keine Aussage über laufende DEV-/PROD-Assets."}


def get_asset(repo, ref, path):
    if not _allow_path(path) or PurePosixPath(path).suffix.lower() not in PREVIEW_EXT:
        raise MediaError(404, "Für dieses Format keine interne Vorschau")
    tree = _tree(repo, ref)
    entry = tree["files"].get(path)
    if not entry or not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("sha", ""))):
        raise MediaError(404, "Datei im gewählten Ref nicht vorhanden")
    if not isinstance(entry.get("size"), int) or entry["size"] > MAX_BLOB:
        raise MediaError(413, "Datei zu groß für sichere Vorschau")
    raw = _request("https://api.github.com/repos/" + repo + "/git/blobs/" + entry["sha"])
    if raw.get("encoding") != "base64":
        raise MediaError(502, "Nicht unterstützte GitHub-Blobkodierung")
    try:
        data = base64.b64decode(raw["content"], validate=False)
    except (ValueError, KeyError) as exc:
        raise MediaError(502, "Blobinhalt ungültig") from exc
    if len(data) != entry["size"] or len(data) > MAX_BLOB:
        raise MediaError(502, "Blobgröße weicht vom verifizierten Dateibaum ab")
    return data, PurePosixPath(path).suffix.lower()


def preview_table(repo, ref, path):
    data, ext = get_asset(repo, ref, path)
    if ext == ".xlsx":
        try:
            wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
            try:
                sheets = []
                for sheet in list(wb)[:5]:
                    rows = []
                    for row in sheet.iter_rows(min_row=1, max_row=8, max_col=8, values_only=True):
                        rows.append([str(v)[:120] if v is not None else "" for v in row])
                    sheets.append({"name": sheet.title[:80], "rows": rows})
                return {"sheets": sheets, "truncated": True}
            finally:
                wb.close()
        except Exception as exc:
            raise MediaError(422, "Excel-Vorschau konnte nicht sicher gelesen werden") from exc
    if ext == ".csv":
        import csv
        import itertools
        text = data.decode("utf-8-sig", errors="replace")
        rows = [[v[:120] for v in row[:8]] for row in itertools.islice(csv.reader(io.StringIO(text)), 8)]
        return {"sheets": [{"name": "CSV", "rows": rows}], "truncated": True}
    raise MediaError(404, "Keine tabellarische Vorschau verfügbar")


def content_type(ext):
    return {".svg": "image/svg+xml", ".pdf": "application/pdf",
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp",
            ".gif": "image/gif"}.get(ext, "application/octet-stream")
