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

## 7. Access-v2 decision record ACV2-2026-11-12-r1 — PROPOSED / NOT APPROVED

Reviewed on 2026-11-12 against Core main `c1d9fccf39767048bceabe93e7b8676df180868f`, approved Product System `bcs-product-model-v2.1` (`00-core/product-model.yaml` blob `79efa719bb6311f8cb20e30e667e617355fdeadf`), Core Draft PRs #154/#156/#157/#165. The Product System is the normative commercial authority. This document is an approval proposal, **not** a new runtime or released contract.

| Dimension | Current approved / main | Proposed future Access-v2 | Compatibility and proof required |
|---|---|---|---|
| Initial Free | One initial full-depth scan, aggregate-only | Same, permanently reopenable Free report | One original scan ID, no re-registration credit, no findings/EUR leak, scoped archive |
| Quick | Permanent paid disclosure, <=5 findings, no scan credit, Fiverr BASIC | No new Quick package in proposed three-Gig lineup | Never revoke/shorten existing Quick entitlements; decide whether new Quick sales stop |
| Full | Same baseline, 7d, optional one +7d extension | Same baseline, 14d, zero scan credits | New grants versioned; old windows unchanged; paid baseline preserved |
| Renewal | Limited +7d extension | +14d, no scan | Explicit timing / stacking / overlap / refund rules; no duplicate grants |
| Validation | Prior paid Full; +1 scan; 7d from credit consumption | Renewal + Validation gives +14d access and +1 scan | Independent Validation offer decision; immutable comparable BC27 scan pair required |
| Monitoring | Separate recurring product, deferred from initial Fiverr pilot | Separate subscription Gig | Cadence, limits, billing periods, cancellation, refund, access/history and evidence required |
| Report access | Backend scan-aware variant resolver, expiry and token TTL distinct | Perpetual Free archive; scoped 14d Full; evidence-only Validation | Tenant/company/scan/variant scope; fail closed on missing evidence; tokens may expire |
| Prices | Main Fiverr USD price snapshots conflict internally; direct EUR tiers distinct | No new v2 SKU prices approved | Owner signs channel/tier matrix; no fabricated or hard-coded launch price |

### Decision requests — require explicit product-owner sign-off

- **D1 (P0):** Confirm three launch Gigs Assessment, Validation, Monitoring; determine whether legacy Quick remains orderable for new buyers or is retired for new sales only. Existing Quick purchases remain protected.
- **D2 (P0):** Approve new Full=14 days and Renewal=14 days for *new* v2 grants; select clock policy for pre-expiry overlapping renewals, late renewal, cancellation/refund and repeated purchases; never alter historical 7-day terms silently.
- **D3 (P0):** Approve whether Validation is sold standalone after an earlier paid Full, or only bundled with Renewal+Validation; specify one validation credit and failed/incomparable scan treatment.
- **D4 (P0):** Approve per-Gig Fiverr USD prices, record-volume tiers, overage/custom-offer process and the separate existing direct EUR price policy.
- **D5 (P0):** Specify Monitoring interval, entitled scans/history, suspension, renewals, cancellation/refund and support/SLA terms; don't publish until real subscription E2E.
- **D6 (P0):** Approve legacy migration mapping including Quick permanent rights, original 7d Assessment/Validation, consumed credits, purchased archives, and independently purchased subscriptions.

### Downstream sprint gate matrix

| Sprint | Contract dependency | Allowed before approval | Blocked until approval / runtime E2E |
|---|---|---|---|
| 4.02 | Free to Full 14d, baseline, scope, legacy | Isolated tests, fail-closed feature-flag candidate | Customer-facing 14d activation, paid launch |
| 4.03 | Renewal timing and idempotency | Draft integration tests | Selling/issuing unapproved +14d |
| 4.04 | Renewal+Validation credit and provenance | Contract fixtures / negative tests | Comparable report and commercial grant |
| 4.05 | Monitoring subscription boundaries | Design and negative tests | Subscription Gig / recurring scan claims |
| 4.06 | Operator grant and reversals #156 | Test-mode, strict authorization regression | Real Fiverr purchase-to-grant until signoff |
| 3.02 | Full-v6 report/token/role | Isolated viewer smoke | Authenticated BC27 E2E and live Full14 promise |
| 3.03 | Validation baseline and immutable check evidence | Fail-closed negative tests | Before/after claims until real comparable pair |
| 3.04 | Monitoring cadence/history/company isolation | Contract-level tests | Live monitoring report/subscription |
| 6.02 | DE/EN public copy, price/CTA | Editorial Draft #166 | Publishing pricing, expiry and Monitoring claims |
| 7.03 | Buyer offer, FAQ, support and refund | Editorial Draft #165 | Fiverr offer publication / buyer acceptance |

### Regression and acceptance checklist (no PASS implied)

