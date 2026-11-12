FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8090
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 control
COPY app.py project_store.py pm_sync.py pm_mapping.py readiness.py progress_history.py acceptance_review.py blocker_plan.py task_coverage.py pm_insights.py ai_pm_brief.py agent_control.py team_roster.py backup_verify.py index.html team.html light-theme.css executive.js ./
COPY data/evidence-status.json ./data/evidence-status.json
USER control
EXPOSE 8090
CMD ["python", "app.py"]
