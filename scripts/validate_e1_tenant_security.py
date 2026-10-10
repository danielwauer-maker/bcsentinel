from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "backend/app/security/tenant.py",
    ROOT / "backend/app/security/tenant_session.py",
    ROOT / "backend/app/services/tenant_access_service.py",
    ROOT / "backend/app/tenant_access_models.py",
    ROOT / "backend/app/routers/auth.py",
    ROOT / "backend/alembic/versions/0022_tenant_access_states.py",
    ROOT / "backend/tests/test_e1_tenant_security.py",
    ROOT / "dashboard/src/api/client.ts",
    ROOT / "dashboard/src/foundation/contexts.tsx",
    ROOT / "docs/security/E1_TENANT_SECURITY_CONTRACT.md",
]
for path in required:
    if not path.exists():
        raise SystemExit(f"E1 missing required file: {path.relative_to(ROOT)}")

tenant_security = (ROOT / "backend/app/security/tenant.py").read_text(encoding="utf-8")
session_security = (ROOT / "backend/app/security/tenant_session.py").read_text(encoding="utf-8")
tenant_access = (ROOT / "backend/app/services/tenant_access_service.py").read_text(encoding="utf-8")
auth_router = (ROOT / "backend/app/routers/auth.py").read_text(encoding="utf-8")
reports = (ROOT / "backend/app/routers/reports.py").read_text(encoding="utf-8")
migration = (ROOT / "backend/alembic/versions/0022_tenant_access_states.py").read_text(encoding="utf-8")
dashboard_client = (ROOT / "dashboard/src/api/client.ts").read_text(encoding="utf-8")
dashboard_contexts = (ROOT / "dashboard/src/foundation/contexts.tsx").read_text(encoding="utf-8")
e1_tests = (ROOT / "backend/tests/test_e1_tenant_security.py").read_text(encoding="utf-8")
contract = (ROOT / "docs/security/E1_TENANT_SECURITY_CONTRACT.md").read_text(encoding="utf-8")

# Credential authentication must not enumerate tenant identifiers.
if tenant_security.count("Invalid tenant credentials.") < 1:
    raise SystemExit("E1 requires a uniform invalid-tenant credential response.")
if 'status_code=404, detail="Tenant not found."' in tenant_security:
    raise SystemExit("E1 tenant authentication must not reveal unknown tenant identifiers.")
if "enforce_tenant_is_active" not in tenant_security:
    raise SystemExit("E1 tenant lifecycle must be enforced centrally after authentication.")
if "status_code=403" not in tenant_security or "authenticated tenant scope" not in tenant_security:
    raise SystemExit("E1 tenant scope mismatches must be authorization failures.")

# Browser session token: short lived, scoped and bound to the current machine credential.
for marker in [
    'TENANT_SESSION_TOKEN_TYPE = "tenant_dashboard_session"',
    'TENANT_SESSION_SCOPE = "tenant:dashboard"',
    'TENANT_SESSION_ROLE = "dashboard_runtime"',
    "TENANT_SESSION_MINUTES = 15",
    "credential_binding",
]:
    if marker not in session_security:
        raise SystemExit(f"E1 dashboard session contract missing: {marker}")
if '@router.post("/auth/session"' not in auth_router:
    raise SystemExit("E1 session exchange endpoint is missing.")

# Tenant lifecycle is separate from billing/license state.
for status in ["active", "suspended", "deactivated"]:
    if status not in tenant_access:
        raise SystemExit(f"E1 tenant lifecycle status missing: {status}")
if 'down_revision = "0021_pilot_interests"' not in migration:
    raise SystemExit("E1 migration does not extend migration 0021.")
if "tenant_access_states" not in migration:
    raise SystemExit("E1 migration does not create tenant lifecycle storage.")

# Dashboard prefers short-lived Authorization bearer sessions over raw machine credentials.
if "sessionToken?: string" not in dashboard_client:
    raise SystemExit("E1 dashboard session token support is missing.")
if "Authorization" not in dashboard_client or "Bearer ${session.sessionToken}" not in dashboard_client:
    raise SystemExit("E1 dashboard must send the short-lived session as a Bearer token.")
if dashboard_client.index("session.sessionToken") > dashboard_client.index("session.apiToken"):
    raise SystemExit("E1 dashboard must prefer sessionToken over legacy apiToken.")
if "localStorage" in dashboard_client and "apiToken" in dashboard_client:
    raise SystemExit("E1 dashboard must not persist tenant API credentials in localStorage.")

# Authentication and entitlement state remain independent in the UI foundation.
if "AuthContext" not in dashboard_contexts or "EntitlementContext" not in dashboard_contexts:
    raise SystemExit("E1 requires separate auth and entitlement contexts.")
if "authenticated: Boolean(tenant)" not in dashboard_contexts:
    raise SystemExit("E1 auth context no longer reflects the runtime session boundary.")
if "access: 'pending'" not in dashboard_contexts:
    raise SystemExit("E1 authentication must not auto-grant entitlement access.")

# Resource existence must be masked across tenants and shared links honor lifecycle state.
for marker in ["_require_owned_scan", "Scan.tenant_id == tenant_id", 'status_code=404, detail="Report not found."']:
    if marker not in reports:
        raise SystemExit(f"E1 report tenant isolation marker missing: {marker}")
if "enforce_tenant_is_active" not in reports:
    raise SystemExit("E1 shared report links must honor tenant lifecycle status.")

# Automated attack matrix evidence.
for test_marker in [
    "test_unknown_tenant_and_wrong_token_have_same_failure",
    "test_short_lived_dashboard_session_authenticates_without_raw_api_token",
    "test_dashboard_session_is_revoked_by_api_token_rotation",
    "test_suspended_tenant_blocks_valid_machine_and_browser_credentials_before_entitlements",
    "test_authentication_never_implies_paid_entitlement",
    "test_report_resource_existence_is_masked_across_tenants",
    "test_remediation_detail_and_list_do_not_cross_tenant_boundary",
    "test_scan_status_is_scoped_to_authenticated_tenant",
    "test_payload_tenant_mismatch_is_authorization_failure_and_preserves_data",
    "test_shared_report_link_is_invalidated_when_tenant_is_suspended",
]:
    if test_marker not in e1_tests:
        raise SystemExit(f"E1 attack-matrix evidence missing: {test_marker}")

for statement in [
    "Authentication never implies entitlement",
    "Business Central operational roles",
    "Resource isolation",
    "Shared report links",
]:
    if statement not in contract:
        raise SystemExit(f"E1 security contract incomplete: {statement}")

print("Entitlement & Tenant Security Quality Gate: PASS")
