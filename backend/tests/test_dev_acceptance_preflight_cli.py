"""The standalone DEV acceptance probe is non-mutating and never logs secrets."""
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
from urllib.request import Request

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_dev_bc_acceptance.py"
spec = importlib.util.spec_from_file_location("check_dev_bc_acceptance", SCRIPT)
assert spec and spec.loader
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class _Response:
    status = 200
    def __init__(self, payload: dict):
        self.data = io.BytesIO(json.dumps(payload).encode("utf-8"))
    def __enter__(self):
        return self.data_wrapper()
    def data_wrapper(self):
        return self
    def __exit__(self, *args):
        self.data.close()
    def read(self, *args):
        return self.data.read(*args)


def test_unsafe_url_rejected_before_network():
    for url in ("http://dev-api.bcsentinel.com", "https://user:pass@example.com",
                "https://example.com/?token=123", "https://example.com/#secret"):
        with pytest.raises(ValueError):
            probe._url(url)


def test_probe_sends_tenant_credentials_in_headers_only(monkeypatch):
    captured: dict = {}
    payload = {
        "scan_id": "free-test-001", "preflight_only": True,
        "premium_active": True, "scope_state": "auto",
        "company_bound": True, "eur_currency_verified": True,
    }
    def fake_urlopen(request: Request, timeout: int):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["method"] = request.get_method()
        return _Response(payload)
    monkeypatch.setattr(probe, "urlopen", fake_urlopen)
    result = probe.fetch_preflight(
        "https://dev-api.bcsentinel.com", "tenant-private", "secret-test-token", "free-test-001",
    )
    assert result == payload
    assert captured["method"] == "GET"
    assert captured["url"].endswith("/scans/free-test-001/report-preflight")
    assert "secret-test-token" not in captured["url"]
    assert captured["headers"]["X-api-token"] == "secret-test-token"


def test_probe_requires_scope_and_active_premium():
    ready = dict(
        preflight_only=True, original_free_scan=True,
        scope_state="auto", company_bound=True,
        company_id="11111111-2222-3333-4444-555555555555",
        eur_currency_verified=True, premium_active=True,
        missing_prerequisites=["confirmed_scope_missing"],
    )
    assert probe.evaluate(ready, "11111111-2222-3333-4444-555555555555")[0]
    assert not probe.evaluate(ready, "aaaaaaaa-2222-3333-4444-555555555555")[0]
    ready["premium_active"] = False
    assert not probe.evaluate(ready, None)[0]
    ready["premium_active"] = True
    ready["scope_state"] = "missing"
    assert not probe.evaluate(ready, None)[0]
    ready["scope_state"] = "auto"
    ready["original_free_scan"] = False
    assert not probe.evaluate(ready, None)[0]
