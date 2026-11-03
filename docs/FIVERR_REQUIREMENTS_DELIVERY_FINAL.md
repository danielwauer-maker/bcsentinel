# BCSentinel Fiverr Requirements & Delivery Contract

Status: **FROZEN for controlled Fiverr launch**  
Date: 2026-11-03  
Authority: this document is the launch authority for Fiverr buyer requirements, order handoff and delivery wording. It complements `FIVERR_GIG_LAUNCH_KIT.md` and `FIVERR_NEXT_PURCHASE_EMAIL.md`.

## 1. Purpose

Keep the Fiverr order flow simple, secure and operationally unambiguous.

Rules:

- Fiverr is the commercial/order/payment channel.
- BCSentinel Extension is the technical onboarding and scan channel.
- Never request passwords, API tokens, usernames, secrets or screenshots containing secrets through Fiverr.
- Do not request the Report & Notification Email in Fiverr. It is entered inside the Extension for technical lifecycle/report delivery.
- The buyer's approximate record volume is a scoping estimate only. Completed `Scan.total_records` is authoritative.
- Quick and Full reuse the same qualifying initial scan. Validation is a separate post-remediation follow-up and creates one new scan.
- The Fiverr delivery always includes the customer-facing PDF as the formal Fiverr artifact. Secure BCSentinel links may additionally be referenced, but they do not replace Fiverr delivery.

---

## 2. BASIC / Quick Assessment — Fiverr Requirements

Use the following buyer questions in Fiverr.

### R1 — Business Central edition
**Question**  
`Are you using Microsoft Dynamics 365 Business Central Online?`

**Required:** Yes  
Options: `Yes / No / Not sure`

If `No`, do not proceed as a standard launch order. The controlled launch supports Business Central Online only.

### R2 — Environment
**Question**  
`Which Business Central environment is in scope?`

**Required:** Yes  
Example answer: `Production / Sandbox / Production + company name`

Do not request credentials.

### R3 — Company / companies in scope
**Question**  
`Which Business Central company or companies should be included in the assessment?`

**Required:** Yes  
Free text.

### R4 — Extension installation authority
**Question**  
`Can an authorized Business Central administrator install and configure the BCSentinel .app Extension?`

**Required:** Yes  
Options: `Yes / No / I need guidance`

### R5 — Preferred report language
**Question**  
`Which language should be used for the BCSentinel report?`

**Required:** Yes  
Options: `English / German`

### R6 — Estimated record volume
**Question**  
`What is your approximate analyzed record volume? This is only for initial scoping; the completed BCSentinel scan determines the final record-volume class.`

**Required:** Yes  
Options:
- `Up to 100,000`
- `100,001–250,000`
- `250,001–1,000,000`
- `1,000,001–5,000,000`
- `5,000,001–20,000,000`
- `More than 20,000,000`
- `Not sure`

### R7 — Optional focus
**Question**  
`Are there known data-quality or process areas you would especially like the assessment to consider?`

**Required:** No

This does not change the canonical scan depth or calculations. It is context for interpretation only.

### R8 — Security acknowledgement
**Question**  
`Please confirm that you will NOT send Business Central usernames, passwords, API tokens, access keys or other secrets through Fiverr.`

**Required:** Yes  
Required acknowledgement.

### R9 — Buyer cooperation / delivery timing
**Question**  
`Please confirm that an authorized person can complete the BCSentinel Extension installation, registration and initial scan steps promptly after the order starts. Delivery depends on these customer-side steps being completed.`

**Required:** Yes  
Required acknowledgement.

---

## 3. ADVANCED / Full Assessment — Fiverr Requirements

Use the **same R1–R9 requirements** as Quick Assessment.

Add one optional question:

### R10 — Existing BCSentinel scan
**Question**  
`Have you already completed a BCSentinel Free Health Check or Quick Assessment for this Business Central environment?`

**Required:** No  
Options: `Yes / No / Not sure`

Operational meaning:

- `Yes`: reuse the qualifying existing scan. No rescan.
- `No`: complete the included initial BCSentinel scan workflow first.
- `Not sure`: operator verifies the registered environment before granting Full access.

Do not ask the buyer for an API token or hidden BCSentinel Tenant ID.

---

## 4. Validation follow-up — Fiverr Requirements

Validation has different requirements because it depends on a paid Full Assessment baseline.

### V1 — Prior Full Assessment
**Question**  
`Was a paid BCSentinel Full Assessment completed for the same Business Central environment?`

**Required:** Yes  
Options: `Yes / No / Not sure`

Validation must not be granted if no qualifying paid Full baseline exists.

### V2 — Remediation status
**Question**  
`Have the planned data-quality improvements or remediation measures been implemented since the Full Assessment?`

**Required:** Yes  
Options: `Yes / Partly / Not yet`

If `Not yet`, clarify that Validation is intended after remediation. Do not consume the Validation scan credit prematurely.

### V3 — Environment/company scope
**Question**  
`Confirm the Business Central environment and company/companies to be validated.`

**Required:** Yes

### V4 — Preferred report language
**Question**  
`Which language should be used for the Validation Report?`

**Required:** Yes  
Options: `English / German`

### V5 — Estimated current record volume
Use the same volume choices as R6. The new completed Validation scan remains authoritative.

### V6 — Security acknowledgement
Use the same acknowledgement as R8.

### V7 — Buyer cooperation / scan timing
**Question**  
`Please confirm that an authorized person can start the BCSentinel Validation scan after access is granted.`

**Required:** Yes

---

## 5. Tenant/order matching rule

