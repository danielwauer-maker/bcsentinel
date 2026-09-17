# EXT-50-12C.2 — Runtime detection reconciliation

## 1. Executive summary

**READY_FOR_EXT_50_12C_REPAIR. LARGE remains BLOCKED.** No product fix, merge, deployment, generator execution, cleanup or BC data mutation was performed.

The supplied real BC SaaS export establishes 95 persisted findings with 95 different Check-IDs, 224,999 check occurrences, EUR 2,202,021.49 estimated annual loss and EUR 1,541,415.04 potential saving. All 95 amounts replay exactly with current backend default definitions. All ten module scores reconstruct from findings; the seven-module weighted score is 38. All four intended scenarios reconcile: 2,000/2,000 generated matches, plus 53 non-owned matches. These are no longer merely static coverage claims.

The backend's last-per-Check-ID projection is a confirmed defect under duplicate groups, reproduced through the actual API, isolated test persistence and dashboard API. **This DEV export has no duplicate Check-ID and does not exhibit that loss.** No live backend export/deployment SHA was supplied, so expected persistence from source is distinguished from directly observed BC persistence.

The former claim of three excess runtime checks is withdrawn: `RunChecks` replaces its local counter with `GetExpectedChecksCount`. The actual 165 is correct. Historical 12C/12C.1 reports are retained; this report supersedes their runtime-unavailable, unexplained-score and runtime-check-count conclusions.

## 2. Runtime environment

Company BCS-PERF-DEV, BC27 SaaS Sandbox (user environment and diagnostic sandbox guards), BCSentinel 1.0.2.21, generator 1.0.0.1. Generator run 1, DEV, seed 5001, error rate 10%, 6,000 Customers + 2,000 Vendors + 12,000 Items; these generator counters/configuration were required by the read-only exporter, not all serialized independently in its context.

Scan `RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B`, BC entry 1. Start 2026-09-16T16:31:22.217Z, finish 16:39:44.443Z: **502.226 seconds**. Export 22:26:49.798Z. Status/synchronization ordinal 2 correspond to the completed/synchronized user observation. This is not a new scan or a performance extrapolation. 20,000 / 502.226 = 39.823 business records/s is only normalization, not the number of actual table reads.

## 3. Evidence provenance and SHA256

Original user download: `BCSentinel-DEV-Run1-evidence.json` (53,155 bytes). Byte-preserving versioned copy: [raw evidence](../quality/release/ext-50-12c-dev-run1-evidence.json).

SHA256: **4914706b1f8d259a0c46e4002a7dda20ac347be08b5bee5c46226504e4ba179f**.

Privacy review before copying inspected every field class and string value: no tokens, credentials, tenant binding identifiers, URLs, contact contents, customer/vendor/item identifiers or personal names. Row titles equal technical Check-IDs. Included company/scan identifiers, entry numbers, version strings, counts and amounts are authorized technical QA evidence. No redaction was needed. `.gitattributes` disables text conversion for this file. The hash proves byte identity, not cryptographic attestation of the SaaS instance.

Exporter code: `bc-diagnostics/src/BCREvidenceExport.Codeunit.al`. It reads persisted findings plus **current** owned-field/exception observations; this is not an immutable per-record scan-time snapshot. The direct ownership observations report zero changed/missing records. Other checks have no owned/non-owned membership export.

Replay (run Python using the repository backend venv; no credentials or network):

```powershell
backend\.venv\Scripts\python.exe scripts/reconcile_ext_50_12c.py --authoritative-runtime --input quality/release/ext-50-12c-dev-run1-evidence.json --output .build/replayed-dev-evidence.json
```

Use the original checkout's backend venv absolute path when running from the audit worktree. [Machine-readable result](../quality/release/ext-50-12c-runtime-reconciled.json) includes every row's predicate, source procedure, attribution boundary, pricing parameters and verdict. [Closed structural schema](../quality/release/ext-50-12c-export-schema.json) rejects unknown/missing keys/types. CLI checks the raw hash; semantic mutation tests independently reject changed totals, scores and attribution. The old user-reported-only tool mode remains BLOCKED and cannot silently become runtime evidence.

Source baseline: integration `867b1f7cef5f20064a5f61655e1e00edf3d24dd3`; preceding audit commit `c8fff0b4b8673f16bb74a5a58920e7042b128128`. Generator source snapshot pins PR38 `89faeb721ed5488ee97c07a620c5184deba6f2e8`. Product source has not been edited in this PR. The runner, check catalog, impact service, sync and analytics files also have an empty diff against PR39 head00b7b4ed31b70fd14681f0e3b913337bf29c1f78. The deployed backend revision/settings history remains unavailable; exact replay demonstrates compatibility with defaults, not proof no overrides were configured.

## 4. Generator reconciliation

| Scenario | Generated / owned matching | Non-owned matching | BC finding count | Missing / modified / excluded |
|---|---:|---:|---:|---:|
| CUSTOMERS_MISSING_EMAIL | 600 / 600 | 1 | 601 | 0 / 0 / 0 |
| VENDORS_MISSING_PHONE | 200 / 200 | 8 | 208 | 0 / 0 / 0 |
| ITEMS_WITHOUT_UNIT_PRICE | 600 / 600 | 30 | 630 | 0 / 0 / 0 |
| ITEMS_WITHOUT_UNIT_COST | 600 / 600 | 14 | 614 | 0 / 0 / 0 |
| Total | 2,000 / 2,000 | 53 | 2,053 | 0 / 0 / 0 |

