from __future__ import annotations

import json
from pathlib import Path

FRONTEND_SHA = "742e3257c8db6af6d732fcca02da0047a48b69b5"
FRONTEND_CLOSURE_SHA = "20464e4c8e15f139a21b6226f974cfc951ae180d"
DEV_DEPLOY_RUN = 40747919204

state_path = Path("release/current-product-state.json")
state = json.loads(state_path.read_text(encoding="utf-8"))

frontend = state["repositories"]["frontend"]
frontend["main_sha"] = FRONTEND_SHA
frontend["state"] = "s2_autonomous_technical_closure_complete_and_dev_deployed"
frontend["implemented_routes"] = [
    "/",
    "/overview",
    "/findings",
    "/actions",
    "/financial-impact",
    "/reports",
    "/scans",
    "/validation",
    "/monitoring",
    "/settings",
    "/subscription",
    "/support",
    "/datenschutz",
    "/impressum",
]
frontend["planned_routes"] = []
frontend["known_prod_blocker"] = (
    "manual visual QA and final legal/provider review remain; report-family polish/integration remains a later release gate"
)
frontend["s2_closure_sha"] = FRONTEND_CLOSURE_SHA
frontend["s2_dev_deploy_run_id"] = DEV_DEPLOY_RUN
frontend["s2_dev_deploy_conclusion"] = "success"

state["lovable"]["frontend"]["status"] = (
    "historical_authoring_reference; canonical frontend main advanced through S2"
)
state["lovable"]["landing_master"]["status"] = (
    "visual_reference_only; runtime Lovable asset dependency removed in S2"
)

dev = state["deployment"]["dev"]
dev["frontend_automatic_deployment_branch"] = "main"
dev["frontend_deployed_ref"] = FRONTEND_SHA
dev["frontend_deploy_run_id"] = DEV_DEPLOY_RUN
dev["frontend_deploy_conclusion"] = "success"
dev["status"] = "latest_known_core_and_frontend_dev_deploys_successful"

caps = state["capability_state"]
caps["monitoring"] = "implemented_frontend_route_complete_runtime_acceptance_required"
caps["landing"] = "technical_closure_complete_local_assets_and_legal_routes_reachable_manual_visual_legal_signoff_pending"
caps["remaining_dashboard_pages"] = "s2_core_routes_implemented_backend_bound_manual_visual_acceptance_and_report_family_polish_pending"
caps["reports"] = "service_route_implemented_backend_and_design_advanced_report_family_integration_and_visual_acceptance_pending"

controlled = state["release_gates"]["controlled_pilot"]
controlled = [
    item
    for item in controlled
    if item
    not in {
        "localize frontend Lovable-hosted assets",
        "ensure Impressum and Datenschutz are reachable in the current frontend",
    }
]
state["release_gates"]["controlled_pilot"] = controlled
state["release_gates"]["public_paid_launch"] = [
    item
    for item in state["release_gates"]["public_paid_launch"]
    if item != "remove placeholder dashboard navigation or implement all routes"
]

state["autonomous_sprints"] = {
    "S2": {
        "name": "Frontend Production Closure",
        "technical_status": "complete",
        "frontend_closure_sha": FRONTEND_CLOSURE_SHA,
        "frontend_main_sha": FRONTEND_SHA,
        "dev_deploy_run_id": DEV_DEPLOY_RUN,
        "dev_deploy_conclusion": "success",
        "manual_gates_remaining": [
            "responsive/visual acceptance",
            "final legal/provider review",
        ],
        "note": "Manual gates are deferred and do not negate autonomous technical closure.",
    }
}
state["next_sprint"]["manual_acceptance_deferred_by_owner"] = True
state["next_sprint"]["autonomous_next_sprint"] = "S3"

state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

master_path = Path("docs/BCSENTINEL_MASTER_STATE.md")
master = master_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global master
    count = master.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match, found {count}: {old[:80]!r}")
    master = master.replace(old, new, 1)


