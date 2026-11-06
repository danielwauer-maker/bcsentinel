# BCSentinel Fiverr Next-Purchase Lifecycle Email

Status: frozen for controlled Fiverr launch  
Date: 2026-11-03

## Purpose

BCSentinel reports remain professional and channel-neutral. Fiverr package selection, record-volume pricing and Add-on guidance are communicated in lifecycle email instead of being embedded into Free, Quick or Full report content.

The recommendation uses the completed scan's persisted `Scan.total_records` value. Buyer estimates are not authoritative.

## Next-step mapping

| Current result layer | Recommended Fiverr purchase | New scan? |
|---|---|---|
| Free Health Check | BASIC — Quick Assessment | No; unlock same initial scan |
| Quick Assessment | ADVANCED — Full Assessment | No; unlock same initial scan |
| Full Assessment | Validation follow-up Gig | Yes, but only after remediation |
| Validation | No launch upsell in this email | — |

## Price presentation

The email must use `record_volume_pricing_service.py` as the pricing authority. It must not maintain a second price table.

For a fixed-price class above Micro, the customer receives one clear instruction:

`base Fiverr Gig + data-volume Add-on = total frozen Fiverr price`

Examples:

- 800,000 records, next step Quick: BASIC $149 + $130 Add-on = $279 total.
- 800,000 records, next step Full: ADVANCED $349 + $200 Add-on = $549 total.
- 800,000 records, next step Validation: Validation base $179 + $110 Add-on = $289 total.

For the Micro class, no Add-on is shown because the base Gig price already equals the total price.

For more than 20,000,000 analyzed records, no calculated Add-on is shown. The email instructs the customer to use an individual Fiverr Custom Offer.

## Commercial guardrails

- Reports do not contain Fiverr package prices or Add-on mechanics.
- Fiverr-origin commercial communication and payment stay on Fiverr.
- The email may explain the required Fiverr package, Add-on and total price.
- No new scan is implied for Free -> Quick or Quick -> Full.
- Validation must be described as a post-remediation follow-up and uses exactly one new scan against the paid Full Assessment baseline.
- Monitoring is intentionally not added as an automatic launch upsell.
- A public Fiverr URL is not hard-coded into backend email logic. The published Gig link can be added through an explicit channel configuration later without changing report contracts or pricing semantics.

## Language

The lifecycle guidance is rendered in German or English according to the existing tenant lifecycle profile language.

## Automated acceptance

The focused quality gate verifies:

1. Free -> Quick mapping and Add-on amount.
2. Quick -> Full mapping and no-rescan wording.
3. Full -> Validation mapping and post-remediation wording.
4. >20m Custom Offer behavior.
5. German and English rendering.
6. Real `scan.completed` worker delivery includes the calculated recommendation.
7. The shared frozen Fiverr pricing regression remains green.
