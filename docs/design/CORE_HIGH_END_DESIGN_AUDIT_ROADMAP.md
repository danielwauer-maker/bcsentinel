# BCSentinel Core — High-End Design & UX Audit Roadmap

Status: **DEFERRED UNTIL TECHNICAL CORE CLOSURE**

## Purpose

This document records the agreed design phase without consuming implementation effort before the Core pilot foundation is technically ready. The target is a consistently premium SaaS experience across Dashboard, Landing Page, Pilot Page and Executive Reports.

## Scope after technical closure

The design phase must review, at minimum:

- Dashboard overview and all Core subpages
- Free / Full Analysis / Validation / Monitoring states
- Landing Page and conversion journey
- Pilot Page and trust/onboarding surfaces
- Executive Report / PDF
- Docs, Support, Contact and Legal presentation
- Light / Dark mode
- DE / EN
- desktop / tablet / mobile
- loading / empty / locked / error states

## Quality target

Target score before broader commercial launch: **>= 9.5 / 10** in the final design audit.

Dimensions:

1. usability and task clarity
2. professional SaaS appearance
3. information hierarchy
4. typography, spacing and sizing
5. color and semantic state system
6. accessibility and contrast
7. consistency across surfaces
8. conversion and trust
9. responsiveness
10. extensibility for future Intelligence and Automation editions

## Lovable usage strategy

Lovable is intentionally **not** the permanent implementation source of truth. It may be used later as a focused concept accelerator to establish one or more high-quality visual foundations. After a direction is selected, the canonical implementation continues in GitHub and is refined without unnecessary repeated Lovable generation.

No Lovable design work is required for the current technical Core-closure gate.

## Evidence to collect before design sprint

For every final visual review, capture real or sanitized product states rather than invented UI:

- Free/Core initial state
- Full Analysis state
- Validation state
- Monitoring state
- real findings
- real scan history
- real Executive Report
- permissions/locked state
- error and empty state
- DE and EN
- light and dark
- desktop, tablet and mobile

## Screenshot and video backlog

The required media content and capture instructions are maintained in `landingpage_neu/docs.html`. Screenshots must not expose API tokens, invitation codes, personal customer information or non-sanitized tenant identifiers.

## Exit condition

The design phase starts when:
- automated Core closure is green,
- only documented manual BC/runtime, legal/business sign-off and visual acceptance remain,
- the pilot RC baseline is technically stable enough that UI redesign will not mask unresolved product defects.
