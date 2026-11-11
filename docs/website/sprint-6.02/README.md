---
title: Sprint 6.02 – Documentation, repository/design review and acceptance
owner: BCSentinel Documentation
status: draft_review_required
updated: 2026-11-11
---

# Sprint 6.02 – Website DE/EN, DEV-first documentation package

## Scope and limitations

This PR contains **documentation only**: complete editorial DE/EN candidates for all planned public website page families, including legally reviewable outlines. No frontend/runtime files, pricing schemas, workflows, environments or deployment configs are changed. No GO/PROD approval.

**Tracker:** The user's current XLSX is the authoritative planning/status source (see the tracker handoff at commit `a31f43edc4f9`, PR #163). The binary workbook was not available in this session; therefore the exact `6.02` task row / checklist cannot be independently matched or marked complete here. The website family follows the known Sprint 6 landing scope. Mark this deliverable **editorial draft ready / acceptance pending**, not closed in the workbook.

## Review of authoritative repositories (read-only)

| Authority | Reviewed file | Finding |
| --- | --- | --- |
| Core technical / release baseline | `docs/BCSENTINEL_MASTER_STATE.md` on main; `release/current-product-state.json` on main | Historical content includes older access, Extension and report/pricing information. Must not be treated as current runtime proof. |
| Core tracker handoff | `docs/BCSENTINEL_GO_LIVE_TRACKER_HANDOFF.md` from commit `a31f43edc4f9` | Current workbook controls task status; old 7-day vs draft 14-day access-v2 models must be reconciled before publication. |
| Normative Product System | `00-core/CURRENT_STATUS.md` (2026-11-03), `00-core/PRODUCT_MODEL.md` | Free → Quick → Full → Validation → Monitoring; Fiverr pilot excludes Monitoring and paid Free. Avoid divergent product tiers/prices. |
| Financial semantics | `00-core/FINANCIAL_OUTCOME_CONTRACT.md` | Estimated Loss and Potential Saving are modeled; Realized Saving is not granted by scan deltas. |
| Design and marketing | `02-design-system/DESIGN_TOKEN_AUTHORITY.md`, `05-pages/landingpage/README.md`, `05-pages/EXISTING_PAGES_PRODUCT_TRUTH_SWEEP.md` | Normative semantic tokens, orange CTA distinct from blue actions / amber warnings; controlled pilot and truthful claims; B6 target design is not deployment evidence. |
| Frontend | `danielwauer-maker/bcsentinel-frontend/main/README.md` | Lovable-origin frontend; GitHub connector searches for `LandingPage` / `Pricing` and assumed `src/App.tsx`, `src/pages/Index.tsx`, `src/index.css` did **not** identify current runtime source. Exact rendered route inventory / responsive behavior cannot be certified from this review. |

## Design implementation handoff

- Preserve the approved BCSentinel visual identity: Inter, executive-friendly information density, navy-based structure, restrained surfaces and semantic tokens. Use Orange for brand/primary marketing CTA, Blue for analytics/generic interaction, Amber only for warning.
- Render consistent header/footer and language selector on all pages, with DE/EN parity for navigation, CTAs, forms, errors and legal links.
- Landing composition: hero + credible dashboard/illustration + benefits + workflow + report teaser + FAQ + CTA. Use **synthetic/demo-only** data; no fabricated customer testimonials or guaranteed financial results.
- Pricing: components bind to approved pricing source, with explicit channel/currency/record class; do **not** duplicate static numbers from this documentation. Distinguish free entry, Fiverr-controlled-pilot, and direct commercial availability.
- Security: avoid shield badges reading “DSGVO-konform”, “data never leaves BC” or “tenant isolation proven” until real Evidence allows it. Hosting location, TLS, retention, DPA and sub-processors require verification.
- Forms: accessible labels, validation and loading/success/error states; explicit privacy links; safe support intake without secrets; no dead CTAs.
- Desktop/tablet/mobile QA, focus/keyboard/navigation, contrast, alt text, headings, canonical/hreflang, locale-specific SEO and URLs are implementation acceptance tests, **not validated here**.

## Claim / product-truth risk register

| ID | Finding | Required release gate |
| --- | --- | --- |
| W602-01 P0 | Tracker XLSX not accessible for exact row/DoD check | Reconcile exact Sprint 6.02 checklist and evidence fields in current workbook |
| W602-02 P0 | Older Core main access semantics vs newer open PR #154 / draft access-v2 | Freeze one reviewed entitlement/access contract for public copy and current runtime |
| W602-03 P0 | Older Core main extension evidence vs BC 1.0.2.58 acceptance candidate | Real non-SUPER and tenant A/B runtime evidence; no automatic claim upgrades |
| W602-04 P0 | Legal operator identity, contact data, privacy flows, DPA/TOM, subprocessors unknown | Legal/DSB review before publication |
| W602-05 P0 | Frontend route/UI code and actual responsive rendering not verified | Inspect frontend branch and perform real visual/manual QA |
| W602-06 P0 | Pilot, pricing, Fiverr and direct CTAs are channel-dependent | Verify live destinations and channel compliance; no premature payment/GO |
| W602-07 P1 | Financial illustration, trust badges and demo reports can mislead | Label synthetic examples, financial estimates and limit claims |
| W602-08 P1 | Mailing/consent/cookie and support workflows unverified | Verify endpoints, policies, security and delivery evidence |
| W602-09 P1 | Product System B6 target frozen, but implementation may lag | Compare rendered frontend/landing to B6 contract and document deviations |

## Acceptance checklist

- [x] DE website editorial draft for Home, Pricing, Pilot, Security, Contact, Support, Help, Impressum, Privacy, Terms and DPA
- [x] EN counterpart for all same page families and key UI states
- [x] Claims constrained to Business Central Online, modeled impact, no autonomous remediation, no general-availability assertion
- [x] Review of canonical product and design contracts; drift/risk register
- [x] Documentation-only isolated branch; draft PR targeting DEV integration branch
- [ ] Verify exact Sprint 6.02 workbook row(s), dependencies, DoD and status
- [ ] Confirm live website routes and design fidelity across devices
- [ ] Check legally complete business particulars/privacy/DPA with responsible reviewer
- [ ] Approve actual security and hosting claims against runtime evidence
- [ ] Freeze currently approved access-v2/product hierarchy and dynamic price mappings
- [ ] Validate all form submissions, localization, links, accessibility and SEO
- [ ] Run approved DEV acceptance and capture test evidence
- [ ] Release owner sign-off; **never automatic Go-Live**

## Files

- [German content](WEBSITE_CONTENT_DE.md)
- [English content](WEBSITE_CONTENT_EN.md)

## Change control

Review the docs before a separate UI implementation PR. Do not merge a documentation commit into a deploy-triggered branch without inspecting CI branch trigger rules. In particular: **no PROD deployment, no migration, no pricing/entitlement mutation, no GO**.
