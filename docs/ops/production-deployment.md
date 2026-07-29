# Production Deployment

Status: P2.12 go-live readiness baseline plus LP-LEGAL-02 contact delivery.

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

## Public contact delivery (Brevo)

LP-LEGAL-02 requires the following production settings in `.env.prod` or the deployment secret store:

```env
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=<Brevo-SMTP-Login>
SMTP_PASSWORD=<Brevo-SMTP-Key>
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=<verified-sender@bcsentinel.com>
SMTP_FROM_NAME=BCSentinel
CONTACT_RECIPIENT_EMAIL=support@bcsentinel.com
CONTACT_RATE_LIMIT_ATTEMPTS=5
CONTACT_RATE_LIMIT_WINDOW_SECONDS=600
```

Requirements:

- `SMTP_FROM_EMAIL` must be verified in Brevo.
- `SMTP_PASSWORD` must exist only in the server-side secret store.
- Never expose Brevo credentials in landing-page JavaScript, logs, screenshots, or repository files.
- Remove any legacy FormSubmit configuration or secrets from the deployment environment.
- Confirm that the Brevo data-processing agreement and current subprocessor information have been reviewed.

The endpoint is `POST /public/contact`. Missing mail configuration returns `503`; provider delivery failures return `502` without exposing provider secrets.

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

Validate the contact endpoint with a controlled test address and non-sensitive message:

```bash
curl -i https://api.bcsentinel.com/public/contact \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://www.bcsentinel.com' \
  --data '{
    "name":"BCSentinel Deployment Test",
    "email":"verified-test-address@example.com",
    "company":"BCSentinel",
    "topic":"Support",
    "message":"Controlled production contact delivery smoke test.",
    "locale":"en",
    "website":null
  }'
```

Expected result:

- HTTP `202`
- JSON field `accepted: true`
- message delivered to `CONTACT_RECIPIENT_EMAIL`
- reply address equals the submitted test email
- no message content appears in structured application logs

Then run the manual checklist in `backend/GO_LIVE_SMOKE_TESTS.md`, especially tenant auth, scan sync, report share links, Stripe checkout, Stripe webhook delivery, Admin UI, and public contact delivery.
