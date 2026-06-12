from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

import app.main as app_main
from app.core.settings import validate_settings
from app.db import Base, SessionLocal, engine, ensure_schema_is_migrated, get_required_alembic_revision
from app.routers.reports import _shared_report_url


class DummyRequest:
    base_url = "http://internal.local:8000/"


def test_required_alembic_revision_uses_current_head():
    head = get_required_alembic_revision()

    assert head
    assert head.startswith("00")


def test_schema_check_accepts_current_alembic_head():
    head = get_required_alembic_revision()
    with SessionLocal() as db:
        db.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(255) NOT NULL)"))
        db.execute(text("INSERT INTO alembic_version (version_num) VALUES (:head)"), {"head": head})
        db.commit()

    ensure_schema_is_migrated()


def test_startup_succeeds_with_current_alembic_head_schema():
    head = get_required_alembic_revision()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(255) NOT NULL)"))
        db.execute(text("INSERT INTO alembic_version (version_num) VALUES (:head)"), {"head": head})
        db.commit()

    with TestClient(app_main.app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["checks"]["database"] == "ok"


def test_prod_cors_requires_explicit_origins(settings_state):
    settings_state(
        ENV="prod",
        APP_BASE_URL="https://api.bcsentinel.com",
        CORS_ALLOW_ORIGINS="",
        TENANT_REGISTRATION_INVITE_CODE="pilot-invite",
    )

    with pytest.raises(RuntimeError, match="CORS_ALLOW_ORIGINS is required"):
        validate_settings()


def test_prod_cors_rejects_dev_origin(settings_state):
    settings_state(
        ENV="prod",
        APP_BASE_URL="https://api.bcsentinel.com",
        CORS_ALLOW_ORIGINS="https://bcsentinel.com,https://dev.bcsentinel.com",
        TENANT_REGISTRATION_INVITE_CODE="pilot-invite",
    )

    with pytest.raises(RuntimeError, match="dev origins"):
        validate_settings()


def test_prod_cors_fallback_does_not_include_dev_origin(settings_state):
    settings_state(ENV="prod", CORS_ALLOW_ORIGINS="")

    assert app_main._public_frontend_origins() == [
        "https://www.bcsentinel.com",
        "https://bcsentinel.com",
    ]


def test_share_link_uses_app_base_url_in_prod(settings_state):
    settings_state(ENV="prod", APP_BASE_URL="https://api.bcsentinel.com")

    url = _shared_report_url(DummyRequest(), "scan 1", "html", "token value")

    assert url.startswith("https://api.bcsentinel.com/reports/executive/scan%201/html/shared")
    assert "http://internal.local" not in url
