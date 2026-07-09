# EXT-04 Scan History

## Scope

EXT-04 improves the Business Central scan history for the first go-live without changing dashboard, portal, scheduler architecture, AI features, or EXT-05 currency handling.

## Changed Objects

- Page 53130 `DH Deep Scan Runs`
  - Adds customer-facing display columns: Scan Type, Result, Rating.
  - Keeps Run ID, Scan Date, Score, Modules, Checks, Issues Count, and Impact in the main list.
  - Keeps the old Headline field hidden from the standard list view.
  - Derives localized display values for scan type, result, and rating.
  - Keeps descending Scan Date sorting.
  - Uses confirmation and success messages for delete actions.
- Codeunit 53124 `DH Deep Scan Mgt.`
  - Marks background scheduled runs with scan mode `monitoring`.
- Codeunit 53100 `DH API Client`
  - Preserves `monitoring` scan mode during backend status updates.
- Codeunit 53127 `DH Deep Scan Runner`
  - Preserves `monitoring` scan mode during runner-side status updates.

## Display Rules

- Quick scan and Data Health Score runs display as Free Scan.
- Runs with scan mode `monitoring` or `scheduled` display as Monitoring Scan.
- Deep, validation, full analysis, and one-time runs display as Validation Scan.
- Unlinked or unclassifiable history entries display as Manual Scan.
- Completed scans display as Completed.
- Failed, cancelled, and error-like statuses display as Failed.

## Checks

- AL compile with project analyzers should be run before release packaging.
- Open BCSentinel Scan History and verify newest scans are shown first.
- Verify existing quick and deep runs still appear.
- Verify Open Scan, Open Issues, Open Scan Monitor, Refresh, Reconcile Scan History, and delete actions still work.
- Verify delete confirmations appear for single and multi-select deletion.

## Follow-Up

- EXT-05: complete currency-aware amount display and formatting.
- EXT-03: complete broader language cleanup across setup, monitor, dashboard, issue lists, and backend-facing messages.
