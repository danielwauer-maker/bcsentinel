from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PILOT_DOCS = ROOT / "docs" / "pilot"

REQUIRED_FILES = {
    "OPERATOR_HANDBOOK_1.0.2.20.md": [
        "## 2. Täglicher Systemcheck",
        "## 3. Onboarding",
        "## 6. Incidentablauf",
        "## 7. Backup und Restore",
        "## 8. Rollback",
        "## 10. Offboarding",
    ],
    "SUPPORT_ESCALATION_PROCESS.md": [
        "## 2. Schweregrade",
        "## 3. Eskalationsweg",
        "## 5. Eskalationsmatrix",
        "## 6. Abschlusskriterien",
    ],
    "KNOWN_LIMITATIONS_1.0.2.20.md": [
        "## Betrieb",
        "## Login und E-Mail",
        "## Dashboard und Report",
        "## Skalierung",
        "## Recht und Kaufmännisches",
    ],
    "PILOT_ONBOARDING_OFFBOARDING_CHECKLIST.md": [
        "## A. Onboarding je Kunde",
        "## B. Sieben-Tage-Nachkontrolle",
        "## C. Offboarding",
    ],
}


def test_required_operator_documents_exist_and_are_not_empty():
    for filename in REQUIRED_FILES:
        path = PILOT_DOCS / filename
        assert path.exists(), f"Missing operator document: {path}"
        assert path.stat().st_size > 500, f"Operator document is unexpectedly small: {path}"


def test_operator_documents_contain_required_sections():
    for filename, headings in REQUIRED_FILES.items():
        content = (PILOT_DOCS / filename).read_text(encoding="utf-8")
        for heading in headings:
            assert heading in content, f"{filename} lacks required section {heading!r}"


def test_operator_package_has_explicit_open_real_world_gates():
    handbook = (PILOT_DOCS / "OPERATOR_HANDBOOK_1.0.2.20.md").read_text(encoding="utf-8")
    limitations = (PILOT_DOCS / "KNOWN_LIMITATIONS_1.0.2.20.md").read_text(encoding="utf-8")
    combined = handbook + "\n" + limitations
    for required_phrase in (
        "realen Restore",
        "Alarm",
        "Rollback",
        "10-Tenant",
        "SPF/DKIM/DMARC",
        "Passwortreset",
    ):
        assert required_phrase.lower() in combined.lower()


def test_onboarding_checklist_covers_customer_lifecycle_controls():
    content = (PILOT_DOCS / "PILOT_ONBOARDING_OFFBOARDING_CHECKLIST.md").read_text(encoding="utf-8")
    for required_phrase in (
        "APP-Artefakt und SHA-256",
        "Tenant-/Company-/Membership-Zuordnung",
        "Dashboardeinladung",
        "Monitoring aktiviert",
        "Known Limitations",
        "Datenexport oder Löschung",
    ):
        assert required_phrase in content