Four exact aggregate equations reconcile with current unchanged owned fields and source predicates. Deterministic generation reconstructs 600/200/600/600 from seed/rate; runtime detection coverage is **100% for these four targeted scenarios**. This is not 100% coverage of 199 product checks. “Non-owned” means not owned by generator run 1; it does not prove that every such record originated in CRONUS. The company was copied from CRONUS, but provenance of each non-owned record is not exported.

## 5. All 95 findings

Legend used in every row below: **C** = one company-wide count for this Check-ID after predicate/exclusions; no per-record or group key persisted. **D** = direct detection count reconciled (runtime + unchanged owned-field evidence). **A** = row arithmetic/score/default pricing reconciled; predicate membership and record attribution unproven. “?” means unknown, never zero. CRONUS provenance is unproven in every row. No individual row has a confirmed count or amount defect. The table's last column states the correctness boundary/confidence, not a blanket endorsement of each business rule. Technical Check-ID is also the exported check name. Run ID is the common scan above. Full source table/field/filter definitions are linked in the [199-check catalog](EXT_50_12C_PRODUCT_CHECK_CATALOG.md); direct fields are E-Mail/Phone No./Unit Price/Unit Cost on Customer/Vendor/Item.

| Entry | Check-ID | Module | Severity | Count | EUR impact | Generated | Non-owned / CRONUS | Aggregation | Correctness / evidence; row defect |
|---:|---|---|---|---:|---:|---:|---|---|---|
| 1 | GL_ENTRIES_MISSING_DIM1 | System | medium | 3,936 | 31,488.00 | ? | ? / ? | C | A; none proven |
| 2 | GL_ENTRIES_MISSING_DIM2 | System | medium | 1,692 | 13,536.00 | ? | ? / ? | C | A; none proven |
| 3 | GL_ENTRIES_MISSING_BOTH_DIMS | System | critical | 1,634 | 13,072.00 | ? | ? / ? | C | A; none proven |
| 4 | GL_ACCOUNTS_NO_DIRECT_POSTING_BUT_USED | System | medium | 2 | 64.00 | ? | ? / ? | C | A; none proven |
| 5 | SYSTEM_ITEMS_MISSING_INVENTORY_POSTING | System | high | 8 | 256.00 | ? | ? / ? | C | A; none proven |
| 6 | CUSTOMERS_MISSING_ADDRESS | Finance | high | 1 | 11.20 | ? | ? / ? | C | A; none proven |
| 7 | CUSTOMERS_MISSING_CITY | Finance | medium | 1 | 5.33 | ? | ? / ? | C | A; none proven |
| 8 | CUSTOMERS_MISSING_POST_CODE | Finance | medium | 1 | 5.33 | ? | ? / ? | C | A; none proven |
| 9 | CUSTOMERS_MISSING_EMAIL | Finance | medium | 601 | 4,327.20 | 600 | 1 / ? | C | D; none proven |
| 10 | CUSTOMERS_MISSING_PHONE | Finance | low | 6 | 19.20 | ? | ? / ? | C | A; none proven |
| 11 | CUSTOMERS_MISSING_PAYMENT_METHOD | Finance | medium | 5 | 84.00 | ? | ? / ? | C | A; none proven |
| 12 | CUSTOMERS_MISSING_CREDIT_LIMIT | Finance | low | 6 | 48.00 | ? | ? / ? | C | A; none proven |
| 13 | VENDORS_MISSING_ADDRESS | Finance | high | 2 | 22.40 | ? | ? / ? | C | A; none proven |
| 14 | VENDORS_MISSING_CITY | Finance | medium | 3 | 16.00 | ? | ? / ? | C | A; none proven |
| 15 | VENDORS_MISSING_POST_CODE | Finance | medium | 2 | 10.67 | ? | ? / ? | C | A; none proven |
| 16 | VENDORS_MISSING_EMAIL | Finance | medium | 3 | 21.60 | ? | ? / ? | C | A; none proven |
| 17 | VENDORS_MISSING_PHONE | Finance | low | 208 | 665.60 | 200 | 8 / ? | C | D; none proven |
| 18 | VENDORS_MISSING_PAYMENT_TERMS | Finance | high | 1 | 21.60 | ? | ? / ? | C | A; none proven |
| 19 | VENDORS_MISSING_PAYMENT_METHOD | Finance | medium | 7 | 109.76 | ? | ? / ? | C | A; none proven |
| 20 | VENDORS_MISSING_BANK_ACCOUNT | Finance | medium | 2,008 | 106,022.40 | ? | ? / ? | C | A; none proven |
| 21 | CUSTOMER_LEDGER_OVERDUE_30 | Finance | high | 13 | 582.40 | ? | ? / ? | C | A; none proven |
| 22 | VENDOR_LEDGER_OVERDUE_30 | Finance | medium | 21 | 940.80 | ? | ? / ? | C | A; none proven |
| 23 | CUSTOMERS_MISSING_VAT_REG_NO | Finance | medium | 6,001 | 288,048.00 | ? | ? / ? | C | A; none proven |
| 24 | CUSTOMERS_MISSING_SALESPERSON | Finance | low | 6,001 | 48,008.00 | ? | ? / ? | C | A; none proven |
| 25 | CUSTOMERS_MISSING_PRICE_GROUP | Finance | medium | 6,006 | 48,048.00 | ? | ? / ? | C | A; none proven |
| 26 | CUSTOMERS_MISSING_DISC_GROUP | Finance | medium | 6,006 | 48,048.00 | ? | ? / ? | C | A; none proven |
| 27 | CUSTOMERS_MISSING_REMINDER_TERMS | Finance | medium | 6,001 | 48,008.00 | ? | ? / ? | C | A; none proven |
| 28 | CUSTOMERS_MISSING_FIN_CHARGE_TERMS | Finance | low | 6,006 | 48,048.00 | ? | ? / ? | C | A; none proven |
| 29 | CUSTOMERS_MISSING_CONTACT | Finance | low | 6,001 | 48,008.00 | ? | ? / ? | C | A; none proven |
| 30 | CUSTOMERS_MISSING_HOME_PAGE | Finance | low | 6,006 | 48,048.00 | ? | ? / ? | C | A; none proven |
| 31 | VENDORS_MISSING_VAT_REG_NO | Finance | medium | 2,003 | 16,024.00 | ? | ? / ? | C | A; none proven |
| 32 | VENDORS_MISSING_PURCHASER | Finance | low | 2,008 | 16,064.00 | ? | ? / ? | C | A; none proven |
| 33 | VENDORS_MISSING_CONTACT | Finance | low | 2,003 | 16,024.00 | ? | ? / ? | C | A; none proven |
| 34 | VENDORS_MISSING_HOME_PAGE | Finance | low | 2,008 | 16,064.00 | ? | ? / ? | C | A; none proven |
| 35 | CUSTOMER_LEDGER_OVERDUE_60 | Finance | high | 13 | 104.00 | ? | ? / ? | C | A; none proven |
| 36 | CUSTOMER_LEDGER_OVERDUE_90 | Finance | high | 13 | 104.00 | ? | ? / ? | C | A; none proven |
| 37 | VENDOR_LEDGER_OVERDUE_60 | Finance | medium | 21 | 168.00 | ? | ? / ? | C | A; none proven |
| 38 | VENDOR_LEDGER_OVERDUE_90 | Finance | medium | 21 | 168.00 | ? | ? / ? | C | A; none proven |
| 39 | SALES_ORDERS_OLD_OPEN | Sales | medium | 9 | 288.00 | ? | ? / ? | C | A; none proven |
| 40 | SALES_HEADERS_MISSING_PAYMENT_TERMS | Sales | medium | 5 | 160.00 | ? | ? / ? | C | A; none proven |
| 41 | SALES_HEADERS_MISSING_PAYMENT_METHOD | Sales | medium | 9 | 288.00 | ? | ? / ? | C | A; none proven |
| 42 | SALES_HEADERS_MISSING_REQUESTED_DELIVERY_DATE | Sales | medium | 5 | 40.00 | ? | ? / ? | C | A; none proven |
| 43 | SALES_HEADERS_MISSING_SHIPMENT_METHOD | Sales | low | 9 | 72.00 | ? | ? / ? | C | A; none proven |
| 44 | SALES_HEADERS_MISSING_EXTERNAL_DOC_NO | Sales | low | 4 | 32.00 | ? | ? / ? | C | A; none proven |
| 45 | SALES_HEADERS_PAST_REQUESTED_DELIVERY_DATE | Sales | high | 4 | 32.00 | ? | ? / ? | C | A; none proven |
| 46 | SALES_LINES_PRICE_BELOW_UNIT_COST | Sales | critical | 6 | 48.00 | ? | ? / ? | C | A; none proven |
| 47 | SALES_LINES_OUTSTANDING_PAST_SHIPMENT_DATE | Sales | medium | 12 | 96.00 | ? | ? / ? | C | A; none proven |
| 48 | SALES_LINES_MISSING_LOCATION | Sales | medium | 5 | 40.00 | ? | ? / ? | C | A; none proven |
| 49 | PURCHASE_ORDERS_MISSING_EXPECTED_DATE | Purchasing | medium | 9 | 151.20 | ? | ? / ? | C | A; none proven |
| 50 | PURCHASE_ORDERS_OLD_OPEN | Purchasing | medium | 29 | 928.00 | ? | ? / ? | C | A; none proven |
| 51 | PURCHASE_LINES_MISSING_DIMENSIONS | Purchasing | critical | 50 | 500.00 | ? | ? / ? | C | A; none proven |
| 52 | PURCHASE_HEADERS_MISSING_PAYMENT_TERMS | Purchasing | medium | 3 | 96.00 | ? | ? / ? | C | A; none proven |
| 53 | PURCHASE_HEADERS_MISSING_PAYMENT_METHOD | Purchasing | medium | 16 | 512.00 | ? | ? / ? | C | A; none proven |
| 54 | PURCHASE_HEADERS_MISSING_PURCHASER | Purchasing | low | 29 | 232.00 | ? | ? / ? | C | A; none proven |
| 55 | PURCHASE_HEADERS_PAST_EXPECTED_RECEIPT_DATE | Purchasing | high | 20 | 160.00 | ? | ? / ? | C | A; none proven |
| 56 | PURCHASE_LINES_RECEIVED_NOT_INVOICED | Purchasing | medium | 24 | 192.00 | ? | ? / ? | C | A; none proven |
| 57 | PURCHASE_LINES_OUTSTANDING_PAST_RECEIPT_DATE | Purchasing | medium | 28 | 224.00 | ? | ? / ? | C | A; none proven |
| 58 | PURCHASE_LINES_MISSING_LOCATION | Purchasing | medium | 48 | 384.00 | ? | ? / ? | C | A; none proven |
| 59 | PURCHASE_LINES_COST_BELOW_LAST_DIRECT_COST | Purchasing | low | 20 | 160.00 | ? | ? / ? | C | A; none proven |
| 60 | ITEMS_MISSING_CATEGORY | Inventory | medium | 10 | 64.00 | ? | ? / ? | C | A; none proven |
| 61 | ITEMS_MISSING_INVENTORY_POSTING | Inventory | high | 8 | 345.60 | ? | ? / ? | C | A; none proven |
| 62 | ITEMS_WITHOUT_VENDOR_NO | Inventory | medium | 38 | 243.20 | ? | ? / ? | C | A; none proven |
| 63 | ITEMS_WITHOUT_UNIT_COST | Inventory | critical | 614 | 35,366.40 | 600 | 14 / ? | C | D; none proven |
| 64 | ITEMS_WITHOUT_UNIT_PRICE | Inventory | medium | 630 | 42,336.00 | 600 | 30 / ? | C | D; none proven |
| 65 | ITEMS_NEGATIVE_INVENTORY | Inventory | critical | 16 | 1,536.00 | ? | ? / ? | C | A; none proven |
| 66 | ITEMS_PRICE_BELOW_UNIT_COST | Inventory | critical | 2 | 16.00 | ? | ? / ? | C | A; none proven |
| 67 | ITEMS_PRICE_BELOW_STANDARD_COST | Inventory | high | 5 | 40.00 | ? | ? / ? | C | A; none proven |
| 68 | ITEMS_STANDARD_COST_ZERO | Inventory | medium | 12,033 | 96,264.00 | ? | ? / ? | C | A; none proven |
| 69 | ITEMS_LAST_DIRECT_COST_ZERO | Inventory | medium | 12,014 | 96,112.00 | ? | ? / ? | C | A; none proven |
| 70 | ITEMS_MISSING_LEAD_TIME | Inventory | medium | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 71 | ITEMS_SAFETY_STOCK_ZERO | Inventory | low | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 72 | ITEMS_REORDER_POINT_ZERO | Inventory | low | 12,061 | 96,488.00 | ? | ? / ? | C | A; none proven |
| 73 | ITEMS_MAX_INVENTORY_ZERO | Inventory | low | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 74 | ITEMS_MIN_ORDER_QTY_ZERO | Inventory | low | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 75 | ITEMS_ORDER_MULTIPLE_ZERO | Inventory | low | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 76 | ITEMS_MISSING_SHELF_NO | Inventory | low | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 77 | ITEMS_MISSING_TARIFF_NO | Inventory | low | 12,081 | 96,648.00 | ? | ? / ? | C | A; none proven |
| 78 | ITEMS_GROSS_WEIGHT_ZERO | Inventory | low | 12,066 | 96,528.00 | ? | ? / ? | C | A; none proven |
| 79 | ITEMS_NET_WEIGHT_ZERO | Inventory | low | 12,044 | 96,352.00 | ? | ? / ? | C | A; none proven |
| 80 | ITEMS_UNIT_VOLUME_ZERO | Inventory | low | 12,066 | 96,528.00 | ? | ? / ? | C | A; none proven |
| 81 | DEAD_STOCK_90 | Inventory | medium | 41 | 328.00 | ? | ? / ? | C | A; none proven |
| 82 | DEAD_STOCK_180 | Inventory | medium | 38 | 304.00 | ? | ? / ? | C | A; none proven |
| 83 | DEAD_STOCK_365 | Inventory | critical | 34 | 272.00 | ? | ? / ? | C | A; none proven |
| 84 | INVENTORY_WITHOUT_UNIT_COST | Inventory | critical | 1 | 72.80 | ? | ? / ? | C | A; none proven |
| 85 | CONTACTS_MISSING_EMAIL | CRM | medium | 6 | 43.20 | ? | ? / ? | C | A; none proven |
| 86 | CONTACTS_MISSING_PHONE | CRM | low | 26 | 83.20 | ? | ? / ? | C | A; none proven |
| 87 | CONTACTS_MISSING_MOBILE_PHONE | CRM | low | 26 | 83.20 | ? | ? / ? | C | A; none proven |
| 88 | CONTACTS_MISSING_ADDRESS | CRM | low | 3 | 16.00 | ? | ? / ? | C | A; none proven |
| 89 | CONTACTS_MISSING_CITY | CRM | low | 4 | 32.00 | ? | ? / ? | C | A; none proven |
| 90 | CONTACTS_MISSING_POST_CODE | CRM | low | 3 | 16.00 | ? | ? / ? | C | A; none proven |
| 91 | MFG_ROUTING_LINES_ZERO_SETUP | Manufacturing | medium | 3 | 24.00 | ? | ? / ? | C | A; none proven |
| 92 | MFG_ROUTING_LINES_ZERO_RUN | Manufacturing | high | 1 | 8.00 | ? | ? / ? | C | A; none proven |
| 93 | MFG_WORK_CENTERS_ZERO_COST | Manufacturing | medium | 1 | 72.80 | ? | ? / ? | C | A; none proven |
| 94 | MFG_MACHINE_CENTERS_ZERO_COST | Manufacturing | medium | 13 | 946.40 | ? | ? / ? | C | A; none proven |
| 95 | MFG_ITEMS_MISSING_ROUTING_NO | Manufacturing | high | 2 | 16.00 | ? | ? / ? | C | A; none proven |

