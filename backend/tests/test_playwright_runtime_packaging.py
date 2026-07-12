from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_backend_image_installs_shared_playwright_chromium_runtime():
    dockerfile = (REPOSITORY_ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright" in dockerfile
    assert "python -m playwright install --with-deps chromium" in dockerfile
    assert "chmod -R a+rX" in dockerfile
    assert "p.chromium.launch(headless=True)" in dockerfile
    assert "pdf.startswith(b'%PDF-')" in dockerfile
    assert "verify_playwright_runtime.py" in dockerfile


def test_playwright_version_is_pinned():
    requirements = (REPOSITORY_ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
    assert "playwright==1.48.0" in requirements.splitlines()
