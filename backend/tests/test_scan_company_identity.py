from __future__ import annotations

import pytest

from app.services.scan_company_service import canonical_company_id, canonical_lcy_code

VALID = "11111111-2222-3333-4444-555555555555"


def test_canonical_company_guids_accept_braces_and_case():
    assert canonical_company_id("{" + VALID.upper() + "}") == VALID
    assert canonical_company_id(VALID) == VALID


@pytest.mark.parametrize("value", ["", "contoso", "00000000-0000-0000-0000-000000000000", "not-a-guid"])
def test_invalid_company_guids_fail(value):
    with pytest.raises(ValueError):
        canonical_company_id(value)


@pytest.mark.parametrize("raw,want", [("eur", "EUR"), ("Sek", "SEK"), (" usd ", "USD"), ("CHF", "CHF")])
def test_lcy_codes_normalize(raw, want):
    assert canonical_lcy_code(raw) == want


@pytest.mark.parametrize("raw", ["", "EU", "EURO", "12A", "€UR", "İRL"])
def test_invalid_lcy_codes_fail(raw):
    with pytest.raises(ValueError):
        canonical_lcy_code(raw)
