# BCSentinel — Legal / Privacy / Provider Acceptance

Status: **repository audit prepared; final legal/provider sign-off is manual**  
Date: 2026-11-03  
Scope: controlled paid Fiverr pilot.

This document is a release checklist, not legal advice. Repository automation can verify that required surfaces and claims are present and consistent; it cannot confirm legal sufficiency, contractual status, tax/company facts or a processor agreement.

## Repository findings

### Present

- Public privacy route exists in the frontend: `/datenschutz`.
- Public imprint route exists in the frontend: `/impressum`.
- Public contact email is shown as `info@bcsentinel.com`.
- Technical support email is shown as `support@bcsentinel.com`.
- Privacy copy explicitly tells users not to send passwords/API tokens through public forms.
- Privacy copy states Business Central Online scope, German hosting intent, tenant separation and encrypted communication.
- Product/report copy treats modeled financial impact as decision-support estimates rather than guaranteed savings.
- Fiverr requirements explicitly prohibit credentials/secrets and keep Fiverr-origin commercial communication/payment on Fiverr.

### Deliberately still open

The current frontend itself labels privacy/imprint as controlled-pilot drafts. Before the first paid customer, manually confirm and replace/finalize:

- responsible legal person/entity;
- complete service-provider identification;
- serviceable postal address;
- applicable tax/VAT identifiers, if required;
- registry details, if applicable;
- concrete hosting/provider identity and data-processing facts;
- processor/subprocessor agreements (AVV/DPA) and relevant locations/transfers;
- retention/deletion periods for tenant registration, scan data, findings, reports, lifecycle email/outbox and logs;
- legal bases and data-subject rights wording;
- contact process for privacy requests;
- terms/service scope and liability wording appropriate to the chosen business setup;
- statement that modeled Estimated Loss / Potential Saving values are not guaranteed/accounting-confirmed savings;
- Fiverr-specific commercial terms remain on Fiverr and do not redirect payment off-platform.

## URL consistency gate

The final accepted Business Central Extension manifest must point its `privacyStatement` and help/support metadata to real production URLs that return the intended content. Do not approve the Extension runtime gate until these URLs have been manually opened from the installed artifact.

Current frontend canonical privacy path: `https://bcsentinel.com/datenschutz`.

If the manifest uses another path (for example historical `/privacy.html`), either provide a permanent production redirect or update the manifest before freezing the release candidate.

## Manual acceptance evidence

Record PASS/FAIL plus evidence for:

- [ ] Imprint/provider facts finalized
- [ ] Privacy text finalized
- [ ] Hosting/provider facts verified
- [ ] AVV/DPA/subprocessor position verified
- [ ] retention/deletion policy verified
- [ ] terms/service-scope wording verified
- [ ] modeled-impact disclaimer verified
- [ ] `privacyStatement` URL returns HTTP 200 in production
- [ ] help/support URL returns the intended customer support content
- [ ] Fiverr Gig description/FAQ does not conflict with privacy/terms

## Release rule

This gate remains **MANUAL / OPEN** until the actual business/provider facts have been reviewed and the public pages have been updated. No CI test or code review may mark legal sufficiency as PASS.
