# LP-GL-03 — Final Page Blueprint and Design Approval

## Status

Implemented on branch `landingpage-redesign-01`.

This sprint creates the complete visual and structural blueprint before the productive homepage is rebuilt. The existing `landingpage/index.html` remains unchanged.

## Deliverables

- `landingpage/blueprint.html`
- `landingpage/css/landingpage-blueprint.css`

The blueprint uses the canonical visual foundation from:

- `landingpage/css/bcsentinel-enterprise-system.css`
- `landingpage/content/canonical-messaging.json`

## Design direction

Approved working direction: **Hybrid Enterprise**.

- Light product and information surfaces
- Dark navy report, lifecycle and final-CTA sections
- Orange reserved for primary conversion actions
- Blue for analytical context
- Green, amber and red reserved for data states and severity
- Realistic product UI rather than abstract illustrations
- Restrained depth and animation
- Reduced card density compared with the previous homepage

## Final homepage sequence

1. Sticky enterprise navigation
2. Hero with dashboard, finding and report composition
3. Product trust strip
4. Business problem and example cost impact
5. Estimated Loss transparency preview
6. Four-stage operating process
7. Assessment–Validation–Monitoring lifecycle
8. Findings list and detail
9. Executive Report dark section
10. Dashboard proof section
11. Target-audience value section
12. Security and data-flow section
13. Pricing
14. FAQ
15. Final CTA
16. Enterprise footer

## Hero decision

### German headline

`Machen Sie Datenqualität messbar und steuerbar.`

### Supporting message

BCSentinel identifies data-quality risks, evaluates operational and financial impact, and helps teams prioritize remediation.

### Primary CTA

`Assessment starten`

### Secondary CTA

`Beispielreport ansehen`

The hero deliberately avoids an absolute claim that the customer's data is already costing money. It starts with control, measurement and business decisions.

## Product visual

The hero product stage combines three recognizable product artifacts:

- dashboard overview
- floating high-priority finding
- executive-report preview

This composition becomes the central BCSentinel marketing motif. It should later use real local application assets while preserving the same hierarchy.

## Estimated Loss integration

The blueprint gives Estimated Loss its own early homepage section.

It separates:

- measured scan data
- model assumptions
- rate or cost inputs
- explicit calculation
- modeled annual result
- disclaimer

The CTA links to the existing `loss-examples.html`, which remains a P0 part of the public information architecture.

Required implementation behavior:

- preserve the existing page during migration
- modernize its visual system in LP-GL-05A
- keep backward-compatible links
- provide DE and EN content
- distinguish direct measurements and assumptions visually

## Product lifecycle

Assessment, Validation and Monitoring are presented as consecutive operating stages rather than generic price tiers.

- **Assessment:** establish the current state
- **Validation:** confirm improvements
- **Monitoring:** maintain ongoing control

`Premium` and `Full Analysis` are not used as visible product names.

## Findings decision

Findings are the primary product-proof section.

The blueprint shows:

- severity
- title
- affected records
- business impact
- recommendation
- status
- exception state

The final implementation should add owner and priority where supported by the product data.

## Executive Report decision

The report receives a dedicated dark section with realistic A4 proportions. It is positioned as a management deliverable rather than a decorative screenshot.

The section must eventually use the current productive report asset or a sanitized sample generated from the same report layout.

## Dashboard decision

The dashboard preview includes tabs for:

- Overview
- Findings
- Monitoring

The first implementation can use a static preview. Interactive tab switching is optional and must not compromise accessibility or performance.

## Security decision

Security content is intentionally conservative. The final implementation may only contain claims verified against the current architecture and deployment.

The blueprint reserves content groups for:

- Access
- Processing
- Governance
- Data flow

No certification, Microsoft partnership, hosting region or compliance claim may be introduced without evidence.

## Pricing decision

The three visible commercial products are:

- Assessment — €79 one-time
- Validation — €49 one-time
- Monitoring — €149 monthly

The annual Monitoring option remains part of the pricing data and can be shown as a billing toggle or supporting annual note in the implementation sprint.

All displayed prices must clearly state whether VAT is included or excluded and that the offer is intended for business customers.

## Responsive behavior

The blueprint includes layouts for:

- wide desktop
- standard desktop and tablet
- mobile below 700 px

Important mobile decisions:

- single-column hero
- simplified dashboard preview
- vertical lifecycle
- one-column pricing
- reduced report-page size
- compact navigation
- no horizontal content dependency

## Accessibility requirements carried forward

- skip link
- semantic landmarks
- real anchors for navigation
- visible keyboard focus from the enterprise design system
- no color-only severity communication
- reduced-motion support inherited from the enterprise system
- responsive text sizing
- details/summary for FAQ

The implementation sprint must additionally validate ARIA state for mobile navigation and any interactive tabs.

## Explicit non-goals

This sprint does not:

- replace `landingpage/index.html`
- connect checkout actions
- change production routes
- implement final translations
- publish a pull request
- modify `main`, `staging` or `arch-02a-product-model-alignment`

## Acceptance result

The blueprint now defines the full intended homepage and is suitable as the implementation reference for LP-GL-04 and subsequent content sprints.

## Next sprint

**LP-GL-04 — Hero and Conversion Core**

Planned scope:

- rebuild the productive header and hero on the redesign branch
- preserve shared shell and existing integrations where useful
- introduce the canonical CTA hierarchy
- create the real product composition from local assets
- implement desktop, tablet and mobile behavior
- add accessibility and semantic validation
- keep remaining legacy sections operational until their dedicated migration sprints
