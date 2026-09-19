#!/usr/bin/env python3
"""Fail-closed Linux-only PR41 deployment. No existing resources are adopted.

Requires Python 3.10+, git, authenticated gh, Docker Compose v2 and ss.
Default rerun of a completed deployment only verifies it. Partial state stops.
No teardown, public routing, DNS, firewall or real BC operations are performed.
"""
import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import uuid

REPO = "danielwauer-maker/bcsentinel"
BRANCH = "sprint/ext-50-12c-3-lossless-findings"
SHA = "f483d78bf8bc9d00d0f6fd61a8247a05e3f955fb"
PROJECT = "bcsentinel-pr41"
VOLUME = PROJECT + "_postgres_data"
NETWORK = PROJECT + "_network"
DB = "bcs_pr41_candidate"
USER = "bcs_pr41_user"
PORT = 8004
IMAGE = "bcsentinel-backend:pr41-f483d78"
NAMES = {"bcs-pr41-backend", "bcs-pr41-postgres", "bcs-pr41-migrate"}
LABEL = "io.bcsentinel.pr41.source"
TOOLS = {"scripts/deploy_pr41_candidate.py",
         "backend/tests/test_pr41_candidate_deployment.py",
         "docs/EXT_50_12C_3_RUNTIME_CANDIDATE_BACKEND.md"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def port_free():
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", PORT))
        except OSError:
            raise RuntimeError("Port 8004 is occupied; no resources will be replaced.") from None


def compare_existing(before, after):
    for kind in ("containers", "volumes", "networks"):
        for name, value in before[kind].items():
            require(after[kind].get(name) == value,
                    f"Existing {kind} invariant changed: {name}. STOP; no cleanup.")
    require(set(before["listeners"]) <= set(after["listeners"]),
            "An existing listening endpoint disappeared. STOP; no cleanup.")


def fresh_resources(snapshot):
    require(not NAMES.intersection(snapshot["containers"]), "Candidate container name already exists.")
    require(VOLUME not in snapshot["volumes"], "Candidate volume already exists; no adoption.")
    require(NETWORK not in snapshot["networks"], "Candidate network already exists; no adoption.")
    for kind in ("containers", "volumes", "networks"):
        require(not any(v.get("project") == PROJECT for v in snapshot[kind].values()),
                "Existing candidate project resources require manual inspection.")


def compose_config(root, pg_image, backend_image=IMAGE):
    # JSON is valid Compose YAML. All resources explicit; no inherited .env or overrides.
    backend = {
        "image": backend_image, "container_name": "bcs-pr41-backend",
        "env_file": [str(root / ".env.pr41-candidate")],
        "labels": {LABEL: SHA}, "networks": ["isolated"],
        "ports": [f"127.0.0.1:{PORT}:8000"], "restart": "unless-stopped",
        "healthcheck": {"test": ["CMD", "python", "-c",
            "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready',timeout=5)"],
            "interval": "10s", "timeout": "6s", "retries": 12, "start_period": "30s"}}
    return {"name": PROJECT, "services": {
        "backend": backend,
        "migration": {"image": backend_image, "env_file": backend["env_file"],
            "labels": {LABEL: SHA}, "networks": ["isolated"], "restart": "no", "profiles": ["tools"]},
        "postgres": {"image": pg_image, "container_name": "bcs-pr41-postgres",
            "env_file": [str(root / ".env.pr41-candidate-db")],
            "labels": {LABEL: SHA}, "networks": ["isolated"],
            "restart": "unless-stopped",
            "volumes": ["data:/var/lib/postgresql/data"],
            "healthcheck": {"test": ["CMD-SHELL", 'pg_isready -U "$${POSTGRES_USER}" -d "$${POSTGRES_DB}"'],
                "interval": "5s", "timeout": "5s", "retries": 24}}},
        "volumes": {"data": {"external": True, "name": VOLUME}},
        "networks": {"isolated": {"external": True, "name": NETWORK}}}


def smoke(request, rows):
    """Regular API calls, based on existing identity tests; no fixture/SQL writes."""
    ready = request("GET", "/health/ready")
    assert ready["checks"]["database"] == "ok"
    schema = request("GET", "/openapi.json")
    assert "finding_id" in schema["components"]["schemas"]["ScanIssuePayload"]["properties"]
    registration = request("POST", "/tenant/register", {
        "environment_name": "PR41-CANDIDATE-SMOKE", "environment_type": "sandbox",
        "entra_tenant_id": str(uuid.uuid4()), "company_id": str(uuid.uuid4()),
        "company_name": "SYNTHETIC-PR41-SMOKE", "app_version": "1.0.2.22",
        "contact_email": "pr41-smoke@example.invalid", "preferred_language": "en"})
    assert registration["dashboard_invite_sent"] is False
    assert registration["dashboard_invite_error"] == "SMTP not configured."
    tenant = registration["tenant_id"]
    headers = {"X-Tenant-Id": tenant, "X-Api-Token": registration["api_token"]}
    run_id = "PR41_SMOKE_" + uuid.uuid4().hex
    payload = {"tenant_id": tenant, "scan_id": run_id, "scan_type": "data_health_score",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "data_score": 88, "checks_count": 1, "issues_count": 2,
        "headline": "Synthetic PR41 candidate smoke", "rating": "good",
        "enabled_modules": ["sales"], "issues": [
            {"finding_id": str(uuid.uuid4()), "code": "CUSTOMERS_DUPLICATE_EMAIL",
             "category": "CUSTOMER", "title": "Synthetic candidate group",
             "severity": "high", "affected_count": count, "premium_only": True}
            for count in (2, 3)]}
    first = request("POST", "/scan/sync", payload, headers)
    expected = {i["finding_id"]: i["affected_count"] * 36 for i in payload["issues"]}
    assert {i["finding_id"]: i["estimated_impact_eur"] for i in first["issues"]} == expected
    assert first["commercials"]["estimated_loss_eur"] == 180
    stored = rows(run_id, tenant)
    assert len(stored) == 2
    assert {r["finding_id"]: float(r["estimated_impact_eur"]) for r in stored} == expected
    assert sum(r["affected_count"] for r in stored) == 5
    payload["issues"].reverse()
    second = request("POST", "/scan/sync", payload, headers)
    assert {i["finding_id"]: i["estimated_impact_eur"] for i in second["issues"]} == expected
    assert rows(run_id, tenant) == stored  # Includes original database row IDs.
    return {"readiness": "PASS", "registration": "PASS", "finding_id_schema": "PASS",
            "multi_group_persistence": "PASS", "reordered_retry": "PASS",
            "run_id": run_id, "rows": 2, "occurrences": 5, "impact_eur": 180,
            "mail": "DISABLED: SMTP not configured; no external mail sent"}


SCHEMA_CHECK = '''
import json
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url
from app.db import engine, get_required_alembic_revision
from app.core.settings import settings
url = make_url(settings.DATABASE_URL)
assert url.host == 'postgres' and url.database == 'bcs_pr41_candidate' and url.username == 'bcs_pr41_user'
assert get_required_alembic_revision() == '0029_finding_identity'
with engine.connect() as c:
    assert c.execute(text('SELECT current_database()')).scalar_one() == 'bcs_pr41_candidate'
    assert c.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '0029_finding_identity'
inspector = inspect(engine)
columns = {c['name']: c for c in inspector.get_columns('scan_issues')}
assert not columns['finding_id']['nullable']
assert columns['finding_id']['type'].length == 128
constraints = inspector.get_unique_constraints('scan_issues')
assert any(c['column_names'] == ['scan_id', 'finding_id'] for c in constraints)
assert not any(c['column_names'] == ['scan_id', 'code'] for c in constraints)
assert any(i['unique'] and i['column_names'] == ['scan_id', 'finding_id'] for i in inspector.get_indexes('scan_issues'))
print(json.dumps({'current':'0029_finding_identity','head':get_required_alembic_revision(), 'schema':'PASS'}))
'''

SMOKE_ADAPTER = '''
import datetime, json, urllib.request, uuid
from sqlalchemy import text
from app.db import engine
from app.core.settings import settings
assert not settings.SMTP_HOST and not settings.STRIPE_SECRET_KEY
def request(method, path, value=None, headers=None):
    hdr = dict(headers or {})
    hdr['Content-Type'] = 'application/json'
    if path == '/tenant/register':
        hdr['X-Registration-Invite'] = settings.TENANT_REGISTRATION_INVITE_CODE
    req = urllib.request.Request('http://127.0.0.1:8000' + path,
        data=None if value is None else json.dumps(value).encode(), headers=hdr, method=method)
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=30) as response:
        assert response.status == 200
        return json.load(response)
def rows(run_id, tenant):
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text(
            'SELECT i.id, i.finding_id, i.affected_count, i.estimated_impact_eur FROM scan_issues i '
            'JOIN scans s ON s.scan_id=i.scan_id WHERE s.scan_id=:run AND s.tenant_id=:tenant ORDER BY i.id'),
            {'run':run_id, 'tenant':tenant}).mappings()]
'''


class Deployment:
    def __init__(self, root):
        self.root = root
        self.evidence = root / ".candidate"
        self.env = {k: v for k, v in os.environ.items()
                    if k in {"PATH", "HOME", "USER", "LANG", "SSH_AUTH_SOCK", "XDG_RUNTIME_DIR", "DOCKER_CONFIG", "GH_CONFIG_DIR"}}
        self.env.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1",
                        GIT_SSH_COMMAND="ssh -o BatchMode=yes -o StrictHostKeyChecking=yes")
        self.before = None
        self.owned = {"containers": {}, "volumes": {}, "networks": {}}

    def run(self, args, data=None, ok=True, cwd=None, timeout=1800):
        result = subprocess.run(args, input=data, text=True, capture_output=True,
                                env=self.env, cwd=cwd, timeout=timeout)
        # Never print command output or raw exception (DB URLs/tokens can occur there).
        require(not ok or result.returncode == 0,
                f"Command failed ({args[0]} {args[1] if len(args)>1 else ''}); exit {result.returncode}. No cleanup performed.")
        return result.stdout.strip()

    def docker_json(self, *args):
        return json.loads(self.run(["docker", *args]))

    def snapshot(self):
        result = {"containers": {}, "volumes": {}, "networks": {}}
        for cid in self.run(["docker", "ps", "-aq"]).split():
            c = self.docker_json("inspect", cid)[0]
            labels = c["Config"].get("Labels") or {}
            result["containers"][c["Name"].lstrip("/")] = {
                "id": c["Id"], "image": c["Image"], "image_name": c["Config"]["Image"],
                "status": c["State"]["Status"], "started": c["State"]["StartedAt"],
                "restarts": c["RestartCount"], "ports": c["HostConfig"]["PortBindings"],
                "mounts": [{k: m.get(k) for k in ("Type", "Name", "Source", "Destination", "RW")} for m in c["Mounts"]],
                "networks": sorted(c["NetworkSettings"]["Networks"]),
                "project": labels.get("com.docker.compose.project"), "source": labels.get(LABEL)}
        for kind, singular, key in (("volumes", "volume", "Name"), ("networks", "network", "Id")):
            for item in self.run(["docker", singular, "ls", "-q"]).split():
                v = self.docker_json(singular, "inspect", item)[0]
                labels = v.get("Labels") or {}
                result[kind][v["Name"]] = {"id": v[key], "driver": v["Driver"],
                    "created": v.get("CreatedAt", v.get("Created")),
                    "options_sha256": hashlib.sha256(json.dumps(v.get("Options"), sort_keys=True).encode()).hexdigest(),
                    "project": labels.get("com.docker.compose.project"), "source": labels.get(LABEL)}
        result["listeners"] = sorted({" ".join(line.split()[3:4]) for line in self.run(["ss", "-H", "-ltn"]).splitlines()})
        return result

    def guard(self):
        require(not self.root.is_symlink(), "Checkout may not be a symlink.")
        now = self.snapshot()
        if self.before is not None:
            compare_existing(self.before, now)
        for kind in self.owned:
            for name, identity in self.owned[kind].items():
                actual = now[kind].get(name)
                require(actual is not None and actual["id"] == identity and actual["project"] == PROJECT
                        and actual["source"] == SHA, "Candidate ownership changed; refusing mutation.")
        for kind in self.owned:
            for name, value in now[kind].items():
                if value["project"] == PROJECT or name in NAMES or name in {VOLUME, NETWORK}:
                    require(name in self.owned[kind], "Untracked candidate resource appeared; refusing adoption.")
        return now

    def mutate(self, args, **kwargs):
        self.guard()
        return self.run(args, **kwargs)

    def remember(self, kind, name):
        value = self.snapshot()[kind][name]
        require(value["project"] == PROJECT and value["source"] == SHA, "New resource lacks ownership labels.")
        self.owned[kind][name] = value["id"]

    def write(self, path, value):
        self.guard()
        with path.open("x", encoding="utf-8") as out:
            out.write(value)

    def compose(self, *args):
        return ["docker", "compose", "--project-directory", str(self.root), "-p", PROJECT,
                "--env-file", str(self.root / ".env.pr41-candidate"),
                "-f", str(self.evidence / "docker-compose.pr41-candidate.yml"), *args]

    def wait_health(self, name):
        for _ in range(90):
            self.guard()
            info = self.docker_json("inspect", name)[0]
            if info["State"].get("Health", {}).get("Status") == "healthy":
                return
            require(info["State"]["Status"] == "running", "Candidate exited during startup.")
            time.sleep(2)
        raise RuntimeError("Candidate health timed out. Resources retained for inspection.")

    def verify(self):
        after = self.guard()
        backend = after["containers"]["bcs-pr41-backend"]
        postgres = after["containers"]["bcs-pr41-postgres"]
        require(backend["ports"] == {"8000/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]}, "Backend binding differs.")
        require(not postgres["ports"], "Postgres must not expose a host port.")
        for c in (backend, postgres):
            require(c["networks"] == [NETWORK], "Candidate is attached to another network.")
        require(not backend["mounts"], "Backend must have no host or data mounts.")
        require(len(postgres["mounts"]) == 1 and postgres["mounts"][0]["Name"] == VOLUME,
                "Postgres volume differs.")
        require(backend["image"] == self.image_id, "Backend image changed.")
        self.wait_health("bcs-pr41-postgres")
        self.wait_health("bcs-pr41-backend")
        schema = json.loads(self.run(["docker", "exec", "-i", "bcs-pr41-backend", "python", "-"], data=SCHEMA_CHECK))
        for command in ("current", "heads"):
            output = self.run(["docker", "exec", "bcs-pr41-backend", "python", "-m", "alembic", command])
            require(output.strip() == "0029_finding_identity (head)", "Alembic CLI revision differs.")
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(f"http://127.0.0.1:{PORT}/health/ready", timeout=10) as r:
            require(r.status == 200 and json.load(r)["checks"]["database"] == "ok", "Readiness failed.")
        return after, schema

    def deploy(self):
        self.before = self.snapshot()
        if self.root.exists():
            state_path = self.evidence / "complete.json"
            require(state_path.is_file(), "Checkout exists without completion evidence. STOP; no overwrite/resume.")
            state = json.loads(state_path.read_text())
            require(state["source"] == SHA and state["root"] == str(self.root), "Completion provenance differs.")
            self.before = json.loads((self.evidence / "before.json").read_text())
            self.owned = state["owned"]
            self.image_id = state["image_id"]
            require(self.run(["git", "rev-parse", "HEAD"], cwd=self.root) == SHA, "Checkout HEAD differs.")
            require(not self.run(["git", "status", "--porcelain"], cwd=self.root), "Checkout is dirty.")
            self.verify()
            print("Existing completed candidate verified read-only. READY_FOR_SECURE_BC_SAAS_EXPOSURE")
            return
        fresh_resources(self.before)
        for name in ("dhm-backend", "dhm-dev-backend", "dhm-postgres", "dhm-dev-postgres"):
            require(self.before["containers"].get(name, {}).get("status") == "running",
                    "Expected DHM container is absent or not running; review server inventory first.")
        for name, port in (("dhm-backend", "8000"), ("dhm-dev-backend", "8001")):
            require(self.before["containers"][name]["ports"].get("8000/tcp") == [{"HostIp":"127.0.0.1", "HostPort":port}],
                    "DHM port baseline differs; review server inventory first.")
        port_free()
        require(not self.run(["docker", "image", "ls", "-q", IMAGE]), "Candidate image tag already exists; refusing overwrite.")
        self.mutate(["gh", "repo", "clone", REPO, str(self.root), "--", "--no-checkout", "--single-branch", "--branch", BRANCH])
        remote = self.run(["git", "remote", "get-url", "origin"], cwd=self.root)
        require(remote in {f"https://github.com/{REPO}.git", f"git@github.com:{REPO}.git"}, "Unexpected repository origin.")
        changed = set(self.run(["git", "diff", "--name-only", SHA, f"origin/{BRANCH}"], cwd=self.root).splitlines())
        require(changed <= TOOLS, "Remote contains unapproved changes beyond candidate tooling. STOP.")
        self.mutate(["git", "checkout", "-B", BRANCH, SHA], cwd=self.root)
        require(self.run(["git", "rev-parse", "HEAD"], cwd=self.root) == SHA, "Pinned checkout failed.")
        self.guard()
        self.evidence.mkdir(mode=0o700)
        self.write(self.evidence / "before.json", json.dumps(self.before, indent=2))
        self.guard()
        with (self.root / ".git/info/exclude").open("a") as out:
            out.write("\n/.candidate/\n")
        # Build before creating secrets. Dockerfile is the unmodified pinned product file.
        require(not self.run(["docker", "image", "ls", "-q", IMAGE]), "Candidate image tag appeared; refusing overwrite.")
        self.mutate(["docker", "build", "--target", "production", "--label", f"{LABEL}={SHA}",
                     "--label", f"org.opencontainers.image.revision={SHA}", "-t", IMAGE,
                     "-f", str(self.root / "backend/Dockerfile"), str(self.root)])
        self.image_id = self.docker_json("image", "inspect", IMAGE)[0]["Id"]
        pg = self.run(["docker", "image", "ls", "-q", "postgres:15"])
        if not pg:
            self.mutate(["docker", "pull", "postgres:15"])
        pg_image = self.docker_json("image", "inspect", "postgres:15")[0]["Id"]
        password, secret, admin_password, invite = [secrets.token_hex(32) for _ in range(4)]
        self.write(self.root / ".env.pr41-candidate-db", f"POSTGRES_DB={DB}\nPOSTGRES_USER={USER}\nPOSTGRES_PASSWORD={password}\n")
        self.write(self.root / ".env.pr41-candidate",
            f"ENV=dev\nAPP_ENV=dev\nDATABASE_URL=postgresql+psycopg://{USER}:{password}@postgres:5432/{DB}\n"
            f"SECRET_KEY={secret}\nADMIN_USERNAME=pr41-qa-admin\nADMIN_PASSWORD={admin_password}\n"
            f"TENANT_REGISTRATION_INVITE_CODE={invite}\nAPP_BASE_URL=http://127.0.0.1:{PORT}\n"
            f"CORS_ALLOW_ORIGINS=http://127.0.0.1:{PORT}\nSITE_TRANSLATIONS_PATH=/app/landingpage/lang\n")
        self.run(["git", "check-ignore", ".env.pr41-candidate", ".env.pr41-candidate-db"], cwd=self.root)
        config = compose_config(self.root, pg_image, self.image_id)
        self.write(self.evidence / "docker-compose.pr41-candidate.yml", json.dumps(config, indent=2))
        self.run(self.compose("config", "--quiet"))
        for singular, kind, name in (("volume", "volumes", VOLUME), ("network", "networks", NETWORK)):
            self.mutate(["docker", singular, "create", "--label", f"com.docker.compose.project={PROJECT}",
                         "--label", f"{LABEL}={SHA}", name])
            self.remember(kind, name)
        port_free()
        self.mutate(self.compose("up", "-d", "--no-recreate", "--no-build", "--pull", "never", "postgres"))
        self.remember("containers", "bcs-pr41-postgres")
        self.wait_health("bcs-pr41-postgres")
        count = self.run(["docker", "exec", "bcs-pr41-postgres", "psql", "-U", USER, "-d", DB, "-Atc",
                          "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"])
        require(count == "0", "Candidate DB is not empty; refusing migration.")
        migration = "from alembic.config import Config\nfrom alembic import command\nfrom alembic.script import ScriptDirectory\nc=Config('alembic.ini')\nassert ScriptDirectory.from_config(c).get_heads()==['0029_finding_identity']\ncommand.upgrade(c,'head')\n" + SCHEMA_CHECK
        self.mutate(self.compose("run", "--name", "bcs-pr41-migrate", "--no-deps", "--pull", "never", "-T",
                                 "migration", "python", "-c", migration))
        self.remember("containers", "bcs-pr41-migrate")
        port_free()
        self.mutate(self.compose("up", "-d", "--no-deps", "--no-recreate", "--no-build", "--pull", "never", "backend"))
        self.remember("containers", "bcs-pr41-backend")
        self.verify()
        code = SMOKE_ADAPTER + "\n" + inspect.getsource(smoke) + "\nprint(json.dumps(smoke(request,rows)))\n"
        result = json.loads(self.mutate(["docker", "exec", "-i", "bcs-pr41-backend", "python", "-"], data=code))
        after, schema = self.verify()
        counts = {}
        for name in sorted(NAMES):
            raw = subprocess.run(["docker", "logs", name], env=self.env, text=True, capture_output=True, timeout=30)
            require(raw.returncode == 0, "Cannot inspect candidate logs.")
            lines = (raw.stdout + raw.stderr).splitlines()
            errors = sum(bool(re.search(r'\b(ERROR|CRITICAL|FATAL|Traceback)\b', line, re.I)) for line in lines)
            warnings = [line for line in lines if re.search(r'\bWARNING\b', line, re.I)]
            local_trust = sum('trust' in line and 'local connections' in line for line in warnings)
            counts[name] = {"errors": errors, "warnings": len(warnings),
                "postgres_init_local_socket_trust": local_trust,
                "unclassified_warnings": len(warnings) - local_trust}
            require(errors == 0, "Candidate logs contain errors. Inspect privately; no automatic cleanup.")
            require(len(warnings) == local_trust, "Unclassified candidate log warning. Inspect privately before exposure.")
        self.write(self.evidence / "after.json", json.dumps(after, indent=2))
        report = {"source": SHA, "root": str(self.root), "repository": REPO, "branch": BRANCH,
            "server": socket.gethostname(), "project": PROJECT, "owned": self.owned,
            "image_id": self.image_id, "image_digests": self.docker_json("image", "inspect", IMAGE)[0].get("RepoDigests", []),
            "postgres_image": pg_image, "database": DB, "volume": VOLUME, "binding": f"127.0.0.1:{PORT}",
            "candidate_containers": {name: after["containers"][name] for name in sorted(NAMES)},
            "migration": schema, "smoke": result, "logs": counts,
            "proxy_inventory_files": {str(path): sorted(p.name for p in path.iterdir())
                for path in (Path('/etc/nginx/sites-enabled'), Path('/etc/caddy'), Path('/etc/traefik'))
                if path.is_dir() and os.access(path, os.R_OK | os.X_OK)},
            "existing_stack_invariant": "PASS", "public_https": "NOT_CONFIGURED",
            "status": "READY_FOR_SECURE_BC_SAAS_EXPOSURE"}
        self.write(self.evidence / "complete.json", json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))


def main():
    require(len(sys.argv) == 1, "No command-line options supported; refusing ambiguous invocation.")
    require(sys.platform == "linux", "Run only on the named Linux server.")
    import fcntl
    import pwd
    require(socket.gethostname().split('.')[0] == "bcsentinel-main", "Unexpected server hostname.")
    account = pwd.getpwuid(os.getuid())
    require(os.getuid() != 0 and account.pw_name == "daniel", "Run as daniel, without sudo.")
    require(Path.home().resolve() == Path(account.pw_dir).resolve(), "HOME differs from daniel's account home.")
    require(not any(os.environ.get(k) for k in ("DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME")),
            "Unset Docker/Compose overrides first; no remote daemon or inherited project allowed.")
    for command in ("git", "gh", "docker", "ss"):
        require(shutil.which(command), f"Missing prerequisite: {command}")
    os.umask(0o077)
    root = Path.home() / "bcsentinel-pr41"
    require(not root.is_symlink(), "Checkout may not be a symlink.")
    deployment = Deployment(root)
    context = deployment.docker_json("context", "inspect")[0]
    require(context["Endpoints"]["docker"]["Host"].startswith("unix:///"), "Docker daemon must be local Unix socket.")
    require(deployment.run(["docker", "info", "--format", "{{.OSType}}" ]) == "linux", "Linux Docker required.")
    version = deployment.run(["docker", "compose", "version", "--short"])
    parsed = re.match(r'v?(\d+)\.(\d+)', version)
    require(parsed and tuple(map(int, parsed.groups())) >= (2, 20), "Docker Compose >= 2.20 required.")
    deployment.run(["gh", "auth", "status"])
    # Nonblocking lock protects concurrent invocations; never deletes another lock.
    lock_path = Path.home() / ".bcsentinel-pr41-deploy.lock"
    require(not lock_path.is_symlink(), "Lock may not be a symlink.")
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        deployment.deploy()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Errors deliberately omit captured subprocess output and credentials.
        print("STOP: " + (str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__), file=sys.stderr)
        sys.exit(1)