1. Permanent old Quick access survives new grants, expiry and refund of unrelated purchase; entitled detail constrained to Quick layer.
2. Historical 7d purchase/extension/Validation remains at originally granted terms; no retroactive blanket 14d migration.
3. First Free scan ID is unchanged on Full upgrade; Free re-registration blocked; initial scan grants zero extra Full credits.
4. Paid access respects tenant/company/scan/variant and token revocation, expiry and replay resistance.
5. Concurrent/repeated operator order positions are idempotent; refund/dispute removes unused credits only and rebases later paid windows without deleting consumed scan history.
6. Validation before/after requires original paid Full baseline, real distinct second scan and immutable comparable source identities; absent evidence yields fail-closed result.
7. Monitoring rejects foreign-company history, missing company identity and inactive subscription; cancellation and renewal covered.
8. Approved offer-price projection matches Fiverr DE/EN copy, operator console, website, report links and canonical Product System after contract version bump.

**CI observation on PR #164 previous head `a1a6fe139b135bf2ea9280180b14f0cdb3bacf91`:** E5 Recovery Automation Quality Gate FAILED at *Install PostgreSQL client*; downstream restore steps were skipped. This is not a passing recovery acceptance and is unrelated to this documentation contract approval. Other observed workflows passed; no new complete CI PASS inferred.

**Release disposition:** Sprint 4.01 audit/documentation candidate updated; technical contract implementation OPEN, real DEV acceptance OPEN, commercial signoff OPEN, Fiverr Go-Live NO_GO. No runtime, environments, entitlements, tracker flags, or pricing changed.


## 8. Product-owner clarification ACV2-2026-11-12-r2 — DIRECTION CONFIRMED, NOT RUNTIME APPROVAL

**Source:** product-owner statements on 2026-11-12. This section supersedes the *proposed target* portions of §§2, 3, and 7 where they disagree; historical `main` evidence remains intact. No version change in normative Product System has occurred, and no live entitlement/price publication is implied.

| ID | Clarified direction | Remaining technical/commercial gate |
|---|---|---|
| PC-01 | **No Quick Assessment in the new launch catalog.** There is one real full-depth DeepScan engine across products; Free versus Full access is an entitlement/report boundary, not scan depth. | Remove Quick from new-channel offers/marketing after reviewed migration. Inspect legacy `quick_assessment` storage/entitlements and preserve any genuinely granted historical rights; do not delete compatibility code without evidence. |
| PC-02 | **14 days is the chosen v2 access duration** for new Full and new renewal grants, replacing the proposed old 7-day offering for new sales. | Preserve existing contractual 7-day grants; define overlap, start clock, expiry, refunds, validation-specific windows, and verify by regression and DEV E2E. |
| PC-03 | Pricing has been previously discussed and source tables exist; user invites fresh fit-for-product reconciliation. | No current single approved v2 Fiverr USD price matrix has been identified. Compare historical references, then sign off final record tiers, currency, packages and monitoring pricing. |
| PC-04 | Owner requests technical explanation/review rather than taking a product decision. | Reconcile historic F0–F8 completion language with actual BC27 in-place upgrade, non-SUPER roles, immutable comparable scans, Validation/Monitoring E2E. Do not change measured task gates without evidence. |
| PC-05 | **Monitoring is mandatory in the first Fiverr Go-Live**, not deferred. | P0 real recurring lifecycle: cadence, included scans, payment/renewal, company-isolated history, cancellation, security and reports; cannot launch merely because wording is ready. |
| PC-06 | Professionally reconcile public website and claims to approved product contract. | Review source and deployed revision/landing, DE/EN CTA and prices after contract freeze; real visual, legal, and functional QA. |
| PC-07 | Improve protective controls. | Permanent scoped Free archive, independent share-token TTL, server-side entitlements, replay/revoke, company isolation, expired paid fallback and refund compatibility; fail-closed negative tests. |
| PC-08 | Freeze one real authoritative pricing table. | Versioned single-price authority, derived channel views, tested parity; no historical price value arbitrarily promoted. |

### Proposed v2 target offer/entitlement design (owner direction, not released)

- **Free:** one qualifying initial full-depth DeepScan per newly registered tenant; aggregate-only persistent Free report.
- **Full Assessment:** open *the same first completed scan* at full report scope for **14 days**; zero additional scans.
- **Renewal:** **14 more days** of access, zero scans; start/stacking policy remains an explicit commercial detail.
- **Renewal + Validation:** a 14-day access extension and exactly one additional full-depth Validation scan credit; only authenticated comparable immutable scan evidence permits a comparison report.
- **Monitoring:** first-wave Fiverr Gig, separately entitled recurring subscription, with fresh governed DeepScans, periodic/history scope and cancellation semantics requiring P0 E2E.
- **Quick:** excluded from **new** offer catalog. Historic records/codes are a compatibility problem, not proof that the new launch includes a Quick SKU.

### Price discrepancy evidence, not approved v2 offers