## 6. Explanation of 224,999

These are **check matches**, not 224,999 unique records or intentional errors. One BC record can contribute to many rules. Distinguish (A) unique BC records, (B) check occurrences, (C) persisted finding rows, (D) each row's affected_count, (E) 2,000 deliberately injected scenarios, (F) naturally matching generated defaults, and (G) pre-existing CRONUS data. Only C/D and the four direct E-attributions are fully measured here.

| Module | Finding rows | Occurrences | EUR impact |
|---|---:|---:|---:|
| System | 5 | 7,272 | 58,416.00 |
| Finance | 33 | 59,007 | 801,897.49 |
| Sales | 10 | 68 | 1,096.00 |
| Purchasing | 11 | 276 | 3,539.20 |
| Inventory | 25 | 158,288 | 1,335,732.00 |
| CRM | 6 | 68 | 273.60 |
| Manufacturing | 5 | 20 | 1,067.20 |
| Service | 0 | 0 | 0.00 |
| Jobs | 0 | 0 | 0.00 |
| HR | 0 | 0 | 0.00 |
| Total | 95 | 224,999 | 2,202,021.49 |

Thirteen near-population-wide item default checks alone contribute **156,851** matches (69.71% of all occurrences). Each tests the named field for blank/zero and applies check-specific exclusions; none requires a particular replenishment method, item type or regulatory relevance. Thus these are valid matches against the implemented predicates, not evidence of thirteen distinct populations. Seven of these each contribute 12,081: lead time, safety stock, maximum inventory, minimum order quantity, order multiple, shelf number and tariff number. Together: **84,567**.

