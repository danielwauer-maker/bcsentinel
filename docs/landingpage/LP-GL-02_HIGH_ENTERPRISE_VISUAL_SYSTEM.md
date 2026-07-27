# LP-GL-02 — High-Enterprise Visual System

## Status

Implemented on `landingpage-redesign-01`.

## Objective

Create a reusable visual foundation for the BCSentinel marketing site that feels credible for enterprise buyers, remains consistent with the product dashboard and executive report, and avoids generic AI-startup styling.

## Design direction

The approved direction is **Hybrid Enterprise**:

- predominantly light product and information sections;
- selective deep-navy sections for executive reporting, security and trust;
- orange reserved for primary conversion actions;
- blue reserved for analysis and information;
- green, amber and red reserved for product status and finding severity;
- real product UI and report artifacts instead of abstract illustrations;
- restrained shadow, radius and motion usage.

## Implemented assets

- `landingpage/css/bcsentinel-enterprise-system.css`
- `landingpage/design-system.html`

The reference page is intentionally marked `noindex,nofollow` and exists only for design review and implementation guidance.

## Canonical color roles

| Role | Token | Value |
|---|---|---|
| Enterprise background | `--bc-navy-950` | `#081426` |
| Dark surface | `--bc-navy-900` | `#0D1B31` |
| Primary conversion | `--bc-orange-500` | `#F47A2A` |
| Analysis and information | `--bc-blue-500` | `#367BF5` |
| Positive state | `--bc-green-500` | `#2F9C69` |
| Warning state | `--bc-amber-500` | `#D99A24` |
| Critical state | `--bc-red-500` | `#D95C5C` |
| Main text | `--bc-text` | `#13233D` |
| Secondary text | `--bc-text-soft` | `#42516A` |
| Page surface | `--bc-surface-50` | `#F8FAFC` |

## Usage rules

### Orange

Use for:

- primary CTA;
- active conversion state;
- one or two high-priority accents per viewport.

Do not use for:

- general decoration;
- every icon or badge;
- severity information;
- large background areas.

### Blue

Use for:

- analysis;
- information;
- links and focused states;
- technical diagrams;
- Assessment or neutral product states.

### Severity colors

- critical: red;
- high/warning: amber;
- healthy/completed: green;
- informational/medium-neutral: blue or neutral text.

Severity must never be conveyed by color alone. Text labels remain mandatory.

## Typography

Primary family: Inter with system-font fallback.

Rules:

- avoid excessive 800–900 weights;
- hero headings use controlled line lengths;
- body copy targets a maximum measure of approximately 68 characters;
- KPI values use tight tracking and strong hierarchy;
- uppercase text is limited to short eyebrows and table headers.

## Layout

- maximum content width: 1220 px;
- standard desktop grids: 2, 3 and 4 columns;
- tablet: four columns collapse to two;
- mobile: all primary grids collapse to one;
- standard section spacing uses responsive `clamp()` values;
- cards are not mandatory containers for every piece of content.

## Components included

- section surfaces: light, soft and dark;
- responsive containers and grids;
- eyebrow, hero, section and card typography;
- primary, secondary and quiet buttons;
- standard, featured, flat and dark cards;
- KPI metric component;
- severity and product badges;
- responsive data table shell;
- information, loss and success callouts;
- focus-visible states;
- reduced-motion support.

## Accessibility baseline

The system includes:

- visible keyboard focus rings;
- minimum 48 px primary action height;
- semantic color labels in the reference implementation;
- reduced-motion handling;
- responsive stacking;
- high-contrast light and dark surface combinations.

Full contrast testing remains part of LP-GL-10.

## Estimated Loss design requirement

The visual system establishes a mandatory distinction between:

1. measured scan data;
2. modeled or configured assumptions;
3. calculated result;
4. explanatory disclaimer.

The reference implementation demonstrates this with four separate calculation blocks. The final `loss-examples` implementation must preserve this distinction.

## Implementation policy

The existing production-facing `landingpage/styles.css` is not replaced in LP-GL-02. The new system remains isolated until the homepage implementation sprint begins, preventing partial redesign changes from affecting existing pages.

During LP-GL-04 and later implementation sprints:

- the new homepage will import the enterprise system first;
- page-specific CSS will only extend the canonical tokens and components;
- legacy rules will be migrated selectively;
- duplicate theme definitions and inline styles will be removed gradually;
- functional pricing, language, checkout and site-shell integrations will be retained.

## Acceptance criteria

- [x] Canonical color system defined.
- [x] Typography scale defined.
- [x] Layout and spacing tokens defined.
- [x] Button hierarchy defined.
- [x] Light and dark section system implemented.
- [x] Finding severity states implemented.
- [x] Responsive component behavior implemented.
- [x] Focus-visible states implemented.
- [x] Reduced-motion baseline implemented.
- [x] Estimated Loss measured-versus-modeled presentation implemented.
- [x] Visual reference page created.
- [x] Existing public landing page left functionally unchanged.

## Next sprint

LP-GL-03 — Design Mockups and Final Page Blueprint.

The next sprint should translate the approved visual system into a complete page-level blueprint covering desktop and mobile composition, exact section order, product visuals, report presentation, pricing, security, FAQ and final CTA before the primary homepage is rebuilt.
