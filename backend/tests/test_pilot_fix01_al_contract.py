from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension"
XLIFF_NAMESPACE = {"x": "urn:oasis:names:tc:xliff:document:1.2"}


def test_registration_maps_stable_codes_without_raw_response_or_string_replacement():
    source = (AL_ROOT / "app/src/codeunits/DHApiClient.Codeunit.al").read_text(encoding="utf-8")
    for error_code in (
        "REGISTRATION_IDENTITY_CONFLICT",
        "TENANT_MEMBERSHIP_NOT_ALLOWED",
        "TENANT_ACCESS_FORBIDDEN",
        "TENANT_NOT_FOUND",
        "INVALID_REGISTRATION_PAYLOAD",
        "DASHBOARD_USER_DISABLED",
        "TENANT_MEMBERSHIP_DISABLED",
        "REGISTRATION_TEMPORARILY_UNAVAILABLE",
        "REGISTRATION_UNEXPECTED_ERROR",
    ):
        assert f"'{error_code}'" in source
    registration_mapping = source.split("local procedure GetRegistrationErrorMessage", 1)[1].split("procedure EnsureTenantRegistered", 1)[0]
    assert "StrPos(" not in registration_mapping
    assert "ResponseText" not in registration_mapping.split("case ErrorCode", 1)[1]


def test_registration_action_always_recovers_page_state_and_can_retry():
    source = (AL_ROOT / "app/src/pages/DHSetup.Page.al").read_text(encoding="utf-8")
    action = source.split("action(RegisterTenant)", 1)[1].split("action(ResetRegistration)", 1)[0]
    assert "TryRegisterTenantAndRefresh" in action
    assert "GetLastErrorText()" in action
    assert "ClearLastError()" in action
    assert "CurrPage.Update(false)" in action
    assert "BCSentinelTenantRegistrationStartedLbl" not in action
    assert "[TryFunction]" in source


def test_multi_tenant_success_and_error_labels_have_complete_german_targets():
    generated = ElementTree.parse(AL_ROOT / "Translations/BCSentinel.g.xlf")
    german = ElementTree.parse(AL_ROOT / "Translations/BCSentinel.de-DE.xlf")
    generated_units = {
        unit.attrib["id"]: unit.find("x:source", XLIFF_NAMESPACE).text or ""
        for unit in generated.findall(".//x:trans-unit", XLIFF_NAMESPACE)
    }
    german_units = {
        unit.attrib["id"]: (
            unit.find("x:source", XLIFF_NAMESPACE).text or "",
            unit.find("x:target", XLIFF_NAMESPACE).text or "",
        )
        for unit in german.findall(".//x:trans-unit", XLIFF_NAMESPACE)
    }
    required_ids = {
        "Codeunit 3727721143 - NamedType 3256243383",
        "Codeunit 3727721143 - NamedType 287489686",
        "Codeunit 3727721143 - NamedType 3983854201",
        "Codeunit 3727721143 - NamedType 1656882053",
        "Codeunit 3727721143 - NamedType 915500328",
        "Codeunit 3727721143 - NamedType 2456901938",
        "Codeunit 3727721143 - NamedType 2826323179",
        "Codeunit 3727721143 - NamedType 1207520993",
        "Codeunit 3727721143 - NamedType 3518287738",
        "Codeunit 3727721143 - NamedType 800054683",
        "Codeunit 3727721143 - NamedType 3332878286",
        "Page 392523509 - NamedType 3518287738",
    }
    for unit_id in required_ids:
        assert german_units[unit_id][0] == generated_units[unit_id]
        assert german_units[unit_id][1].strip()
