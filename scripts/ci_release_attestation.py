#!/usr/bin/env python3
"""Read-only, exact-SHA pre-merge CI evidence attestation for BCSentinel.

This is NOT deployment authorization or a replacement for branch protection.
Requires an explicit PR number, full PR-head SHA and full staging-base SHA.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REQUIRED_PR_WORKFLOWS = (
    "EXT-50-12B Copied Company Recovery",
    "EXT-50-12C.3 lossless findings backend",
    "EXT-50-12C Runtime Evidence Contracts",
    "PILOT-E2E-01A Automated Readiness",
    "EXT-50-01 Release Baseline",
    "EXT-50-03 Upgrade Contract",
    "EXT-50-12A Generator Safety Contract",
    "P0-05 PostgreSQL Backup Restore",
    "EXT-50-12C.3 BC finding identity",
    "P0-07 Dashboard Report Contract",
    "BC Native Report Access Integration Tests",
    "Portfolio Evidence Export",
    "Core Pilot 50 Readiness",
    "S06 Release Readiness",
    "EXT-50-04 Permission Role Matrix",
    "EXT-50-12B BC27 Runtime Gate",
    "BC AL Compile and Cop Gate",
    "ARCH-02A Compatibility Gate",
    "BC Extension AL Build (Sandbox Test)",
    "P0-04 PostgreSQL Migration Cycle",
)
FINDING_WORKFLOW = "EXT-50-12C.3 BC finding identity"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def get_json(url: str, token: str) -> dict:
    req = Request(
        url,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "bcsentinel-ci-opt01-readonly-attestation",
        },
    )
    with urlopen(req, timeout=25) as response:
        return json.load(response)


def fetch_pages(base_url: str, token: str, collection: str) -> list[dict]:
    rows: list[dict] = []
    for page in range(1, 11):
        sep = "&" if "?" in base_url else "?"
        body = get_json(f"{base_url}{sep}per_page=100&page={page}", token)
        batch = body.get(collection)
        if not isinstance(batch, list):
            raise ValueError(f"Missing {collection} in GitHub API response")
        rows.extend(batch)
        if len(batch) < 100:
            return rows
    raise ValueError("GitHub API pagination exceeded 1,000 entries: fail closed")


def newest_by_name(runs: list[dict], event: str, sha: str) -> dict[str, dict]:
    grouped: dict[str, dict] = {}
    for run in runs:
        if run.get("event") != event or run.get("head_sha") != sha:
            continue
        name = str(run.get("name") or "")
        prior = grouped.get(name)
        identity = (str(run.get("created_at") or ""), int(run.get("run_attempt") or 0), int(run.get("id") or 0))
        if prior is None or identity > (
            str(prior.get("created_at") or ""),
            int(prior.get("run_attempt") or 0),
            int(prior.get("id") or 0),
        ):
            grouped[name] = run
    return grouped


def verify_evidence(
    pr: dict, runs: list[dict], finding_jobs: list[dict],
    *, pr_number: int, head_sha: str, base_sha: str,
) -> dict:
    problems: list[str] = []
    if pr.get("number") != pr_number:
        problems.append("PR number mismatch")
    if pr.get("state") != "open":
        problems.append("PR must remain open for pre-merge attestation")
    if pr.get("base", {}).get("ref") != "staging":
        problems.append("PR must target staging")
    if pr.get("head", {}).get("sha") != head_sha:
        problems.append("PR head SHA changed")
    if pr.get("base", {}).get("sha") != base_sha:
        problems.append("staging base SHA changed: re-review diff and rerun")
    if pr.get("mergeable") is not True:
        problems.append("PR mergeable status is not confirmed true")

    pr_runs = newest_by_name(runs, "pull_request", head_sha)
    verified: list[dict] = []
    for name in REQUIRED_PR_WORKFLOWS:
        run = pr_runs.get(name)
        if run is None:
            problems.append(f"Missing required PR workflow: {name}")
        elif run.get("status") != "completed" or run.get("conclusion") != "success":
            problems.append(f"Required PR workflow not PASS: {name} ({run.get('status')}/{run.get('conclusion')})")
        else:
            verified.append({"name": name, "id": run["id"], "sha": head_sha, "event": "pull_request"})

    push = newest_by_name(runs, "push", head_sha).get(FINDING_WORKFLOW)
    if push is None:
        problems.append("Independent finding AL PUSH workflow absent")
    elif push.get("status") != "completed" or push.get("conclusion") != "success":
        problems.append(f"Independent finding AL PUSH not PASS ({push.get('status')}/{push.get('conclusion')})")
    else:
        verified.append({"name": FINDING_WORKFLOW, "id": push["id"], "sha": head_sha, "event": "push"})

    # GitHub matrix jobs: success of both distinct BC27 paths, not only workflow-level status.
    for deployment in ("fresh", "upgrade"):
        matching = [job for job in finding_jobs if
                    str(job.get("name") or "").endswith(f"({deployment})")]
        if len(matching) != 1 or any(j.get("conclusion") != "success" for j in matching):
            problems.append(f"Independent finding AL {deployment} job not uniquely PASS")

    return {
        "schema_version": 1,
        "kind": "premerge_evidence_only_not_deploy_authorization",
        "pr_number": pr_number,
        "pr_head_sha": head_sha,
        "staging_base_sha": base_sha,
        "required_pr_workflows": len(REQUIRED_PR_WORKFLOWS),
        "verified_workflows": verified,
        "finding_al_matrix_jobs": [
            {"name": str(j.get("name") or ""), "conclusion": j.get("conclusion")}
            for j in finding_jobs
        ],
        "passed": not problems,
        "errors": problems,
    }


def self_test() -> None:
    head, base = "a" * 40, "b" * 40
    pr = {
        "number": 172, "state": "open", "mergeable": True,
        "head": {"sha": head}, "base": {"sha": base, "ref": "staging"},
    }
    runs = [
        {"name": name, "id": i, "head_sha": head, "event": "pull_request",
         "created_at": "2026-11-12T00:00:00Z", "status": "completed",
         "conclusion": "success"}
        for i, name in enumerate(REQUIRED_PR_WORKFLOWS, 1)
    ]
    runs.append({"name": FINDING_WORKFLOW, "id": 99, "head_sha": head,
                 "event": "push", "created_at": "2026-11-12T00:00:00Z",
                 "status": "completed", "conclusion": "success"})
    jobs = [
        {"name": "BC 27 AL compile with CodeCop and PTECop (fresh)", "conclusion": "success"},
        {"name": "BC 27 AL compile with CodeCop and PTECop (upgrade)", "conclusion": "success"},
    ]
    def check_ok():
        return verify_evidence(pr, runs, jobs, pr_number=172, head_sha=head, base_sha=base)
    assert check_ok()["passed"]
    assert not verify_evidence(pr, runs, jobs, pr_number=172, head_sha=head, base_sha="c"*40)["passed"]
    assert not verify_evidence(pr, runs, jobs, pr_number=172, head_sha="c"*40, base_sha=base)["passed"]
    jobs[0]["conclusion"] = "failure"
    assert not check_ok()["passed"]
    jobs[0]["conclusion"] = "success"
    runs[-1]["conclusion"] = "failure"
    assert not check_ok()["passed"]
    runs[-1]["conclusion"] = "success"
    runs[0]["status"] = "in_progress"
    assert not check_ok()["passed"]
    runs[0]["status"] = "completed"
    runs.append({**runs[0], "id": 101, "created_at": "2026-11-12T01:00:00Z",
                 "conclusion": "failure"})
    assert not check_ok()["passed"], "newer failed run must invalidate prior PASS"
    print("RELEASE_ATTESTATION_SELF_TEST=PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--head")
    parser.add_argument("--base")
    parser.add_argument("--output", default="release-attestation.json")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.pr or not args.head or not args.base:
        parser.error("--pr, --head and --base are all mandatory")
    if not SHA_PATTERN.fullmatch(args.head) or not SHA_PATTERN.fullmatch(args.base):
        parser.error("--head and --base must be complete lowercase 40-hex commit SHAs")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not REPO_PATTERN.fullmatch(repo) or not token:
        parser.error("GITHUB_REPOSITORY and GITHUB_TOKEN required")
    api = f"https://api.github.com/repos/{repo}"
    pr = get_json(f"{api}/pulls/{args.pr}", token)
    query = urlencode({"head_sha": args.head})
    runs = fetch_pages(f"{api}/actions/runs?{query}", token, "workflow_runs")
    finding = newest_by_name(runs, "push", args.head).get(FINDING_WORKFLOW)
    jobs = (
        fetch_pages(f"{api}/actions/runs/{finding['id']}/jobs", token, "jobs")
        if finding else []
    )
    result = verify_evidence(pr, runs, jobs, pr_number=args.pr,
                             head_sha=args.head, base_sha=args.base)
    result["checked_at_utc"] = datetime.now(timezone.utc).isoformat()
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
        file.write("\n")
    print(f"Release premerge attestation: {'PASS' if result['passed'] else 'NO_GO'}")
    for error in result["errors"]:
        print(f"BLOCKED: {error}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (HTTPError, URLError, OSError, ValueError, KeyError) as exc:
        print(f"Release attestation NO_GO: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
