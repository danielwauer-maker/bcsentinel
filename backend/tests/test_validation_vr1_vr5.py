from app.services.validation_report_service import (
    BUSINESS_AREAS,
    _business_area_label,
    _normalize_category,
)


def test_vr1_validation_uses_canonical_business_areas():
    assert BUSINESS_AREAS == (
        "Finance",
        "Sales",
        "Purchasing",
        "Inventory",
        "CRM",
        "Manufacturing",
        "Service",
        "Jobs",
        "HR",
        "System",
    )
    assert _normalize_category("purchase", "") == "Purchasing"
    assert _normalize_category("customer", "") == "CRM"
    assert _normalize_category(None, "ITEM_STALE") == "Inventory"
    assert _normalize_category(None, "G_L_LEDGER_GAP") == "Finance"
    assert _normalize_category("unknown", "OTHER") == "System"


def test_vr1_validation_localizes_business_area_labels_without_changing_keys():
    assert _business_area_label("Purchasing", "de") == "Einkauf"
    assert _business_area_label("Inventory", "de") == "Lager & Artikel"
    assert _business_area_label("CRM", "de") == "CRM & Stammdaten"
    assert _business_area_label("Purchasing", "en") == "Purchasing"
