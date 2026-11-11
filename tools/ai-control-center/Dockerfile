FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8090
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 control
COPY app.py project_store.py pm_sync.py index.html ./
COPY data/evidence-status.json ./data/evidence-status.json
USER control
EXPOSE 8090
CMD ["python", "app.py"]
