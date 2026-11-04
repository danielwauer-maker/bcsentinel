(function () {
    "use strict";

    var root = null;
    var latestPayload = null;
    var ready = false;

    function clamp(value) {
        var parsed = Number(value);
        return Number.isFinite(parsed) ? Math.max(0, Math.min(100, Math.round(parsed))) : 0;
    }
    function node(tag, className, textValue) {
        var element = document.createElement(tag);
        if (className) element.className = className;
        if (textValue !== undefined && textValue !== null) element.textContent = String(textValue);
        return element;
    }
    function localize(key, language) {
        var de = language === "de";
        var labels = {
            progress: ["Overall progress", "Gesamtfortschritt"],
            modules: ["Module progress", "Modulfortschritt"],
            scores: ["Module scores", "Modul-Scores"],
            checks: ["Checks", "Prüfungen"],
            issues: ["Findings", "Auffälligkeiten"],
            health: ["Data Health Score", "Data Health Score"],
            empty: ["No scan selected", "Kein Scan ausgewählt"],
            finalizing: ["Finalizing", "Finalisierung"],
            completed: ["Completed", "Abgeschlossen"],
            failed: ["Failed", "Fehlgeschlagen"],
            running: ["Running", "Wird ausgeführt"],
            queued: ["Queued", "In Warteschlange"],
            canceled: ["Canceled", "Abgebrochen"]
        };
        return labels[key] ? labels[key][de ? 1 : 0] : key;
    }
    function statusClass(status) {
        var value = String(status || "").toLowerCase();
        if (value === "completed") return "done";
        if (value === "failed" || value === "canceled") return "error";
        if (value === "running" || value === "finalizing") return "active";
        return "neutral";
    }
    function progressBar(value, label, className) {
        var outer = node("div", "bcs-bar " + (className || ""));
        outer.setAttribute("role", "progressbar");
        outer.setAttribute("aria-label", label);
        outer.setAttribute("aria-valuemin", "0");
        outer.setAttribute("aria-valuemax", "100");
        outer.setAttribute("aria-valuenow", String(clamp(value)));
        var fill = node("div", "bcs-bar-fill");
        fill.style.width = clamp(value) + "%";
        outer.appendChild(fill);
        return outer;
    }
    function metric(label, value, detail, variant) {
        var card = node("div", "bcs-metric " + (variant || ""));
        card.appendChild(node("div", "bcs-metric-label", label));
        card.appendChild(node("div", "bcs-metric-value", value));
        if (detail) card.appendChild(node("div", "bcs-metric-detail", detail));
        return card;
    }
    function render() {
        if (!root) return;
        root.replaceChildren();
        var data = latestPayload || {};
        var lang = String(data.language || "en").toLowerCase() === "de" ? "de" : "en";
        var status = String(data.status || "queued").toLowerCase();
        if (!data.runId) {
            root.appendChild(node("div", "bcs-empty", localize("empty", lang)));
            return;
        }
        var header = node("div", "bcs-header");
        var identity = node("div", "bcs-header-main");
        identity.appendChild(node("div", "bcs-eyebrow", "BCSentinel · Scan Monitor"));
        identity.appendChild(node("div", "bcs-run", data.runId));
        header.appendChild(identity);
        var pill = node("span", "bcs-status " + statusClass(status), localize(status, lang));
        header.appendChild(pill);
        root.appendChild(header);

        var grid = node("div", "bcs-metrics");
        var hasScore = status === "completed";
        var score = clamp(data.score);
        grid.appendChild(metric(localize("health", lang), hasScore ? score + "/100" : "—", hasScore ? (score < 60 ? (lang === "de" ? "Kritisch" : "Critical") : score < 80 ? (lang === "de" ? "Erhöht" : "Elevated") : (lang === "de" ? "Gut" : "Good")) : "", hasScore ? "score" : ""));
        grid.appendChild(metric(localize("checks", lang), Math.max(0, Number(data.checks) || 0).toLocaleString(lang === "de" ? "de-DE" : "en-US")));
        grid.appendChild(metric(localize("issues", lang), Math.max(0, Number(data.issues) || 0).toLocaleString(lang === "de" ? "de-DE" : "en-US")));
        root.appendChild(grid);

        var overall = node("section", "bcs-section");
        var row = node("div", "bcs-section-header");
        row.appendChild(node("div", "bcs-title", localize("progress", lang)));
        row.appendChild(node("div", "bcs-percentage", clamp(data.progress) + "%"));
        overall.appendChild(row);
        overall.appendChild(progressBar(data.progress, localize("progress", lang), statusClass(status)));
        var context = node("div", "bcs-context");
        context.appendChild(node("span", "", data.currentModule || localize("finalizing", lang)));
        if (data.currentStep) context.appendChild(node("span", "", data.currentStep));
        overall.appendChild(context);
        root.appendChild(overall);

        var modules = Array.isArray(data.modules) ? data.modules : [];
        var columns = node("div", "bcs-columns");
        var progress = node("section", "bcs-panel");
        progress.appendChild(node("h3", "bcs-title", localize("modules", lang)));
        var scores = node("section", "bcs-panel");
        scores.appendChild(node("h3", "bcs-title", localize("scores", lang)));
        modules.forEach(function (m) {
            var moduleName = String(m.name || "");
            var pr = clamp(m.progress);
            var sr = clamp(m.score);
            var line = node("div", "bcs-module");
            var labels = node("div", "bcs-module-labels");
            labels.appendChild(node("span", "", moduleName));
            labels.appendChild(node("span", "", pr + "%"));
            line.appendChild(labels);
            line.appendChild(progressBar(pr, moduleName + " " + localize("progress", lang), statusClass(status)));
            progress.appendChild(line);

            var scoreLine = node("div", "bcs-module");
            var scoreLabels = node("div", "bcs-module-labels");
            scoreLabels.appendChild(node("span", "", moduleName));
            scoreLabels.appendChild(node("span", "", status === "completed" ? sr + "/100" : "—"));
            scoreLine.appendChild(scoreLabels);
            scoreLine.appendChild(progressBar(status === "completed" ? sr : 0, moduleName + " " + localize("scores", lang), status === "completed" ? (sr < 60 ? "error" : sr < 80 ? "warning" : "done") : "neutral"));
            scores.appendChild(scoreLine);
        });
        columns.appendChild(progress);
        columns.appendChild(scores);
        root.appendChild(columns);
    }
    function initialize() {
        if (ready) return;
        var host = document.getElementById("controlAddIn") || document.body;
        if (!host) throw new Error("Business Central control host is unavailable.");
        root = node("main", "bcs-root");
        root.setAttribute("aria-label", "BCSentinel Scan Monitor");
        host.appendChild(root);
        ready = true;
        render();
        if (window.Microsoft && window.Microsoft.Dynamics && window.Microsoft.Dynamics.NAV &&
            typeof window.Microsoft.Dynamics.NAV.InvokeExtensibilityMethod === "function") {
            window.Microsoft.Dynamics.NAV.InvokeExtensibilityMethod("ControlReady", []);
        }
    }
    window.SetScanData = function (raw) {
        try {
            latestPayload = JSON.parse(String(raw || "{}"));
        } catch (e) {
            latestPayload = null;
        }
        if (ready) render();
    };
    // Called by the dedicated StartupScript after this library has loaded.
    window.BCSentinelScanVisualInit = initialize;
})();