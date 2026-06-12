# Production Deployment

Status: P2.12 go-live readiness baseline.

## Required release order

1. Build the backend image.
2. Start PostgreSQL and wait until it is healthy.
3. Run Alembic migrations:

```bash
docker compose -f docker-compose.prod.yml run --rm migration
```

This executes:

```bash
python -m alembic upgrade head
```

4. Start or restart the API:

```bash
docker compose -f docker-compose.prod.yml up -d backend
```

The API validates the database revision during startup and exits if the database is not at the current Alembic head. Do not bypass this check in production.

## Production ENV minimum

- `ENV=prod`
- `APP_ENV=prod`
- `DATABASE_URL`
- `SECRET_KEY` with at least 32 random characters
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD` with at least 16 characters
- `APP_BASE_URL=https://api.bcsentinel.com`
- `CORS_ALLOW_ORIGINS=https://bcsentinel.com,https://www.bcsentinel.com`
- `TENANT_REGISTRATION_INVITE_CODE`
- Stripe keys and Price IDs for enabled paid products

`CORS_ALLOW_ORIGINS` must be explicit in production. Do not include `https://dev.bcsentinel.com` in production CORS.

## Reverse proxy

The compose file binds the backend to `127.0.0.1:8000`. Put TLS in front of it with nginx, Caddy, Traefik, or a managed load balancer.

The repository includes a minimal nginx example at `config/nginx/bcsentinel.conf`. It covers:

- HTTP to HTTPS redirect.
- TLS termination.
- `Host`, `X-Forwarded-Proto`, `X-Forwarded-For`, `X-Real-IP`, and `X-Request-Id`.
- Proxying to `127.0.0.1:8000`.
- Explicit Stripe webhook route at `/billing/webhook`.
- Optional Admin IP allowlist block.

## Smoke checks

After deployment:

```bash
curl -i https://api.bcsentinel.com/health
curl -i https://api.bcsentinel.com/health/ready
```

Then run the manual checklist in `backend/GO_LIVE_SMOKE_TESTS.md`, especially tenant auth, scan sync, report share links, Stripe checkout, Stripe webhook delivery, and Admin UI.
