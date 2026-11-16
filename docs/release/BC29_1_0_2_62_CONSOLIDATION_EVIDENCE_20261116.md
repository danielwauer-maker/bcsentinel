# BC29 1.0.2.62 integration – curated evidence

**Status: source-integrated release candidate only. No AL compile, BC29 runtime, QA preservation, deployment or Go-Live acceptance has yet been demonstrated for 1.0.2.62.**

## Scope and provenance

Integration branch: `integration/bc29-1.0.2.62-free-hardening-20261116`, based on `staging`.

- PR #203, commit `1a39fba6`: sandbox-only local reset from installed version 1.0.2.61.
- PR #204, commit `1f50bdf6`: mode-specific scan headlines and authenticated original-Free report share links; Full-v6 paid access stays protected.
- PR #205, commit `0b205331`: Free-tier hardening F02–F07 (exceptions, module/check changes, Full-or-Monitoring guards, Findings notices and access labels).

Both `bc-extension/app.json` and `bc-extension/app.cloud.json` were changed to **1.0.2.62**. No backend or database runtime changes were introduced. The exact EUR impact in the Free scan remains unchanged by product decision.

## Merge verification

All three source branches were one commit ahead of the same original `staging` commit `f46e77c`. Their changed-file sets were integrated into this branch. The three overlapping files were merged from original source baselines, with disjoint source-change hunks:
- `DHSetup.Page.al`: preserved Reset Sandbox action, Free Report link routing and scan-check access handling.
- `DHSetup.Table.al`: preserved reset of premium/monitoring/registration and Free access-display labels.
- `tools/ai-control-center/data/evidence-status.json`: preserved both report-fix and F02–F07 evidence entries.

This integration has **not** been compiled or locally executed yet. The component branches' reported source tests (33 and 84 focused tests, plus reset source validation) do not constitute integrated-build evidence.

## Required acceptance gates

1. Review integrated diff and confirm no unintended changes compared with PRs #203–#205.
2. Run relevant Python regression and AL source validators on the **combined branch**.
3. Compile `BCSentinel_1.0.2.62.app` with available AL compiler and symbols; a BC27 symbol build alone is not BC29 runtime proof.
4. Check new DE translations and the existing unrelated localization baseline findings.
5. Install as an upgrade only in BC29 Sandbox, keeping the three separate QA extensions and M/L/XL test data.
6. Verify original Free scan opens a Free Report, Full-v6 remains denied to Free, scan headings match modes, F02–F07 guards work in Free and Full.
7. Investigate F01 re-registration welcome/scan email separately. Resolve the Free EUR-impact product decision separately.
8. Update authoritative AI-PM acceptance only with verified test and runtime evidence.

**No automatic merge, deployment, PROD modification or release authorization.**
