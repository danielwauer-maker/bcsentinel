"""Fail-closed live sprint radar: PR observations are not approvals or runtime proofs."""
from __future__ import annotations
import datetime as dt
import re
import threading
import time

ROOT_REPOS = ("danielwauer-maker/bcsentinel", "danielwauer-maker/bcsentinel-frontend")
CACHE_TTL = 300
_lock = threading.Lock()
_cache = None
_cached_at = 0.0

def recent_prs(fetch, *, clock=time.monotonic):
    """Read only the latest 100 PRs per repository; never invent completeness."""
    global _cache, _cached_at
    now = clock()
    with _lock:
        if _cache is not None and now - _cached_at < CACHE_TTL:
            return dict(_cache)
        prs, errors = {}, []
        for repo in ROOT_REPOS:
            result = fetch(f"repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=100&page=1")
            if not isinstance(result, list):
                errors.append({"repo": repo, "reason": "GitHub read unavailable"})
                continue
            for p in result:
                try:
                    number = int(p["number"])
                    if number <= 0 or p.get("html_url") != f"https://github.com/{repo}/pull/{number}":
                        continue
                    prs[f"{repo}#{number}"] = {
                        "number": number, "repo": repo, "url": p["html_url"],
                        "title": str(p.get("title") or "")[:180],
                        "state": ("merged" if p.get("merged_at") else
                                  "draft" if p.get("state") == "open" and p.get("draft") else
                                  "open" if p.get("state") == "open" else "closed_unmerged"),
                        "updated_at": p.get("updated_at")
                    }
                except (ValueError, KeyError, TypeError):
                    continue
        result = {"state": "partial" if errors else "loaded",
                  "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                  "coverage": "latest_100_per_repository; older PRs unknown",
                  "observations": prs, "errors": errors}
        # Do not extend validity of stale data on a failed source; next request may retry.
        if not errors:
            _cache, _cached_at = result, now
        return dict(result)

def reference_key(ref):
    match = re.fullmatch(r"https://github\.com/(danielwauer-maker/(?:bcsentinel|bcsentinel-frontend))/pull/(\d+)", ref or "")
    return match.group(1) + "#" + match.group(2) if match else None

def area_for(item_id):
    major = item_id.split(".", 1)[0]
    return {"1": "Release & BC27", "2": "Datenqualität & Provenance",
            "3": "Reports & Monitoring", "4": "Produkt & Access-v2",
            "6": "Website & Vertrieb", "7": "Fiverr Buyer Journey"}.get(major, "Weitere Bereiche")

def _classify(item, linked, approved):
    status = item.get("status")
    if approved:
        return ("manual_attested", "Manuell belegter Gate-Status", "Nachweis und Freigabe separat überprüfen")
    if status == "editorial_complete":
        return ("waiting", "Redaktionell fertig – Veröffentlichung offen", "Implementierung und finale Freigabe prüfen")
    if status in ("tracker_checked",):
        return ("waiting", "Historisch abgehakt – erneut verifizieren", "Artefakt und DEV-Laufzeit erneut abgleichen")
    if status == "manual_gate":
        return ("next", "Als Nächstes: manuelle Abnahme", "BC27-Sandbox-Abnahme durchführen")
    if status == "audit_draft":
        return ("waiting", "Wartet auf Vertragsentscheidung", "Aktiven Access-v2-Vertrag freigeben")
    if status in ("partial", "implementation_draft", "code_candidate"):
        if any(p["state"] == "merged" for p in linked):
            return ("waiting", "Quellcode teilweise integriert – E2E offen", "DEV-/BC27-Funktion und Abnahme belegen")
        return ("in_progress", "Implementierung / Evidence offen", "PR- und CI-Evidence gezielt prüfen")
    return ("unverified", "Status nicht unabhängig verifiziert", "Nachweise und Zuständigkeit klären")

