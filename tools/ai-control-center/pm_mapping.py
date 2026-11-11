"""Conservative multi-task PR evidence mapping.

Sources: curated versioned review references, or unique explicit Sprint/Task tokens.
No semantic guesses, task-stage transitions, or approvals.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_PREFIX = "https://github.com/danielwauer-maker/"
DIRECT_RE = re.compile(r"(?<![\w])(?:sprint|task|arbeitspaket)\s*[:#-]?\s*(\d{1,2}\.\d{2})(?![\w.])", re.I)
SHORT_RE = re.compile(r"(?<![\w])s(\d{1,2}\.\d{2})(?![\w.])", re.I)
TRACKER_KEY_RE = re.compile(r"^(?:fiverr|saas):[^\s]+$")
PR_REF_RE = re.compile(r"^https://github\.com/(danielwauer-maker/[\w-]+)/pull/(\d+)(?:/)?$")


def curated_map(source):
    """Only reviewed work_items; cross_cutting is context, not task attribution."""
    mapping = {}
    for item in source.get("work_items", []):
        task_id = str(item.get("id", "")).strip()
        for url in item.get("refs", []):
            match = PR_REF_RE.fullmatch(url)
            if not match:
                continue
            mapping.setdefault((match.group(1), int(match.group(2))), set()).add(task_id)
    return mapping


def evidence_source(root=None):
    path = Path(root or Path(__file__).resolve().parent) / "data" / "evidence-status.json"
    try:
        source = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(source.get("work_items"), list):
            return {}
        return curated_map(source)
    except (OSError, ValueError, TypeError):
        return {}


def match_evidence(pr, tasks, reviewed):
    """Return 0-N separately justified links; conflicts are deferred for review."""
    index = {}
    for task in tasks:
        index.setdefault(str(task["source_id"]), []).append(str(task["task_key"]))
    repo_number = (pr["repo"], int(pr["number"]))
    reviewed_ids = reviewed.get(repo_number, set())
    # Multi-task reviewed references are allowed and individual evidence links stay attributable.
    if reviewed_ids:
        links = []
        missing = []
        for code in sorted(reviewed_ids):
            candidates = index.get(code, [])
            if len(candidates) == 1 and candidates[0].startswith("fiverr:"):
                links.append({"task_key": candidates[0], "source": "reviewed_reference",
                              "reason": "Versionierter Evidence-Review enthält exakten GitHub-PR-Link"})
            else:
                missing.append(code)
        if missing:
            return {"state": "review", "links": [], "reason": "Review-Referenz ohne eindeutige Fiverr-Aufgabe: "+", ".join(missing)}
        return {"state": "reviewed", "links": links, "reason": "Explizite kuratierte PR-Referenz"}

    # Only unique direct tokens in PR title or branch. Body can contain many incidental
    # references (dependency lists, checklist, future sprints), and must never silently attribute.
    text = " ".join(str(pr.get(k) or "") for k in ("title", "head_ref"))
    found = set(DIRECT_RE.findall(text)) | set(SHORT_RE.findall(text))
    if len(found) > 1:
        return {"state": "review", "links": [], "reason": "Mehrere Sprint-Kennungen in Titel/Branch: "+", ".join(sorted(found))}
    if not found:
        return {"state": "unmatched", "links": [], "reason": "Keine eindeutige Sprint-Kennung oder kuratierte PR-Referenz"}
    code = next(iter(found))
    candidates = index.get(code, [])
    if len(candidates) != 1 or not candidates[0].startswith("fiverr:"):
        return {"state": "review" if candidates else "unmatched", "links": [],
                "reason": "Kennung "+code+" hat keine eindeutige Fiverr-Aufgabe"}
    return {"state": "matched", "links": [{"task_key": candidates[0],
             "source": "explicit_sprint_marker", "reason": "Eindeutige Kennung in PR-Titel/Branch"}],
            "reason": "Explizite Sprint-Kennung"}


def review_summary(rows, limit=30):
    pending = [r for r in rows if r["match_state"] in ("review","unmatched")]
    return {"pending_count": len(pending),
            "items": [{"repo": r["repo"], "number": r["number"],
                       "title": r["title"], "url": r["url"],
                       "reason": r.get("reason", "Ohne eindeutige Zuordnung"),
                       "state": r["match_state"]} for r in pending[:limit]]}
