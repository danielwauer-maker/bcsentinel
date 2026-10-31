# BCSentinel Product Access Contract

Status: F0 contract candidate for the Fiverr/Pilot release train

## 1. One scan engine

BCSentinel has one current product scan: the **Deep Scan**.

The historical Quick Scan implementation is legacy compatibility code and is not a separate current product tier. Free Entry, Assessment, Validation and Monitoring must not differ by scan depth. They differ by access rights, lifecycle and repetition.

## 2. Free Entry

A newly registered tenant receives exactly **one initial Free Entry Deep Scan**.

The scan runs the full current Deep Scan engine. Free Entry does not unlock paid detail access.

Free Entry may expose only aggregate/preview information such as:
- Data Health Score
- checks/issues counts
- severity distribution
- risk areas/categories
- impact band/range

Free Entry must not expose:
- detailed finding titles where they reveal protected issue detail
- record-level drilldown
- root causes
- full recommendations/remediation detail
- concrete financial impact values
- paid Executive/Assessment report content

After the initial Free Entry Deep Scan has been consumed, another Deep Scan requires an appropriate paid scan credit or active Monitoring.

## 3. Assessment

Assessment is a one-time product that unlocks full detail access for **7 days**.

When a valid completed Free Entry Deep Scan already exists, activating Assessment should unlock that existing scan; a rescan is not required merely to reveal paid detail.

Assessment access includes the paid finding/detail and Assessment Report views allowed by the current product contract.

Expiry revokes live paid access but does not delete the stored scan or an already delivered/downloaded customer report.

## 4. Validation

Validation is a new measurement after remediation.

A Validation purchase/grant provides the required scan credit for one new Deep Scan and unlocks full Validation detail access for **7 days**.

The Validation result is compared with the relevant prior Assessment/baseline scan. The Validation Report should distinguish resolved, improved, unchanged/regressed and new findings, plus score/business-impact changes where supported by the methodology.

## 5. Monitoring

Monitoring provides ongoing full access while the Monitoring entitlement/subscription is active.

Monitoring permits recurring Deep Scans without requiring an individual one-time scan credit for every run and enables the supported history/trend/monitoring capabilities.

## 6. Sales channel separation

Sales channel and product entitlement are separate concerns.

Examples of acquisition/payment channels include:
- Fiverr
- Malt
- Contra
- Direct/BCSentinel
- AppSource/partner channels

The product entitlement remains one of the canonical BCSentinel products (for example `assessment`, `validation_check`, `monitoring_monthly`, `monitoring_annual`). Channel/source metadata must not create duplicate Fiverr-specific product codes or a separate Fiverr extension.

A Fiverr-sourced Assessment therefore remains `assessment` with channel/source metadata identifying Fiverr. Direct customers may obtain the same entitlement through the normal BCSentinel billing flow.

## 7. Fiverr payment boundary

For Fiverr-sourced customers, BCSentinel must not require or encourage off-platform payment for the Fiverr-origin service. Direct checkout actions should be suppressed or replaced with channel-appropriate guidance when the tenant/order is bound to the Fiverr channel.

This channel-specific presentation must not change the scan engine, report calculation or entitlement semantics.

## 8. Seven-day extension

A short Assessment access extension may be offered as a controlled commercial action. It extends live access to the same Assessment result and does not create a new scan.

Repeated extensions must not become a substitute for Validation or Monitoring. The commercial policy and maximum allowed extension count are defined outside the scan engine.

## 9. Non-negotiable acceptance invariants

1. A fresh registered tenant can run exactly one initial Free Entry Deep Scan without a paid product.
2. The Free Entry scan does not unlock paid issue/report/financial detail.
3. A second Deep Scan is blocked after the Free Entry scan unless an appropriate paid credit or Monitoring is active.
4. Assessment can unlock an existing qualifying scan for 7 days without forcing a new scan.
5. Validation requires a new Deep Scan and grants 7 days of full Validation access.
6. Monitoring permits recurring Deep Scans while active.
7. Expiry removes live paid access but does not delete historical scan data.
8. Sales channel does not alter scan depth or canonical product codes.
9. Tenant isolation and Free/Paid data-boundary enforcement apply to every channel.
