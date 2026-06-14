from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.models import LandingpagePageVisibility
from app.services.billing_service import utc_now


@dataclass(frozen=True)
class LandingpagePageDefinition:
    key: str
    label: str
    path: str
    protected: bool = False


LANDINGPAGE_PAGE_DEFINITIONS: tuple[LandingpagePageDefinition, ...] = (
    LandingpagePageDefinition("home", "Home", "/landingpage_neu/index.html", True),
    LandingpagePageDefinition("pricing", "Preise", "/landingpage_neu/pricing.html"),
    LandingpagePageDefinition("about", "Ueber uns", "/landingpage_neu/about.html"),
    LandingpagePageDefinition("trust", "Trust Center", "/landingpage_neu/trust.html"),
    LandingpagePageDefinition("support", "Hilfe & Support", "/landingpage_neu/support.html"),
    LandingpagePageDefinition("contact", "Kontakt", "/landingpage_neu/contact.html"),
    LandingpagePageDefinition("executive_reports", "Executive Reports", "/landingpage_neu/executive-reports.html"),
    LandingpagePageDefinition("why_bcsentinel", "Warum BCSentinel", "/landingpage_neu/why-bcsentinel.html"),
)

LANDINGPAGE_PAGE_KEYS = {page.key for page in LANDINGPAGE_PAGE_DEFINITIONS}
PROTECTED_LANDINGPAGE_PAGE_KEYS = {page.key for page in LANDINGPAGE_PAGE_DEFINITIONS if page.protected}


def ensure_default_landingpage_visibility(db) -> None:
    now = utc_now()
    existing_keys = set(
        db.scalars(select(LandingpagePageVisibility.page_key)).all()
    )
    for page in LANDINGPAGE_PAGE_DEFINITIONS:
        if page.key in existing_keys:
            continue
        db.add(
            LandingpagePageVisibility(
                page_key=page.key,
                is_visible=True,
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
    db.flush()


def list_landingpage_visibility(db) -> list[dict]:
    ensure_default_landingpage_visibility(db)
    rows = {
        row.page_key: row
        for row in db.scalars(select(LandingpagePageVisibility)).all()
    }
    return [
        {
            "page_key": page.key,
            "label": page.label,
            "path": page.path,
            "protected": page.protected,
            "is_visible": bool(rows[page.key].is_visible),
            "updated_at": rows[page.key].updated_at_utc.isoformat()
            if rows[page.key].updated_at_utc
            else None,
        }
        for page in LANDINGPAGE_PAGE_DEFINITIONS
    ]


def update_landingpage_visibility(db, visible_page_keys: set[str]) -> list[dict]:
    unknown = visible_page_keys - LANDINGPAGE_PAGE_KEYS
    if unknown:
        raise ValueError(f"Unknown landingpage page keys: {', '.join(sorted(unknown))}")

    ensure_default_landingpage_visibility(db)
    visible_page_keys = set(visible_page_keys) | PROTECTED_LANDINGPAGE_PAGE_KEYS
    now = utc_now()
    rows = {
        row.page_key: row
        for row in db.scalars(select(LandingpagePageVisibility)).all()
    }
    for page in LANDINGPAGE_PAGE_DEFINITIONS:
        row = rows[page.key]
        next_visible = page.key in visible_page_keys
        if row.is_visible != next_visible:
            row.is_visible = next_visible
            row.updated_at_utc = now
    db.flush()
    return list_landingpage_visibility(db)


def public_landingpage_visibility_payload(db) -> dict:
    rows = list_landingpage_visibility(db)
    return {
        "source": "database",
        "pages": [
            {
                "page_key": row["page_key"],
                "is_visible": row["is_visible"],
            }
            for row in rows
        ],
    }