| Item default check | Occurrences | Meaning of predicate / design question |
|---|---:|---|
| ITEMS_STANDARD_COST_ZERO | 12,033 | Zero standard cost; applicability by costing method needs product policy |
| ITEMS_LAST_DIRECT_COST_ZERO | 12,014 | Zero last direct cost; new/unpurchased items can legitimately match |
| ITEMS_MISSING_LEAD_TIME | 12,081 | Blank lead-time formula; applicability to procurement policy not filtered |
| ITEMS_SAFETY_STOCK_ZERO | 12,081 | Zero safety stock; zero can be intentional |
| ITEMS_REORDER_POINT_ZERO | 12,061 | Zero reorder point; replenishment policy not filtered |
| ITEMS_MAX_INVENTORY_ZERO | 12,081 | Zero maximum inventory; replenishment policy not filtered |
| ITEMS_MIN_ORDER_QTY_ZERO | 12,081 | Zero minimum order; may mean no minimum |
| ITEMS_ORDER_MULTIPLE_ZERO | 12,081 | Zero order multiple; may mean no constraint |
| ITEMS_MISSING_SHELF_NO | 12,081 | Blank shelf; storage applicability not filtered |
| ITEMS_MISSING_TARIFF_NO | 12,081 | Blank tariff; cross-border applicability not filtered |
| ITEMS_GROSS_WEIGHT_ZERO | 12,066 | Zero gross weight; logistics applicability not filtered |
| ITEMS_NET_WEIGHT_ZERO | 12,044 | Zero net weight; logistics applicability not filtered |
| ITEMS_UNIT_VOLUME_ZERO | 12,066 | Zero unit volume; logistics applicability not filtered |

