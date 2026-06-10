# Deployment Dry Run

Datum: 2026-06-10

Umgebung: lokale Repository-Pruefung auf Windows/Codex-Arbeitsplatz. Docker, Python, Alembic, pytest und nginx waren in dieser Umgebung nicht auf PATH verfuegbar. Deshalb sind alle Infrastruktur- und Runtime-Schritte, die diese Tools benoetigen, als NOT EXECUTED markiert.

## Scope

- DEV Compose: `docker-compose.dev.yml`
- PROD Compose: `docker-compose.prod.yml`
- Backend Image: `backend/Dockerfile`
- Nginx: `config/nginx/bcsentinel.conf`
- Alembic Migrationen: `backend/alembic/versions`
- Healthchecks: `/health`, `/health/ready`
- Landingpage static files: `landingpage/*.html`, `landingpage/js`, `landingpage/lang`
- Admin Translations: `SITE_TRANSLATIONS_PATH=/app/landingpage/lang`

## Ausgefuehrte Checks

| Check | Befehl | Ergebnis |
|---|---|---|
| Toolchain vorhanden | `Get-Command docker, python, py, pytest, alembic, node, nginx` | PARTIAL: nur `node` gefunden |
| DEV Compose gelesen | `Get-Content docker-compose.dev.yml` | PASS |
| PROD Compose gelesen | `Get-Content docker-compose.prod.yml` | PASS |
| Dockerfile gelesen | `Get-Content backend/Dockerfile` | PASS |
| Nginx Config gelesen | `Get-Content config/nginx/bcsentinel.conf` | PASS |
| Alembic Versionen inventarisiert | `Get-ChildItem backend/alembic/versions` | PASS: Head-Datei `0017_tenant_preferred_language.py` vorhanden |
| Landingpage JSON parse | `node -e "...JSON.parse..."` | PASS: `de.json` und `en.json` jeweils 775 Keys, 0 leere Werte |
| Landingpage JS Syntax | `node --check landingpage/script.js`; `node --check landingpage/js/site-shell.js` | PASS |
| Legacy/Mojibake Landingpage | `rg` nach alten sichtbaren Produktbegriffen und Mojibake-Mustern in `landingpage` | PASS fuer sichtbare Werte |
| Backend Test Packaging | `backend/Dockerfile`, `.dockerignore`, `docker-compose.dev.yml`, `docker-compose.prod.yml` geprueft | PASS: Runtime/Production Images bleiben ohne Tests; DEV hat separaten `backend-tests` Service |

## Nicht ausgefuehrte Runtime-Checks

| Check | Soll-Befehl | Status | Grund |
|---|---|---|---|
| Alembic Upgrade | `cd backend && alembic upgrade head` | NOT EXECUTED | `alembic`/`python` nicht verfuegbar |
| Docker Build | `docker compose -f docker-compose.dev.yml build` | NOT EXECUTED | `docker` nicht verfuegbar |
| Docker Start | `docker compose -f docker-compose.dev.yml up -d` | NOT EXECUTED | `docker` nicht verfuegbar |
| Nginx Syntax | `sudo nginx -t` | NOT EXECUTED | `nginx` nicht verfuegbar, Zielserverzugriff nicht vorhanden |
| Backend Health | `curl -fsS http://127.0.0.1:8001/health/ready` | NOT EXECUTED | Backend nicht gestartet |
| Landingpage Health | `curl -fsS https://dev.bcsentinel.com/` | NOT EXECUTED | kein Live-Serverzugriff aus dieser Umgebung |
| Admin Login Smoke | `GET /admin` plus Login | NOT EXECUTED | Backend nicht gestartet |
| Dashboard Smoke | `GET /analytics/embed?...` | NOT EXECUTED | benoetigt Tenant/API-Kontext |
| Report HTML Smoke | `GET /reports/executive/{scan_id}/html` | NOT EXECUTED | benoetigt Tenant/API-Kontext |
| Report PDF Smoke | `GET /reports/executive/{scan_id}/pdf` | NOT EXECUTED | benoetigt Tenant/API-Kontext |
| Product Licensing Tests im Container | `docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_product_licensing_p0.py` | NOT EXECUTED | `docker` nicht verfuegbar in dieser Umgebung |
| Billing Tests im Container | `docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_billing.py` | NOT EXECUTED | `docker` nicht verfuegbar in dieser Umgebung |
| Executive Report Tests im Container | `docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_executive_report.py` | NOT EXECUTED | `docker` nicht verfuegbar in dieser Umgebung |
| Localization Tests im Container | `docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_localization.py` | NOT EXECUTED | `docker` nicht verfuegbar in dieser Umgebung |

