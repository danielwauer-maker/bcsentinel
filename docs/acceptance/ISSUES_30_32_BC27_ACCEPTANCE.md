# Issues #30 and #32 — DEV-first implementation and acceptance contract

Status: **DRAFT / NO DEPLOY / no issue closure until real BC SaaS evidence**.

## #30 — Record-level remediation and navigation

The purchase-line findings worklist now binds correction and exclusion to the **Purchase Line's own SystemId**, original document number, caption and exact issue code. It no longer marks the related Item record in response to a purchase-line finding. The purchase order opens from the document-number drilldown and explicit Correct Data action. Correction history is accessible for the same line/check. Sales-line findings gain the missing issue-bound Exclude from Analysis action.

The existing dispatcher passes the issue code into Sales/Purchase line worklists; the remediation context must remain set to that exact code. No exception may be created for an unrecognized code or missing context. **Limits:** Other standard-page dispatcher routes are not universally proven to offer the same UX for every record-based check. Issue #30 therefore stays open pending a per-check inventory and non-SUPER BC27 runtime testing.

## #32 — Effective product access display

The existing `DH Setup Effective Access` page extension already hides the base field labelled Product Access Until and shows effective expiry from Monitoring Until when Monitoring Active; otherwise it uses Premium Until. This PR makes the separate `Full Analysis Access Until` explicit, avoiding a false impression that the earlier Full expiry is the Monitoring expiry. The independently displayed Monitoring Until remains visible. No server entitlement or access policy is changed.

## Test plan / gates

1. Run targeted source-contract regression in `backend/tests/test_issue_30_32_al_contract.py`.
2. Keep PR Draft while cheap CI runs; only Ready-for-review after source, backend and migration checks pass. Run final BC27 Fresh / Upgrade / Runtime tests once on the final SHA.
3. In real BC27 SaaS, use a **non-SUPER** account to open a paid Sales Line and Purchase Line finding. Verify original order navigation, exact issue code, corrections and exclusions on the line (not master Item), persistence and second scan. Verify Free cannot drill down or trigger remediation.
4. Grant Full then Monitoring Monthly, refresh access, compare Product Access Until / Full Analysis Access Until / Monitoring Until, and test expired Full with active Monitoring and expired Monitoring with active Full. Also validate annual Monitoring.
5. Record screenshots and sanitized test evidence in the AI Control Center evidence status only after observed results. No automatic DEV/PROD deployment; Fiverr remains NO-GO.
