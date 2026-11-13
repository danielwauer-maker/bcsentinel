# DEV Consolidation Report — 2026-11-13

## Scope and candidate heads

This is a source-only DEV release candidate.  No merge to `main` or `staging`,
no deployment, no production database action, and no interaction with the
running AI Control Center on port 8092 occurred.

| Repository | Integration branch | Candidate SHA | Selected core |
| --- | --- | --- | --- |
| `danielwauer-maker/bcsentinel` | `integration/dev-consolidation-20261113` | `b34f96c127509c77830dd9700b95dce487c8e4ca` | PR #172 `f5dd128693a4d79209ac8bc66d860f9e10d6bed6` |
| `danielwauer-maker/bcsentinel-frontend` | `integration/dev-consolidation-20261113` | `69ab09d5603669570c8e1f9223c65b664b40c636` | PR #13 `60af4902a294488f87ff151ffd41f26a79f7d365` |

GitHub API/Actions status could not be queried from this environment (no
authenticated API access).  Open PRs were inventoried reproducibly from their
available `refs/pull/<n>/merge` refs; a merge ref exists only while GitHub can
calculate an open PR merge result.  “Included” below is supported by ancestry,
exact reverse-patch testing, or a recorded merge/cherry-pick.

## Backend PR disposition

| PR | Head SHA | Disposition |
| --- | --- | --- |
| #115 | `bc3ebf22ee4a7225516f5fb55f8a65abd707377c` | Blocked separately: very old monolithic divergence; not safe to merge without a focused rebase. |
| #151 | `3e01b28e94cdcc995efbcfa4a2a7a014818caf9e` | Included as an ancestor of #172. |
| #152 | `7eb8dbe17bb35ef908e063a189ad7aa5801f295c` | Replaced/blocked: it would regress extension identity from `1.0.2.59` to `1.0.2.52`; rebase the permission-only fixes onto the current candidate. |
| #153 | `04ff58b12450f01b294170e5f12e08f0313b30fe` | Replaced/blocked: same version regression and removal of newer dashboard action during trial merge; requires a current BC27 rebase. |
| #154 | `ad7f570c21c37fbb6b0cce04e8c462a76c604947` | Included as an ancestor of #172. |
| #155 | `8089f510802177cde90ff9dd8c9997b1f6170fcc` | Included as an ancestor of #172. |
| #156 | `5540af9f578c5d244216e94ef8b4b2d9c4441a9a` | Included as an ancestor of #172. |
| #157 | `85f5bf168c6aa5a4181e2d5097918c82aa27615c` | Included as an ancestor of #172. |
| #158 | `0f4bce6ba93c8ed8548b239c16a679f076917844` | Included as an ancestor of #172; exact patch also reverse-applies. |
| #159 | `54a8876772e007393071cdcc024e2856d6d0b531` | Included as an ancestor of #172. |
| #162 | `a8b870eb41d29913cc0837a558c30637be8c57f2` | Included as an ancestor of #172; exact patch also reverse-applies. |
| #163 | `98a44b0e36629fecc164775a3521b3287a4a210c` | Included by focused documentation cherry-picks. |
| #164 | `034f4665c203ae6b17f15119708634fd2d528fa0` | Included by focused documentation cherry-picks. |
| #165 | `1cd30bf6976dd6353c53ce41d7b42b965928a0e3` | Included by focused documentation cherry-picks. |
| #166 | `f4faf120ae334f6b3fef9cac84a2777ac53930d3` | Included by merge commit `d402367b`. |
| #167 | `ef4afcca55888ae2b8497fa3d55d7fb7a128d309` | Included through the #176 AI Control Center history. |
| #168 | `114a206ac3f84587a787894823a6a96936577c7a` | Included as an ancestor of #172; exact patch also reverse-applies. |
| #169 | `e0a05ce896a42b4811b5d136155d6960c9840d15` | Included through the #176 AI Control Center history. |
| #170 | `86ab6af7118a1b8d3a7a898833abbdedca4ad38c` | Blocked separately: its dashboard evidence snapshot carries stale/unverified external CI/runtime assertions. Refresh it against this candidate before merge. |
| #171 | `264e5c21b30255c554979ec04884de9b7c72807d` | Included through the #176 AI Control Center history. |
| #172 | `f5dd128693a4d79209ac8bc66d860f9e10d6bed6` | Selected backend core. |
| #173 | `a0dd1a55eff8eed8fc91a3411888bc75aeffb363` | Included by merge commit `39460ff5`; static CI concurrency contract passes. |
| #174 | `523ea533f6ec23e05671635b06d5e9e2ee4b8cc1` | Included by merge commit `5d97db8b`; exact-SHA attestation self-test passes. |
| #175 | `122241b529c9e497e0c9a01d6c225a4fd9f89413` | Included by `6be485e3`, resolving conflict in favor of manual exact-SHA DEV dispatch while retaining the Core's stricter remote-checkout/nginx preservation. |
| #176 | `92d2cc3d76e18b13a837207d03cddeba4bcd9af5` | Included by merge commit `bf7c9379`; the pre-existing Draft PR itself was not modified. |

