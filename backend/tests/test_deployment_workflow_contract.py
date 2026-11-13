from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_legacy_deployment_workflow_cannot_run_on_branch_pushes():
    workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "  push:" not in workflow
    assert "test \"${{ inputs.target }}\" = \"prod\"" in workflow
    assert "dev-release.yml" in workflow


def test_dev_release_requires_manual_approval_and_current_staging_sha():
    workflow = (ROOT / ".github/workflows/dev-release.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "  push:" not in workflow
    assert 'test "$TARGET_ENVIRONMENT" = "dev"' in workflow
    assert '[[ "$RELEASE_SHA" =~ ^[0-9a-f]{40}$ ]]' in workflow
    assert 'test "$DEV_RELEASE_ENABLED" = "true"' in workflow
    assert 'test "$APPROVED_RELEASE_SHA" = "$RELEASE_SHA"' in workflow
    assert 'test "$(git rev-parse origin/staging)" = "$RELEASE_SHA"' in workflow
    assert "\n          git clean" not in workflow
    assert "cp config/nginx" not in workflow
    assert "rm -rf /var/www" not in workflow

def test_dev_release_builds_migration_image_before_running_alembic():
    workflow = (ROOT / ".github/workflows/dev-release.yml").read_text(encoding="utf-8")
    build = "docker compose -f docker-compose.dev.yml --env-file .env.dev build backend"
    migrate = "docker compose -f docker-compose.dev.yml --env-file .env.dev run --rm --no-deps backend alembic upgrade head"
    assert build in workflow
    assert migrate in workflow
    assert workflow.index(build) < workflow.index(migrate)


def test_dev_nginx_permission_preflight_precedes_checkout_mutation():
    workflow = (ROOT / ".github/workflows/dev-release.yml").read_text(encoding="utf-8")
    preflight = "sudo -n /usr/sbin/nginx -t"
    reset = 'git reset --hard "$RELEASE_SHA"'
    assert workflow.count(preflight) == 1
    assert preflight in workflow
    assert reset in workflow
    assert workflow.index(preflight) < workflow.index(reset)
