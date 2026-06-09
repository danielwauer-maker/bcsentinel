FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/alembic.ini ./alembic.ini
COPY --chown=appuser:appuser backend/alembic ./alembic
COPY --chown=appuser:appuser landingpage ./landingpage

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
