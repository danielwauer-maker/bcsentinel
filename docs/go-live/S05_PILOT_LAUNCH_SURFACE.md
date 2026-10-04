# S05 Pilot Launch Surface

Status: **AUTOMATED PUBLIC-SURFACE CLOSURE COMPLETE / RELEASE-TIME SIGNOFF MANUAL**

## Implemented

- dedicated `landingpage_neu/pilot.html` for the controlled Core pilot;
- explicit cap of up to 50 tenants with staged admission wording;
- no AppSource/production/SLA promise;
- pilot navigation integrated into the public shell;
- contact surface uses an explicit mailto handoff instead of a fake successful submit;
- support page no longer publishes unverified uptime percentages;
- fallback support time is evidence-safe;
- all current public HTML pages are included in the unsupported-claims contract.

## Manual release-time boundary

Before inviting real pilot customers, confirm the actual mailbox is reachable and perform a final legal/privacy/brand read-through. These are release signoffs, not missing product code.


## Core launch-surface closure

The current Core pilot surface also includes:

- a persistent API-backed contact form with privacy acknowledgement and rate limiting;
- stored contact requests even when notification email delivery is unavailable;
- Pilot Page routed through the same contact workflow;
- current-shell Legal Notice, Privacy, Pilot Terms and DPA/AVV working templates;
- visible warnings that legal templates are examples and require manual legal/business review;
- a Core documentation page with exact screenshot/video capture instructions;
- removal of invented uptime/support-hour claims from the current surface.

Final legal, tax, operator identity/address, support-policy and visual-design sign-off remain manual.
