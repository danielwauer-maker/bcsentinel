# BCSentinel – Fiverr USD Pricing Decision Candidate (ACV2-2026-11-12-P1)

**Prepared:** 2026-11-12  
**Status:** PROPOSED, **NOT approved**, not published, not activated.  
**Scope:** First Fiverr release: Full Assessment, Validation and Monitoring; no new Quick offer.  
**Authority:** Product System `00-core/product-model.yaml` and `00-core/record-based-pricing-contract.yaml` remain normative for existing direct/EUR offers until reviewed versioned amendment. This proposal is for Fiverr USD channel only; do not silently alter direct EUR prices or current main releases.

## Proposed volume-based Fiverr USD prices

| Analyzed record volume | Full Assessment (one time) | Validation (one time) | Monitoring (per 30-day service period) |
|---|---:|---:|---:|
| Micro 0–100,000 | 349 | 179 | 279 |
| Small 100,001–250,000 | 449 | 249 | 399 |
| Medium 250,001–1,000,000 | 699 | 399 | 649 |
| Large 1,000,001–5,000,000 | 1199 | 649 | 999 |
| Enterprise 5,000,001–20,000,000 | 1999 | 999 | 1599 |
| Custom >20,000,000 | quote | quote | quote |

Count distinct records **actually analyzed** once per completed scan; do not multiply by the number of checks, and do not infer final tier solely from buyer self-report. Before purchase, quote a tier estimated from customer evidence; define bounded discrepancy handling and consent to custom order before extra charges or a scope change. Never silently downgrade a purchased order.

## Service boundaries (proposed; technical acceptance outstanding)

- All products run the same governed full-depth DeepScan engine (199 configured checks, actual coverage evidence subject to BC27 acceptance); Free entry has aggregate-only report and one initial scan per new tenant.
- Full Assessment unlocks **the same qualifying initial scan**, no extra scan, 14 days of scoped Full report detail for new Access-v2 grants; immutable report/archive access remains governed after expiry.
- Validation is a follow-up to a paid Full baseline; exactly one authorized new DeepScan after remediation and a report **only when comparable immutable source identity exists**. Proposed package also includes 14-day renewal of Full access; this bundling must be explicitly approved and tested before customer offer.
- Monitoring is a **mandatory initial Fiverr launch Gig**, with a proposed scope of **one governed new DeepScan and one report delivery per paid 30-day period per licensed BC company**; no unlimited scans, no implicit multi-company access, no unmanaged support or automatic BC data correction. Actual per-period grant/scan usage, cancellation, retry, history and eligible Fiverr recurring checkout must be verified prior to offer. If Fiverr subscription eligibility is missing, use explicit permitted Fiverr Custom Offers/manual repeat orders, without advertising automatic subscription billing.
- Scope supports reports and prioritized recommendations, not included data cleanup, ERP implementation, financial certification, guarantee of recoverable savings, or unlimited consulting. Price matrix excludes a separately priced renewal-only option and multi-company license. Historical Quick/7-day purchases protected while compatibility assessed.

## Evidence and competitor anchors (checked 2026-11-12)

- Fiverr Help Center: freelancers receive 80% of completed order amount; use 20% marketplace retention for model, not final after-tax income: https://help.fiverr.com/hc/en-us/articles/9234443621137-Your-earnings-page
- Fiverr subscription eligibility is conditional and recurrence terms depend on eligible account/category: https://help.fiverr.com/hc/en-us/articles/33272731177105-Subscription-orders-for-freelancers
- Sample CRM data health listing: basic $75 / fuller audit $400, not a direct BC-native or automated equivalent: https://www.fiverr.com/sanderver/audit-your-crm-and-deliver-a-clear-action-plan
- BC consultation $50/h and BC implementation $2500 list prices are weak category anchors, not like-for-like sales or proof of volume: https://www.fiverr.com/rahulchaddha27/be-your-business-central-expert and https://www.fiverr.com/d365zone/microsoft-dynamics-365-business-central-implementation

## Economic planning model – not measured operations

Assume seller retention = 80%, internal opportunity cost **$55 per active support/onboarding hour**, variable processing/infrastructure reserve by tier, and exclude taxes, ads, currency conversion, chargebacks, legal/accounting overhead and shared development cost. Use as planning scenarios, **not proven margins**.

| Tier | Modeled Full manual hours | Full variable reserve USD | Full contribution after 20% Fiverr, hours and reserve USD |
|---|---:|---:|---:|
| Micro | 1.5 | 10 | 186.70 |
| Small | 2.0 | 15 | 234.20 |
| Medium | 3.0 | 30 | 364.20 |
| Large | 5.0 | 60 | 624.20 |
| Enterprise | 8.0 | 120 | 1039.20 |

Formula: `contribution = USD_price*0.8 - hours*55 - variable_reserve`. These reserves/hours are sensitivities to validate with actual scans, not observed costs.

## Mandatory approval and release gates

1. Approve proposed USD amounts, number of eligible BC companies, the tier metric, actual Fiverr category/package editor limits, and explicit monthly Monitoring deliverable/cadence. Validate whether a buyer can use native Fiverr Subscription at all.
2. Approve Validation price bundling (single new scan plus 14d renewal) and standalone renewal pricing/overlap policy; do not infer authorization from the price table.
3. Approve possible market/tax/FX/fee exposure and refund/overage policy; prices here are **USD** and not equivalent EUR values.
4. Produce a versioned normative Product System decision; then make generated Core/operator, Buyer Kit #165 and DE/EN website #166 projections consistent. Keep old customer entitlements and historic purchases.
5. Verify BC27 real scan count, non-SUPER, Full/Validation/Monitoring E2E, report scopes, payment/grant, refunds, cancellation and tenant/company isolation.
6. Run source/CI regressions and operator Marketplace/visual/legal QA. Do not mark tracker 4.01 technical or live gates PASS by this candidate.

