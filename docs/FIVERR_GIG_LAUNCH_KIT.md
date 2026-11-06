# BCSentinel Fiverr Gig Launch Kit

Last reviewed: 2026-11-03  
Target: controlled Fiverr launch for Microsoft Dynamics 365 Business Central Online.

## Frozen product journey

`Free Health Check -> Quick Assessment -> Full Assessment -> Validation -> Monitoring later`

BCSentinel uses one technical initial Data Health Scan and progressively unlocks more value from that stored result.

- **Free Health Check is not a paid Fiverr package.** It is the aggregate BCSentinel entry layer created by the initial scan.
- **Quick Assessment and Full Assessment reuse the same initial scan.** Neither creates a second scan.
- **Quick Assessment is permanent until explicitly revoked.** Secure share/email tokens may expire, but the entitlement itself does not.
- **Validation is separate and creates the next scan only after remediation.**
- A customer may skip Quick Assessment and buy Full Assessment directly.
- Validation requires a prior paid Full Assessment baseline; Quick alone is not sufficient.
- Fiverr is a sales/order/payment channel only. Do not create a Fiverr-specific BCSentinel product or Extension build.

## Positioning

**Gig title**  
`I will audit your Microsoft Dynamics 365 Business Central data quality`

**Primary promise**  
A structured Business Central Online data-quality assessment using BCSentinel. The initial full scan evaluates up to 10 business areas / 199 checks. The purchased product determines which result layer is unlocked from that same stored scan.

**Search tags**

- Business Central
- data quality
- Microsoft Dynamics
- ERP audit
- data audit

## Frozen Fiverr launch products

Launch commercially with two assessment levels plus a separate Validation follow-up:

| Product | Launch role | Customer receives |
|---|---|---|
| **BASIC — Quick Assessment** | entry paid assessment | initial scan if required, permanent Quick access, Top 5 prioritized findings, affected counts, normalized severity, risk area, impact band, concise next step, Quick Assessment PDF |
| **ADVANCED — Full Assessment** | complete assessment | initial scan if required, 7-day Full Assessment access, complete finding set, exact modeled financial impact, root-cause context, prioritization, remediation guidance, Full Assessment PDF |
| **Validation** | separate follow-up Gig / offer | one new scan after remediation, comparison with the paid Full Assessment baseline, Validation PDF and 7-day validation detail window |

There is **no paid Fiverr Free Health Check package** and **no Assessment Plus / Premium launch package**. The technically available one-time Full Assessment extension is not sold as a separate launch tier.

## Frozen volume-based Fiverr pricing

The authoritative record class is derived from completed `Scan.total_records`.

| Analyzed records | BASIC — Quick | ADVANCED — Full | Validation follow-up |
|---|---:|---:|---:|
| ≤100,000 | **$149** | **$349** | **$179** |
| 100,001–250,000 | **$199** | **$399** | **$219** |
| 250,001–1,000,000 | **$279** | **$549** | **$289** |
| 1,000,001–5,000,000 | **$429** | **$799** | **$429** |
| 5,000,001–20,000,000 | **$649** | **$1,199** | **$649** |
| >20,000,000 | **Custom Offer** | **Custom Offer** | **Custom Offer** |

Rules:

- Buyer estimates are useful for pre-sale scoping, but completed `Scan.total_records` is authoritative.
- If the final volume exceeds the purchased scope, resolve the commercial difference on Fiverr before releasing paid detail beyond the purchased scope.
- Fiverr pricing is channel metadata only; it does not change entitlement semantics and does not overwrite direct/Stripe EUR pricing.

## Fiverr customer paths

### Direct Fiverr buyer

1. Customer buys BASIC Quick Assessment or ADVANCED Full Assessment on Fiverr.
2. Customer completes Fiverr requirements without sending credentials or secrets.
3. Customer installs/configures the normal BCSentinel Extension.
4. Customer enters consent, report/notification email and preferred language inside the Extension.
5. Tenant is registered.
6. If no qualifying initial scan exists, the included Free Entry credit runs the one full initial Data Health Scan.
7. Operator verifies payment/order and grants the purchased generic BCSentinel entitlement using the Fiverr Order ID.
8. Backend resolves the correct report variant automatically.
9. Delivery remains on Fiverr.

### Existing BCSentinel Free customer

1. Customer buys BASIC Quick or ADVANCED Full on Fiverr.
2. Operator verifies tenant and order.
3. Existing qualifying initial scan is unlocked.
4. **No rescan occurs.**

### Upgrade and follow-up

`Quick Assessment -> Full Assessment` reuses the same initial scan.  
`Full Assessment -> Validation` creates one new scan only after remediation.

## Product boundaries

### BASIC — Quick Assessment

Includes:

- up to five highest-priority findings;
- title;
- normalized severity;
- affected-record count;
- localized risk area;
- non-monetary impact band;
- concise finding-specific next review step;
- Quick Assessment report.

Does not include:

- complete finding set;
- exact modeled EUR values;
- issue codes;
- complete root-cause catalogue;
- record-level drilldown;
- full remediation worklist.

### ADVANCED — Full Assessment

Includes the complete paid assessment boundary for the qualifying initial scan:

- all findings;
- affected counts;
- exact modeled Estimated Loss / Potential Saving where supported;
- root-cause context;
- prioritization;
- remediation guidance;
- allowed drilldown/detail surfaces;
- Full Assessment report;
- 7-day full-detail access.

### Validation

Validation is offered only after a paid Full Assessment baseline exists and the customer has implemented changes.

Includes:

