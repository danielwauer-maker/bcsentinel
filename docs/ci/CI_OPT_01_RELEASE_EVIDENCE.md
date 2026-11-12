# CI-OPT-01 — exact-SHA release evidence attestation

**Status: standalone DRAFT, informational only. Never deploys or merges.** Independent from PR #172 and PR #173.

## Purpose

Before the final staging integration, prove that the **exact reviewed PR head SHA** and **unchanged staging base SHA** have the complete required automated evidence. A green overall GitHub check with skipped jobs or a prior SHA is not sufficient.

- Mandatory inputs: integration PR number, full reviewed PR head SHA, full staging base SHA.
- Live GitHub API verification of PR existence, `open` state, `base.ref=staging`, `head.sha`, `base.sha`, and `mergeable=true`.
- Compare 20 exact required named `pull_request` workflows against the target commit SHA, including completion and `success` conclusion for the **latest** corresponding run. A newer failed/pending run invalidates an older PASS.
- Additionally require the independent `EXT-50-12C.3 BC finding identity` **push** workflow, with both successful and uniquely present `fresh` and `upgrade` Windows matrix jobs. This prevents the previously missed zero-job YAML failure from being mistaken for a pass.
- Explicit failure on missing, skipped, cancelled, failed or pending workflow; changed PR head/base; API errors; malformed inputs; missing matrix jobs; pagination truncation. Persist a compact evidence JSON artifact with names and run IDs, not secrets.
- The GitHub API `actions/runs?head_sha=<SHA>` filter was checked against an actual BCSentinel commit and returned both PR and push runs at that exact SHA.

## Dispatch availability caveat (verified repository default branch)

The repository's default branch is **`main`**, not `staging`. GitHub Actions `workflow_dispatch` typically requires the workflow file to exist on the default branch to be accessible from the Actions UI/API. Therefore **merging this draft only to staging does not guarantee that the manual action can actually be launched**. Do not merge the workflow to `main` merely to enable dispatch: the existing main-push deployment policy can deploy PROD. An explicit, separately reviewed workflow-only installation on the default branch (with a verified no-PROD-deploy window) or an authorized external read-only invocation of `scripts/ci_release_attestation.py` is necessary before claiming the manual control operational.

## Safe usage (after this workflow is merged and available)

From GitHub → Actions → **CI OPT 01 Exact SHA Release Evidence (informational)** → Run workflow, supply the three mandatory fields:

```
pull_request_number: 172
expected_pr_head_sha: <actual 40-hex PR HEAD as checked at run time>
expected_staging_base_sha: <actual 40-hex staging base as checked at run time>
```

**No default SHA is assumed.** The workflow explicitly reads Actions and pull request metadata but has no write permissions and performs no SSH, database, BC installation, merge or deployment. Review JSON evidence and both Finding-Identity Windows jobs.

Even a PASS is **pre-merge test evidence only**, not permission to deploy. A merge creates a different `staging` SHA, so the deployment authorization and runtime checks still require that exact **post-merge staging SHA**. This checker does **not** claim that the merged SHA was tested.

## Relationship to CI-OPT-01 Stage A (#173) and Stage B

- #173 independently adds PR-only obsolete-run cancellation. Never cancel `staging` push or manually dispatched release evidence.
- This standalone exact-SHA verifier provides a foundation for a later fail-closed fast-PR / full-release system, but it is not yet a required branch-protection check.
- **DO NOT disable the current 45-minute PR BC27 tests yet.** The GitHub App's staging branch protection API returned HTTP 403; an authorized admin must confirm required status checks first.
- Future Stage B must provide a mandatory always-present gate status required by branch protection, capable of validating immutable full-release artifacts and every necessary contract before a merge. A manual workflow that can be forgotten is not such a gate.
- Revalidate changes to the mandatory workflow inventory if workflows are renamed or consolidated; never silently reduce test coverage.

## Acceptance

- [x] Script is read-only and fails closed on missing, stale or unsuccessful evidence.
- [x] Offline tests include successful evidence, changed base/head, missing/failing AL matrix, failed push, pending PR workflow and newer failed PR run.
- [x] Verified BCSentinel GitHub Actions endpoint accepts exact head_sha and reports PR plus push event runs.
- [ ] Self-test workflow success on this draft PR exact HEAD.
- [ ] Manual workflow_dispatch sample against a known incomplete PR returns NO_GO with evidence artifact.
- [ ] Manual workflow_dispatch sample with genuinely complete independent AL/PR evidence returns PASS.
- [ ] Admin verifies branch protection requirements before any trigger changes or merge enforcement.
- [ ] CI-OPT-01 #173 separately accepted with actual supersession behavior smoke.

Fiverr remains **NO_GO**. No deployment or PROD change is part of this work.