**Release disposition:** Price proposal ready for commercial review; Access-v2 normative approval OPEN; technical/DEV acceptance OPEN; Fiverr GO-LIVE NO_GO. No main/staging/PROD writes or deployments.


## 2026-11-12 Owner pricing approval + discount policy direction (ACV2-2026-11-12-P2)

**Commercial decision:** Product owner adopts the six-tier Fiverr USD Full/Validation/Monitoring list-price matrix **above as the intended standard list prices**. This replaces the pending *price amounts* signoff in the original proposal. The previous "PROPOSED" document status refers to the technical/normative release, Fiverr publication, eligibility, cadence, and remaining contract decisions; it no longer indicates that the list amounts themselves are awaiting owner approval. **Do not interpret the price approval as implementation, a Product System contract version bump, a complete Monitoring service contract, or Fiverr offer publication.**

**New commercial requirement:** Seller must be able to grant individually negotiated early-customer discounts below standard list price; discounts should later be controlled in the BCSentinel Admin Backend and displayed as approved promotional offers on the landing page and, where supported by Fiverr's own tools, on Fiverr. The system **cannot** change Fiverr's price/discount/checkout state merely by displaying a discount in BCSentinel.

### Proposed discount architecture — implementation not yet authorized or accepted

- Separate `list_price_usd`, `discount_type` (percentage / fixed amount / negotiated fixed final price), `discount_value`, `eligible_product`, `eligible_tier`, `sales_channel`, `customer_reference`, `campaign_id`, validity window, per-customer/order limits, `requires_approval`, `fiverr_promotion_reference`, `actual_fiverr_order_amount_usd` and immutable application/audit record. Track `pricing_contract_version` and policy revision on orders.
- Seller-controlled **first-customer launch campaign**, **one-to-one custom offer**, and **Monitoring introductory period** are separate intents. Any non-default rate for an existing Monitoring subscription must have an explicit end-of-discount and renewal-price rule. No silent perpetual discount or post-purchase price mutation.
- Suggested *future* Admin-Backend guardrails (not business-authorized discount percentages): standard approval up to 20% discount; >20% requires explicit elevated confirmation; nonnegative effective price, minimum contribution/price warnings, expiry, uses, authorization, CSRF, audit and idempotency. No discounts stack unless a separately approved rule explicitly changes this.
- Site rendering can show `standard $349 / eligible promotional $314.10` with start/end, eligible tier, channel and material conditions; **never promise a Fiverr checkout discount that has not been created and confirmed on Fiverr**. A campaign CTA may point to the appropriate published Gig or invite the customer to request an on-platform Custom Offer, without suggesting off-platform Fiverr payment.
- **Fiverr marketplace authority:** Fiverr's own Seller Plus first-time client promotions may offer 5% or 10% if account eligible; Fiverr-specific coupons (up to 30% where eligible) and personalized Custom Offers have provider eligibility and nonstacking rules. Coupons do not apply after the original order was paid. For first-time buyers, a discounted Custom Offer or permitted coupon attached to a Custom Offer may be appropriate; **verify eligibility in the seller account before advertising.** Do not assume an external app can programmatically create Fiverr promotions or change checkout prices. On confirmed payment, operator verifies exact final order value and terms; only then grant entitlements.
- Discounts reduce seller earnings: with a 20% Fiverr fee assumption, seller revenue is `0.80 * discounted_fiverr_order_amount`, not `0.80 * list_price`. Preserve platform fee, tax, currency and operational cost assumptions separately.
- Customer-specific discounts must not be publicly visible unless intentionally published. Never put customer identities or private coupon tokens into public frontend JSON. Prevent unauthorized price overrides and tenant/company cross-contamination.

**Verified Fiverr policy references (read 2026-11-12):**
- https://help.fiverr.com/hc/en-us/articles/5244747923985-Growth-Tools-for-Seller-Plus
- https://help.fiverr.com/hc/en-us/articles/360049448134-Coupons-promo-codes-and-discounts

### Cross-sprint acceptance dependencies

- **4.01:** USD list matrix owner-approved, discount policy scoped. **Still open** until versioned normative Product System change, compatibility, final Monitoring/bundling terms, CI and channel parity.
- **4.02–4.06:** Freeze grants based on verified paid order and entitled product, not marketing-struck-through price. Operator must store list, discount, final Fiverr amount, external order ID and application audit; refunds on *actual* order value, no extra scans.
- **6.02:** Landingpage DE/EN promotional badge/strike-through only on a verified eligible promotion; default shows approved list prices; no fake countdown or unsupported coupon application.
- **7.03:** Seller Buyer Kit states Fiverr payment/discount as authoritative and customer-facing qualification, limited offer/expiry, Custom Offer and post-expiry terms.
- **3.04 / Monitoring:** discounted initial recurring period explicitly distinct from future periods; verify provider-native subscription capability and provider terms before advertising automatic renewal.

**No discount campaign active. No Admin functionality implemented by this document. No Fiverr coupons, promotions, Custom Offers, list-price changes, runtime entitlement changes, main/staging merges, or deployments were performed.**
