from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    full = ROOT / path
    assert full.exists(), f"Missing D3 artifact: {path}"
    return full.read_text(encoding="utf-8-sig")


def require(text: str, *needles: str) -> None:
    for needle in needles:
        assert needle in text, f"Missing D3 contract fragment: {needle}"


def main() -> None:
    router = read("backend/app/routers/remediation.py")
    models = read("backend/app/remediation_models.py")
    migration = read("backend/alembic/versions/0018_remediation_read_model.py")
    license_router = read("backend/app/routers/license.py")

    require(router,
            'APIRouter(prefix="/remediation"',
            '@router.post("/sync")',
            '@router.get("/actions")',
            '@router.get("/actions/{action_id}")',
            '@router.get("/actions/{action_id}/history")',
            '@router.get("/metrics")',
            'RemediationActionRead.tenant_id == header_tenant_id',
            'load_authenticated_tenant',
            'enforce_tenant_match',
            '"completed does not imply validated resolved"')

    # Dashboard surface is read-only: only BC synchronization may mutate this read model.
    assert router.count('@router.post(') == 1
    for forbidden in ['@router.put(', '@router.patch(', '@router.delete(']:
        assert forbidden not in router, f"Forbidden dashboard mutation route: {forbidden}"

    require(models,
            'class RemediationActionRead',
            'class RemediationAuditRead',
            'UniqueConstraint("tenant_id", "action_id"',
            'validation_result_ref',
            'synced_at_utc')
    require(migration,
            'revision = "0018_remediation_read_model"',
            'down_revision = "0017_tenant_preferred_language"',
            'remediation_actions_read',
            'remediation_audit_read')
    require(license_router, 'router.include_router(remediation_router)')

    print("Backend remediation API contract: PASS")


if __name__ == "__main__":
    main()