The generator leaves these fields at defaults in pinned source. Their large runtime counts are consistent with natural generated-data matches. **Per-check attribution to all 12,000 generated items is LIKELY, not measured by this export.** Calling them accidental generator contamination or defective business rules requires an agreed “clean baseline” contract and applicability policy. Do not change generator or rule thresholds based solely on high counts.

Additional dominant groups are eight customer default checks around 6,000 each, four vendor defaults around 2,000, vendor bank details 2,008, and G/L dimension counts 3,936 / 1,692 / 1,634. The 29 findings with at least 1,000 matches sum to **222,171**; the remaining 66 sum to **2,828**. G/L both-dimension findings and 30/60/90-day overdue rules illustrate intentional overlapping predicates.

Exact disjoint occurrence accounting available: **2,000 direct generated + 53 direct non-owned + 222,946 other unattributed = 224,999**. These are occurrence partitions, not unique-record partitions. Other generated matches, CRONUS baseline and overlap cannot be separately quantified from the present export. The old conditional source estimate 216,000 and residual 8,999 must NOT be upgraded to measured provenance. We have now explained every occurrence by its finding row; the remaining uncertainty concerns membership/origin, not an unexplained arithmetic residual.

Unique affected records cannot be reconstructed. Required future evidence: scan-time company/run + table ID + stable record SystemId membership per check/finding (or suitably scoped irreversible identifiers), exception/applicability snapshot, duplicate-group identity and generator ownership provenance. Then compute distinct (table,SystemId) across findings, with explicit treatment of headers/lines/ledger entries. Design retention/access controls before storing identifiers; do not use personal field values as public aggregation keys. Current drilldowns re-query live data and cannot supply immutable historical membership.

