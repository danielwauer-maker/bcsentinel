# BCSentinel Fiverr Gig Launch Kit

Last reviewed: 2026-11-01  
Target: controlled Fiverr pilot for Microsoft Dynamics 365 Business Central Online.

## Frozen product journey

BCSentinel uses one technical initial Data Health Scan and progressively unlocks more value from that stored result:

`Free Health Check -> Quick Assessment -> Full Assessment -> Validation -> Monitoring later`

Important:

- **Free Health Check is not a paid Fiverr package.** It is the aggregate BCSentinel entry layer created by the initial scan.
- **Quick Assessment and Full Assessment reuse the same initial scan.** Neither creates a second scan.
- **Validation is the first follow-up product that creates a new scan** after remediation.
- A customer may skip Quick Assessment and buy Full Assessment directly.
- Fiverr is a sales/order channel only. Do not create a Fiverr-specific BCSentinel product or Extension build.

## Positioning

**Gig title**  
`I will audit your Microsoft Dynamics 365 Business Central data quality`

**Primary promise**  
A structured Business Central Online data-quality assessment using BCSentinel. The initial full scan evaluates up to 10 business areas / 199 checks. Fiverr packages unlock prioritized findings, modeled business impact and remediation guidance from that same stored scan.

**Search tags**

- Business Central
- data quality
- Microsoft Dynamics
- ERP audit
- data audit

## Fiverr package model

Visible Fiverr package prices are the **Micro tier for up to 100,000 analyzed records**. Larger environments use the same products but are priced through a Custom Offer after scope/record volume is known.

| Package | Base price | Delivery | Revision | Customer receives |
|---|---:|---:|---:|---|
| BASIC — Quick Assessment | **$129** | 3 days | 1 | Guided setup + initial full scan if required + 7-day Quick access + Top 5 prioritized findings + affected counts + severity/risk area + concise next steps + Quick Assessment PDF |
| STANDARD — Full Assessment | **$299** | 4 days | 1 | Initial full scan if required + 7-day Full Assessment access + all findings + exact modeled impact + root-cause context + prioritized remediation + Assessment PDF |
| PREMIUM — Assessment Plus | **$399** | 4 days | 1 | Full Assessment + one allowed additional 7-day access extension for the same scan |

The Premium package is a commercial wrapper around Full Assessment. It is not a separate core entitlement and does not create another scan.

### Volume-based Fiverr pricing

The authoritative price recommendation is derived from `Scan.total_records` after analysis.

| Analyzed records | Quick Assessment | Full Assessment | Validation |
|---|---:|---:|---:|
| ≤100,000 — Micro | **$129** | **$299** | **$149** |
| 100,001–250,000 — Small | **$169** | **$349** | **$179** |
| 250,001–1,000,000 — Medium | **$229** | **$449** | **$229** |
| 1,000,001–5,000,000 — Large | **$349** | **$649** | **$329** |
| 5,000,001–20,000,000 — Enterprise | **Custom Offer** | **Custom Offer** | **Custom Offer** |
| >20,000,000 — Custom | **Individual review** | **Individual review** | **Individual review** |

For Assessment Plus above Micro, use the applicable Full Assessment recommendation plus **$100** for the one allowed 7-day extension unless the operator deliberately overrides it for the pilot.

If a buyer orders a fixed Micro package but the authoritative completed scan places the environment in a higher class, do not silently deliver expanded scope. Keep all commercial discussion on Fiverr and resolve the difference with a Fiverr Custom Offer before paid-detail delivery.

## Follow-up Validation offer

Validation is **not** a first purchase. Offer it only after a paid Full Assessment baseline exists and the customer has implemented changes.

Validation includes:

- exactly one new full Data Health Scan,
- comparison against the paid Full Assessment baseline,
- Resolved / Improved / Remaining / Regressed / New,
- score and modeled-impact change,
- Validation Report,
- 7-day Validation result access beginning with the new Validation scan.

Base Micro price: **$149**. Use the volume table above for larger environments.

## Fiverr customer paths

### Customer arrives directly from Fiverr

1. Customer orders Quick Assessment or Full Assessment on Fiverr.
2. Requirements are completed on Fiverr.
3. Customer installs/configures the normal BCSentinel Extension.
4. If no qualifying initial scan exists, BCSentinel runs the one full initial scan using the Free Entry credit.
5. The Free aggregate result exists technically, but the purchased Fiverr product is then unlocked by the operator using the Fiverr Order ID.
6. Delivery is made through Fiverr with the correct Quick or Full report.

### Customer already has a BCSentinel Free Health Check

1. Customer buys Quick Assessment or Full Assessment on Fiverr.
2. Operator verifies the tenant/order and unlocks the existing qualifying scan.
3. **No rescan** occurs.

### Upgrade path

`Quick Assessment -> Full Assessment` reuses the same initial scan.  
`Full Assessment -> Validation` creates the next scan only after remediation.

## Gig description

Use this as the default English Fiverr description. Keep all commercial communication and payment on Fiverr.

