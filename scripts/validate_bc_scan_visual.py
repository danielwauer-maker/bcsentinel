"""Static contract for the embedded BCSentinel scan monitor Control Add-in.

This is not a replacement for Microsoft's AL compiler or a Business Central UI test.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "bc-extension" / "app" / "src"
AL = (SRC / "controladdin" / "ScanVisualAddIn.al").read_text(encoding="utf-8-sig")
PAGE = (SRC / "pages" / "DHDeepScanMonitor.Page.al").read_text(encoding="utf-8-sig")
JS = (SRC / "controladdin" / "js" / "scanvisual.js").read_text(encoding="utf-8-sig")
STARTUP = (SRC / "controladdin" / "js" / "scanvisual-startup.js").read_text(encoding="utf-8-sig")
CSS = (SRC / "controladdin" / "css" / "scanvisual.css").read_text(encoding="utf-8-sig")
REPORT_ACTIONS = (SRC / "pageextensions" / "DHDeepScanMonitorReports.PageExt.al").read_text(encoding="utf-8-sig")
REPORT_ACCESS = (SRC / "codeunits" / "DHReportAccessClient.Codeunit.al").read_text(encoding="utf-8-sig")

def check(condition: bool, description: str) -> None:
    if not condition:
        raise AssertionError(description)

def main() -> None:
    for piece in ('controladdin "BCSentinel Scan Visual"', "procedure SetScanData(JsonData: Text);",
                  "event ControlReady();", "Scripts = './js/scanvisual.js';",
                  "StartupScript = './js/scanvisual-startup.js';",
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
    check("window.BCSentinelScanVisualInit = initialize;" in JS, "Control add-in library must export explicit initialization")
    check("window.BCSentinelScanVisualInit();" in STARTUP, "Startup must initialize library after it loads")
    check('document.getElementById("controlAddIn")' in JS, "Render into BC control host")
    check("DOMContentLoaded" not in JS, "Do not wait for already-fired DOMContentLoaded")
    check("innerHTML" not in JS, "Do not inject AL-provided text through innerHTML")
    check("fetch(" not in JS and "XMLHttpRequest" not in JS,
          "Frontend must not fetch external data or handle tenant tokens")
    check("https://" not in JS and "@import" not in CSS,
          "Frontend assets must be packaged without external dependencies")
    check(".bcs-v2-fill" in CSS and ".bcs-v2-kpis" in CSS, "Missing V2 visual styles")
    # The visible menu must not expose specific report tiers; the backend
    # chooses the correct report variant for the scan and current entitlement.
    for obsolete in ("action(OpenFreeHealthReport)", "action(OpenFreeHealthPdf)",
                     "action(OpenQuickAssessmentReport)", "action(OpenQuickAssessmentPdf)",
                     "action(OpenAssessmentReport)", "action(OpenAssessmentPdf)",
                     "action(OpenValidationReport)", "action(OpenValidationPdf)"):
        check(obsolete not in REPORT_ACTIONS, f"Report tier exposed in BC action menu: {obsolete}")
    check("action(OpenBestAvailableReport)" in REPORT_ACTIONS, "Missing authorized report action")
    check("action(OpenBestAvailablePdf)" in REPORT_ACTIONS, "Missing authorized PDF action")
    check("procedure GetPreferredReportVariant(ScanId: Code[50])" in REPORT_ACCESS, "Backend preferred-report lookup missing")
    check("Caption = 'Scan Details';" in PAGE, "Duplicate overview not condensed")
    check("Visible = false; // Rendered in the add-in to avoid duplicate technical fields." in PAGE, "Native diagnostics must not duplicate V2")
    check("RequestedHeight = 800;" in AL, "Add-in must show all ten scan modules")
    # Never send paid scan results to the browser for unverified Free/Quick access.
    for expected in (
        "ResolveVisualAccess();",
        'ReportAccess.GetMonitorInsights(ScanId)',
        "VisualAccessVariant := 'unavailable';",
        "Payload.Add('canViewFullScores', (VisualAccessVariant in ['assessment', 'validation', 'monitoring']));",
        "if VisualAccessVariant in ['assessment', 'validation'] then",
        "ModuleData.Add('score', Score);",
        "Payload.Add('warning', GetDisplayWarningText());",
    ):
        check(expected in PAGE, "Missing gated AL field or event: " + expected)
    for expected in (
        "data.canViewFullScores === true",
        'data.accessTier === "assessment"',
        'data.accessTier === "validation"',
        "typeof data.issues ===",
        "data.events",
        "bcs-v2-disclosure",
        'button.addEventListener("click"',
        "aria-expanded",
        "bcs-v2-hero",
    ):
        check(expected in JS, "Missing client gating or UX behavior: " + expected)
    check("Visible = false; // The graphical add-in renders these details" in PAGE,
          "Native scan detail group must not duplicate the add-in")
    check("Visible = false; // Rendered in the add-in" in PAGE,
          "Native diagnostics must not duplicate the add-in")
    check(".bcs-v2-hero" in CSS and ".bcs-v2-disclosure" in CSS, "Missing V2 styles")
    check("#controlAddIn { height: 100%; max-height: 100%; overflow-x: hidden; overflow-y: auto;" in CSS,
          "Control Add-in must scroll internally when long")
    check("Payload.Add('insights', VisualInsights);" in PAGE, "Missing server-vetted report data")
    check('procedure GetMonitorInsights(ScanId: Code[50])' in REPORT_ACCESS, "Missing monitor insights client")
    check('data.insights && data.insights.tier === data.accessTier' in JS, "Frontend must validate matching tier")

    print("Embedded scan Control Add-in static contract: PASS")
    print("AL: Package and sandbox UI acceptance still required.")

if __name__ == "__main__":
    main()
