# E2 Automated Regression Contract

Sprint E2 turns the existing BCSentinel quality gates into one release-oriented automated regression gate. It does not create a second source of product truth. Existing D1-D10 and E1 validators remain authoritative for their domains; E2 orchestrates and proves that they pass together on one revision.

## Required regression domains

1. **AL / Business Central static contracts**
   - AL localization validation
   - remediation contract validation
   - notification contract validation
   - No claim is made that this replaces real BC runtime acceptance. That remains E3.

2. **Backend / APIs**
   - Python compile check
   - Alembic revision graph check
   - complete `backend/tests` pytest suite
   - remediation and notification read-model contracts

3. **Pricing / public production surfaces**
   - canonical pricing consistency
   - Landing/Pilot pricing, claims, SEO and accessibility contract
   - pilot intake regression

4. **Executive Report**
   - one shared D10 report contract across JSON, HTML, PDF and Monitoring

5. **Tenant security**
   - E1 security contract remains mandatory
   - tenant lifecycle, credential/session and cross-tenant/resource boundaries remain regression protected

6. **Dashboard**
   - D6 Foundation, D7 Core Pages and D8 Service Pages validators
   - TypeScript check
   - production build
   - responsive contract markers

7. **Accessibility / responsive**
   - automated static/semantic checks are included in E2
   - real browser/tenant visual acceptance and Business Central role behavior remain E3 and must not be reported as completed by E2

## Aggregate acceptance rule

The GitHub workflow `E2 Automated Regression Quality Gate` contains three required groups:

- contract-and-al-regression
- backend-regression
- dashboard-regression

The final `release-gate` passes only when all three groups succeed on the same commit. A partial pass is not an E2 pass.

## Source of truth

The machine-readable regression matrix is `config/e2-regression-matrix.json`. The workflow and `scripts/validate_e2_automated_regression.py` enforce that matrix. Portfolio readiness must only be advanced after the merged PR has a successful aggregate E2 gate.

## Explicit exclusions

E2 does not claim completion of:

- real Viewer / Scan / Setup / Scheduler / Admin acceptance in Business Central (E3)
- real visual acceptance against a production-like tenant (E3)
- real Stripe checkout, customer portal, invoice provider behavior or SMTP/DNS delivery (E4)
- recovery/restore evidence (E5)
- pilot journey, soak or launch gates (E6-E8/F1)