The consolidation additionally fixes the discovered route-mount defect in
`4817f984`: the reserved commercial checkout endpoint is mounted directly and
always responds from its deliberate fail-closed `503` handler.  The broader
prepilot aggregate remains unmounted.

## Frontend PR disposition

| PR | Head SHA | Disposition |
| --- | --- | --- |
| #6 | `46bed836f7cc25514ef7757cd672fc04ceac3dc5` | Included by the two focused architecture/documentation cherry-picks. |
| #9 | `7da35e3896198ec1b9facb68089a8f7874805234` | Replaced by the later Full-v6 candidate #13; do not merge the older source snapshot in parallel. |
| #10 | `265def8656ac2fc7f81351d4857e7edf6199fbda` | Included in #13; reverse-patch check passes. |
| #11 | `d667b22818138a92b33bd6b68965b3c1cbb53efe` | Included in #13; reverse-patch check passes. |
| #12 | `c374bc996c450eef7f2864f798eca5546a12d914` | Replaced by #13: the current Full-v6 source retains the one-time-code race protection and test coverage; its historical evidence document needs no parallel merge. |
| #13 | `60af4902a294488f87ff151ffd41f26a79f7d365` | Selected frontend core. |

## Verification

| Gate | Result |
| --- | --- |
| Targeted backend admin, AI proxy and BC contract tests | PASS — 52 tests. |
| Commercial checkout route regression plus admin/AI tests | PASS — 26 tests after the route-mount fix. |
| Full backend suite | PASS — 964 passed, 22 skipped, 2 xfailed. |
| CI optimization static validator | PASS — all seven guarded workflows. |
| Release-attestation self-test | PASS. |
| BC extension source preflight | PASS — 134 AL objects; configured analyzer ranges found. |
| Isolated PostgreSQL 16 migration | PASS — upgraded empty disposable database to head. |
| Isolated PostgreSQL locking/evidence/migration suite | PASS — 14 passed, 1 skipped. The running `dhm-dev-postgres` container was never used. |
| Frontend tests | PASS — 14 files, 243 tests. |
| Frontend production build | PASS. Bundle-size warnings remain advisory. |
| Actual BC27 compiler/runtime | Not run locally: required Microsoft symbols/BC container toolchain is CI-only. Static AL preflight passed; required CI matrix remains a merge gate. |

The reported PostgreSQL `transaction_timeout` issue is not present in the final
workflow/configuration search and could not be reproduced on isolated
PostgreSQL 16.  The reported checkout HTTP 404 has no source-local reproduction:
all current workflows use `actions/checkout@v4`; GitHub runner logs/API access
are still required to identify an external checkout failure if it recurs.

## Required merge order and remaining blockers

1. Run the required GitHub Actions suite on the exact backend candidate SHA,
   including both BC27 fresh/upgrade matrix jobs and PostgreSQL migration jobs.
2. Resolve/rebase #152/#153 rather than merging their stale extension version.
3. Refresh #170's evidence file from verifiable current CI evidence, or retain
   it as a separate documentation PR.
4. Merge the frontend candidate only after its repository's required checks
   pass; no `staging` branch is assumed for that repository.
5. Review the two Draft PRs, then merge in their repository-specific DEV flow.
   A production/staging deployment requires a separately approved exact SHA.

No customer data, production data, or local AI Control Center data was migrated
or deleted during this sprint.