## 7. Impact reconstruction

Current `backend/app/services/impact_service.py`: configured active IssueImpactConfig first, otherwise explicit code definition, otherwise fallback. For each row:

`round(count × minutes_per_occurrence / 60 × probability × frequency_per_year × hourly_rate_eur, 2)`.

Default hourly rate EUR 40; fallback usually 5 minutes × 0.2 × 12 gives EUR 8 per occurrence. The result JSON records all 95 selected parameter sets. Python production code uses binary-float `round(..., 2)` (ties-to-even, subject to float representation), rounds each row and sums/rounds rows. Audit monetary sums use Decimal to avoid accumulating float error. It executes the actual pure pricing functions without importing DB/application configuration. **95/95 replayed row amounts match exactly**, sum EUR 2,202,021.49, equal both persisted run total and exported row total.

Four direct row calculations: email 601 × 7.20 = 4,327.20; phone 208 × 3.20 = 665.60; price 630 × 67.20 = 42,336.00; cost 614 × 57.60 = 35,366.40. Other rules contribute the rest; there is no unexplained euro residual. Formula execution with standard definitions is proven; historical configured definitions/hourly rate are not independently exported.

Saving: 2,202,021.49 × 0.7 = 1,541,415.043 -> **1,541,415.04** (cent rounding). This agrees exactly with the default factor, but the historic settings record itself is not available. Dashboard KPI formatting to zero fraction digits gives **2,202,021 EUR** loss and **1,541,415 EUR** saving; BC/other currency views retain cents. No discrepancy in these display values.

Impact is an additive modeled annual process cost/opportunity across check occurrences. It is not unique-record valuation, actual incurred loss, or verified realized saving. Counts multiply impact; severity/module weights do **not** multiply money (severity may instead be promoted from impact). Overlapping checks intentionally accumulate under current implementation. No duplicate finding rows/Check-IDs exist here, so repeated-group sync loss cannot inflate this scan's amount. Economic double-counting between related checks remains UNPROVEN until the product defines independent/remediable cost components; numerical overlap alone is not an arithmetic defect.

## 8. Score reconstruction

Before sync, `RecalculateScoreMetrics` sums severity penalties (low 1, medium 3, high 6, critical 10) plus affected tiers (0 for zero, 1 for 1–49, 2 for 50–249, 4 for 250–999, 6 for 1,000–4,999, 8 for 5,000+). Base severity comes from each actual AddCountFinding call; ResolveImpactSeverity promotes high on critical-code markers, penalty >=7 with count >=10, or count >=1,000. All reconstructed pre-sync severities equal the exported severities for this scan (no post-sync promotion mismatch).

`module_score = 100 - floor(100 × penalty / (penalty + 40))`.

| Module | Penalty | Score | Weight | Enabled |
|---|---:|---:|---:|---|
| System | 45 | 48 | 15 | yes |
| Finance | 215 | 16 | 20 | yes |
| Sales | 46 | 47 | 15 | yes |
| Purchasing | 51 | 44 | 10 | yes |
| Inventory | 218 | 16 | 15 | yes |
| CRM | 14 | 75 | 5 | yes |
| Manufacturing | 26 | 61 | 10 | yes |
| Service | 0 | 100 | 5 | no |
| Jobs | 0 | 100 | 3 | no |
| HR | 0 | 100 | 2 | no |

Weighted numerator 3,410, active denominator 90; AL `(3410 + (90 div 2)) div 90 = 38`. All ten enabled would give 44, but that contradicts the reported seven-module setup. Export setup is explicitly current, not scan-time: user observation, absent inactive-module findings, 165 checks and all reconstructed scores together support the seven-module history. No score defect demonstrated. Untested inactive modules' 100 is “no penalty” rather than evidence they were scanned successfully.

## 9. Check-count reconstruction

199 registered checks = System 13 + Finance 56 + Sales 21 + Purchasing 20 + Inventory 29 + CRM 9 + Manufacturing 17 + Service 12 + Jobs 10 + HR 12. First seven = **165**. `DH Scan Check Mgt.GetExpectedChecksCount` counts included modules and only restricts individual Enabled flags when Monitoring is active; the free scan therefore uses all checks of the included modules.

`RunSystemConfigurationChecks +=14` vs 13 and `RunInventoryValueChecks +=21` vs 19 are real intermediate source discrepancies, but `RunChecks` finishes with `ChecksCount := ScanCheckMgt.GetExpectedChecksCount(Setup)`. Hence **NOT_A_DEFECT for the persisted/runtime count 165**. Two old strict XFAIL tests stay intact as metadata hygiene observations, not two confirmed customer defects. A new passing test proves final normalization. No checks were disabled to achieve this reconciliation.

## 10. Full sync and aggregation pipeline

