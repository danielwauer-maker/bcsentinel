"""Deployment fail-closed guards and real API smoke behavior; no Docker mutations."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest
from sqlalchemy import text

from app.db import engine

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/deploy_pr41_candidate.py"
spec = importlib.util.spec_from_file_location("pr41_deployment", SCRIPT)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def inventory():
    return {"containers": {"dhm-backend": {"id": "unchanged", "project": "dhm", "ports": "8000"}},
            "volumes": {"dhm_postgres_data": {"id": "original", "project": "dhm"}},
            "networks": {"dhm_default": {"id": "network-original", "project": "dhm"}},
            "listeners": ["127.0.0.1:8000", "127.0.0.1:8001"]}


@pytest.mark.parametrize("kind", ["containers", "volumes", "networks"])
@pytest.mark.parametrize("change", ["replace", "delete"])
def test_existing_resource_mutation_is_rejected(kind, change):
    before = inventory()
    after = copy.deepcopy(before)
    name = next(iter(after[kind]))
    if change == "delete":
        del after[kind][name]
    else:
        after[kind][name]["id"] = "changed"
    with pytest.raises(RuntimeError, match="invariant changed"):
        deploy.compare_existing(before, after)


def test_new_resources_allowed_but_disappearing_listener_rejected():
    before = inventory()
    after = copy.deepcopy(before)
    after["containers"]["bcs-pr41-backend"] = {"id": "candidate"}
    after["listeners"].append("127.0.0.1:8004")
    deploy.compare_existing(before, after)
    after["listeners"].remove("127.0.0.1:8000")
    with pytest.raises(RuntimeError, match="disappeared"):
        deploy.compare_existing(before, after)


@pytest.mark.parametrize("kind,name", [
    ("containers", "bcs-pr41-backend"), ("volumes", deploy.VOLUME),
    ("networks", deploy.NETWORK), ("containers", "unexpected-project-container")])
def test_collision_never_adopted(kind, name):
    state = inventory()
    state[kind][name] = {"project": deploy.PROJECT}
    with pytest.raises(RuntimeError):
        deploy.fresh_resources(state)


def test_guard_stops_before_mutating_command_on_foreign_ownership(tmp_path, monkeypatch):
    runner = deploy.Deployment(tmp_path)
    state = inventory()
    runner.before = copy.deepcopy(state)
    runner.owned["containers"]["bcs-pr41-backend"] = "owned-id"
    state["containers"]["bcs-pr41-backend"] = {"id": "owned-id", "project": "dhm", "source": deploy.SHA}
    monkeypatch.setattr(runner, "snapshot", lambda: state)
    calls = []
    monkeypatch.setattr(runner, "run", lambda *a, **kw: calls.append(a))
    with pytest.raises(RuntimeError, match="ownership"):
        runner.mutate(["docker", "compose", "up"])
    assert calls == []


def test_partial_checkout_stops_without_commands(tmp_path, monkeypatch):
    runner = deploy.Deployment(tmp_path)
    monkeypatch.setattr(runner, "snapshot", inventory)
    calls = []
    monkeypatch.setattr(runner, "run", lambda *a, **kw: calls.append(a))
    with pytest.raises(RuntimeError, match="without completion"):
        runner.deploy()
    assert calls == []


def test_occupied_port_rejected(monkeypatch):
    class Occupied:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def bind(self, target):
            assert target == ("127.0.0.1", 8004)
            raise OSError("in use")
    monkeypatch.setattr(deploy.socket, "socket", Occupied)
    with pytest.raises(RuntimeError, match="occupied"):
        deploy.port_free()


def test_compose_has_only_own_resources_and_loopback(tmp_path):
    config = deploy.compose_config(tmp_path, "sha256:postgres", "sha256:backend")
    services = config["services"]
    assert services["backend"]["ports"] == ["127.0.0.1:8004:8000"]
    assert "ports" not in services["postgres"]
    assert "ports" not in services["migration"]
    assert services["migration"]["restart"] == "no"
    assert services["postgres"]["volumes"] == ["data:/var/lib/postgresql/data"]
    assert "volumes" not in services["backend"]
    assert config["volumes"]["data"] == {"external": True, "name": deploy.VOLUME}
    assert config["networks"]["isolated"] == {"external": True, "name": deploy.NETWORK}
    for service in services.values():
        assert service["networks"] == ["isolated"]
        assert service["labels"][deploy.LABEL] == deploy.SHA
    assert services["backend"]["image"] == "sha256:backend"


def test_failed_subprocess_does_not_disclose_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(deploy.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 1, "SECRET_SENTINEL", "DATABASE_PASSWORD"))
    with pytest.raises(RuntimeError) as failure:
        deploy.Deployment(tmp_path).run(["docker", "exec"])
    assert "SECRET_SENTINEL" not in str(failure.value)
    assert "DATABASE_PASSWORD" not in str(failure.value)


def test_snapshot_does_not_disclose_env_or_driver_credentials(tmp_path, monkeypatch):
    runner = deploy.Deployment(tmp_path)
    outputs = {("docker", "ps", "-aq"): "cid", ("docker", "volume", "ls", "-q"): "vol",
               ("docker", "network", "ls", "-q"): "net", ("ss", "-H", "-ltn"): "LISTEN 0 128 127.0.0.1:8000 0.0.0.0:*"}
    monkeypatch.setattr(runner, "run", lambda args: outputs[tuple(args)])
    container = {"Id":"cid", "Name":"/dhm-backend", "Image":"sha256:image",
        "Config":{"Image":"dhm:existing", "Env":["PASSWORD=ENV_SENTINEL"], "Labels":{}},
        "State":{"Status":"running", "StartedAt":"unchanged"}, "RestartCount":0,
        "HostConfig":{"PortBindings":{}}, "Mounts":[], "NetworkSettings":{"Networks":{}}}
    volume = {"Name":"vol", "Driver":"local", "Options":{"password":"DRIVER_SENTINEL"}}
    network = {"Name":"net", "Id":"nid", "Driver":"bridge", "Options":{}}
    monkeypatch.setattr(runner, "docker_json", lambda *args:
        [container if args[0] == "inspect" else volume if args[0] == "volume" else network])
    snapshot = runner.snapshot()
    serialized = json.dumps(snapshot)
    assert "ENV_SENTINEL" not in serialized
    assert "DRIVER_SENTINEL" not in serialized
    assert len(snapshot["volumes"]["vol"]["options_sha256"]) == 64


def test_api_smoke_against_real_candidate_contract(client, monkeypatch):
    from app.core.settings import settings
    monkeypatch.setattr(settings, "TENANT_REGISTRATION_INVITE_CODE", None)
    monkeypatch.setattr(settings, "SMTP_HOST", None)
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", None)
    def request(method, path, value=None, headers=None):
        response = client.request(method, path, json=value, headers=headers)
        assert response.status_code == 200, response.text
        return response.json()
    def rows(run_id, tenant):
        with engine.connect() as conn:
            return [dict(r) for r in conn.execute(text(
                "SELECT i.id,i.finding_id,i.affected_count,i.estimated_impact_eur FROM scan_issues i "
                "JOIN scans s ON i.scan_id=s.scan_id WHERE s.scan_id=:run AND s.tenant_id=:tenant ORDER BY i.id"),
                {"run": run_id, "tenant": tenant}).mappings()]
    result = deploy.smoke(request, rows)
    assert result["rows"] == 2
    assert result["occurrences"] == 5
    assert result["impact_eur"] == 180
    assert result["reordered_retry"] == "PASS"
    assert "api_token" not in json.dumps(result)


def test_embedded_schema_and_smoke_scripts_compile():
    compile(deploy.SCHEMA_CHECK, "candidate-schema", "exec")
    compile(deploy.SMOKE_ADAPTER + "\n" + deploy.inspect.getsource(deploy.smoke)
            + "\nprint(json.dumps(smoke(request,rows)))", "candidate-smoke", "exec")