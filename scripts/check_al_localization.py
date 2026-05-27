#!/usr/bin/env python3
"""Audit AL localization hygiene for BCSentinel."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BC_ROOT = REPO_ROOT / "bc-extension"
AL_ROOT = BC_ROOT / "app" / "src"
APP_JSON = BC_ROOT / "app.json"

GERMAN_PATTERN = re.compile(
    r"[äöüÄÖÜß]|\b("
    r"Abrechnung|Adresse|Analyse|Antwort|Artikel|Auftrag|Ausnahme|Beschreibung|"
    r"Bitte|Daten|Datensätze|Debitor|Einkauf|Einstand|Empfehlung|Ergebnis|"
    r"Fehler|Freigabe|Gefunden|Geschäft|Gesperrt|Korrektur|Kreditor|Kunde|"
    r"Lieferant|Mandant|Mitarbeiter|MwSt|Offene|Prüfung|Rabatt|Rechnung|"
    r"Ressource|Sachposten|Scan starten|Stammdaten|USt|Verkauf|Verlust|"
    r"Zahlung|ausgenommen|ergänzen|gefunden|korrigieren|öffnen|pflegen|"
    r"prüfen|wurde"
    r")\b",
    re.IGNORECASE,
)

LOCALIZED_TEXT_LINE = re.compile(
    r"\b(Caption|ToolTip|Label|Message|Error|Confirm|Dialog|StrSubstNo|"
    r"OptionCaption|InstructionalText|AboutTitle|AboutText)\b"
)

ML_PATTERN = re.compile(r"\b(CaptionML|ToolTipML|OptionCaptionML|AboutTextML)\b")


def main() -> int:
    violations: list[str] = []

    if not APP_JSON.exists():
        violations.append(f"{APP_JSON}: missing app.json")
    else:
        app = json.loads(APP_JSON.read_text(encoding="utf-8-sig"))
        features = app.get("features") or []
        if "TranslationFile" not in features:
            violations.append(f"{APP_JSON}: features must include TranslationFile")

    for path in sorted(AL_ROOT.rglob("*.al")):
        rel = path.relative_to(REPO_ROOT)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if ML_PATTERN.search(line):
                violations.append(f"{rel}:{lineno}: ML localization property is not allowed")

            if LOCALIZED_TEXT_LINE.search(line) and GERMAN_PATTERN.search(line):
                violations.append(f"{rel}:{lineno}: German text found in localized AL source")

            if re.search(r"[äöüÄÖÜß]", line):
                violations.append(f"{rel}:{lineno}: German umlaut found in AL source")

    if violations:
        print("AL localization audit failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("AL localization audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
