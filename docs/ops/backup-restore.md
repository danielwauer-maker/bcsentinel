# Backup and Restore

Status: Phase 1 manual checklist.

## Backup minimum

- Back up the PostgreSQL volume or run `pg_dump` daily during pilot operation.
- Store backups encrypted and outside the application host.
- Keep at least 7 daily backups for pilot operation unless the customer agreement says otherwise.
- Protect `.env.prod` separately; database backups alone are not enough to restore service.

## Manual backup command example

Run from the production host with the correct compose project:

```bash
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > bcsentinel-backup.sql
```

## Manual restore checklist

1. Start a fresh PostgreSQL instance.
2. Restore the dump into the target database.
3. Confirm `alembic_version` equals the backend required revision.
4. Start backend and check `/health/ready`.
5. Run a known tenant auth check.
6. Load Admin UI and verify tenant/scans.
7. Run one non-destructive scan status/history check.

## Reverse proxy and HTTPS

- Terminate TLS in a reverse proxy such as nginx, Caddy, Traefik, or a managed load balancer.
- Expose the backend only through HTTPS.
- Keep the compose backend bound to `127.0.0.1:8000` when running on a single host.
- Forward `X-Forwarded-Proto` and request ids if the proxy supports them.
- In production, HSTS is only emitted when the incoming request scheme is HTTPS.

## Restore test cadence

Before the first paid pilot, perform one restore into a temporary database and document:

- Backup timestamp.
- Restore duration.
- Backend health result.
- Tenant sample verified.
- Operator name and date.