1. BC checks count company-wide predicate matches with exceptions. AddCountFinding inserts one row when positive. Duplicate email/VAT/name paths can insert multiple groups separately. Findings persist in DH Deep Scan Finding (53129), run in DH Deep Scan Run (53128). No historical per-record membership/group marker is persisted.
2. BC score metrics sum Finding.Affected Count over all rows. BuildSyncPayload sends every persisted finding in default Entry No. order; no last-by-code collapse there. Free UI may separately group temporary display rows by category/severity, not replace persisted rows.
3. `backend/app/routers/scans.py::sync_scan` authenticates tenant and preserves identity guards. `_calculate_commercials` calculates every incoming issue amount and total first.
4. `list({str(issue['code']): issue for issue in commercials['issues']}.values())` retains the **last value** per code (first insertion order of code keys). Only retained rows populate ScanIssueRecord, which has unique (scan_id,code). Scan.issues_count remains payload count, while commercial total remains pre-projection sum.
5. Response sends the retained issues. BC ApplySyncFindingImpacts filters run + Issue Code and uses **FindFirst**, assigning the last backend group's impact/severity to the first BC row. Other group rows initially retain zero impact. It does not restore the missing group identity.
6. Analytics loads persisted ScanIssueRecords and sums affected_count. It takes estimated_loss from stored scan commercials, independently of that sum. UI formats currency to whole EUR for KPIs; its “Affected records” label does not perform deduplication of record identities.

Deterministic actual endpoint/persistence/dashboard regression: two CUSTOMERS_DUPLICATE_EMAIL groups of 2 and 3, EUR 36 per match -> input 2 rows / 5 occurrences / EUR 180. Last group alone persists: 1 row / 3 occurrences / EUR 108 row amount, but Scan.issues_count=2 and Scan.estimated_loss=180. Dashboard reports 3 and 180. Reversing order keeps 2 / EUR 72 while total stays 180. This proves data loss and payload-order sensitivity without SaaS writes. Existing source tests additionally expose the first-BC-row impact mapping. AL group runtime reproduction is still required before repair release.

**Actual DEV case:** 95 distinct Check-IDs means projection retains all 95, predicted dashboard sum 224,999, total EUR 2,202,021.49; observed dashboard numbers supplied by user agree. A further local test replays all95 real rows through API, test persistence and dashboard:95 rows,224,999 occurrences,EUR2,202,021.49, savingEUR1,541,415.04, score38 and165 checks all pass. This uses a synthetic test tenant/run and is not a downloaded production/backend inventory. Actual backend persisted inventory/API response is not supplied, so this is not claimed as independently downloaded backend evidence. No duplicate-group finding occurs in the 95 rows.

## 11. Dashboard semantics

“Betroffene Datensätze” / “Affected records” plus “Records with action potential” imply distinct records while the implementation sums overlaps. This is a CONFIRMED UX/semantic defect, independent of whether the exact DEV number is mathematically correct.

Recommended DE: **Prüftreffer (Mehrfachzählungen möglich)**. EN: **Check matches (records may be counted more than once)**. Keep “Finding-Zeilen / Finding rows” for 95 and reserve “Eindeutig betroffene Datensätze / Unique affected records” for an actual distinct membership computation. No UI wording was changed in this audit.

## 12. Authoritative prioritized defect backlog

CONFIRMED below means source/repro evidence establishes the mechanism; the evidence column explicitly states whether it occurred in DEV. No security weakness or cross-tenant access is demonstrated by any of these findings. No source business-record corruption is shown; integrity impact concerns diagnostic data/reporting.

| ID | Status / severity | Component and root cause | Evidence / affected behavior | Customer and integrity impact | Security | Recommended repair and mandatory regression | LARGE / pilot / 50-customer gate |
|---|---|---|---|---|---|---|---|
| EXT-50-12C-DEF-001 | CONFIRMED / High | Backend sync/model: last-per-code dict + unique(scan_id,code), after commercial summation | Real API + isolated DB + dashboard tests, both orders; not triggered in DEV (95 unique codes) | Group evidence and occurrence counts lost; count/row/impact totals diverge; unreliable prioritization | No isolation bypass proven; preserve existing identity guards | Decide lossless stable finding/group IDs end-to-end or documented check-level sum with full group detail retained; preserve payload compatibility; PG uniqueness/migration and tenant isolation, order-independent 2+3 groups, retry/idempotency tests | Blocks unrestricted LARGE, customer pilot sign-off, 50 customers; bounded observation-only DEV can continue |
| EXT-50-12C-DEF-002 | CONFIRMED source / High | AL sync response joins only code and FindFirst | Exact ApplySyncFindingImpacts source; existing counterexample test; no multi-group SaaS evidence | Last group's amount/severity mapped to first BC finding; other groups zero/stale; BC row sum may differ from run total | None demonstrated | Repair with DEF-001 identity contract; test two groups with different counts/severities, reorder/retry, each BC row and total; execute in isolated BC QA | Same unrestricted gates blocked pending BC runtime regression |
| EXT-50-12C-DEF-003 | CONFIRMED source / High | Duplicate VAT/name marker searched in Title but InsertFinding stores only Check-ID | Four VAT/name customer/vendor paths; strict XFAIL marker contract; absent in DEV | Nonmatching marker group with k members emits k rows each count k, potentially k² occurrences and repeated impact before backend loss; marker coincidentally contained in title can suppress incorrectly | No cross-tenant issue shown; repair must not export VAT/name as public key | Persist/track safe group identity or group once; exact group-of-2/3, multiple groups, exclusions, repeated/reordered records, AL runtime tests; inspect performance | Blocks unrestricted LARGE/pilot/50-customer gates; runtime validation still required |
| EXT-50-12C-DEF-004 | CONFIRMED / Medium | Dashboard terminology uses records for sum of check matches | Actual DEV224,999=sum95 counts; analytics.py labels/aggregation | Misleading scale/ROI interpretation; no source-record loss | None | Change DE/EN labels/helpers together, tooltips/API documentation; assert no unique-count claim; localization and visual regression | Blocks presentation/acceptance gate for LARGE/pilot/50 customers, not technical generation |
| EXT-50-12C-DEF-005 | NOT_A_DEFECT (runtime); Low source hygiene | Two intermediate counter discrepancies superseded by catalog normalization | 165 catalog + real run165 + final assignment | No persisted count/score effect demonstrated | None | Optional remove redundant drift later; preserve final catalog count and seven/ten-module tests | No gate blocker |
| EXT-50-12C-DEF-006 | LIKELY design limitation; severity not assigned as confirmed defect | Generated defaults trigger broad optional-field checks | Pinned generator defaults +13 large item findings; no ownership split for these checks | Synthetic workload is not a clean baseline for all199 checks; business applicability uncertain | None shown | Agree clean-baseline scope; read-only membership/exception evidence and applicability cases; keep deterministic intentional scenarios | Evidence/design question; not a proven independent defect blocker |
| EXT-50-12C-DEF-007 | UNPROVEN economic overlap; NOT_A_DEFECT arithmetic | Additive annual impact across related rules |95/95 defaults replay; no duplicated code here | Same remediation may remove several estimated costs; no proof of actual realized loss | None shown | Define cost-component overlap policy, sensitivity/documentation; test chosen model separately | Requires product sign-off for ROI promises; no numerical bug established |

