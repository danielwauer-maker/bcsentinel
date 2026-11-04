"""Static contract for the embedded BCSentinel scan monitor Control Add-in.

This is not a replacement for Microsoft's AL compiler or a Business Central UI test.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "bc-extension" / "app" / "src"
AL = (SRC / "controladdin" / "ScanVisualAddIn.al").read_text(encoding="utf-8-sig")
PAGE = (SRC / "pages" / "DHDeepScanMonitor.Page.al").read_text(encoding="utf-8-sig")
JS = (SRC / "controladdin" / "js" / "scanvisual.js").read_text(encoding="utf-8-sig")
CSS = (SRC / "controladdin" / "css" / "scanvisual.css").read_text(encoding="utf-8-sig")

def check(condition: bool, description: str) -> None:
    if not condition:
        raise AssertionError(description)

def main() -> None:
    for piece in ('controladdin "BCSentinel Scan Visual"', "procedure SetScanData(JsonData: Text);",
                  "event ControlReady();", "StartupScript = './js/scanvisual.js';",
                  "StyleSheets = './css/scanvisual.css';"):
        check(piece in AL, f"Control Add-in contract missing: {piece}")
    for piece in ('usercontrol(ScanVisual; "BCSentinel Scan Visual")',
                  "trigger ControlReady()", "ScanVisualReady := true;",
                  "CurrPage.ScanVisual.SetScanData(JsonText);", "Payload.WriteTo(JsonText);",
                  "PushScanVisual();", "Visible = false; // Replaced by graphical module progress bars.",
                  "Visible = false; // Replaced by graphical module score bars."):
        check(piece in PAGE, f"Monitor page integration missing: {piece}")
    for field in ("status", "progress", "score", "checks", "issues", "modules", "runId"):
        check(f"Payload.Add('{field}'" in PAGE, f"AL scan JSON missing {field}")
    for field in ("name", "progress", "score"):
        check(f"ModuleData.Add('{field}'" in PAGE, f"AL module JSON missing {field}")
    for piece in ("window.SetScanData", "JSON.parse(", "InvokeExtensibilityMethod",
                  "ControlReady", "aria-valuenow", "role", "progressbar", "textContent"):
        check(piece in JS, f"Safe frontend rendering / event contract missing {piece}")
    check("innerHTML" not in JS, "Do not inject AL-provided text through innerHTML")
    check("fetch(" not in JS and "XMLHttpRequest" not in JS,
          "Frontend must not fetch external data or handle tenant tokens")
    check("https://" not in JS and "@import" not in CSS,
          "Frontend assets must be packaged without external dependencies")
    check(".bcs-bar-fill" in CSS and ".bcs-metrics" in CSS, "Missing visual styles")
    print("Embedded scan Control Add-in static contract: PASS")
    print("AL: Package and sandbox UI acceptance still required.")

if __name__ == "__main__":
    main()
