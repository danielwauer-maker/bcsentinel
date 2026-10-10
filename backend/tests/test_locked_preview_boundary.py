from __future__ import annotations

from app.routers.analytics import _build_locked_preview_findings


def test_locked_preview_exposes_only_aggregate_safe_fields() -> None:
    source = [
        {
            "title": "Customer has missing bank account",
            "group": "CRM",
            "count": 17,
            "impact_eur": 12345.67,
            "recommendation_preview": "Fix the affected records",
            "open_in_bc_url": "https://businesscentral.dynamics.com/private",
            "code": "CUSTOMERS_PRIVATE",
        }
    ]

    preview = _build_locked_preview_findings(source)

    assert preview == [{"group": "CRM", "count": 17}]
    forbidden = {
        "title",
        "impact_eur",
        "recommendation_preview",
        "open_in_bc_url",
        "code",
        "record_identifiers",
        "root_cause",
    }
    assert forbidden.isdisjoint(preview[0])


def test_locked_preview_is_bounded_to_three_aggregate_cards() -> None:
    preview = _build_locked_preview_findings(
        [{"group": f"Area {index}", "count": index} for index in range(1, 6)]
    )
    assert len(preview) == 3
    assert all(set(item) == {"group", "count"} for item in preview)
