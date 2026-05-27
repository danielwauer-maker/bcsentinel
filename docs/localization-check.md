# BCSentinel Localization Check

BCSentinel uses English (`en-US`) as the AL source language. German (`de-DE`) text is maintained only in XLIFF files under `bc-extension/Translations/`.

## Updating XLIFF Files

1. Ensure `bc-extension/app.json` contains `"TranslationFile"` in `features`.
2. Build/package the AL extension with the AL compiler. The compiler updates the generated source XLF, normally `Translations/BCSentinel.g.xlf`.
3. Copy new or changed `source` units from the generated XLF into `Translations/BCSentinel.de-DE.xlf`.
4. Add a German `target` for every translatable unit and keep `target-language="de-DE"`.
5. Do not edit object IDs, field IDs, API endpoints, or business logic while updating translations.

## Adding New Texts

- Write all AL `Caption`, `ToolTip`, `Label`, `Message`, `Error`, `Confirm`, and dialog source text in English.
- Use `Label` variables for dynamic user-facing messages, especially texts with placeholders such as `%1` and `%2`.
- Do not use `CaptionML`, `ToolTipML`, `OptionCaptionML`, or `AboutTextML`.
- Add or refresh the German translation in `BCSentinel.de-DE.xlf`; do not put German fallback text in AL.

## Release Checklist

- `app.json` includes `"TranslationFile"`.
- No German UI text remains in `.al` files.
- No `CaptionML`, `ToolTipML`, `OptionCaptionML`, or `AboutTextML` exists.
- `BCSentinel.g.xlf` is current after the latest AL build.
- Every unit in `BCSentinel.de-DE.xlf` has a professional German `target`.
- The extension still compiles and no business logic changed.

## Local Audit

Run:

```powershell
& 'C:\Users\Daniel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\check_al_localization.py
```

Useful manual searches:

```powershell
rg -n "[äöüÄÖÜß]" bc-extension/app/src -g "*.al"
rg -n "CaptionML|ToolTipML|OptionCaptionML|AboutTextML" bc-extension/app/src -g "*.al"
rg -n "Caption|ToolTip|Label|Message|Error|Confirm|Dialog|StrSubstNo|InstructionalText|AboutTitle|AboutText" bc-extension/app/src -g "*.al"
```
