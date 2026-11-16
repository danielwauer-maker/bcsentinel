# AI Control Center — DEV Admin activation handoff (2026-11-14)

**Status: SOURCE/CI PREPARED; SERVER ACCEPTANCE NOT EXECUTED.** Only authorized operator actions may change the running host.

## Canonical source
- DEV core branch `staging`, reviewed baseline `caf245b23a74d4691fe62dfc5c4de805c730a171`.
- Latest curated Evidence/Control Center improvements in Draft PR **#193**, against `staging`; do not deploy an unrelated older media-library branch.
- Existing AI Control Center is intended to keep its **current** private SQLite state, Tracker Excel, GitHub read-only token and loopback port `127.0.0.1:8092` (Dashboard service internal port 8090).
- New backend admin-auth route `/_internal/admin-auth`, guarded by existing administrator Basic Auth; no tenant login or customer bearer token can grant operator access.
- `/admin/ai-control-center` nginx source configuration exists but runtime activation is **not proven**. Control Center token mode needs `PROXY_AUTH_TOKEN`, `URL_PREFIX=/admin/ai-control-center`. The browser mount needs same-origin `base-uri 'self'` CSP; historical root mode remains `base-uri 'none'`.

## Operator read-only preflight FIRST
1. Identify actual 8092 container ID and immutable image ID, mounts, Compose file, git HEAD, listener (`ss -lnt`), nginx module support, and loaded DEV virtual-host configuration. **Do not paste environment values**. Reject public `0.0.0.0:8092` or IPv6 wildcard.
2. Verify both private SQLite databases and read-only Excel mount remain present; preserve existing agent budget 0, no active agents or unauthorized approvals, tasks inventory 61 Fiverr + 24 SaaS.
3. Make **consistent SQLite online backups** and verify isolated restore using `tools/ai-control-center/backup_verify.py` before any image restart. Never `cp` the active SQLite files as the sole backup, never `docker compose down -v`.
4. Run 401 for unauthenticated Dashboard/Team/Media/API on the existing private listener and confirm legacy operator browser still works. Inspect host firewall/other nginx routes, but do not claim global reachability from loopback evidence alone.

## DEV-only activation plan — requires operator-approved window
1. Build the exact approved candidate in **separate preview**, with existing state copied/restored in isolation (never mounting live state rw into preview).
2. Create unique high-entropy proxy token stored only in root-owned nginx include (0600) and private Control Center environment. Never use product API/DB/Stripe credentials or print token.
3. Only target **DEV API virtual host** `dev-api.bcsentinel.com`. The repository's sample `config/nginx/bcsentinel.conf` includes **DEV and PROD vhosts**; **DO NOT copy/reload that whole file** when implementing DEV-only integration. Inspect and minimally patch the exact live DEV vhost after backup. Keep other vhosts byte-identical.
4. Ensure nginx `auth_request` is available; verify Nginx syntax before reload. In nginx, all paths under the prefix (HTML, JS, CSS, media and API) must require the same admin guard, and incoming client proxy-auth headers must be overwritten; Authorization must be removed before forwarding to 8092.
5. Check no-auth 401, wrong Basic 401, normal customer bearer no access; real admin 200 for Dashboard, Team, Mediathek, API and assets; `/_internal/admin-auth` 204 only for admin, and direct anonymous admin mount never returns content.
6. Verify the new CSP allows base-uri 'self' only under mount and maintains frame-ancestors 'none', no-store, nosniff. Confirm correct relative resources from the prefix and no cross-site credentials.
7. Preserve old dashboard image/Compose config for rollback and compare task counts/state and recent audit events after switch. **Do not roll back the live SQLite state automatically**, it may lose writes.
8. Manual approval after acceptance only. Keep Fiverr NO_GO and BC27 gates independent.

## Status recording
After operator supplies runtime logs, record actual SHA/image ID, backup hash, nginx config backup hash, sanitized negative-auth test statuses, manual reviewer, and date in `tools/ai-control-center/data/evidence-status.json` as a new verified observation. Update the curated evidence on the deployed dashboard branch via a separate reviewed PR/CI. Do not modify tracker checkmarks or claim the Admin mount is active until HTTP tests pass.
