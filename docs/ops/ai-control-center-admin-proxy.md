# AI Control Center behind BCSentinel Admin

Status: Draft architecture and source validation only. This change does not deploy,
restart, reconfigure or otherwise alter the running Control Center on port 8092.

## Decision

The existing AI-PM 2.2/2.3 application remains a separate, read-only service. It
is mounted by nginx below `/admin/ai-control-center` and authenticated through the
existing BCSentinel administrator Basic-Auth dependency. Tenant account sessions,
tenant membership roles (`VIEWER` and tenant `ADMIN`) and customer API tokens never
grant this access.

```text
browser -- TLS + existing Admin Basic credentials --> nginx
                                                    | auth_request
                                                    v
                                           BCSentinel :8000/:8001
                                                    |
                                                    | 204 only for an administrator
                                                    v
                    nginx -- opaque proxy token --> AI Control Center 127.0.0.1:8092
```

The Control Center never receives the administrator's Basic authorization header.
After successful `auth_request`, nginx overwrites any client-supplied
`X-AI-Control-Center-Proxy-Auth` header with a root-only random token. When
`PROXY_AUTH_TOKEN` is configured, the Control Center accepts only this header; its
legacy local Basic credentials are deliberately ignored. A direct request to 8092
therefore has neither public reachability nor a usable application credential.

## Source changes

- `backend/app/routers/admin.py` adds a no-data `/_internal/admin-auth` endpoint
  protected by the already used `require_admin` dependency and an AI Control Center
  navigation entry. It does not create an administrator, session or role.
- `config/nginx/bcsentinel.conf` protects the exact mount path and every descendant
  path in all production and DEV API/site vhosts. The same authentication covers
  HTML, APIs, media, static assets and HTTP Upgrade/WebSocket requests.
- `tools/ai-control-center/app.py` supports proxy-token mode and rewrites only its
  own same-origin absolute links, script URLs and `fetch` calls below the configured
  `URL_PREFIX`. The existing dashboard, executive view, PR view, evidence data,
  team view and media library remain the same application.
- `tools/ai-control-center/compose.example.yml` retains loopback publication. The
  current server-specific `127.0.0.1:8092:8090` override must be retained; it is not
  versioned or changed by this branch.

## Required operator acceptance after explicit deployment approval

1. Verify the existing listener is exactly loopback-bound (`127.0.0.1:8092`) and
   not reachable by public IPv4/IPv6, Docker publish-all, another proxy route or a
   host-network container. Do not change the listener while checking it.
2. Confirm nginx has the `auth_request` module and create the root-owned,
   mode-0600 include file
   `/etc/nginx/snippets/bcsentinel-ai-control-center-proxy-auth.conf`. It must have
   exactly one directive:

   ```nginx
   proxy_set_header X-AI-Control-Center-Proxy-Auth "<new random token>";
   ```

   Put the same unique token only in the Control Center's uncommitted environment
   as `PROXY_AUTH_TOKEN`; set
   `URL_PREFIX=/admin/ai-control-center`. Do not copy `ADMIN_PASSWORD`, customer
   credentials, database passwords or GitHub tokens into the nginx file.
3. Validate nginx syntax before a reload. The missing include is intentionally a
   fail-closed configuration error, not a fallback to an unprotected route.
4. On a dedicated DEV preview, verify unauthenticated HTML, API, media and
   WebSocket-upgrade requests return the admin authentication challenge; verify an
   authorized administrator can load Dashboard, Executive Dashboard, PR overview,
   Sprint Evidence, Team and Mediathek below the prefix.
5. Re-run the existing dashboard/backend regressions and inspect the Control Center
   process/container mounts and networks. It must remain separate from product
   PostgreSQL, tenant data, and the BCSentinel DEV/PROD networks.

## Blockers and non-goals

- Live nginx module availability, the real 8092 bind, IPv6/firewall state and the
  current service environment are not observable from this checkout. They are
  mandatory operator acceptance gates, not asserted as completed here.
- The Control Center currently reads its own isolated SQLite state, read-only Excel
  mount and optional GitHub/DEV health data. This integration adds no BCSentinel
  database mount, tenant lookup, migration, backup change or write endpoint.
- No deployment, nginx reload, Control Center restart, data migration, backup
  operation, port change or secrets change is authorized by this draft.
