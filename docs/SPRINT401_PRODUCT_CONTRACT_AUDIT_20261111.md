# Sprint 4.01 — Cross-Repository Commercial Product Contract Audit

**Date:** 2026-11-11  
**Status:** AUDITED / PROPOSED MIGRATION; **NOT** approved contract migration or runtime release  
**Tracker:** BCSentinel Go-Live Master XLSX, Fiverr task `4.01`; technical and go-live checkmarks remain **OPEN** until acceptance criteria below pass.  
**Branch scope:** Documentation only; no direct write to `main`, `staging`, `dev-acceptance` or deployment.

## 1. Evidence and authority snapshot

| Authority | Exact inspected source | Finding |
|---|---|---|
| Core `main` | `docs/BCSENTINEL_MASTER_STATE.md`, blob `04f818c5ff9fe03bda4d8736c2b62ae0da3cd751` | 2026-11-01: permanent **Quick**, **Full 7d**, one +7d extension, **Validation 7d**, Monitoring deferred for Fiverr pilot; Extension 1.0.2.29 |
| Core `main` | `release/current-product-state.json`, blob `924cc4993ba58ada9dc1133b08d8144f1826b4b7` | 2026-11-03: Quick/Full/Validation 7d funnel, prices from November 3; differs from Master State's earlier price snapshot |
| Core `main` | `docs/FIVERR_GIG_LAUNCH_KIT.md` | Quick Fiverr BASIC $149, Full ADVANCED $349, Validation $179, volume tiers including ≤100k, and 7d detail access |
| Core PR #154 | `feature/access-renewal-14d-policy-20261108`, head `ad7f570c21c37fbb6b0cce04e8c462a76c604947`, PR body | **Draft only**, Free one original scan/archived Free report; Full 14d on original scan; Renewal +14d no scan; Renewal+Validation +14d and one credit; separate Monitoring subscription; v2 SKUs disabled/unpriced; checkout disabled; unresolved BC upgrade and E2E gates |
| Core PR #162 | `integration/sprint3a2-consolidated-20261110`, head `a8b870eb41d29913cc0837a558c30637be8c57f2` | Draft runtime/Evidence work; BC27 1.0.2.58 acceptance not yet evidenced at this audit |
| Product System `main` | `00-core/product-model.yaml`, `bcs-product-model-v2.1`, last updated 2026-10-09 | Approved normative offers **Assessment**, **Validation**, **Monitoring** (monthly/annual as billing variants); Free Entry not paid; Quick is not a normative commercial offer; pricing centralization and legacy-rights preservation required |
| Product System `main` | `00-core/PRODUCT_MODEL.md` | Product System is normative; Core runtime is evidence/implementation; **no independent marketing, pricing or entitlement truth** |
| Frontend `main` | `README.md` | README still Lovable template; no proof that live frontend implements 14d model. Needs targeted source/build/runtime verification |
| Core handoff PR #163 | `docs/BCSENTINEL_GO_LIVE_TRACKER_HANDOFF.md` | 61 Fiverr tasks and 24 excluded SaaS/Stripe tasks, separate tech vs Go-Live status, no implicit PASS |

> This audit is a repository-document and PR-metadata comparison. It does **not** assert that PR #154 is merged, source implementation works end-to-end, contract authority was amended, prices have been approved, or a live environment is using these semantics.

## 2. Confirmed drift / blockers

| ID | Severity | Drift | Required resolution |
|---|---|---|---|
| PC-01 | **P0** | Approved Product System names `Assessment`, `Validation`, `Monitoring`; Core main still sells `Quick Assessment`; PR #154 proposes Free/Full14/Renewal/Validation/Monitoring. | Product-leadership-approved **versioned** contract amendment on Product System. Model Renewal as an access/billing variant or separate commercial offer **only after** its semantics are approved. Do not invent a fourth normative offer from a UI label. |
| PC-02 | **P0** | Core main `Full=7d`, `extension=+7d`, `Validation=7d`; PR #154 `Full=14d`, `Renewal=+14d`, `Renewal+Validation=+14d + one credit`. | Versioned entitlement mapping and data migration; grandfather existing purchases and preserve previously granted rights; prove no extra baseline scans and no double credit. |
| PC-03 | **P0** | Core main Fiverr packages and prices support Quick Basic and a different six-volume-class USD matrix; v2 PR explicitly has v2 SKU prices disabled and unset. | Commercial signoff for actual Fiverr Gigs, minimum price, all record tiers and volume-mismatch process; publish no v2 prices until approved. Price consistency generation vs multiple hand-maintained copies. |
| PC-04 | **P0** | Main documentation and release JSON claim automatic F0-F8 nearly done, but newer 3A.2 provenance/BC27 runtime still blocked and comparison capability not proven for all checks. | Replace stale completeness and 1.0.2.29 runtime claims **after versioned migration and evidence**, never simply by changing percentages. No unproven Validation/Monitoring or report unlock. |
| PC-05 | **P0** | Core main Fiverr kit positions Monitoring as future and Quick as current entry; planned launch is Assessment/Validation/Monitoring (3 Gigs). | Define per-Gig scope and actual acceptable E2E/operational Monitoring subscription terms; treat Monitoring as **blocked** until running subscription / cancellation / operational evidence is present. |
| PC-06 | **P0** | Frontend README does not establish current public product copy or pricing; deployed revision and live pages not validated. | Inspect actual frontend components, source refs, environment config and build, then audit every CTA, product name, pricing teaser, retention promise and report entitlement against approved v2 contract. |
| PC-07 | **P0** | One initial free full Deep Scan is aligned conceptually but archive, revocation, report TTL and scope claims differ in implementation versions. | Freeze explicit access matrix for Free/Full/Renewal/Renewal+Validation/Monitoring; test security on original scan and company scope, reports after expiry, offline/legacy cases. |
| PC-08 | **P1** | Core Master State 2026-11-01 Fiverr price table and 2026-11-03 release JSON/Launch Kit price table differ. | De-duplicate historical price authority. Mark old amounts deprecated once actual v2 prices are approved; generated channel projection and source-provenance checks. |