For the controlled launch, do **not** ask the Fiverr buyer to provide a hidden Tenant ID.

Match the order operationally using:

1. Fiverr Order ID/reference;
2. Business Central environment supplied in Requirements;
3. company/company names supplied in Requirements;
4. registered BCSentinel tenant/environment visible in the operator workflow;
5. scan state and timing.

The internal BCSentinel Tenant ID is not a buyer credential and is not currently exposed in the Extension UI; therefore it is not part of the Fiverr Requirements contract.

If more than one registered tenant could plausibly match the order, stop entitlement granting and clarify the environment/company with the buyer on Fiverr. Never guess.

---

## 6. Record-volume / Add-on handling

The buyer selects the estimated class before or during purchase. The completed BCSentinel scan is authoritative.

### If actual volume is within purchased scope
Proceed normally.

### If actual volume is lower than estimated
Proceed with the purchased order. Do not invent an automatic off-platform refund workflow. Any commercial adjustment, if offered, remains on Fiverr.

### If actual volume is higher than purchased scope
Do **not** release paid detail beyond the purchased scope until the commercial difference is resolved on Fiverr.

Send a concise Fiverr message explaining:

- analyzed record count;
- authoritative record class;
- purchased class;
- required Fiverr Add-on / Custom Offer;
- that the scan does not need to be repeated for Quick or Full.

For more than 20,000,000 records, use a Fiverr Custom Offer; do not calculate a fixed Add-on.

---

## 7. Internal seller order checklist

Before granting an entitlement:

- Fiverr order/payment verified.
- Correct product verified: Quick / Full / Validation.
- Requirements completed.
- No credentials or secrets received/stored in Fiverr messages.
- BC Online environment/company identified.
- Registered BCSentinel environment matched unambiguously.
- Initial scan completed for Quick/Full, or paid Full baseline exists for Validation.
- Authoritative `Scan.total_records` checked against purchased record-volume class.
- Any required Fiverr Add-on / Custom Offer resolved before paid detail release.
- Fiverr Order ID recorded when granting the entitlement.

Before Fiverr delivery:

- Correct entitlement granted.
- Correct report variant verified.
- PDF opens successfully.
- Customer/company/scan metadata looks plausible.
- No placeholders, `None`, `undefined`, secrets or API tokens in report/link.
- Quick: permanent Quick entitlement confirmed.
- Full: 7-day full-detail access window confirmed.
- Validation: 7-day validation detail window anchored to the consumed Validation scan.
- Formal PDF attached to Fiverr delivery.

---

## 8. Final Fiverr delivery messages

### BASIC — Quick Assessment

`Your BCSentinel Quick Assessment is complete.`

`I have attached your Quick Assessment Report to this Fiverr delivery. It summarizes the five highest-priority findings from your BCSentinel Data Health Scan, including severity, affected-record counts, risk area, impact band and concise next steps.`

`Your Quick Assessment access remains available in BCSentinel. If you want the complete finding set, detailed modeled financial impact and the full remediation roadmap, the Full Assessment can unlock those results from the same scan — no new scan is required.`

`Please note: modeled impact information is decision-support information and does not represent guaranteed or accounting-confirmed savings.`

### ADVANCED — Full Assessment

`Your BCSentinel Full Assessment is complete.`

`I have attached your Full Assessment Report to this Fiverr delivery. It includes the complete paid assessment boundary for the analyzed scan: detailed findings, affected-record counts, modeled business impact where supported, prioritization and remediation guidance.`

`Your Full Assessment live-detail access is available for the 7-day Assessment window shown in BCSentinel. The delivered PDF remains your assessment artifact after that live-access window ends.`

`After you implement the recommended improvements, BCSentinel Validation can be ordered separately. Validation runs one new scan and compares the result with this paid Full Assessment baseline.`

`Please note: modeled financial values are decision-support estimates and are not guaranteed or accounting-confirmed savings.`

### Validation

`Your BCSentinel Validation is complete.`

`I have attached your Validation Report to this Fiverr delivery. It compares the new post-remediation scan with your paid Full Assessment baseline and classifies findings as resolved, improved, remaining, regressed or new.`

`The report also shows score and modeled-impact changes where supported. Your 7-day Validation detail window started when the Validation scan was consumed.`

`Please note: modeled financial values are decision-support estimates and are not guaranteed or accounting-confirmed savings.`

---

## 9. Revision policy text for Fiverr

Use this wording in the Gig / FAQ / delivery policy:

`One revision is included for corrections to report presentation or clarification based on the same BCSentinel scan data. A revision does not include a new scan, changed company scope, changed source data, remediation work or a different record-volume class. A post-remediation rescan is a separate Validation service.`

---

## 10. What Fiverr delivery must NOT contain

Do not include:

- external payment instructions;
- requests to buy the Fiverr-origin service off-platform;
- passwords, API tokens or hidden credentials;
- claims of guaranteed savings or guaranteed ROI;
- a promise that a revision includes a rescan;
- a claim that Quick or Full requires another scan;
- a Validation delivery without a paid Full Assessment baseline.

---

## 11. Acceptance status

Requirements/Delivery is considered launch-ready when:

- the Fiverr Gig uses the frozen Quick/Full requirements above;
- the separate Validation Gig uses V1–V7;
- volume classes match the frozen Fiverr pricing matrix;
- the buyer cooperation acknowledgement is enabled;
- delivery messages are copied without changing product semantics;
- one real dry-run order confirms that Fiverr Requirements, tenant matching, report attachment and formal delivery work end-to-end.

**Code/document contract: ready. Real Fiverr dry-run: pending until Gig publication/test order.**
