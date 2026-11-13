---
title: Sprint 6.02 – Frontend / Design / Content Gap Audit
owner: Product Content and Frontend Review
status: evidence_based_source_review_not_visual_qa
updated: 2026-11-11
---

# Source-based frontend review for Sprint 6.02

## Revisions and authority

Reviewed live source repository **`danielwauer-maker/bcsentinel-frontend/main`**, particularly `src/routes/index.tsx`, `src/routes/__root.tsx`, `src/styles.css`, `package.json`. Review is of source text only, **not** browser screenshots, responsive visual acceptance, running DEV, security tests or PROD runtime. Frontend `main` is not automatically equal to a deployed immutable release.

Normative Product System: `05-pages/landingpage/LANDING_PILOT_PRICING_CLAIMS_CONTRACT.md`, `05-pages/landingpage/README.md`, `02-design-system/DESIGN_TOKEN_AUTHORITY.md`, `00-core/CURRENT_STATUS.md`, `00-core/FINANCIAL_OUTCOME_CONTRACT.md`. Technical Master State on Core `main` may be historical; Access-v2 draft must be approved separately.

## Grounded source audit

| ID / priority | Source | Actual observation | Target / follow-up |
| --- | --- | --- | --- |
| UI-01 P0 | `index.tsx:42–48` | Trust badge explicitly says **DSGVO-konform**; others say Germany hosting, tenant isolation and encrypted communication | Remove/qualify any claim lacking verified legal, infrastructure and tenant A/B evidence; use factual controls only |
| UI-02 P0 | `index.tsx:344–363` | Hero states **Schlechte Daten kosten Geld** and financial impact; may imply actual losses | Align with conditional and modeled fin-v1 semantics; avoid actual-loss implication |
| UI-03 P0 | `index.tsx:422–471` | Section title **Konkrete Einsparpotenziale aus der Praxis**, monetary scenarios are hard-coded; without clear always-visible fictional disclaimer they can appear empirical | Label each as **illustrative model example / fiktive Beispielrechnung** and explicitly non-guaranteed, non-customer evidence; review calculation methodology and parameters |
| UI-04 P1 | `index.tsx:95–132` | Dashboard sample shows Score 82, 17 findings and €12.4k potential saving. Contains a small Demo label | Verify demo label remains obvious on narrow screens; value must not be mistaken for real customer proof |
| UI-05 P0 | `index.tsx:306–394` | `VITE_FIVERR_GIG_URL` conditionally switches hero between Fiverr pilot CTA and waitlist | Preserve channel separation. Verify real approved URL, package, USD volume classes and any current sales freeze |
| UI-06 P1 | `index.tsx:156–204` | Waitlist submits to `/public/pilot-interest`, supplies `preferred_language: "de"`, captures privacy consent and input validation | Implement locale-sensitive submission only in a separate implementation PR; independently test API, consent storage, error/success conditions |
| UI-07 P1 | `index.tsx:485–497` | Footer links `/impressum`, `/datenschutz`, mailto and fixed year; does not show Terms/DPA/Help pages | Verify destination implementations and add approved legal/support links; no broken routes |
| UI-08 P1 | `__root.tsx` | `<html lang="en">` while landing content is German; 404 and root errors English | Implement locale-specific html lang, 404 and error labels; hreflang and language selection where supported |
| UI-09 P1 | `index.tsx` | Current landing combines hero, trust, model examples and footer in one route; planned content families are not evidenced as separate implemented pages | Treat new DE/EN docs as specifications, not as a claim of deployed routes; trace each proposed route in UI implementation |
| UI-10 P1 | `styles.css` | Semantic CSS roles exist and Inter / Source Serif 4 are used; `index.tsx` includes some hard-coded color values | Map brand/CTA/analytic/warning roles to normative Product System tokens; do not unilaterally change visual design |
| UI-11 P2 | `index.tsx:320–399`, `styles.css` | Responsive utility classes are present in source | Does **not** prove no clipping, correct mobile focus order, contrast or final visual fidelity. Run device/browser screenshots and keyboard checks separately |
| UI-12 P0 | Core access-v2 vs older frozen Product System | Public access-duration and renewal text cannot be finalized from contradictory historical authorities | Publication gate: approve exact current entitlement/access terms before displaying days, deadlines and renewals |

## Implementation mapping

| Planned family | Current source evidence | Next work |
| --- | --- | --- |
| Home | `src/routes/index.tsx` yes, German copy | Replace reviewed text in separate PR, preserve existing design |
| Pricing | Fiverr conditional teaser in home; no verified standalone page in this source review | Route inventory + dynamic canonical pricing |
| Pilot | Waitlist in home | Consent, locale and submission E2E |
| Security | Trust strip in home | Evidence-qualified copy; remove unsupported badge |
| Report examples | KPI teaser and 3 financial scenario cards | Show fictional warning and link to gated synthetic example pages |
| Contact | Footer mailto | Approved contact endpoint / route if needed |
| Help / Support | No verified route in this review | Route/knowledge integration after validation |
| Legal | Footer links | Confirm actual rendered destinations and legal review |
| EN locale | `html lang=en` but visible DE landing | Genuine content localization and hreflang |

## Design acceptance checklist (not yet executed)

- [ ] Desktop 1440px / 1280px screenshots reviewed against approved landing composition
- [ ] Tablet 768px and phone 390px / 320px screenshots reviewed for no clipping and readable microcopy
- [ ] Page navigation, all legal/support paths and DE↔EN switch verified in running DEV
- [ ] H1/H2 structure, keyboard focus, skip links, form labels, status announcements and visible contrast checked
- [ ] Marketing examples permanently labeled fictional, with amounts and model limits explained
- [ ] Security/hosting/tenant separation claims linked to verifiable acceptance evidence
- [ ] Real approved access-v2, channel-specific pricing and CTA destinations verified
- [ ] Visual test evidence linked to appropriate immutable commit
- [ ] No deploy workflow triggered by docs-only PR; no merge until approved

## Result

**Source / text audit complete. Visual/runtime acceptance NOT complete.** Editorial deliverables and a precise source-to-content map are available for the next implementation sprint. This PR does not assert a live QA PASS, legal PASS or Fiverr GO.
