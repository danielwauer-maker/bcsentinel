from app.core.settings import settings
from app.main import _public_frontend_origins


def test_dev_origin_is_always_allowed_in_non_prod(monkeypatch):
    monkeypatch.setattr(settings, "ENV", "dev")
    monkeypatch.setattr(settings, "CORS_ALLOW_ORIGINS", "https://some-other-dev.example")

    origins = _public_frontend_origins()

    assert "https://dev.bcsentinel.com" in origins
    assert "https://some-other-dev.example" in origins


def test_prod_does_not_add_dev_origin(monkeypatch):
    monkeypatch.setattr(settings, "ENV", "prod")
    monkeypatch.setattr(settings, "CORS_ALLOW_ORIGINS", "https://bcsentinel.com,https://www.bcsentinel.com")

    origins = _public_frontend_origins()

    assert "https://dev.bcsentinel.com" not in origins
