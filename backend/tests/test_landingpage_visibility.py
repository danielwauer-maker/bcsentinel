import base64

from app.db import SessionLocal
from app.models import AdminAuditEvent, LandingpagePageVisibility
from app.services.landingpage_visibility_service import (
    LANDINGPAGE_PAGE_KEYS,
    list_landingpage_visibility,
    update_landingpage_visibility,
)


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _admin_csrf(client, path: str = "/admin/config/landingpage-pages") -> dict[str, str]:
    response = client.get(path, headers=_admin_auth_header())
    assert response.status_code == 200
    token = client.cookies.get("bcs_csrf")
    assert token
    return {"csrf_token": token}


def test_landingpage_visibility_defaults_to_all_phase_1_pages(db_session):
    rows = list_landingpage_visibility(db_session)

    assert {row["page_key"] for row in rows} == LANDINGPAGE_PAGE_KEYS
    assert all(row["is_visible"] for row in rows)
    assert {row.page_key for row in db_session.query(LandingpagePageVisibility).all()} == LANDINGPAGE_PAGE_KEYS


def test_public_landingpage_visibility_api_returns_page_flags(client):
    response = client.get("/landingpage/pages/visibility")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "database"
    pages = {row["page_key"]: row["is_visible"] for row in payload["pages"]}
    assert pages["home"] is True
    assert pages["pricing"] is True


def test_update_landingpage_visibility_keeps_home_visible(db_session):
    rows = update_landingpage_visibility(db_session, {"pricing"})
    by_key = {row["page_key"]: row for row in rows}

    assert by_key["home"]["is_visible"] is True
    assert by_key["pricing"]["is_visible"] is True
    assert by_key["about"]["is_visible"] is False


def test_admin_landingpage_visibility_update_changes_flags_and_audits(client):
    response = client.post(
        "/admin/config/landingpage-pages",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "visible_pages": ["home", "pricing", "contact"],
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    with SessionLocal() as db:
        rows = {row.page_key: row for row in db.query(LandingpagePageVisibility).all()}
        event = db.query(AdminAuditEvent).filter(
            AdminAuditEvent.action == "config.landingpage_visibility.update"
        ).one()

    assert rows["home"].is_visible is True
    assert rows["pricing"].is_visible is True
    assert rows["contact"].is_visible is True
    assert rows["about"].is_visible is False
    assert event.target_id == "phase_1"