## 3. Proposed target contract — awaiting versioned Product System approval

The following is **the user's chosen product direction and PR #154 design**, **not** a claim of approved contract or deployed behavior:

| Surface | Proposed rule | Required proof |
|---|---|---|
| Free Entry | One full-depth initial Scan per newly registered qualifying tenant, only aggregate safe Free output; persistent Free report/history | Repeat registration cannot produce extra credit; initial scan consent and scope; no EUR/titles/root cause leaks; immutable archived scan |
| Assessment / Full | 14-day full-detail unlock of the qualifying existing first scan, with no automatic new scan | Same scan-ID; scope binding; expiration; report tokens and replay; old grants preserved |
| Renewal | 14-day access renewal without a new scan | Accurate non-stacking/stacking policy and timestamp semantics must be expressly approved; no extra scan on purchase |
| Renewal + Validation | 14-day access renewal plus **exactly one** new authorized Validation scan credit after correction | Paid Full baseline; no duplicate credit; report unlock withheld without comparable immutable check evidence |
| Monitoring | Separate recurring subscription, not an extension of Assessment | Period, rights, permitted scan frequency, history, cancellation, refunds, operational policy, reporting evidence; product not launched until PASS |
| Direct SaaS / Stripe | Separate subsequent track, not part of Fiverr percent | Fiverr origin remains Fiverr payment, channel metadata only; disabled v2 Stripe checkout is not a Fiverr readiness PASS nor a SaaS readiness PASS |

**Need explicit business decisions before freezing:** final Fiverr package count, prices/tier mapping, treatment of existing Quick purchasers, renewal stacking/activation and overlap behavior, Monitoring period / scan entitlements / cancellation, compatibility with existing 7d Full and Validation grants, whether Validation without renewal remains offered independently, what claims are admissible while most checks are only aggregated.

## 4. Cross-repository implementation plan (no code changes in this PR)

1. **Product System**: propose controlled `product-model.yaml` contract version bump, human contract amendments and approved record-based pricing matrix, migration mapping for legacy `quick_assessment`, `assessment`, `validation_check`, renewal and Monitoring; identify approver.
2. **Core**: regenerate/revise `docs/BCSENTINEL_MASTER_STATE.md`, `release/current-product-state.json`, operator and report contract mapping from the approved normative version; do not overwrite current approved main merely because Draft PR #154 exists.
3. **Core access v2**: reconcile PR #154 with the latest PR #162 Evidence model and BC27 runtime gates. Keep `ACCESS_MODEL_V2_ENABLED` and `ACCESS_V2_PAID_CHECKOUT_ENABLED` off until authorized DEV tests and a separately controlled production promotion.
4. **Frontend**: audit actual UI source and report viewer branch, map visible prices, product names, CTAs, lock-state and access expiration against approved product projection; remove legacy Quick/7d claims only as reviewed changes.
5. **Fiverr**: produce one versioned operator-facing offer matrix (Free, Full14, Renewal14, Renewal+Validation, Monitoring) including credits, access windows, customer deliverables, scope classes, price and explicit order-handling evidence.
6. **Tests/evidence**: product model schema/contract test, compatibility mapping, old entitlement preservation, channel parity, permanent Free archive and no-leak boundary, payment-to-grant idempotency, 14d time-travel, Validation and Monitoring negative gates.
7. **Release gates**: exact SHAs for three repos, GitHub CI, real BC27 Sandbox/Non-SUPER, E2E with fresh tenant and Fiverr purchase, final GO/NO-GO. Do not infer runtime status from a YAML/JSON update.

## 5. Checklist for marking Fiverr Tracker 4.01

- [x] Preliminary source comparison, major drift and safety dependencies recorded.
- [ ] Product leadership explicitly approves v2 semantics and package + price matrix.
- [ ] Product System canonical contract version updated in its own reviewed PR.
- [ ] Core/Frontend/Fiverr surfaces mapped to the approved contract, no conflicting active copy.
- [ ] Compatibility strategy and automated negative regression proofs verified.
- [ ] Precise evidence/SHAs reviewed and task Owner signs off.

**Tracker:** `4.01 TECHNISCH FERTIG = unchecked`; `GO-LIVE ABGENOMMEN = unchecked` at this point. This audit removes ambiguity; it does not silently manufacture an approved release contract.

## 6. No-risk disposition

Documentation-only Draft PR. No data/database changes, no schema changes, no branch promotion, no deployment, no product activation, no Fiverr pricing publication.

Associated parallel technical work: Sprint 3B.01 and 3B.02 in independent Codex feature branches; the PR #162 BC27 sandbox acceptance is independent and still required.