> Poor Business Central data can quietly create reporting errors, process friction and avoidable financial impact.
>
> I use BCSentinel to run a structured Data Health Scan for Microsoft Dynamics 365 Business Central Online and turn the result into a clear, management-ready assessment.
>
> The initial scan evaluates up to 10 business areas using 199 automated checks. Your package determines how much of that same scan is unlocked:
>
> - **Quick Assessment:** Top 5 prioritized findings, affected counts, severity, risk area and concise next steps.
> - **Full Assessment:** all findings, modeled Estimated Loss / Potential Saving, root-cause context and prioritized remediation actions.
> - **Assessment Plus:** Full Assessment plus one additional 7-day access extension for the same scan.
>
> After you implement changes, a separate Validation Check can run a new scan and compare the results with the paid Full Assessment baseline.
>
> Base package prices apply to environments with up to 100,000 analyzed records. Larger environments are priced by analyzed record volume and may require a Fiverr Custom Offer.
>
> The technical scan runs through the normal BCSentinel Business Central Extension. Your order, commercial communication and payment remain on Fiverr. Never send passwords, API tokens or other credentials through Fiverr.

## Package short descriptions

### BASIC — Quick Assessment

`Top 5 prioritized BC data-quality findings + concise actions.`

### STANDARD — Full Assessment

`All findings, modeled impact, root causes and prioritized actions.`

### PREMIUM — Assessment Plus

`Full Assessment + one additional 7-day access extension.`

## Buyer requirements

Do not request an external contact email in Fiverr. The transactional Report & Notification Email is entered inside the BCSentinel Extension because it is technically required for report/lifecycle delivery.

1. **Are you using Microsoft Dynamics 365 Business Central Online?** — Required: Yes / No / Not sure.
2. **Which Business Central environment/company is in scope?** — Required; no credentials.
3. **Which company or companies are in scope?** — Required free text.
4. **Can an authorized BC administrator install a `.app` Extension?** — Required: Yes / No / Need guidance.
5. **Preferred report language** — English / German.
6. **Approximate record volume** — ≤100k / ≤250k / ≤1m / ≤5m / ≤20m / >20m / Not sure.
7. **Known data-quality/process areas to focus on?** — Optional.
8. **Confirm that you will not send usernames, passwords, API tokens or secrets through Fiverr.** — Required acknowledgement.

The completed BCSentinel scan, not the buyer estimate, is authoritative for the final record class.

## FAQ

### 1. Do you need my Business Central password?
No. Never send passwords, API tokens or user credentials. The BCSentinel Extension performs the scan inside the authorized Business Central environment.

### 2. Is this for Business Central Online or on-premises?
The controlled pilot is for Microsoft Dynamics 365 Business Central Online.

### 3. Is the Free Health Check a Fiverr package?
No. Free Health Check is the aggregate BCSentinel entry layer generated by the initial scan. Fiverr Basic is the **Quick Assessment**, which unlocks actionable detail from that scan.

### 4. What does Quick Assessment include?
Up to the five highest-priority findings with title, severity, affected-record count, risk area and a concise next step, plus the Quick Assessment Report. It does not include the full finding list, exact modeled EUR values, full root-cause analysis or record-level drilldown.

### 5. What does Full Assessment add?
It unlocks the same initial scan for 7 days with all findings, affected counts, exact modeled Estimated Loss / Potential Saving, root-cause context, priorities, remediation guidance and the Full Assessment Report.

### 6. Does Quick or Full Assessment run another scan?
No. Both reuse the existing initial scan. A new scan is created later for Validation.

### 7. Can I skip Quick Assessment?
Yes. You can purchase Full Assessment directly.

### 8. What is Validation?
A follow-up service after a paid Full Assessment. Once fixes are implemented, BCSentinel runs one new full scan and compares it with the paid baseline.

### 9. Why can the price change with tenant size?
The service is priced by the number of analyzed records. The visible Fiverr package price is the Micro tier up to 100,000 records. Larger tenants receive the corresponding Fiverr Custom Offer.

### 10. Are modeled financial values guaranteed savings?
No. They are decision-support estimates based on detected conditions and documented assumptions, not accounting-confirmed or guaranteed savings.

## Gig gallery — 3 images

### Image 1 — Hero

**Headline:** `Business Central Data Quality Assessment`  
**Subline:** `199 checks · 10 business areas`

Visual: BCSentinel navy/orange, score card and anonymized report crop. No contact details or unsupported third-party logos.

### Image 2 — Product depth

**Headline:** `Top 5 → Full Detail → Validation`

Visual: three cards showing Quick / Full / Validate.

### Image 3 — Product journey

**Headline:** `Scan once. Unlock what you need.`

Visual flow: `Initial Scan → Quick → Full → Fix → Validation`. Make it visually explicit that Quick and Full use the same initial scan and Validation is the new scan.

## Gig video — 45–55 seconds

### Scene 1 — 0–7 s
Screen: `How healthy is your Business Central data?`

### Scene 2 — 7–17 s
Screen: `BCSentinel · 199 checks · 10 business areas`
Voice: “BCSentinel runs one structured initial Data Health Scan across up to ten business areas.”

