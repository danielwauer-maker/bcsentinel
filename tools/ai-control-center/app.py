"""BCSentinel AI Control Center: read-only, evidence-aware MVP."""
from __future__ import annotations

import base64
import datetime as dt
import hmac
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
TRACKER = Path(os.getenv("TRACKER_PATH", "/data/master-tracker.xlsx"))
GITHUB_REPOS = ["danielwauer-maker/bcsentinel", "danielwauer-maker/bcsentinel-frontend"]
NO_CACHE = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY"}
STATUS_HEADINGS = ("status", "stand", "bearbeitungsstand", "fortschritt", "state")
ID_HEADINGS = ("sprint", "arbeitspaket", "aufgabe", "task", "id", "nummer")
TITLE_HEADINGS = ("titel", "aufgabe", "beschreibung", "task", "sprint", "name")
SEPARATE_GATES = ("technisch_fertig", "dev_abgenommen", "go_live_freigegeben")


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def github(path):
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        return {"state": "unconfigured", "reason": "GITHUB_TOKEN fehlt"}
    req = urllib.request.Request(
        "https://api.github.com/" + path,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "BCSentinel-Control-Center"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.load(response)
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        return {"state": "unavailable", "reason": str(exc)[:150]}


def tracker():
    if not TRACKER.is_file():
        return {"state": "missing", "filename": TRACKER.name, "rows": [], "sheets": [],
                "reason": "Master-Excel noch nicht eingebunden; keine Fortschrittszahlen ableitbar"}
    try:
        wb = load_workbook(TRACKER, read_only=True, data_only=True)
        sheets, items = [], []
        for sheet in wb:
            values = sheet.iter_rows(values_only=True)
            preview = []
            for idx, row in enumerate(values):
                if idx >= 2500:
                    break
                preview.append([str(v).strip() if v is not None else "" for v in row])
            header_idx, headers = None, []
            for i, row in enumerate(preview[:20]):
                nonempty = [s.lower() for s in row if s]
                if any(any(key in s for key in STATUS_HEADINGS) for s in nonempty) and any(any(key in s for key in ID_HEADINGS) for s in nonempty):
                    header_idx, headers = i, [s.lower() for s in row]
                    break
            sheets.append({"name": sheet.title, "rows_examined": len(preview),
                           "mapped": header_idx is not None})
            if header_idx is None:
                continue
            def col(names):
                return next((i for i, h in enumerate(headers) if any(n in h for n in names)), None)
            id_col, title_col, status_col = col(ID_HEADINGS), col(TITLE_HEADINGS), col(STATUS_HEADINGS)
            for line_no, row in enumerate(preview[header_idx + 1:], start=header_idx + 2):
                ident = row[id_col] if id_col is not None and id_col < len(row) else ""
                title = row[title_col] if title_col is not None and title_col < len(row) else ""
                status = row[status_col] if status_col is not None and status_col < len(row) else ""
                if ident and (title or status):
                    items.append({"sheet": sheet.title, "row": line_no, "id": ident, "title": title,
                                  "status_raw": status, "source": "excel"})
        wb.close()
        return {"state": "loaded", "filename": TRACKER.name, "sheets": sheets,
                "rows": items[:500], "mapped_rows": len(items),
                "warning": "Rohstatus aus Excel; keine automatischen Go-Live-Freigaben"}
    except Exception as exc:
        return {"state": "error", "filename": TRACKER.name, "rows": [],
                "reason": type(exc).__name__ + ": " + str(exc)[:140]}


def dev_health():
    url = os.getenv("DEV_HEALTH_URL", "").strip()
    if not url:
        return {"state": "unconfigured"}
    # Only administrator-configured URL. No user-controlled probe targets.
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return {"state": "reachable" if response.status == 200 else "unhealthy",
                    "http_status": response.status}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"state": "unavailable", "reason": str(exc)[:150]}


def snapshot():
    repos = []
    for repo in GITHUB_REPOS:
        info = github("repos/" + repo)
        pulls = github("repos/" + repo + "/pulls?state=open&per_page=50")
        if isinstance(pulls, list):
            pr_items = [{"number": pr.get("number"), "title": pr.get("title"),
                         "draft": pr.get("draft"), "url": pr.get("html_url"),
                         "base": (pr.get("base") or {}).get("ref"),
                         "updated_at": pr.get("updated_at")} for pr in pulls]
            pr_state = "loaded"
        else:
            pr_items = []
            pr_state = pulls.get("state", "error")
        repos.append({"repo": repo, "state": "loaded" if "default_branch" in info else info.get("state", "error"),
                      "default_branch": info.get("default_branch"), "open_prs": pr_items, "pr_state": pr_state})
    return {"generated_at_utc": utc_now(), "tracker": tracker(), "repositories": repos,
            "dev_health": dev_health(), "gates": {key: "not_verified" for key in SEPARATE_GATES},
            "go_live": "NO_GO_UNTIL_EXPLICIT_ACCEPTANCE",
            "agent_queue": {"state": "not_implemented", "running": 0},
            "ai_cost": {"state": "not_configured", "amount": None, "currency": "EUR"},
            "warnings": ["PRs und Excel-Rohstatus sind keine BC-Runtime- oder Go-Live-Abnahme.",
                         "Datenquellenfehler werden als unbekannt angezeigt, nie als erfolgreich."]}


class Handler(BaseHTTPRequestHandler):
    def authorized(self):
        user = os.getenv("DASHBOARD_USER", "")
        password = os.getenv("DASHBOARD_PASSWORD", "")
        if not user or not password:
            return False
        supplied = self.headers.get("Authorization", "")
        expected = "Basic " + base64.b64encode((user + ":" + password).encode()).decode()
        return hmac.compare_digest(supplied, expected)

    def reply(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        for key, value in NO_CACHE.items():
            self.send_header(key, value)
        if status == 401:
            self.send_header("WWW-Authenticate", 'Basic realm="BCSentinel AI Control Center"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.authorized():
            self.reply(401, b"Authentication required", "text/plain; charset=utf-8")
            return
        if self.path == "/api/snapshot":
            self.reply(200, json.dumps(snapshot(), ensure_ascii=False).encode(), "application/json; charset=utf-8")
        elif self.path in ("/", "/index.html"):
            self.reply(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self.reply(404, b"Not found", "text/plain; charset=utf-8")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8090"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
