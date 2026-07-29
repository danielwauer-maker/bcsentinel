# BCSentinel Landingpage – Go-Live QA

## Automated checks

Run from the repository root:

```powershell
python .\scripts\audit_landing_design.py
python .\scripts\audit_landing_content.py
python .\scripts\validate_landing_translations.py
python .\scripts\audit_landing_go_live.py
```

All four commands must pass before release approval.

## Required browser matrix

Test the current versions of Chrome, Edge and Firefox.

| Viewport | Width | Theme | Required pages |
|---|---:|---|---|
| Desktop | 1440 px | Light + Dark | Home, Estimated Loss, Security, Docs, Contact |
| Tablet | 768 px | Light + Dark | Home, Docs, Partner Login, Billing Success |
| Mobile | 390 px | Light + Dark | Home, Estimated Loss, Contact, Partner Login, Billing Cancel |
| Narrow mobile | 320 px | Light | Home, Contact, Partner Register |

## Acceptance criteria

### Global shell

- Header remains usable without horizontal page scrolling.
- Mobile menu opens, closes and updates `aria-expanded`.
- Language switch works without duplicated header or footer.
- Theme switch persists after navigation and reload.
- Global footer has the same structure on every public page.
- Keyboard focus is clearly visible on links, buttons and form controls.

### Conversion journey

- The primary entry is the Free Scan, not a paid Assessment scan.
- Product order is always: Free Scan → Assessment → Validation → Monitoring.
- Assessment is described as seven days of full access to the existing analysis and contains no scan credit.
- Validation is described as one new scan credit followed by a new seven-day access window.
- Monitoring is described as ongoing access with scheduled scans, history and trends.
- Primary and secondary CTAs are visually distinguishable.

### Product previews

- Dashboard preview is labelled as a concept preview.
- Report preview is labelled as the current design state.
- Preview images do not claim to be final production screenshots.
- Images remain readable or horizontally scrollable on mobile.
- No layout shift occurs when the preview assets load.

### Forms and account pages

- Fields are usable at 320 px without clipping.
- Mobile input text remains at least 16 px.
- Success and error messages are visible and announced through live regions.
- Required fields and privacy consent are understandable.
- Buttons remain at least 44 px high.
- Partner tables scroll horizontally without breaking the page layout.

### Content and trust

- No visible `Full Analysis`, `Premium`, MVP or placeholder wording remains.
- German pages use consistent formal address.
- English pages contain no German fragments.
- Estimated Loss is identified as a modelled decision-support value, not a guarantee.
- Security statements do not claim unverified certifications or partnerships.
- Legal pages contain the actual provider details before public launch.

## Release decision

- **PASS:** automated checks green and no P0/P1 visual defect in the browser matrix.
- **CONDITIONAL:** only minor copy or spacing defects remain and are documented.
- **FAIL:** broken navigation, horizontal page overflow, unreadable contrast, incorrect product model, failed form flow or missing legal provider information.