### Scene 3 — 17–28 s
Screen: `Quick Assessment · Top 5 priorities`
Voice: “Quick Assessment highlights the five most important findings and what to address next.”

### Scene 4 — 28–40 s
Screen: `Full Assessment · complete detail`
Voice: “Full Assessment unlocks every finding, modeled business impact, root-cause context and prioritized remediation.”

### Scene 5 — 40–50 s
Screen: `Fix → New Scan → Validate`
Voice: “After remediation, Validation runs a new scan and shows what improved, what remains and what is new.”

### Scene 6 — 50–55 s
Screen: `Clean Data – Higher Impact`
Voice: “Choose the BCSentinel assessment level that fits your Business Central environment.”

## Gallery PDFs

Use the two Fiverr PDF slots for the clearest paid-tier comparison:

1. **BCSentinel Quick Assessment Report — Sample** — first three pages: cover, score/risk summary, Top 5 findings.
2. **BCSentinel Full Assessment Report — Sample** — first three pages: cover, executive summary, score/business-impact view.

The Free Health Report can remain visible on BCSentinel/portfolio material, but should not be presented as the paid Basic Fiverr deliverable.

## Delivery templates

### Basic / Quick Assessment delivery

`Your BCSentinel Quick Assessment is complete. I have attached the Quick Assessment Report. It contains the five highest-priority findings from the initial Data Health Scan, including severity, affected counts, risk area and concise next steps. The Full Assessment can unlock the complete finding set, modeled financial impact, root-cause context and full remediation guidance from the same scan without running another scan.`

### Full Assessment delivery

`Your BCSentinel Full Assessment is complete. I have attached the Full Assessment Report with all findings, affected counts, modeled business impact, root-cause context and prioritized remediation actions. Your detailed live-result access is active for the 7-day Assessment window shown in BCSentinel. After changes are implemented, Validation can be ordered as a follow-up service.`

### Validation delivery

`Your BCSentinel Validation Check is complete. The attached Validation Report compares the new scan with your paid Full Assessment baseline and identifies resolved, improved, remaining, regressed and new findings. Your 7-day Validation result window starts with the new Validation scan.`

## Revision policy

Use **1 revision** per package.

A revision means correction of report presentation or clarification based on the same scan data. It does **not** include a new scan, changed company scope, changed source data, remediation work or a different record-volume class. A post-remediation rescan is Validation.

## Compliance guardrails

- All Fiverr-origin commercial communication and payment stay on Fiverr.
- Do not use the Free Health Check to divert a Fiverr buyer to an off-platform purchase or contract.
- Do not place email addresses, phone numbers, outside-payment instructions or external checkout CTAs in the Gig, gallery, video or delivery text.
- Technical use of the BCSentinel Extension is part of fulfilling the purchased service; it is not an alternative payment channel.
- The Report & Notification Email entered inside the Extension is transactional/technical only and must not be used to bypass Fiverr communication.
- Never request BC credentials or secrets.
- No Fiverr-specific BCSentinel product code or Extension fork.

## Launch checklist inside Fiverr

- [ ] Category/subcategory selected and current standardized requirements checked in the live Fiverr UI.
- [ ] Gig title and five tags entered.
- [ ] BASIC **Quick Assessment $129**, STANDARD **Full Assessment $299**, PREMIUM **Assessment Plus $399** entered for the ≤100k Micro tier.
- [ ] Each package has 1 revision.
- [ ] Description clearly says base package prices apply up to 100,000 analyzed records.
- [ ] Larger environments route to Fiverr Custom Offers using the central record-volume matrix.
- [ ] Validation retained as follow-up Custom Offer: $149 / $179 / $229 / $329 by Micro/Small/Medium/Large; Enterprise custom.
- [ ] 8 requirements configured with the six current record-volume options.
- [ ] 10 FAQs configured.
- [ ] Gallery journey reads `Initial Scan → Quick → Full → Validation`, not `Scan → Assessment → Validation`.
- [ ] Quick and Full sample PDFs selected; Free PDF is not presented as Basic deliverable.
- [ ] No contact details, external payment CTA, unsupported logos or customer data in assets.
- [ ] Final desktop/mobile Fiverr preview reviewed.
- [ ] Publish only after manual BCSentinel PROD/BC gates are closed.

## Current Fiverr rule references

Re-check these before publishing because category-specific requirements can change:

- Creating a Gig: https://help.fiverr.com/hc/en-us/articles/360010451397-Creating-a-Gig
- Creating/managing Gig packages: https://help.fiverr.com/hc/en-us/articles/360010559138-Creating-and-managing-Gig-packages
- Creating/managing Custom Offers: https://help.fiverr.com/hc/en-us/articles/360010559198-Creating-and-managing-custom-offers
- Gig requirements/guidelines: https://help.fiverr.com/hc/en-us/articles/360011421218-Requirements-and-guidelines-for-your-Gig
- Off-platform policy: https://help.fiverr.com/hc/en-us/articles/12792122691601-Stay-protected-Fiverr-s-off-platform-policy
- Community Standards: https://help.fiverr.com/hc/en-us/articles/37554441398929-Our-Community-Standards
