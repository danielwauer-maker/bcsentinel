# Free-tier hardening F02–F07 — local evidence

Date: 2026-11-16

Scope branch: `codex/free-tier-hardening-f02-f07` (created from `staging`)
Release decision: **NO_GO**

## Implemented source controls

- F02: every Exceptions entry point and the direct remediation exclusion path call the shared fresh Access-v2 `Full Assessment or Monitoring` guard. The exceptions list and exception dialog also guard `OnOpenPage`.
- F03/F04: scan-check bulk operations are guarded in the management codeunit; individual check and module edits validate the same entitlement on the server. The module bulk-operation method is protected at its business-operation boundary. Free users can inspect the pages but cannot mutate selection; a fresh canonical Access-v2 `assessment` offer or `monitoring_access` enables selection. Validation-only access remains blocked.
- F05: the findings pages keep detail data blocked without the fresh entitlement and show the new Full Assessment explanation.
- F06/F07: an exclusive Free state shows `Unlimited – Free`, `In development`, and `Full Assessment required`; entitled Full/Monitoring users retain the actual Access-v2 status display.

No backend API, database migration, deployment, installation, QA extension, or test-data change was made. Euro-impact presentation was not changed.

## Local evidence

| Check | Result |
| --- | --- |
| `backend/.venv/bin/python -m pytest -q backend/tests/test_free_tier_hardening_f02_f07_contract.py` | PASS — 4 passed |
| Contract and Access-v2 regression selection (F02–F07, free access, renewal, fresh snapshot, product model) | PASS — 84 passed |
| `python3 scripts/validate_bc_extension.py` | PASS — 134 AL objects, configured ranges/analyzers |
| `git diff --check` | PASS |
| AL localization audit | NOT PASS — pre-existing unrelated source violations; no violation was added by this change |

## Localization status

The source labels are English, as required by the extension's `TranslationFile` model. The intended German copy is:

> Die detaillierten Datenqualitätsprobleme, Ursachen und Handlungsempfehlungen sind Bestandteil des Full Assessments. Mit einem Full Assessment schalten Sie diese Informationen frei.

The intended Free access values are `Unbegrenzt – Free`, `In Entwicklung`, and `Full Assessment notwendig`.

The generated `.g.xlf`/German target entries cannot be safely hand-authored because their generated identifiers must come from the AL compiler. No BC29 AL compiler or symbols are present in this workspace. Consequently BC29 compilation, generated-XLIFF update, and DE UI rendering are **not verified** and remain acceptance gates.

## Remaining acceptance gates

1. Compile against the intended BC29 symbols and regenerate/review the XLIFF units.
2. In a non-PROD BC29 sandbox, verify direct page access and mutation attempts for Free, Full, and Monitoring users.
3. Verify the Access-v2 canonical product-model parsing and resulting access behavior in a BC29 sandbox.

This is implementation evidence only; it is not a deployment, installation, runtime acceptance, or Go-Live approval.
