# BCSentinel Fiverr DEV BC27 — manual acceptance pack (2026-11-14)

**State: PREPARED / NOT EXECUTED / NO-GO.** This is a preflight and operator execution contract; no BC27 runtime test is claimed here.

## Version anchors
- Backend **DEV** source `caf245b23a74d4691fe62dfc5c4de805c730a171`; independent operator check: running healthy, PostgreSQL **0041_pilot_enrollment**, API 200.
- Frontend DEV source `2af0ae555251600c0dccb29899104dbdf0ea818f`; viewer route returns HTTP 200, no authenticated report proven.
- Core `bc-extension/app.json` version **1.0.2.60**, BC application/platform 27.0, runtime 16.0. **This is a source version, not proof of installed app version.**
- Before any BC installation, record actual current installed extension version, AppId `8c7f0f9c-0c1a-4a4e-9c6f-111111111111`, downloaded .app SHA256, matching build commit and installer role. Do not assume an old .app artifact represents current source.
- Existing historical guides `docs/SPRINT3A2_BC27_ACCEPTANCE_RUNBOOK.md` and `quality/release/sprint3a2-bc27-acceptance-template.json` target **1.0.2.58 / 0040** and are **not** the current release contract. Use them only for historical scenario techniques.

## Execute in this order (one action at a time)
1. Freeze candidate artifact SHA, capture old app version, sandbox/company identifiers (redacted), current BCSentinel setup and history counts. Maintain a SUPER recovery account separate from non-SUPER test users. Never delete app data to force a successful upgrade.
2. In a **BC27 sandbox and dedicated test company**, install/upgrade the exact reviewed `1.0.2.60` .app. Verify setup, registration, existing scans/history and subscriptions survive. Any destructive schema error = FAIL and stop.
3. Test the actual non-SUPER role matrix, documenting baseline BC permissions and each BCSentinel role separately. Negative actions must fail without reading foreign data. Cross-reference `docs/CORE_PILOT_MANUAL_ACCEPTANCE_CHECKLIST.md`.
4. Test approved registration / controlled enrollment through the real BC UI. `PILOT_ENROLLMENT_ENABLED` was previously observed not explicitly set (defaults False); **do not enable it without separate reviewed operator policy and ingress safeguards**. If normal pilot onboarding cannot complete, mark BLOCKED (#43/#21). Never use the QA-only global invite helper to claim a customer onboarding PASS.
5. Create or use authorized **synthetic** test data; run original Free DeepScan, wait for final lifecycle and backend sync, inspect check coverage. No raw customer records, tokens or PII in evidence. Validate Free aggregate-only UI and API; no finding code/title, exact money or drilldown. **Native Free viewer grant remains a separately unresolved requirement** in `docs/release/DEV_V6_BC27_LAUNCH_HANDOFF_20261112.md` — do not label it PASS based on a paid Full link.
6. Apply an explicitly authorized test Full entitlement and use the **same original Free scan**. Validate link issuance, one-use exchange, DE/EN output, rendering/PDF, EUR/LCY, 14-day access only if approved by active contract. If pricing/contract remains draft, mark BLOCKED (not PASS).
7. Use real non-SUPER Purchase/Sales Line findings to test original record drilldown, exact issue-code, line-bound SystemId, exclusion/correction persistence and second scan. Cross-reference `docs/acceptance/ISSUES_30_32_BC27_ACCEPTANCE.md`.
8. Use **two authorized scans** and verified sealed source identities to test Validation. Distinguish comparable vs missing/partial/different tenant/company; 409 or locked variants must not silently show unverified results.
9. Test Monthly and Annual Monitoring separately, history, expiry, cancellation and notifications. Compare effective Product Access Until vs Full Analysis Access Until and Monitoring Until on real BC.
10. With distinct authorized users/companies/tenants, test wrong-company, wrong-tenant, expired, replayed and modified report-link attempts. Capture denial status without secrets.
11. Run a complete Fiverr **test order → operator grant → email/invite → BC → report → support/cancellation/refund** journey. Use test-mode or manual operator grants; do not enable paid checkout against production Stripe.
12. Review screenshot/HTTP/AL/runtime evidence for all cases. Only a human operator may enter an observed PASS; capture reviewer, UTC time, artifact SHA and sanitized evidence refs. Any missing evidence remains `NOT_EXECUTED` or `BLOCKED`, never implicit PASS.

## Evidence register
Use `quality/release/dev-bc27-fiverr-acceptance-20261114.json` as a **read-only source template**. Copy and fill a separate run-specific **sanitized** record; do not silently rewrite this baseline template, Excel checkboxes or project-store approvals. 12 cases are deliberately NOT_EXECUTED and overall NO_GO.

## Test safety & stop rules
- No PROD app, PROD billing, active customer data or destructive rollback.
- No SUPER role for proving a non-SUPER flow.
- No secrets, bearer tokens, invitation tokens, e-mail addresses or raw SystemIds in GitHub evidence.
- No post-hoc PASS for earlier AL compile, static tests or HTTP 200.
- Any unauthorized foreign read, Free premium leak, data-loss upgrade or report replay acceptance: **stop and record FAIL**.
- BC customer-report full-v6 tests only after the approved grant/entitlement and viewer configurations are validated.
- Keep open issues #21, #30–33, #43, #121 and frontend #18 open until evidence-backed acceptance; issue closure is separate from overall Fiverr-GO.

## Exit criteria
All release-critical cases have redacted recorded PASS with a real package, tester, UTC and reviewer. Product-system Access-v2/prices are approved, essential onboarding/legal/operational flows pass, and rollback/recovery evidence is current. Without those, `decision=NO_GO`.
