(function () {
    "use strict";

    var root = null;
    var payload = {};
    var ready = false;
    var panelState = { details: false, diagnostics: false };

    function el(tag, className, value) {
        var item = document.createElement(tag);
        if (className) item.className = className;
        if (value !== undefined && value !== null) item.textContent = String(value);
        return item;
    }
    function percent(value) {
        var number = Number(value);
        return Number.isFinite(number) ? Math.max(0, Math.min(100, Math.round(number))) : 0;
    }
    function count(value, lang) {
        return Math.max(0, Number(value) || 0).toLocaleString(lang === "de" ? "de-DE" : "en-US");
    }
    function t(lang, german, english) { return lang === "de" ? german : english; }
    function identityIcon() {
        // Local, scalable vector mark: rising mountains, data bars and an
        // outlined magnifying glass. No external image or CDN is requested.
        var namespace = "http://www.w3.org/2000/svg";
        var svg = document.createElementNS(namespace, "svg");
        svg.setAttribute("viewBox", "0 0 115 74");
        svg.setAttribute("width", "82");
        svg.setAttribute("height", "54");
        svg.setAttribute("aria-hidden", "true");
        var mountain = document.createElementNS(namespace, "path");
        mountain.setAttribute("d", "M4 62 L34 25 L46 37 L69 5 L97 37 L71 23 L48 52 L36 42 Z");
        mountain.setAttribute("fill", "#FF921F");
        svg.appendChild(mountain);
        [17, 29, 41].forEach(function (height, index) {
            var bar = document.createElementNS(namespace, "rect");
            bar.setAttribute("x", String(34 + index * 16));
            bar.setAttribute("y", String(68 - height));
            bar.setAttribute("width", "12");
            bar.setAttribute("height", String(height));
            bar.setAttribute("rx", "2");
            bar.setAttribute("fill", "#fff");
            svg.appendChild(bar);
        });
        var lens = document.createElementNS(namespace, "circle");
        lens.setAttribute("cx", "83");
        lens.setAttribute("cy", "51");
        lens.setAttribute("r", "17");
        lens.setAttribute("fill", "#14213D");
        lens.setAttribute("stroke", "#fff");
        lens.setAttribute("stroke-width", "5");
        svg.appendChild(lens);
        var handle = document.createElementNS(namespace, "path");
        handle.setAttribute("d", "M95 63 L110 76");
        handle.setAttribute("stroke", "#fff");
        handle.setAttribute("stroke-width", "7");
        handle.setAttribute("stroke-linecap", "round");
        svg.appendChild(handle);
        return svg;
    }
    function bar(value, name, tone) {
        var shell = el("div", "bcs-v2-bar " + (tone || ""));
        shell.setAttribute("role", "progressbar");
        shell.setAttribute("aria-label", name);
        shell.setAttribute("aria-valuemin", "0");
        shell.setAttribute("aria-valuemax", "100");
        shell.setAttribute("aria-valuenow", String(percent(value)));
        var fill = el("div", "bcs-v2-fill");
        fill.style.width = percent(value) + "%";
        shell.appendChild(fill);
        return shell;
    }
    function metric(title, value, subtitle, tone, iconName) {
        var box = el("section", "bcs-v2-metric " + tone);
        var sign = el("div", "bcs-v2-metric-icon", iconName);
        sign.setAttribute("aria-hidden", "true");
        var text = el("div", "bcs-v2-metric-content");
        text.appendChild(el("div", "bcs-v2-metric-label", title));
        text.appendChild(el("div", "bcs-v2-metric-value", value));
        if (subtitle) text.appendChild(el("div", "bcs-v2-metric-hint", subtitle));
        box.appendChild(sign);
        box.appendChild(text);
        return box;
    }
    function moduleItem(name, value, mode) {
        var item = el("div", "bcs-v2-module");
        var captions = el("div", "bcs-v2-module-caption");
        captions.appendChild(el("span", "", name));
        captions.appendChild(el("span", "", mode === "score" ? percent(value) + "/100" : percent(value) + "%"));
        item.appendChild(captions);
        var tone = mode === "score" ? (percent(value) < 60 ? "error" : percent(value) < 80 ? "warning" : "done") : "done";
        item.appendChild(bar(value, name, tone));
        return item;
    }
    function disclosure(id, title, hint, contents) {
        var section = el("section", "bcs-v2-disclosure");
        var button = el("button", "bcs-v2-disclosure-toggle");
        button.type = "button";
        button.setAttribute("aria-expanded", panelState[id] ? "true" : "false");
        var labels = el("span", "bcs-v2-disclosure-heading");
        labels.appendChild(el("strong", "", title));
        labels.appendChild(el("small", "", hint));
        button.appendChild(labels);
        button.appendChild(el("span", "bcs-v2-chevron", panelState[id] ? "⌃" : "⌄"));
        var detail = el("div", "bcs-v2-disclosure-body");
        detail.hidden = !panelState[id];
        detail.appendChild(contents);
        button.addEventListener("click", function () {
            panelState[id] = !panelState[id];
            button.setAttribute("aria-expanded", panelState[id] ? "true" : "false");
            detail.hidden = !panelState[id];
            button.lastChild.textContent = panelState[id] ? "⌃" : "⌄";
        });
        section.appendChild(button);
        section.appendChild(detail);
        return section;
    }
    function detailField(caption, value) {
        var field = el("div", "bcs-v2-detail-field");
        field.appendChild(el("small", "", caption));
        field.appendChild(el("strong", "", value || "—"));
        return field;
    }
    function render() {
        if (!root) return;
        root.replaceChildren();
        var data = payload || {};
        var lang = String(data.language || "en").toLowerCase() === "de" ? "de" : "en";
        var status = String(data.status || "queued").toLowerCase();
        if (!data.runId) {
            root.appendChild(el("div", "bcs-v2-empty", t(lang, "Kein Scan ausgewählt", "No scan selected")));
            return;
        }
        var completed = status === "completed";
        var paid = data.canViewFullScores === true && (data.accessTier === "assessment" || data.accessTier === "validation");
        var statusLabels = {
            completed: t(lang, "Abgeschlossen", "Completed"),
            running: t(lang, "Wird ausgeführt", "Running"),
            failed: t(lang, "Fehlgeschlagen", "Failed"),
            queued: t(lang, "In Warteschlange", "Queued"),
            canceled: t(lang, "Abgebrochen", "Canceled")
        };
        var header = el("header", "bcs-v2-hero");
        var brand = el("div", "bcs-v2-brand");
        brand.appendChild(identityIcon());
        var name = el("div", "bcs-v2-brand-copy");
        name.appendChild(el("div", "bcs-v2-wordmark", "BCSentinel"));
        name.appendChild(el("div", "bcs-v2-claim", "Clean Data – Higher Impact"));
        brand.appendChild(name);
        header.appendChild(brand);
        var descriptor = el("div", "bcs-v2-heading");
        descriptor.appendChild(el("strong", "", "Scan Monitor"));
        descriptor.appendChild(el("span", "", data.runId));
        header.appendChild(descriptor);
        var state = el("div", "bcs-v2-state");
        state.appendChild(el("div", "bcs-v2-pill " + (completed ? "done" : status === "failed" ? "error" : "active"), statusLabels[status] || status));
        state.appendChild(el("small", "", completed ? t(lang, "Scan erfolgreich abgeschlossen.", "Scan completed successfully.") : String(data.currentStep || "")));
        header.appendChild(state);
        root.appendChild(header);

        var kpis = el("div", "bcs-v2-kpis");
        var scoreText = paid && completed ? percent(data.score) + "/100" : "—";
        var scoreHint = paid && completed ? (percent(data.score) < 60 ? t(lang, "Kritisch", "Critical") : percent(data.score) < 80 ? t(lang, "Erhöht", "Elevated") : t(lang, "Gut", "Good")) : t(lang, "Im freigegebenen Bericht", "See authorized report");
        kpis.appendChild(metric("Data Health Score", scoreText, scoreHint, paid && completed ? "critical" : "restricted", "◈"));
        var modules = Array.isArray(data.modules) ? data.modules : [];
        kpis.appendChild(metric(t(lang, "Prüfungen", "Checks"), count(data.checks, lang), modules.length + " " + t(lang, "Module", "modules"), "checks", "☷"));
        var findings = paid && completed && typeof data.issues === "number" ? count(data.issues, lang) : "—";
        kpis.appendChild(metric(t(lang, "Auffälligkeiten", "Findings"), findings,
            paid && completed ? t(lang, "Findings, keine Datensätze", "Finding count, not records") : t(lang, "Details im Bericht", "Details in report"), "issues", "!"));
        root.appendChild(kpis);

        var overview = el("section", "bcs-v2-card bcs-v2-overall");
        var caption = el("div", "bcs-v2-overall-caption");
        caption.appendChild(el("strong", "", t(lang, "Gesamtfortschritt", "Overall progress")));
        caption.appendChild(el("strong", "bcs-v2-percent", percent(data.progress) + "%"));
        overview.appendChild(caption);
        overview.appendChild(bar(data.progress, t(lang, "Gesamtfortschritt", "Overall progress"), completed ? "done" : status === "failed" ? "error" : "active"));
        overview.appendChild(el("small", "bcs-v2-note", String(data.currentStep || data.currentModule || "")));
        root.appendChild(overview);

        var columns = el("div", "bcs-v2-columns");
        var progressPanel = el("section", "bcs-v2-card bcs-v2-panel");
        progressPanel.appendChild(el("h3", "", t(lang, "Modulfortschritt", "Module progress")));
        progressPanel.appendChild(el("p", "bcs-v2-subtitle", t(lang, "Technischer Scanfortschritt je Modul", "Technical scan progress per module")));
        var scorePanel = el("section", "bcs-v2-card bcs-v2-panel");
        scorePanel.appendChild(el("h3", "", t(lang, "Modul-Scores", "Module scores")));
        scorePanel.appendChild(el("p", "bcs-v2-subtitle", t(lang, "Datenqualität je Modul (0–100 Punkte)", "Data quality by module (0–100)")));
        modules.forEach(function (module) {
            progressPanel.appendChild(moduleItem(String(module.name || ""), module.progress, "progress"));
            if (paid && completed && Object.prototype.hasOwnProperty.call(module, "score"))
                scorePanel.appendChild(moduleItem(String(module.name || ""), module.score, "score"));
        });
        if (!paid) {
            var gate = el("div", "bcs-v2-locked");
            gate.appendChild(el("strong", "", t(lang, "Detail-Scores geschützt", "Detailed scores restricted")));
            gate.appendChild(el("p", "", t(lang,
                "Die vollständigen Modul-Scores werden nur mit der entsprechenden Assessment- oder Validation-Berechtigung angezeigt. Ihr Scanfortschritt bleibt sichtbar.",
                "Complete module scores require authorized Assessment or Validation access. Scan progress remains visible.")));
            scorePanel.appendChild(gate);
        } else if (!completed) {
            scorePanel.appendChild(el("p", "bcs-v2-locked", t(lang, "Modul-Scores nach Scanabschluss verfügbar.", "Module scores available after scan completion.")));
        }
        columns.appendChild(progressPanel);
        columns.appendChild(scorePanel);
        root.appendChild(columns);

        var details = el("div", "bcs-v2-details-grid");
        details.appendChild(detailField(t(lang, "Status", "Status"), statusLabels[status] || status));
        details.appendChild(detailField(t(lang, "Aktuelles Modul", "Current module"), data.currentModule));
        details.appendChild(detailField(t(lang, "Startzeit", "Started"), data.startedAt));
        details.appendChild(detailField(t(lang, "Abschlusszeit", "Finished"), data.finishedAt));
        details.appendChild(detailField(t(lang, "Letzter Heartbeat", "Last heartbeat"), data.lastHeartbeat));
        details.appendChild(detailField("ETA", data.eta));
        root.appendChild(disclosure("details", t(lang, "Scan Details", "Scan details"),
            t(lang, "Zeiten, Status und technische Informationen", "Timing, status and technical information"), details));

        var diagnostics = el("div", "bcs-v2-diagnostics");
        if (data.error) diagnostics.appendChild(el("p", "bcs-v2-error", data.error));
        if (data.warning) diagnostics.appendChild(el("p", "bcs-v2-warning", data.warning));
        var events = String(data.events || "").split("|").map(function (x) { return x.trim(); }).filter(Boolean);
        if (events.length) {
            var list = el("ol", "bcs-v2-events");
            events.forEach(function (eventText) {
                list.appendChild(el("li", "", eventText));
            });
            diagnostics.appendChild(list);
        }
        if (!data.error && !data.warning && !events.length)
            diagnostics.appendChild(el("p", "bcs-v2-muted", t(lang, "Keine Ereignisse oder Meldungen vorhanden.", "No events or diagnostics available.")));
        root.appendChild(disclosure("diagnostics", t(lang, "Ereignisse & Diagnosen", "Events & diagnostics"),
            t(lang, "Scanereignisse, Hinweise und Fehlermeldungen", "Scan events, warnings and errors"), diagnostics));
    }
    function initialize() {
        if (ready) return;
        var host = document.getElementById("controlAddIn") || document.body;
        if (!host) throw new Error("Business Central control host is unavailable.");
        root = el("main", "bcs-v2-root");
        root.setAttribute("aria-label", "BCSentinel Scan Monitor");
        host.appendChild(root);
        ready = true;
        render();
        if (window.Microsoft && window.Microsoft.Dynamics && window.Microsoft.Dynamics.NAV &&
            typeof window.Microsoft.Dynamics.NAV.InvokeExtensibilityMethod === "function")
            window.Microsoft.Dynamics.NAV.InvokeExtensibilityMethod("ControlReady", []);
    }
    window.SetScanData = function (raw) {
        try { payload = JSON.parse(String(raw || "{}")); }
        catch (error) { payload = {}; }
        if (ready) render();
    };
    window.BCSentinelScanVisualInit = initialize;
})();