- Core `main` Master State (2026-11-01) has Fiverr Micro Quick **$129**, Full **$299**, Validation **$149**.
- Core `main` release JSON (generated 2026-11-03) has Fiverr Micro Quick **$149**, Full **$349**, Validation **$179**.
- Product System `bcs-product-model-v2.1` is EUR-focused with Assessment/Validation/Monitoring, and does **not** approve new Fiverr v2 price tiers.
- **Do not use either historic price table as v2 customer truth**, and do not advertise new Quick. A real Monitoring Fiverr USD price and monthly/annual billing/cadence policy must be specified.

### Updated gate impact

- **Sprint 4.02:** implement new Full14 same-scan grant only, protect legacy rights; no new Quick sale.
- **Sprint 4.03:** Renewal14 test clock/overlap and no scan credit; pending overlap policy.
- **Sprint 4.04 / 3.03:** one extra Validation DeepScan; baseline and comparisons fail closed; define standalone Validation versus bundled offer in actual Fiverr packaging.
- **Sprint 4.05 / 3.04:** Monitoring upgraded to **mandatory Fiverr P0**, not a deferrable SaaS enhancement.
- **Sprint 4.06:** secure operator purchase grants, refunds and consumption preservation, separate payment evidence.
- **Sprint 3.02:** Full-v6 report opens same baseline; verify token/report/tenant/BC27 and access expires after 14d.
- **Sprint 6.02 / 7.03:** replace historic Quick and 7-day copy in *future reviewed* launch assets, align to three Gigs Full/Validation/Monitoring; do not publish while price/Monitoring runtime are unverified.

### Organizational truth

Product direction for PC-01/PC-02/PC-05 is clarified by the owner. **Normative implementation, contractual price freeze, compatibility regression, BC27 DEV acceptance and Go-Live remain OPEN.** Do not check off tracker 4.01. Dashboard evidence must reflect the clarified decisions without incrementing gates, and must be prepared in a separate draft PR before any controlled deployment.


## 9. Cross-repo normative candidate and Sprint 4.02 evidence review — 2026-11-12

**New Product System Draft PR:** [#33](https://github.com/danielwauer-maker/bcsentinel-product-system/pull/33), candidate commit `79fb7da8fb513c2359be25eaeb90062d275edc83`, file `00-core/fiverr-access-v2-candidate.yaml`. This is **non-active** and preserves the approved Product System `product-model.yaml`, `fiverr-channel-contract.yaml` and separate direct/EUR prices. Standard six-tier Fiverr USD list prices are owner approved; this does **not** approve the final migration, actual Fiverr checkout implementation or operational monitoring cadence.

### Sprint 4.02 (Free → Full14) source inspection

- PR #154 HEAD `ad7f570c21c37fbb6b0cce04e8c462a76c604947` remains Draft, based on `integration/dev-report-v6-sync-20261106`, **not** Core main; dependent PR #156 and #157 are separate stacked branches.
- `backend/app/services/access_renewal_policy.py` defines `ACCESS_DAYS=14`, Free one initial scan/persistent Free access, Full Assessment zero additional scans and 14 days; the renewal without scan and renewal+Validation with one scan are represented as distinct grants.
- `backend/tests/test_access_renewal_policy.py` asserts the 14-day constant, one original Free credit, zero extra Full/renewal credits, 14d renewal, expiration protections and Monitoring report restriction.
- Policy `extend_access` **stacks from the later of existing access expiry or activation timestamp**. This is *implemented policy behavior*, NOT an independently approved timing policy. Separate owner acceptance and refund/overlap tests remain required.
- `GRANTS[MONITORING].additional_scans = None` delegates to fair-use controls. This **does not prove** the proposed one scan per 30-day paid period; current Monitoring scope must be aligned with the mandatory Fiverr-launch Gig before activation.
- `docs/pr154-v2-release-gates.md` documents matching installed BC 1.0.2.52 persisted AL schema sources and prior PTE0004 permission regression; a real successful BC27 non-destructive upgrade, Non-SUPER runtime, tenant/company isolation and authenticated Full-v6 E2E are still missing.
- Core and newer BC extension artifact refs must be reconciled with #162/#168 prior to deploying any candidate. No blanket replacement of old 7-day or permanent-Quick historical rights.

**4.02 status:** Code candidate present; source reviewed here but **no new tests executed against a checked-out branch in this audit**. Technical integration not marked complete; DEV acceptance NOT PASSED; Go-Live NO_GO. Next safe engineering work is branch-aware test/provenance + BC schema/role migration verification, not a PROD toggle.

**Contract change sequencing:** Product System #33 Draft review → resolve specifically renewal overlap, Monitoring monthly scan allowance and Validation bundle → controlled versioned normative contract approval → stacked Core #154/#156/#157 integration/regression → real BC27/DEV End-to-End → buyer/web copy/offer parity → release signoff. Pricing approval alone does not authorize a launch.

**No main/staging merge, PROD/DEV deploy, provider discount creation, Excel or dashboard gate upgrade.** Dashboard evidence for this progress is tracked separately via Core PR #170.