replace_once(
    "- Current `main`: `e84deb14afe90ae3326cd9622d78aa5363d6fc63`\n- Lovable `BCSentinel Frontend` is synchronized to the same SHA.\n- Real routes currently implemented: `/`, `/overview`, `/findings`.\n- Additional SaaS routes still need runtime implementation/integration.",
    f"- Current `main`: `{FRONTEND_SHA}`.\n- S2 technical closure commit: `{FRONTEND_CLOSURE_SHA}`.\n- Real routes implemented: `/`, `/overview`, `/findings`, `/actions`, `/financial-impact`, `/reports`, `/scans`, `/validation`, `/monitoring`, `/settings`, `/subscription`, `/support`, `/datenschutz`, `/impressum`.\n- Runtime Lovable asset dependency removed; sidebar placeholder navigation removed; Free Entry route-level aggregate-only boundary preserved.\n- DEV deployment run `{DEV_DEPLOY_RUN}`: PASS including verify, immutable image deployment, routing diagnostics and public DEV smoke.\n- Manual responsive/visual acceptance and final legal/provider review remain later gates.",
)

replace_once(
    "  - Status: synchronized with `bcsentinel-frontend/main`.",
    "  - Status: historical Lovable authoring reference; canonical `bcsentinel-frontend/main` has advanced through S2.",
)
replace_once(
    "  - Status: current landing visual reference.",
    "  - Status: visual reference only; S2 removed the runtime dependency on its hosted landing assets.",
)

replace_once(
    "- Landing hero/dashboard/logo assets currently depend on Lovable-hosted assets and must be localized before PROD.\n- New frontend currently implements only `/`, `/overview` and `/findings` as real routes.\n- Remaining sidebar destinations require real routes and backend integration.",
    "- Frontend S2 technical closure is complete; manual responsive/visual acceptance remains open.\n- Legal routes are reachable, but final provider facts and legal review remain required before public launch.\n- Current report-family integration/polish and visual acceptance remain later release gates.",
)

replace_once(
    "- Lovable-hosted production assets localized.\n- Impressum and Datenschutz reachable from the current frontend.\n",
    "",
)
replace_once(
    "- No placeholder navigation in the SaaS frontend.\n",
    "",
)

replace_once(
    "Tracking: GitHub issue `#121`.\n",
    "Tracking: GitHub issue `#121`.\n\nThe remaining S1 manual acceptance gates are intentionally deferred by the owner while autonomous technical sprints proceed. This does not close S1.\n",
)

marker = "## Using this file in future ChatGPT/Codex sprint chats\n"
if marker not in master:
    raise SystemExit("Master-state insertion marker missing")
section = f"""## Sprint 2 closure\n\n**Sprint 2 – Frontend Production Closure: AUTONOMOUS TECHNICAL SCOPE COMPLETE**\n\nEvidence:\n\n- Frontend closure commit: `{FRONTEND_CLOSURE_SHA}`.\n- Current frontend `main`: `{FRONTEND_SHA}`.\n- Tests: PASS.\n- Production build: PASS.\n- Lint: PASS after full frontend formatting.\n- Hygiene checks: PASS – no Lovable runtime asset URL, no sidebar `href=\"#\"`, no relative Executive Report `/api/reports/executive/...` link.\n- Free Entry direct service routes preserve aggregate-only boundaries; concrete financial values and action/finding details are not rendered there in Free mode.\n- Validation/Monitoring navigation remains entitlement-aware.\n- DEV deploy run `{DEV_DEPLOY_RUN}`: PASS through public DEV smoke.\n- One-shot S2 finalizer/helper files were removed after successful closure.\n\nManual responsive/visual acceptance and final legal/provider review remain deferred acceptance gates; they are not claimed as complete.\n\n"""
master = master.replace(marker, section + marker, 1)

master_path.write_text(master, encoding="utf-8")
