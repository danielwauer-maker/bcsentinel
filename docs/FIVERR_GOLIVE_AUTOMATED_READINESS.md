# BCSentinel Fiverr Go-Live — Automated Readiness

Status: **automatic repository preparation complete; manual acceptance gates remain**  
Date: 2026-11-03  
Scope: first controlled paid Fiverr pilot for Microsoft Dynamics 365 Business Central Online.

## Authority

For the controlled Fiverr pilot, use these sources in this order:

1. `release/fiverr-golive-state.json`
2. `docs/FIVERR_PILOT_RELEASE_CANDIDATE.md`
3. `docs/FIVERR_GIG_LAUNCH_KIT.md`
4. `docs/FIVERR_REQUIREMENTS_DELIVERY_FINAL.md`
5. `docs/FIVERR_NEXT_PURCHASE_EMAIL.md`
6. `release/current-product-state.json` only for broader product context not superseded above

`docs/MANUAL_GO_LIVE_CHECKLIST.md` is an older broad SaaS checklist and contains historical direct/Stripe assumptions. It must **not** override the frozen Fiverr product, pricing, entitlement or launch-scope contracts above.

## Frozen launch scope

Commercial Fiverr launch:

- BASIC = Quick Assessment
- ADVANCED = Full Assessment
- Validation = separate follow-up Gig / Custom Offer after paid Full Assessment
- Free Health Check = BCSentinel entry layer, not a paid Fiverr package
- Monitoring = later, not a controlled-pilot blocker
- Assessment Plus / Premium = not a launch package

Initial scan model:

- exactly one full initial Data Health Scan for a fresh tenant;
- Free, Quick and Full differ by disclosure/entitlement, not scan depth;
- Quick creates no scan credit and is permanent until revoke;
- Full reuses the same initial scan and has a 7-day detail window;
- Validation requires a paid Full baseline and creates exactly one new scan credit after remediation.

## Frozen Fiverr pricing

| Analyzed records | Quick | Full | Validation |
|---|---:|---:|---:|
| ≤100,000 | $149 | $349 | $179 |
| 100,001–250,000 | $199 | $399 | $219 |
| 250,001–1,000,000 | $279 | $549 | $289 |
| 1,000,001–5,000,000 | $429 | $799 | $429 |
| 5,000,001–20,000,000 | $649 | $1,199 | $649 |
| >20,000,000 | Custom Offer | Custom Offer | Custom Offer |

Completed `Scan.total_records` is authoritative. Buyer estimates are scoping only.

## Automatic sprint status

| Sprint / capability | Automatic state | Manual remainder |
|---|---|---|
| Product / price freeze | PASS | none |
| Free / Quick / Full entitlement funnel | PASS | real BC/PROD journey |
| Validation baseline and second-scan semantics | PASS | real BC/PROD journey |
| Fiverr pricing service | PASS | real order/add-on handling |
| Operator grant flow | PASS | real seller operation |
| Quick report contract | PASS | DE/EN visual QA with real data |
| Full report contract | PASS | Lovable visual target + Appendix real-data QA |
| Validation report contract | PASS | final Lovable visual implementation + real-data QA |
| Monitoring report backend | PASS for later product stage | visual polish deferred; not launch blocker |
| Lifecycle email engine | PASS | real SMTP/DNS/provider acceptance |
| Lifecycle DE/EN Admin Editor | PASS | admin UI smoke + real SMTP delivery |
| Fiverr next-purchase guidance | PASS | final published Fiverr URL/config where desired |
| Fiverr Requirements / Delivery contract | PASS | one real Fiverr order dry-run |
| Backup / restore automation | PASS | off-host operational PROD restore drill |
| Automated tenant-security gates | PASS | real two-tenant BC SaaS negative test |
| Extension source 1.0.2.30 | PASS static gate | build/install/runtime acceptance in real BC Online |
| Combined non-SUPER permission design | PASS static gate | `BCSENTINEL PILOT` runtime acceptance without SUPER |
| Landing Fiverr CTA/copy | PASS CI/build | publish Gig URL and deploy reviewed frontend ref |
| BC install/scan guide text | PASS draft | screenshots from accepted 1.0.2.30 Extension |
| Legal/privacy acceptance checklist | PREPARED | legal/provider-facts sign-off remains manual |
| Fiverr sample-report strategy | DEFINED | final Lovable DE/EN exports |

## Automatic quality gates

Current controlled-pilot automation includes:

- frozen Fiverr launch-contract drift validation;
- BC compatibility contract validation;
- controlled-pilot Extension static validation;
- DE/EN lifecycle Admin Template regression coverage;
- Free/Quick/Full/Validation funnel regressions;
- automated tenant-security tests;
- synthetic pilot journey tests;
- pricing/next-purchase lifecycle regressions;
- frontend frozen Fiverr copy validation + production build;
- PostgreSQL backup/restore automation already present in the project.

The aggregate workflow is `.github/workflows/fiverr-automatic-golive-preflight.yml`.

## Manual P0 gates before first paid Fiverr customer

These are deliberately not marked complete by repository automation:

1. Build/install/upgrade final Extension **1.0.2.30** in real Business Central Online.
2. Assign only the combined **BCSENTINEL PILOT** permission set to the pilot user and confirm the complete selected flow without SUPER.
3. Run real Tenant A / Tenant B negative isolation tests.
4. Run visual QA of real Free, Quick, Full and Validation HTML/PDF outputs in DE/EN where applicable.
5. Configure a real SMTP provider and accept SPF/DKIM/DMARC, inbox/spam placement and bounce behavior.
6. Perform an off-host/operational backup + isolated restore drill against the actual production procedure.
7. Complete privacy/DPA/legal/provider-facts sign-off.
8. Freeze an immutable reviewed release candidate and promote exactly that ref to PROD.
9. Run a fresh external-like PROD E2E from Fiverr order through Quick → Full → Validation.
10. Publish final Fiverr assets and execute one real order dry-run.
11. Set the real Fiverr Gig URL in `VITE_FIVERR_GIG_URL`, deploy and smoke-test the landing CTA.

## Deferred non-blockers

The following must not delay the first controlled Fiverr pilot unless scope changes:

- Monitoring visual/report perfection
- AppSource submission
- public self-service registration
- public Stripe E2E for Fiverr-origin payments
- mobile dashboard polish
- partner program
- LinkedIn launch post

## Release rule

A green automatic gate means the repository contract is internally consistent. It does **not** replace external runtime evidence. No automatic process may mark BC Online runtime, SMTP deliverability, real tenant isolation, legal sign-off, real Fiverr order handling or PROD recovery as PASS without manual evidence.
