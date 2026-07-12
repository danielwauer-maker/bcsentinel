# REPORT-RUNTIME-01 - Persistent Playwright & Chromium PDF Runtime

## Problem

Das Python-Paket `playwright==1.48.0` war im Backend-Image installiert, Chromium und seine Linux-Systembibliotheken jedoch nicht. Manuelle Installationen in laufenden Containern gingen beim nächsten Image-Rebuild verloren. Der Executive-Report fiel dann auf den Emergency-Text-PDF-Renderer zurück.

## Image-Härtung

`backend/Dockerfile` installiert jetzt im gemeinsamen Base-Stage:

```dockerfile
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN python -m playwright install --with-deps chromium
```

`--with-deps` installiert sowohl das zur gepinnten Playwright-Version passende Chromium als auch die erforderlichen Debian-Laufzeitbibliotheken. Der gemeinsame Pfad `/ms-playwright` verhindert, dass Chromium nur im Root-Home liegt und für den nicht privilegierten `appuser` unsichtbar bleibt.

Der Build setzt lesbare/ausführbare Rechte für alle Benutzer und startet Chromium bereits während des Builds. Dabei wird ein A4-Test-PDF erzeugt und dessen `%PDF-`-Signatur geprüft. Ein Image ohne startfähiges Chromium kann deshalb nicht erfolgreich gebaut werden.

## Runtime-Verifikation

Das Image enthält:

```bash
python scripts/verify_playwright_runtime.py
```

Der Befehl prüft Browserpfad, Chromium-Start und echte PDF-Erzeugung. Er eignet sich für Deployment-Smoke-Tests:

```bash
docker compose -f docker-compose.prod.yml run --rm backend python scripts/verify_playwright_runtime.py
```

## Betrieb

Nach Änderungen an Playwright oder dem Dockerfile muss das Backend-Image neu gebaut werden:

```bash
docker compose -f docker-compose.prod.yml build --no-cache backend
docker compose -f docker-compose.prod.yml up -d backend
docker compose -f docker-compose.prod.yml exec backend python scripts/verify_playwright_runtime.py
```

Manuelle `playwright install`-Aufrufe im laufenden Container sind nicht mehr erforderlich und sollen nicht verwendet werden.

## Fehlerdiagnose

Falls der HTML-Renderer trotz gehärtetem Image ausfällt, protokolliert `render_executive_report_pdf()` jetzt den vollständigen Exception-Stack sowie Scan- und Report-ID, bevor der Emergency-Fallback verwendet wird.

## Tests

- Gepinnte Playwright-Version wird geprüft.
- Dockerfile muss `PLAYWRIGHT_BROWSERS_PATH`, `--with-deps chromium`, Berechtigungsfreigabe, Browserstart und PDF-Signaturprüfung enthalten.
- Der vorhandene Executive-Report-Test prüft weiterhin HTML-Renderer, PDF-Signatur und Zwei-Seiten-Ausgabe.

## Bekannte Einschränkung

Chromium vergrößert das Backend-Image deutlich. Dies ist für eine reproduzierbare, offline startfähige PDF-Runtime beabsichtigt.
