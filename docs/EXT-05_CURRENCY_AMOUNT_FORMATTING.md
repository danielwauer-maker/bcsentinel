# EXT-05 Currency & Amount Formatting

## Goal

EXT-05 makes customer-facing financial values in the Business Central extension currency-aware and consistent for go-live. Visible amount fields no longer use hard-coded EUR captions and are displayed with two decimal places plus the tenant local currency code when Business Central provides one.

## Changed Objects

- Codeunit 53197 `DH Currency Mgt.`
  - Reads the tenant currency from `General Ledger Setup`.`LCY Code`.
  - Formats local amounts with two decimal places.
  - Appends the currency code only when the LCY code is available.
- Page 53130 `DH Deep Scan Runs`
  - Shows `Impact` as formatted amount text, for example `21.908,42 EUR`.
- Page 53126 `DH Scan Issues`
- Page 53121 `DH Issues Part`
- Page 53135 `DH Dashboard Issues`
- Page 53161 `DH Dashboard Issues List`
- Page 53131 `DH Deep Scan Findings`
- Page 53160 `DH Deep Scan Findings List`
  - Show `Impact` with two decimals and local currency code.
- Page 53100 `DH Setup`
  - Shows the last scan amount as `Estimated Impact`.
- Page 53124 `DH Dashboard List`
- Page 53127 `DH Key Metrics Part`
  - Replace visible EUR captions with local-currency-aware amount display.
- Tables `DH Scan Header`, `DH Deep Scan Run`, `DH Scan Issue`, `DH Deep Scan Finding`, and `DH Dashboard Issue`
  - Keep existing field names for upgrade safety.
  - Update captions away from hard-coded EUR terminology.

## Currency Source

The only currency source used in this sprint is Business Central `General Ledger Setup`.`LCY Code`. The UI language is not used to infer a currency.

If the LCY code is empty, the amount is still shown with two decimal places and no currency suffix. No fallback to EUR, USD, or GBP is applied.

## Formatting Logic

`DH Currency Mgt.` formats all local amounts via `FormatLocalAmount(Amount)`:

- rounds to `0.01`
- displays exactly two decimal places
- uses Business Central's current regional formatting
- appends the LCY code when available

Examples:

- German region with LCY `EUR`: `21.908,42 EUR`
- English region with LCY `EUR`: `21,908.42 EUR`
- Empty LCY code: `21.908,42`

## Manual Test Notes

- Open BCSentinel Scan History and verify the `Impact` column shows two decimals and the LCY code.
- Open Scan Issues and dashboard issue lists and verify `Impact` shows two decimals and the LCY code.
- Open Setup and verify the last scan field is labeled `Estimated Impact` and shows the formatted amount.
- Verify no customer-facing BCSentinel amount caption still says `EUR`.
- Verify changing `General Ledger Setup`.`LCY Code` changes the displayed suffix.
- Verify an empty LCY code does not raise an error and displays only the amount.

## Non-Goals

- No destructive data model rename of internal `(... EUR)` fields.
- No backend report-system change.
- No dashboard, landing page, account, role center, AI, or portal redesign.
- No broad EXT-03 language cleanup outside affected amount and currency fields.
