"""Fail fast when the container image has no usable Playwright Chromium runtime."""

from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as playwright:
        executable = Path(playwright.chromium.executable_path)
        if not executable.is_file():
            raise SystemExit(f"Playwright Chromium binary is missing: {executable}")
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content("<html><body>BCSentinel PDF runtime</body></html>")
            pdf = page.pdf(format="A4", print_background=True)
        finally:
            browser.close()

    if not pdf.startswith(b"%PDF-"):
        raise SystemExit("Chromium started, but did not produce a valid PDF.")
    print(f"Playwright Chromium PDF runtime ready: {executable}")


if __name__ == "__main__":
    main()
