# S05 Public Claims Audit

Status: **COMPLETE FOR CURRENT LANDING BASELINE**

## Purpose

Prevent BCSentinel marketing from claiming product, hosting, compliance or future capabilities before corresponding runtime/release evidence exists.

## Claims changed

The following statements were removed or downgraded from present-tense claims:

| Previous claim | Current wording / action | Reason |
| --- | --- | --- |
| Available on Microsoft AppSource | AppSource publication in preparation | No AppSource release evidence |
| Hosted in Microsoft Azure | Cloud deployment architecture in preparation | Azure hosting is a later platform sprint |
| GDPR compliant | GDPR-aware design | Formal compliance approval is separate from engineering intent |
| Enterprise ready | Enterprise-readiness roadmap / in progress | Enterprise hardening is S17-S18 |
| Business Central actions included in Monitoring | Removed from current pricing comparison | Controlled BC actions are planned for S16 |
| Founder/customer-project statistics | Removed from public homepage | Stale/unverified prototype content |

## Still acceptable

- Built for Microsoft Dynamics 365 Business Central
- Data Health Score
- Executive Report
- Monitoring/history where implemented
- Role-based access controls
- Evidence-backed financial impact and recommendation presentation

## Automated guard

`backend/tests/test_public_claims_contract.py` fails if known unsupported claims reappear in the public landing baseline.

## Remaining S05 work

- dedicated Design Partner / Pilot page;
- legal/privacy/contact launch polish;
- final pricing feature truth after S02 product-model closure;
- release-time re-audit against actual production hosting/AppSource/compliance evidence.