def build_radar(source, store, github_observation):
    """Build action cards without mutating the tracker, PRs, or approval register."""
    items = source.get("work_items", [])
    observed = github_observation.get("observations", {})
    valid_tasks = store.get("state") == "loaded"
    tasks = {str(x.get("source_id")): x for x in store.get("tasks", [])
             if x.get("area") == "fiverr"} if valid_tasks else {}
    approvals = {}
    if valid_tasks:
        for a in store.get("approvals", []):
            approvals.setdefault(a.get("task_key"), set()).add(a.get("gate"))
    rows = []
    for item in items:
        task_id = str(item.get("id", ""))
        linked, missing = [], []
        for ref in item.get("refs", []):
            key = reference_key(ref)
            if key:
                match = observed.get(key)
                if match is None:
                    missing.append(ref)
                else:
                    linked.append(match)
        task = tasks.get(task_id, {})
        gates = approvals.get(task.get("task_key"), set())
        category, label, next_action = _classify(item, linked, bool(gates))
        if not valid_tasks and category == "manual_attested":
            category = "unverified"
        if github_observation.get("state") != "loaded" and category == "in_progress":
            next_action = "GitHub-Quelle derzeit unvollständig; PR-Stand erneut prüfen"
        if task_id == "1.03":
            next_action = "BC27 1.0.2.60: Paket-SHA, installierte Version und Datenerhalt in Sandbox prüfen"
        elif task_id == "1.02":
            next_action = "Aktuellen DEV-Release und Wiederherstellungsnachweis gegen Release-Evidence prüfen"
        elif task_id == "4.01":
            next_action = "Produkt-System-Vertrag und Preismatrix normativ entscheiden"
        elif task_id == "3.02":
            next_action = "Free-Baseline → Full-Report mit berechtigtem BC27-Nutzer E2E prüfen"
        rows.append({"id": task_id, "title": task.get("title") or task_id,
                     "area": area_for(task_id), "category": category, "label": label,
                     "next_action": next_action, "source_status": item.get("status"),
                     "detail": str(item.get("detail", ""))[:750], "prs": linked,
                     "unresolved_pr_refs": missing[:8], "reviewed_at": source.get("reviewed_at"),
                     "manual_gates": sorted(gates), "task_stage": task.get("stage", "not_loaded")})
    # Display every imported task. Unreviewed entries never claim completion.
    reviewed_keys = {("fiverr", row["id"]) for row in rows}
    if valid_tasks:
        for task in store.get("tasks", []):
            area = str(task.get("area", ""))
            source_id = str(task.get("source_id", ""))
            if area not in ("fiverr", "saas") or (area, source_id) in reviewed_keys:
                continue
            rows.append({
                "id": source_id, "title": str(task.get("title") or source_id)[:200],
                "area": ("SaaS & Stripe" if area == "saas" else area_for(source_id)),
                "category": "unverified", "label": "Noch nicht einzeln reconciliert",
                "next_action": "PRs, Code, CI und Runtime dieser Aufgabe zuordnen",
                "source_status": "not_reviewed", "detail": "Historischer Tracker-Eintrag; noch kein aktueller Einzelreview.",
                "prs": [], "unresolved_pr_refs": [], "reviewed_at": source.get("reviewed_at"),
                "manual_gates": [], "task_stage": task.get("stage", "not_loaded"),
            })
    # Explicit verified infrastructure work is separate from the 61 Fiverr task acceptance gates.
    infra = source.get("observed_gates", {}).get("admin_integration", {})
    runtime = source.get("observed_gates", {}).get("dev_runtime_release_20261116", {})
    milestones = [
        {"name": "AI Control Center / Admin", "state": "dev_verified" if
         "operator_verified" in str(infra.get("nginx_admin_proxy", "")) else "unverified",
         "remaining": "Rollen- und Session-Sicherheit separat abnehmen",
         "source": "Kuratierte Betreiber-Evidence, nicht laufend gemessener Dienst"},
        {"name": "DEV Backend / Migration", "state": "dev_verified" if
         runtime.get("backend", {}).get("state") == "deployed_exact_staging_sha" else "unverified",
         "remaining": "Real BC27 E2E und Backup-Restore-Abnahme",
         "source": "Exact-SHA Release-Evidence"},
        {"name": "BC27 SaaS Runtime", "state": "not_executed",
         "remaining": "12 manuelle Abnahmefälle, derzeit nicht ausgeführt",
         "source": "BC27 Acceptance Register"},
    ]
    counts = {s: sum(x["category"] == s for x in rows)
              for s in ("next", "in_progress", "waiting", "manual_attested", "unverified")}
    priority = sorted(rows, key=lambda x: (0 if x["id"] == "1.03" else
                      1 if x["category"] == "next" else
                      2 if x["id"] == "1.02" else
                      3 if x["category"] == "in_progress" else 4, x["id"]))
    return {"state": "partial" if github_observation.get("state") != "loaded" or not valid_tasks else "loaded",
            "source_date": source.get("reviewed_at"), "github": {k: github_observation.get(k)
                      for k in ("state", "observed_at", "coverage", "errors")},
            "inventory": {"fiverr_total": 61, "saas_total": 24, "reviewed_fiverr": len(items),
                          "other_fiverr_unreviewed": max(0, 61-len(items)),
                          "unreviewed_total": sum(x["category"] == "unverified" for x in rows),
                          "store_state": store.get("state")},
            "counts": counts, "milestones": milestones,
            "next": priority[:5], "items": rows,
            "disclaimer": "PR-Merges sind nur Quellcode-Evidence; kein automatisch bestandenes CI, DEV-, BC27- oder Go-Live-Gate.",
            "go_live": "NO_GO"}
