# AI Control Center 2.5 – Evidence-qualified progress and time accounting

## Source contract
- tracker() reads the SHA-verified immutable Excel V2 plan (61 Fiverr + 24 SaaS tasks). Only numeric Fiverr plan_hours values count. Missing/mismatched workbook means no plan-hour comparison.
- sprint_radar unites 15 reviewed tasks with the 70 other imported tasks. PR references must be attributable to a task; unmatched PRs are not guessed.
- evidence-status.json is versioned operator review. SQLite explicit approvals are the only source of manual task technical/DEV approval.
- GitHub PR creation/merge timestamps are calendar milestones, never CI or runtime approvals. Closed-but-unmerged is not merged.
- Verified backend DEV evidence is applied only to explicitly scoped tasks (1.02 backend; 3.02 Full-report infrastructure). This is not BC27 E2E acceptance.

## Meaning of percentages
Five independent phase-evidence percentages, denominator the task count per Excel sprint: Draft, Integriert, DEV/Preview, Technisch attestiert, Manuell abgenommen.
For each phase, share = linked tasks with evidence divided by total tasks for that sprint. Phases are NOT additive; tasks can occur in multiple phases. Missing evidence is not proof of unfinished source work. This is evidence coverage, not subjective feature completion.

## Plan / actual
Plan hours come from the immutable Excel task baseline. Actual work hours remain NULL/not recorded without verified work logs. PR calendar lead time, CI run duration, commit deltas and agent wallclock duration must never be counted as person-hours. Timeline presents dated source milestones and PR calendar lead days separately.

Future verified time logs require task key, active effort, actor, reviewer/evidence and overlap control. No logs are backfilled in this change.

## Limitations
- 15 of 61 Fiverr tasks have curated reviews; 46 Fiverr + 24 SaaS tasks remain individually unreconciled.
- GitHub PR metadata refreshes on 5-minute cache; newly merged changes still need attributable task references, and CI final-SHA status is not globally verified here.
- Historic Excel 65.6% timeline is only a baseline, not present-day actual project completion.
- BC27 1.0.2.60 manual runtime cases remain NOT_EXECUTED; Fiverr NO_GO, no automatic gate grant.
- No changes to production services, billing, Docker infrastructure, Excel files or operator approval state.

## Acceptance
Test that merged PR is not technical or manual acceptance, closed-but-unmerged does not count as integrated, absent workbook does not fabricate plan hours, and PR calendar days do not become actual labor hours.
