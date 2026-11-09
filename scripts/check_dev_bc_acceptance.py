#!/usr/bin/env python3
"""Read-only DEV evidence preflight for BCSentinel PR #154.

Does not run scans, confirm scopes, issue report tokens, grant licenses, or
trigger paid checkout. Never prints the BC API token.

Usage:
 BCSENTINEL_API_TOKEN=... python scripts/check_dev_bc_acceptance.py \
  --base-url https://dev-api.bcsentinel.com \
  --tenant-id TENANT --scan-id SCAN --expected-company-id BC_COMPANY_GUID

Exit 0: evidence checklist is ready for interactive BC scope confirmation.
Exit 2: evidence incomplete, no install/approval implied.
Exit 3: network/auth/configuration errors.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def _url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("A clean HTTPS DEV API base URL is required.")
    return value.rstrip("/")


def fetch_preflight(base_url: str, tenant_id: str, token: str, scan_id: str) -> dict:
    if not tenant_id or not token or not scan_id:
        raise ValueError("Tenant ID, API token and scan ID must be supplied.")
    url = _url(base_url) + "/scans/" + quote(scan_id, safe="") + "/report-preflight"
    req = Request(url, headers={
        "Accept": "application/json",
        "X-Tenant-Id": tenant_id,
        "X-Api-Token": token,
    }, method="GET")
    with urlopen(req, timeout=20) as response:
        if response.status != 200:
            raise ValueError("Preflight returned an unexpected status.")
        value = json.load(response)
    if not isinstance(value, dict) or value.get("scan_id") != scan_id or value.get("preflight_only") is not True:
        raise ValueError("Unexpected report-preflight response contract.")
    return value


def evaluate(result: dict, expected_company_id: str | None) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    # The original Free scan is the only acceptable Full-v2 baseline.
    # A missing field means the deployed backend is too old for this acceptance.
    if result.get("original_free_scan") is not True:
        blockers.append("Original completed and persisted Free scan is not verified.")
    if not result.get("company_bound"):
        blockers.append("Verified BC company is missing.")
    if not result.get("eur_currency_verified"):
        blockers.append("Company EUR local currency is not verified.")
    if not result.get("premium_active"):
        blockers.append("Test Full Access entitlement is inactive.")
    if result.get("scope_state") == "missing":
        blockers.append("Auto-detected scope snapshot is missing.")
    if result.get("scope_state") not in {"auto", "confirmed"}:
        blockers.append("Scope state is not an expected auto/confirmed state.")
    # The one expected pre-confirmation prerequisite is the user action itself.
    # Any other backend evidence blocker must stop the acceptance workflow.
    missing = result.get("missing_prerequisites")
    if not isinstance(missing, list) or any(not isinstance(item, str) for item in missing):
        blockers.append("Backend prerequisite evidence is missing or malformed.")
    elif set(missing) - {"confirmed_scope_missing"}:
        blockers.append("Backend reports additional prerequisite blockers: " + ", ".join(sorted(set(missing) - {"confirmed_scope_missing"})))
    if expected_company_id:
        # This endpoint intentionally does not disclose company GUID; never
        # claim a GUID match based only on company_bound=True.
        blockers.append("Expected BC Company GUID cannot be matched by this read-only preflight; verify it in the authenticated BC report/link step.")
    return not blockers, blockers


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default="https://dev-api.bcsentinel.com")
    p.add_argument("--tenant-id", required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--expected-company-id", default=None)
    args = p.parse_args()
    token = os.environ.get("BCSENTINEL_API_TOKEN", "").strip()
    try:
        data = fetch_preflight(args.base_url, args.tenant_id, token, args.scan_id)
    except HTTPError as exc:
        print(f"Preflight blocked by HTTP {exc.code}; verify deployment, tenant credentials and scan ownership.", file=sys.stderr)
        return 3
    except (URLError, ValueError, OSError) as exc:
        print(f"Preflight unavailable: {type(exc).__name__}. Verify DEV endpoint and credentials.", file=sys.stderr)
        return 3

    ready, blockers = evaluate(data, args.expected_company_id)
    print("BCSentinel DEV report evidence preflight (read-only)")
    print("Scan ID:", args.scan_id)
    print("Scope state:", data.get("scope_state", "unknown"))
    print("Confirmed scope version:", data.get("confirmed_scope_version") or "not confirmed")
    print("Original completed Free scan:", data.get("original_free_scan") is True)
    print("Company bound:", bool(data.get("company_bound")))
    print("EUR verified:", bool(data.get("eur_currency_verified")))
    print("Premium active:", bool(data.get("premium_active")))
    print("Missing evidence:", ", ".join(data.get("missing_prerequisites") or []) or "none")
    print("Next action:", "Confirm scope in BC and open Full report." if ready else "Fix the evidence/entitlement blockers before BC confirmation.")
    for blocker in blockers:
        print("BLOCKED:", blocker)
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
