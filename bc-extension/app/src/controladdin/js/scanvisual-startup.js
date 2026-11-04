(function () {
    "use strict";
    // This file runs after the Scripts library has been loaded by Business Central.
    // Keep the ready callback separate so the AL side only calls a prepared UI.
    try {
        if (typeof window.BCSentinelScanVisualInit !== "function") {
            throw new Error("BCSentinel scan visual library was not loaded.");
        }
        window.BCSentinelScanVisualInit();
    } catch (error) {
        var host = document.getElementById("controlAddIn") || document.body;
        if (host) {
            var notice = document.createElement("div");
            notice.style.cssText = "padding:24px;color:#b4232b;font:14px Segoe UI,Arial,sans-serif";
            notice.textContent = "BCSentinel Scan Monitor could not initialize. Please refresh the page.";
            host.appendChild(notice);
        }
        if (window.console && console.error) console.error("BCSentinel scan visual startup error", error);
    }
})();