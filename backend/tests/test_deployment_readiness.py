from __future__ import annotations

import pytest
from pathlib import Path
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


def test_dev_frontend_isolated_from_production_webroot() -> None:
    root = Path(__file__).resolve().parents[2]
    nginx = (root / "config" / "nginx" / "bcsentinel.conf").read_text(encoding="utf-8")
    deploy = (root / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")

    assert "server_name dev.bcsentinel.com;" in nginx
    assert "root /var/www/bcsentinel/landingpage-dev;" in nginx
    assert "proxy_pass http://127.0.0.1:8001;" in nginx
    assert "root /var/www/bcsentinel/landingpage;" in nginx

    # The live DEV site and nginx routing are operator-managed until a
    # separately reviewed, reversible site deployment has been accepted.
    dev_section = deploy.split('      - name: Deploy to DEV', 1)[1].split(
        '      - name: Health check DEV', 1
    )[0]
    assert "Fail-closed DEV checkout safety preflight" in dev_section
    assert "git status --porcelain --untracked-files=all" in dev_section
    assert "git clean -fd" not in dev_section.replace(
        "# Never run git clean: untracked operator files are not deployment artifacts.", ""
    )
    assert "cp config/nginx/bcsentinel.conf" not in dev_section
    assert "rm -rf /var/www/bcsentinel/landingpage-dev" not in dev_section
    assert "sudo -n nginx -t" in dev_section
    assert "nginx_status=validated_unchanged" in dev_section
    assert "landingpage_status=preserved_unchanged" in dev_section
    assert "Smoke check DEV Core web surface" in deploy
    # A staging push must not deploy while branch CI is still running.  Only a
    # manually dispatched workflow for the exact, separately approved SHA can
    # execute DEV-mutating steps.
    approved_dispatch = (
        "github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/staging' "
        "&& inputs.release_sha == github.sha "
        "&& vars.DEV_STAGING_DEPLOY_ENABLED == 'true' "
        "&& vars.DEV_STAGING_RELEASE_SHA == github.sha"
    )
    assert "workflow_dispatch:" in deploy
    assert deploy.count("if: " + approved_dispatch) == 4
    assert "github.event_name == 'push' && github.ref == 'refs/heads/staging'" not in deploy
    assert "git fetch origin" in dev_section
    assert 'git reset --hard "${{ github.sha }}"' in dev_section
    # Fail the rollout if the new app is not ready with its database, even
    # when an old /health endpoint or site happens to return HTTP 200.
    health_section = deploy.split('      - name: Health check DEV', 1)[1].split(
        '      - name: Smoke check DEV Core web surface', 1
    )[0]
    assert "git -C /home/daniel/data-health-management-dev rev-parse HEAD" in health_section
    assert "local_ready=false" in health_section
    assert 'if [ "$local_ready" != true ]; then' in health_section
    assert "http://127.0.0.1:8001/health/ready" in health_section
    assert "https://dev-api.bcsentinel.com/health/ready" in health_section
    assert "exit 1" in health_section

