# S04 Customer UX — Automated QA

Status: **AUTOMATED PRE-RUNTIME QA IMPLEMENTED**

## Scope

This evidence covers repository-level customer UX quality that can be verified without a real Business Central tenant.

## Automated checks

### Localization and encoding

- DE and EN dashboard translation files must expose the same keys.
- Dashboard template, JavaScript fallback copy, translation JSON and Executive Report template must be UTF-8 clean.
- Known mojibake markers fail the test.
- The German JavaScript fallback copy was repaired so translation-load failure no longer exposes broken umlauts.

### Responsive and theme contracts

- viewport meta contract exists;
- dashboard exposes DE/EN language selector;
- dashboard exposes dark-mode control;
- CSS contains dark-mode styling;
- responsive breakpoints exist for tablet/mobile layouts.

### Customer-visible states

The shell has explicit hooks for:

- loading;
- global notifications;
- locked analytics;
- locked issue details;
- locked reports;
- empty issue-detail state.

These checks prove that the UI contracts exist; they do not replace visual acceptance of every state.

### Executive Report

Existing automated report evidence already covers:

- HTML and PDF generation;
- Playwright/Chromium rendering path;
- large currency values;
- empty result state;
- missing optional metadata;
- German and English exception disclosure;
- tenant isolation and share-link constraints.

The S04 contract additionally requires the two-page report structure and responsive viewport contract.

## Deliberately open

Manual / runtime acceptance remains required for:

1. real tenant DE/EN visual inspection;
2. dark/light visual comparison;
3. mobile/tablet/desktop customer acceptance;
4. real loading/error/locked flows against live API behavior;
5. visual Executive PDF acceptance with a real BC scan;
6. remediation/correction UX recheck in BC.

No manual PASS is inferred from this automated QA.
