# LP-GL-11A — Translation & Content Management

## Goal

Provide one consistent DE/EN content contract for the redesigned landing page and all public subpages, remove mixed-language UI, preserve versioned static fallbacks, and prepare an explicit integration point for published Admin Backend content.

## Implemented scope

Centralized content bundles now cover:

- homepage redesign,
- Estimated Loss examples,
- Security,
- documentation,
- contact,
- privacy,
- terms,
- legal notice,
- help,
- support,
- partner registration, login and password reset,
- partner portal.

Shared runtime and rendering components include:

- `landingpage/js/content-runtime.js`,
- `landingpage/js/public-content-page.js`,
- `landingpage/js/legal-content-page.js`,
- `landingpage/js/contact-page.js`,
- `landingpage/js/partner-auth-page.js`,
- `landingpage/js/partner-portal.js`,
- shared page-specific CSS files under `landingpage/css/`.

The migration removed duplicated inline translation dictionaries from the redesigned sections and migrated pages. Page titles, meta descriptions, form labels, status messages, product previews and relevant ARIA labels are now language-aware.

## Runtime priority

1. Published content endpoint, when configured.
2. Versioned static locale bundle.
3. Static fallback remains readable when the Admin endpoint is unavailable.

The optional published endpoint is configured through either:

```html
<meta name="bcsentinel-landing-content-endpoint" content="/public/landing-content" />
```

or:

```js
window.BCSENTINEL_LANDING_CONTENT_ENDPOINT = "/public/landing-content";
```

The runtime sends `locale` and `bundle` query parameters and deep-merges a valid published response over the matching static fallback.

## Admin Backend status

No authoritative public Landing Content endpoint could be verified on the working branch. The frontend therefore does not invent or hard-code an API path.

The required backend follow-up is documented separately in:

- `docs/landingpage/LP-GL-11A_ADMIN_CONTENT_PUBLISHING_AUDIT.md`

Recommended publishing lifecycle:

```text
Draft → Preview → Validate DE/EN parity → Publish → Versioned public bundle → Rollback
```

This backend implementation is intentionally separated from the completed frontend content migration.

## Canonical product language

German mode now uses localized process, navigation, finding and severity labels. Canonical product terms remain intentionally stable where useful:

- Assessment
- Validation
- Monitoring
- Health Score
- Estimated Loss
- Potential Saving
- Executive Report

The access model is consistently represented as:

```text
Free Scan → limited preview
Assessment → unlock existing analysis for seven days, no new scan credit
Validation → one new scan credit and a new seven-day access window
Monitoring → ongoing full access, scheduled scans, history and trends
```

## Automated validation

Run both checks from the repository root:

```bash
python scripts/validate_landing_translations.py
python scripts/audit_landing_content.py
```

The translation validator fails on:

- missing DE or EN paths,
- empty values,
- visible translation-key fallbacks,
- invalid locale metadata.

The content audit fails on:

- unclassified public HTML pages,
- missing title or meta description,
- missing shared header/footer or shell script,
- missing content runtime on migrated subpages,
- missing DE/EN bundles,
- executable inline JavaScript,
- inline CSS on migrated pages.

Reference-only files such as `blueprint.html` and `design-system.html` are explicitly excluded from the public-page migration audit.

## Acceptance status

Frontend migration status: **substantially complete**.

Completed acceptance areas:

- central DE/EN content bundles,
- static fallback behavior,
- homepage and public subpage migration,
- partner auth and partner portal localization,
- meta content switching,
- shared visual page shells,
- automated parity validation,
- automated public-page inventory and structural audit.

Remaining items outside the frontend migration:

- implement and verify the Admin Backend publishing endpoint,
- add browser-based rendered-language tests in the final QA sprint,
- perform final accessibility, responsive and SEO validation,
- complete legal review and replace remaining legal placeholders,
- centralize variable numeric content in LP-GL-11F.

## Sprint decision

LP-GL-11A can be considered **frontend-complete with a documented backend publishing dependency** once both local validation scripts pass. The Admin publishing API should be delivered as a focused backend/content-publishing sprint rather than being hidden inside further frontend work.
