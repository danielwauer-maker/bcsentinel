"""BCSentinel AI Control Center: read-only, evidence-aware MVP."""
from __future__ import annotations

import base64
import datetime as dt
import hmac
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from openpyxl import load_workbook
from project_store import read_summary

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


def mark(value):
    return str(value or "").strip() == "✓"


def tracker():
    """Exact DEV-first v2 workbook layout; spreadsheet checkboxes remain authoritative."""
    if not TRACKER.is_file():
        reference = evidence().get("master_tracker", {})
        if reference:
            return {"state": "snapshot_only", "filename": reference.get("filename", TRACKER.name),
                    "reference_sha256": reference.get("sha256"), "rows": [],
                    "sheets": [], "mapped_rows": None,
                    "fiverr_count": reference.get("fiverr_tasks"), "saas_count": reference.get("saas_tasks"),
                    "fiverr_technical": reference.get("checked_technical"),
                    "fiverr_live": reference.get("checked_live"), "saas_technical": 0, "saas_live": 0,
                    "reason": "Verifizierte Momentaufnahme vom 11.11.2026; Excel auf Server noch nicht eingebunden. Keine Live-Synchronisierung."}
        return {"state": "missing", "filename": TRACKER.name, "rows": [], "sheets": [],
                "reason": "Aktuelle Excel noch nicht als read-only Datei auf dem Server eingebunden"}
    try:
        digest = hashlib.sha256(TRACKER.read_bytes()).hexdigest()
        expected = evidence().get("master_tracker", {}).get("sha256", "")
        if expected and digest != expected:
            return {"state": "version_mismatch", "filename": TRACKER.name, "sha256": digest,
                    "expected_sha256": expected, "rows": [], "sheets": [],
                    "reason": "Anderer Excel-Stand als verifiziert. Zuerst Version und Schema abgleichen."}
        wb = load_workbook(TRACKER, read_only=True, data_only=True)
        required = {"Sprint-Tracker", "SaaS-Stripe Roadmap"}
        if not required.issubset(set(wb.sheetnames)):
            wb.close()
            return {"state": "schema_mismatch", "filename": TRACKER.name, "rows": [], "sheets": [],
                    "reason": "Pflichtblätter der DEV-first v2 Masterdatei fehlen"}
        def rows_for(name, start, cols, tech_idx, live_idx, title_idx):
            sheet = wb[name]
            result = []
            for line, values in enumerate(sheet.iter_rows(min_row=start, max_col=cols, values_only=True),start=start):
                v = list(values)
                identifier = str(v[0] or "").strip()
                if not identifier or identifier.lower() == "id":
                    continue
                result.append({"id": identifier, "sheet": name, "row": line,
                               "title": str(v[title_idx] or ""), "sprint": str(v[1] or ""),
                               "technical_checked": mark(v[tech_idx]),
                               "live_checked": mark(v[live_idx]),
                               "status_raw": str(v[tech_idx] or "") + " / " + str(v[live_idx] or ""),
                               "source": "excel", "area": "fiverr" if name == "Sprint-Tracker" else "saas",
                               "notes": str(v[11] or "") if name == "Sprint-Tracker" else ""})
            return result
        main_rows = rows_for("Sprint-Tracker", 3, 24, 20, 21, 3)
        saas_rows = rows_for("SaaS-Stripe Roadmap", 9, 13, 9, 10, 2)
        wb.close()
        if len(main_rows) != 61 or len(saas_rows) != 24:
            return {"state": "schema_mismatch", "filename": TRACKER.name, "rows": [],
                    "sheets": [], "reason": "Aufgabenanzahl anders als verifiziert: "
                    + str(len(main_rows)) + " Fiverr / " + str(len(saas_rows)) + " SaaS"}
        items = main_rows + saas_rows
        return {"state": "loaded", "filename": TRACKER.name, "sha256": digest,
                "rows": items, "mapped_rows": len(items),
                "fiverr_count": len(main_rows), "saas_count": len(saas_rows),
                "fiverr_technical": sum(x["technical_checked"] for x in main_rows),
                "fiverr_live": sum(x["live_checked"] for x in main_rows),
                "saas_technical": sum(x["technical_checked"] for x in saas_rows),
                "saas_live": sum(x["live_checked"] for x in saas_rows),
                "sheets": [{"name": x, "mapped": True} for x in sorted(required)],
                "warning": "Häkchen aus Excel unverändert. PR-Evidence separat; kein automatischer Freigabetransfer."}
    except Exception as exc:
        return {"state": "error", "filename": TRACKER.name, "rows": [],
                "reason": type(exc).__name__ + ": " + str(exc)[:140]}


def evidence():
    """Curated, versioned review findings are separate from spreadsheet checkboxes."""
    try:
        return json.loads((ROOT / "data" / "evidence-status.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"state": "unavailable", "work_items": [], "cross_cutting": []}


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
    return {"generated_at_utc": utc_now(), "tracker": tracker(), "project_store": read_summary(), "sprint_evidence": evidence(), "repositories": repos,
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