- exactly one new full Data Health Scan;
- comparison against the paid Full Assessment baseline;
- Resolved / Improved / Remaining / Regressed / New classification;
- score and modeled-impact change where supported;
- Validation Report;
- 7-day Validation detail window starting with validation scan consumption.

## Default Fiverr description

Poor Business Central data can quietly create reporting errors, process friction and avoidable financial impact.

I use BCSentinel to run a structured Data Health Scan for Microsoft Dynamics 365 Business Central Online and turn the result into a clear, management-ready assessment.

The initial scan evaluates up to 10 business areas using 199 automated checks. Your selected service determines how much of that same scan is unlocked:

- **BASIC — Quick Assessment:** Top 5 prioritized findings, affected counts, severity, risk area, impact band and concise next steps.
- **ADVANCED — Full Assessment:** complete findings, modeled Estimated Loss / Potential Saving, root-cause context and prioritized remediation guidance.

After you implement changes, **Validation** is available separately. Validation runs one new scan and compares it with the paid Full Assessment baseline.

Pricing is based on analyzed record volume. The completed BCSentinel scan is authoritative for the final record class. All Fiverr-origin commercial communication and payment remain on Fiverr. Never send passwords, API tokens or other credentials through Fiverr.

## Package short descriptions

### BASIC — Quick Assessment

`Top 5 prioritized BC data-quality findings + concise next actions.`

### ADVANCED — Full Assessment

`Complete findings, modeled impact, root causes and prioritized remediation.`

### Validation follow-up

`New scan after remediation with before/after proof against the paid Full baseline.`

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

## FAQ

### Do you need my Business Central password?
No. Never send passwords, API tokens or user credentials. The BCSentinel Extension performs the scan inside the authorized Business Central environment.

### Is this for Business Central Online or on-premises?
The controlled launch is for Microsoft Dynamics 365 Business Central Online.

### Is the Free Health Check a Fiverr package?
No. Free Health Check is the aggregate BCSentinel entry layer generated by the initial scan. Fiverr BASIC is Quick Assessment.

### Does Quick Assessment expire?
The Quick entitlement itself is permanent until explicitly revoked. Individual secure share/email links may expire for security and can be regenerated through BCSentinel.

### Does Quick or Full Assessment run another scan?
No. Both reuse the same qualifying initial scan. A new scan is created later for Validation.

### Can I skip Quick Assessment?
Yes. Full Assessment can be purchased directly.

### What does Full Assessment add?
It unlocks the complete paid assessment boundary for the same scan, including all findings, modeled financial impact where supported, root-cause context and prioritized remediation guidance.

### What is Validation?
A separate follow-up after a paid Full Assessment. Once fixes are implemented, BCSentinel runs one new scan and compares the result with the paid baseline.

### Why can price change with tenant size?
The service is priced by authoritative analyzed record volume. Buyer estimates are only for initial scoping.

### Are modeled financial values guaranteed savings?
No. They are decision-support estimates based on detected conditions and documented assumptions, not accounting-confirmed or guaranteed savings.

## Delivery templates

### BASIC / Quick Assessment

`Your BCSentinel Quick Assessment is complete. I have attached the Quick Assessment Report. It contains the five highest-priority findings from the initial Data Health Scan, including severity, affected counts, risk area, impact band and concise next steps. Full Assessment can unlock the complete finding set, modeled financial impact, root-cause context and full remediation guidance from the same scan without running another scan.`

### ADVANCED / Full Assessment

`Your BCSentinel Full Assessment is complete. I have attached the Full Assessment Report with the complete paid finding set, affected counts, modeled business impact, root-cause context and prioritized remediation actions. Your detailed live-result access is active for the 7-day Assessment window shown in BCSentinel. After changes are implemented, Validation can be ordered separately.`

### Validation

`Your BCSentinel Validation is complete. The attached Validation Report compares the new scan with your paid Full Assessment baseline and identifies resolved, improved, remaining, regressed and new findings. Your 7-day Validation detail window starts with the new Validation scan.`

## Revision policy

Use one revision for the assessment deliverable. A revision means correction of report presentation or clarification based on the same scan data. It does not include a new scan, changed company scope, changed source data, remediation work or a different record-volume class. A post-remediation rescan is Validation.

## Compliance guardrails

- All Fiverr-origin commercial communication and payment stay on Fiverr.
- Do not use Free Health Check to divert a Fiverr buyer to an off-platform purchase.
- Do not place external payment instructions in Fiverr assets or delivery text.
- The Report & Notification Email entered inside the Extension is transactional/technical only.
- Never request BC credentials or secrets.
- No Fiverr-specific BCSentinel product code, scan engine or Extension fork.

## Launch checklist inside Fiverr

- [ ] BASIC is Quick Assessment and uses the frozen volume matrix starting at **$149**.
- [ ] ADVANCED is Full Assessment and uses the frozen volume matrix starting at **$349**.
- [ ] Validation is separate and starts at **$179** after a paid Full Assessment baseline.
- [ ] No paid Free Health Check package is published.
- [ ] No Assessment Plus/Premium launch package is published.
- [ ] Description states that pricing is based on analyzed record volume.
- [ ] 5m–20m fixed pricing is $649 Quick / $1,199 Full / $649 Validation.
- [ ] >20m routes to a Custom Offer / individual review.
- [ ] Buyer requirements do not request passwords, API tokens or secrets.
- [ ] Quick and Full sample reports match the final report contracts.
- [ ] Final desktop/mobile Fiverr preview is reviewed.
- [ ] Publish only after the manual BCSentinel production gates are closed.
