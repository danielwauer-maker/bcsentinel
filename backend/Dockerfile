FROM python:3.11-slim-bookworm AS builder

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps chromium \
    && chmod -R a+rX "${PLAYWRIGHT_BROWSERS_PATH}" \
    && python -c "from pathlib import Path; from playwright.sync_api import sync_playwright; p = sync_playwright().start(); executable = Path(p.chromium.executable_path); browser = p.chromium.launch(headless=True); page = browser.new_page(); pdf = page.pdf(format='A4'); browser.close(); p.stop(); assert executable.is_file(), f'Chromium missing: {executable}'; assert pdf.startswith(b'%PDF-'); print(f'Playwright Chromium PDF runtime ready: {executable}')"

FROM python:3.11-slim-bookworm AS runtime

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /ms-playwright /ms-playwright

RUN python -m playwright install --with-deps chromium \
    && chmod -R a+rX "${PLAYWRIGHT_BROWSERS_PATH}" \
    && useradd --create-home --shell /usr/sbin/nologin appuser

COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/alembic.ini ./alembic.ini
COPY --chown=appuser:appuser backend/alembic ./alembic
COPY --chown=appuser:appuser backend/scripts/verify_playwright_runtime.py ./scripts/verify_playwright_runtime.py
COPY --chown=appuser:appuser landingpage ./landingpage

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS test

USER root
COPY --chown=appuser:appuser backend/tests ./tests
USER appuser

CMD ["python", "-m", "pytest", "-p", "no:cacheprovider", "tests"]

FROM runtime AS production