## 13. Unproven questions and limits

No exact unique affected-record count; no immutable membership for91 nondirect checks; no exact CRONUS/non-generated split; no complete archived backend row/config/deployment export; no history of module/check selection; no multi-group BC SaaS reproduction. These gaps do not prevent targeted repair planning for confirmed mechanisms. They do prevent claims that all check semantics are validated, all backend rows were independently observed, or all product gates passed.

Runtime exports for these optional follow-ups must remain read-only. Existing raw evidence is sufficient to proceed with repairs; another generator run or cleanup is neither requested nor necessary. Do not reinterpret synthetic endpoint tests as BC SaaS execution.

## 14. Generator verdict

| Dimension | Verdict |
|---|---|
| Deterministic generation | PASS source oracle, pinned seed/rate distribution |
| Target counts | PASS20,000 runtime context/counters guarded by diagnostic; no fresh full master-table inventory exported |
| Four intentional scenarios | PASS600/200/600/600 owned observations, no missing/modified/excluded targets |
| Detection of those scenarios | PASS2,000/2,000, exact baseline-adjusted finding counts |
| Defaults / collateral matches | Observed broad findings consistent with defaults; exact generated contribution beyond four UNPROVEN; not a targeted injection failure |
| Cleanup safety | Separate gate, no cleanup executed or newly validated |
| LARGE readiness | BLOCKED; generator accuracy is not release readiness |

## 15. LARGE gate

No LARGE authorization. Resolve DEF-001–004 at their stated integrity/presentation gates and prove grouped AL/backend behavior, permissions, copied-company recovery integration, ownership-safe cleanup and performance separately. Preserve these20,000 business records. No forecast from a single DEV duration substitutes for a LARGE trial gate. PR38/39 remain separate and unmodified; no merge performed.

## 16. Pilot implications and verification

Controlled evidence gathering can continue read-only. Unrestricted customer pilot/50-customer readiness cannot be signed off while confirmed reporting-integrity defects and existing CI/recovery/permission/cleanup gates remain open. The real DEV targeted-detection test itself passes.

Current-run test/CI results are recorded in `quality/release/ext-50-12c-2-verification.json`; local JUnit/log files are under `.build/` and CI logs/artifacts under the linked GitHub runs. Existing tests were not removed, weakened or reclassified as runtime passes. Three historical strict XFAILs remain (two intermediate counters, one group marker). PostgreSQL-specific execution is not substituted with SQLite: ordinary API characterization uses the repository's existing isolated test fixture; PG constraints/concurrency still require the dedicated PG CI gate.

## 17. Recommended next repair sequence

**EXT-50-12C.3 — Lossless Finding Identity, Group Aggregation and Honest Metrics.** First define immutable finding/group identity and backwards-compatible sync aggregation jointly for DEF-001/002, including PG migration/upgrade/downgrade evidence if schema changes. Then fix DEF-003 grouping/marker behavior with isolated AL runtime fixtures, exclusions and idempotence. Correct DEF-004 DE/EN terminology and metric documentation. Re-run the preserved real95-row fixture as no-regression evidence plus new grouped fixtures; verify tenant isolation and free/premium visibility unchanged. Obtain BC grouped runtime evidence before repair release.

Handle dated billing-test baseline and AL CI installation diagnosis separately without weakening gates. Keep optional-field applicability/clean generator baseline and economic cost overlap as separately approved product decisions. Do not repair the already-correct165 persisted count. No merge/deploy/BC data mutation is part of this audit.