## Befund

PASS:

- `backend/Dockerfile` baut aus Repo-Root und kopiert `landingpage ./landingpage` in das Backend-Image.
- DEV und PROD mounten `./landingpage/lang:/app/landingpage/lang`.
- `SITE_TRANSLATIONS_PATH` ist in DEV und PROD auf `/app/landingpage/lang` gesetzt.
- Compose-Healthcheck prueft `/health/ready`.
- PROD enthaelt einen separaten `migration` Service mit `python -m alembic upgrade head`.
- Nginx liefert `/docs` und `/docs.html` statisch aus `docs.html` aus und proxyt Backend-Routen getrennt.
- PROD bindet Backend nur auf `127.0.0.1:8000`.
- `backend/tests/` existiert im Repository, wird aber nur in den Dockerfile-Target `test` kopiert.
- `docker-compose.dev.yml` enthaelt den DEV-only Service `backend-tests`.
- `docker-compose.prod.yml` baut explizit den testfreien Target `production`.

WARN:

- DEV Compose hat keinen expliziten Migration-Service. DEV-Runbook sollte vor API-Start `alembic upgrade head` ausfuehren.
- Admin Translation Fix braucht einen echten Image-Rebuild/Container-Restart, weil Dockerfile und Compose geaendert wurden.
- `.env.example` enthaelt `APP_BASE_URL=http://localhost:3000` als Beispielwert; fuer PROD muss `APP_BASE_URL` zwingend oeffentlich gesetzt sein.
- `backend/tests/test_billing.py` enthaelt noch alte Testannahmen aus dem frueheren Planmodell und muss nach dem Product-Code-Checkout-Fix erwartbar angepasst werden.

FAIL / offen:

- Kein ausgefuehrter Docker-/Nginx-/Alembic-Dry-Run in dieser Umgebung moeglich.
- Backup/Restore wurde nicht praktisch getestet.
- Keine Live-Smoke-Tests fuer Admin, Dashboard, Reports.

## Fixes in diesem Block

- Sichtbare alte Landingpage-CTAs auf `loss-examples.html` entfernt.
- Sichtbare Encoding-/Textfehler auf Billing Success/Cancel bereinigt.
- Landingpage i18n-Wert des alten Produktvergleich-Keys auf `Produkte/Products` gesetzt; Key-Name aus Kompatibilitaetsgruenden belassen.

## Rollback

DEV:

```powershell
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
```

PROD:

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml --profile tools run --rm migration
docker compose -f docker-compose.prod.yml up -d --build backend
sudo nginx -t && sudo systemctl reload nginx
```

Wichtig: keine Docker-Volumes loeschen. Kein `docker compose down -v` fuer Rollback verwenden.

## Backup/Restore-Test

Status: NOT EXECUTED.

Soll fuer DEV/PROD vor Pilot:

```bash
pg_dump "$DATABASE_URL" > backup-before-pilot.sql
psql "$RESTORE_TEST_DATABASE_URL" < backup-before-pilot.sql
```

Akzeptanz:

- Restore-Testdatenbank startet.
- `alembic_version` entspricht Head.
- `/health/ready` ist gruen.
- Ein Report/Dashboard-Testtenant ist lesbar.

## Finale Go/No-Go-Bewertung

Go fuer handgefuehrten Pilot erst nach erfolgreichem realem Dry Run auf DEV:

1. `docker compose -f docker-compose.dev.yml build`
2. `docker compose -f docker-compose.dev.yml up -d`
3. `docker compose -f docker-compose.dev.yml exec backend python -m alembic upgrade head`
4. `/health/ready` gruen
5. Admin Translation Seite kann `landingpage/lang/de.json` und `en.json` lesen
6. Landingpage-Unterseiten liefern 200
7. `docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_product_licensing_p0.py`
8. `docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_billing.py tests/test_executive_report.py tests/test_localization.py`

Aktueller Status dieses Dokuments: PREPARED, aber Runtime-Dry-Run NOT EXECUTED.
