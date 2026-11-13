# CI-OPT-01 — staged, fail-safe GitHub Actions optimization (2026-11-12)

Status: **Draft / integration review only.** Base: `staging`. Do **not** merge automatically while PR #172 is awaiting release evidence. This isolated change does not touch application code, Alembic, payments, main/PROD or DEV infrastructure.

## Facts from actual GitHub Actions runs

- The integration PR #172 expands to ~270 changed paths; GitHub's `pull_request.paths` matching is evaluated against the **whole PR diff**, not only the latest commit. Consequently, a docs-only commit to that already-large PR can still re-trigger Windows AL/BC27 jobs.
- Three main expensive Windows workflows: `bc-al-compile.yml` (fresh + upgrade, 60 minute per-job limit), `ext-50-12b-bc27-runtime-gate.yml` (45 minute limit) and `ext-50-12c-3-al.yml` (fresh + upgrade, 60 minute per-job limit).
- Other workflows generally finish in minutes; exact duration varies substantially with runner availability and downloads.
- In #172, a separate push-only Finding AL workflow initially failed before jobs started due to malformed YAML. A green PR-only summary therefore cannot substitute for a full release check inventory.

## Stage A — implemented in this PR (safe PR supersession)

On supported workflows use:
```yaml
concurrency:
  group: ${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || format('{0}-{1}-{2}', github.workflow, github.event_name, github.run_id) }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

A new commit to the *same PR* cancels obsolete invocations of the *same workflow*, including costly BC27 Windows jobs. Only PR-triggered runs are cancelled. Every push or manually dispatched release run uses its unique run ID as its concurrency group; this avoids GitHub replacing a pending release run with another event in the same group, even when `cancel-in-progress` is false. Neither `push` on staging nor a manually dispatched release run is subject to cancellation. Separate workflows retain distinct concurrency groups; different PR numbers do not interfere.

**Important limits:** this does not reduce the duration of the **final** BC27 test; it prevents spending 45+ minutes on outdated versions while new commits arrive. It does not disable any current tests, skip required jobs, or falsely claim final CI PASS.

Workflows modified: `bc-al-compile.yml`, `ext-50-12b-bc27-runtime-gate.yml`, `ext-50-12c-3-al.yml`, `core-pilot-50-readiness.yml`, `pilot-e2e-01a.yml`, `p0-04-postgres-migration-cycle.yml`, `p0-05-postgres-backup-restore.yml`.

## Stage B — design only, NOT enabled (fast PR tier / full release tier)

To avoid 45-minute BC jobs for every minor PR commit, run:
1. **Fast PR tier (automatically):** source/AL static contracts, lint, selected backend/security tests, migration compatibility, report contract and workflow syntax. Expected budget 2–8 minutes, to be measured.
2. **Full release tier (explicit, exact SHA):** all required container-backed BC27 fresh/upgrade tests, runtime/permission checks, backend/DB E2E, migration rehearsal and report integration. Must prove all gates PASS on the precise merge candidate SHA.
3. **Machine-enforced release attestation** must check required workflow IDs/names, exact SHA, conclusion success, artifact freshness and BC27 matrix coverage before staging merge/deploy. Manual dispatch must be checked to use the exact branch SHA; skipped checks are NOT sufficient.
4. **Before switching triggers**, inspect repository branch protection and required status checks. Current GitHub App token cannot access staging branch protection (HTTP 403). Do NOT drop `pull_request` triggers until required check names and a replacement fail-closed gate are confirmed by an authorized administrator.
5. Avoid `paths` as the only security boundary, because huge PR diffs and merge queues can surprise; changes to AL/product models/DB entitlements require Full CI or policy-enforced acceptance.
6. Optional later: reusable immutable BC27 artifact/cache and consolidated container test suites; assess cache integrity, old-version dependencies and reproducibility. Never cache secrets or mutable database state.

## Validation checklist for this PR

- [x] Baseline source inspected (three Windows gates, timeouts, triggers).
- [x] Scoped concurrency added; PR cancellation only, release push and manual dispatch retained.
- [ ] Static contract checker workflow on exact PR head PASS.
- [ ] One throwaway PR smoke: commit A running, commit B submitted; only A canceled; B survives.
- [ ] One manual workflow_dispatch smoke: verify it is not canceled by PR commit.
- [ ] Branch protection review from admin before altering triggers or required-check names.
- [ ] Stage B enforced release attestation and fast-only PR switch (separate future PR).
- [ ] Existing #172 exact-SHA Full CI and independent Finding AL results remain mandatory for DEV merge.

**No changes to protected release authorization:** #172 exact-SHA DEV deployment gates remain independent. A successful CI-OPT-01 draft PR is not a DEV or Fiverr GO.
