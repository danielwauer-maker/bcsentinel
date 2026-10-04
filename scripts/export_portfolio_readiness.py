#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "quality" / "portfolio-readiness-evidence.json"


def read_text(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        raise SystemExit(f"Missing evidence source: {path}")
    return target.read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read_text(path))


def contains(path: str, pattern: str) -> bool:
    return re.search(pattern, read_text(path), flags=re.IGNORECASE) is not None


def build() -> dict:
    fresh = read_json("quality/release/ext-50-02-fresh-installation-evidence.json")
    upgrade = read_json("quality/release/ext-50-03-upgrade-evidence.json")
    s06 = read_json("quality/release/s06-release-readiness.json")

    facts = {
        "s02_pricing_checkout_truth_audit": {
            "complete": contains(
                "docs/product/S02_PRICING_CHECKOUT_TRUTH_AUDIT.md",
                r"AUDIT COMPLETE",
            ),
            "evidence": "docs/product/S02_PRICING_CHECKOUT_TRUTH_AUDIT.md",
            "manual_remaining": [
                "pricing/checkout runtime smoke",
                "legacy premium migration closure",
            ],
        },
        "s03_security_lifecycle_automated": {
            "complete": (
                (ROOT / "backend/tests/test_dashboard_security_lifecycle.py").exists()
                and contains(
                    "docs/S03_PILOT_ONBOARDING_PRE_RUNTIME.md",
                    r"Persistent login throttling",
                )
                and contains(
                    "docs/S03_PILOT_ONBOARDING_PRE_RUNTIME.md",
                    r"Password reset",
                )
                and contains(
                    "docs/S03_PILOT_ONBOARDING_PRE_RUNTIME.md",
                    r"Operator lifecycle",
                )
            ),
            "evidence": "docs/S03_PILOT_ONBOARDING_PRE_RUNTIME.md",
            "manual_remaining": [
                "real SMTP delivery and domain validation",
                "real invitation to BC connection to dashboard journey",
                "customer/operator acceptance",
            ],
        },
        "s04_customer_ux_automated_qa": {
            "complete": (
                (ROOT / "backend/tests/test_s04_customer_ux_contract.py").exists()
                and contains(
                    "docs/S04_CUSTOMER_UX_AUTOMATED_QA.md",
                    r"AUTOMATED PRE-RUNTIME QA IMPLEMENTED",
                )
            ),
            "evidence": "docs/S04_CUSTOMER_UX_AUTOMATED_QA.md",
            "manual_remaining": [
                "real tenant DE/EN visual acceptance",
                "dark/light and responsive visual acceptance",
                "live API state acceptance",
                "real BC Executive PDF visual acceptance",
            ],
        },
        "s05_public_claims_audit": {
            "complete": (
                (ROOT / "backend/tests/test_public_claims_contract.py").exists()
                and contains(
                    "docs/go-live/S05_PUBLIC_CLAIMS_AUDIT.md",
                    r"COMPLETE FOR CURRENT LANDING BASELINE",
                )
            ),
            "evidence": "docs/go-live/S05_PUBLIC_CLAIMS_AUDIT.md",
            "manual_remaining": [
                "Design Partner/Pilot page",
                "legal/privacy/contact launch polish",
                "release-time claims re-audit",
            ],
        },
        "s05_trust_page_present_and_guarded": {
            "complete": (
                (ROOT / "landingpage_neu/trust.html").exists()
                and contains(
                    "backend/tests/test_public_claims_contract.py",
                    r"trust\.html",
                )
            ),
            "evidence": "landingpage_neu/trust.html + backend/tests/test_public_claims_contract.py",
            "manual_remaining": [],
        },
        "s06_fresh_installation": {
            "complete": fresh.get("status") == "VERIFIED_WITH_KNOWN_DEFECTS",
            "status": fresh.get("status"),
            "evidence": "quality/release/ext-50-02-fresh-installation-evidence.json",
            "manual_remaining": [],
        },
        "s06_upgrade_data_preservation": {
            "complete": upgrade.get("status") == "PASS_WITH_KNOWN_DEFECTS",
            "status": upgrade.get("status"),
            "evidence": "quality/release/ext-50-03-upgrade-evidence.json",
            "manual_remaining": [],
        },
        "s06_release_readiness_prework": {
            "complete": s06.get("status") == "AUTOMATED_PREWORK_COMPLETE_MANUAL_GATES_OPEN",
            "status": s06.get("status"),
            "evidence": "quality/release/s06-release-readiness.json",
            "manual_remaining": list(s06.get("manual_gates_open", [])),
        },
    }

    return {
        "schema_version": 1,
        "source_repository": "danielwauer-maker/bcsentinel",
        "source_branch": "staging",
        "principle": "Evidence facts only. Portfolio percentages are calculated downstream.",
        "facts": facts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not OUT.exists():
            raise SystemExit("Committed portfolio-readiness evidence snapshot is missing")
        if OUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Committed portfolio-readiness evidence snapshot is out of date")
        return

    OUT.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
