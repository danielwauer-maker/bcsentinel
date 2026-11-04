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
        button.appendChild(el("span", "bcs-v2-chevron", panelState[id] ? "\\u2303" : "\\u2304"));
        var detail = el("div", "bcs-v2-disclosure-body");
        detail.hidden = !panelState[id];
        detail.appendChild(contents);
        button.addEventListener("click", function () {
            panelState[id] = !panelState[id];
            button.setAttribute("aria-expanded", panelState[id] ? "true" : "false");
            detail.hidden = !panelState[id];
            button.lastChild.textContent = panelState[id] ? "\\u2303" : "\\u2304";
        });
        section.appendChild(button);
        section.appendChild(detail);
        return section;
    }
    function detailField(caption, value) {
        var field = el("div", "bcs-v2-detail-field");
        field.appendChild(el("small", "", caption));
        field.appendChild(el("strong", "", value || "\\u2014"));
        return field;
    }
    function render() {
        if (!root) return;
        root.replaceChildren();
        var data = payload || {};
        var lang = String(data.language || "en").toLowerCase() === "de" ? "de" : "en";
        var status = String(data.status || "queued").toLowerCase();
        if (!data.runId) {
            root.appendChild(el("div", "bcs-v2-empty", t(lang, "Kein Scan ausgew\\u00e4hlt", "No scan selected")));
            return;
        }
        var completed = status === "completed";
        var insights = data.insights && data.insights.tier === data.accessTier ? data.insights : null;
        var tier = insights ? insights.tier : "unavailable";
        var paid = data.canViewFullScores === true &&
            (tier === "assessment" || tier === "validation" || tier === "monitoring");
        var statusLabels = {
            completed: t(lang, "Abgeschlossen", "Completed"),
            running: t(lang, "Wird ausgef\\u00fchrt", "Running"),
            failed: t(lang, "Fehlgeschlagen", "Failed"),
            queued: t(lang, "In Warteschlange", "Queued"),
            canceled: t(lang, "Abgebrochen", "Canceled")
        };
        var header = el("header", "bcs-v2-hero");
        var brand = el("div", "bcs-v2-brand");
        brand.appendChild(identityIcon());
        var name = el("div", "bcs-v2-brand-copy");
        name.appendChild(el("div", "bcs-v2-wordmark", "BCSentinel"));
        name.appendChild(el("div", "bcs-v2-claim", "Clean Data \\u2013 Higher Impact"));
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
        var scoreAvailable = completed && insights && typeof insights.score === "number";
        var score = scoreAvailable ? percent(insights.score) : null;
        var scope = tier === "free-health" || tier === "quick-assessment";
        var scoreHint = scoreAvailable ? (scope ?
            t(lang, "Vorlaeufiger Scope-Score", "Preliminary scope score") :
            (score < 60 ? t(lang, "Kritisch", "Critical") : score < 80 ?
             t(lang, "Erhoeht", "Elevated") : t(lang, "Gut", "Good"))) :
            t(lang, "Vorschau nicht verfuegbar", "Preview unavailable");
        kpis.appendChild(metric("Data Health Score", scoreAvailable ? score + "/100" : "-",
            scoreHint, scoreAvailable && score < 60 ? "critical" : "restricted", "01"));
        var checks = insights && typeof insights.checks === "number" ? insights.checks : data.checks;
        var modules = Array.isArray(data.modules) ? data.modules : [];
        kpis.appendChild(metric(t(lang, "Pruefungen", "Checks"),
            count(checks, lang), modules.length + " " + t(lang, "Module", "modules"), "checks", "02"));
        var findings = completed && insights && typeof insights.findings === "number"
            ? count(insights.findings, lang) : "-";
        kpis.appendChild(metric(t(lang, "Auffaelligkeiten", "Findings"), findings,
            scope ? t(lang, "Im erkannten Standard-Scope", "Within the detected standard scope") :
            t(lang, "Findings, nicht Datensaetze", "Findings, not affected records"), "issues", "03"));
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
        scorePanel.appendChild(el("p", "bcs-v2-subtitle", t(lang, "Datenqualit\\u00e4t je Modul (0\\u2013100 Punkte)", "Data quality by module (0\\u2013100)")));
        modules.forEach(function (module) {
            progressPanel.appendChild(moduleItem(String(module.name || ""), module.progress, "progress"));
            if (paid && completed && Object.prototype.hasOwnProperty.call(module, "score"))
                scorePanel.appendChild(moduleItem(String(module.name || ""), module.score, "score"));
        });
        if (!paid) {
            var gate = el("div", "bcs-v2-locked");
            gate.appendChild(el("strong", "", t(lang, "Detaillierte Modul-Scores", "Detailed module scores")));
            gate.appendChild(el("p", "", tier === "unavailable" ?
                t(lang, "Die Berechtigungspruefung ist derzeit nicht verfuegbar. Ihr Scanfortschritt bleibt sichtbar.",
                      "Entitlement check unavailable. Your scan progress remains visible.") :
                t(lang, "Volle Modul-Scores sind im Full Assessment, Validation oder Monitoring verfuegbar.",
                      "Full module scores are available with Full Assessment, Validation or Monitoring.")));
            scorePanel.appendChild(gate);
        } else if (!completed) {
            scorePanel.appendChild(el("p", "bcs-v2-locked", t(lang, "Modul-Scores nach Scanabschluss verf\\u00fcgbar.", "Module scores available after scan completion.")));
        }
        columns.appendChild(progressPanel);
        columns.appendChild(scorePanel);
        root.appendChild(columns);

        if (insights && completed) {
            var insightPanel = el("section", "bcs-v2-card bcs-v2-insights");
            var tierName = {
                "free-health": "Free Health Check", "quick-assessment": "Quick Assessment",
                "assessment": "Full Assessment", "validation": "Validation", "monitoring": "Monitoring"
            }[tier] || "Report";
            insightPanel.appendChild(el("h3", "", tierName + " - " +
                t(lang, "Freigegebene Erkenntnisse", "Authorized insights")));
            var insightKpis = el("div", "bcs-v2-insight-summary");
            function smallStat(label, value) {
                var stat = el("div", "bcs-v2-stat");
                stat.appendChild(el("small", "", label));
                stat.appendChild(el("strong", "", String(value)));
                insightKpis.appendChild(stat);
            }
            if (typeof insights.affected_records === "number")
                smallStat(t(lang, "Betroffene Datensaetze", "Affected records"), count(insights.affected_records, lang));
            if (insights.impact_band) smallStat("Business Impact Band", insights.impact_band);
            if (typeof insights.score_delta === "number")
                smallStat(t(lang, "Score-Aenderung", "Score change"), (insights.score_delta > 0 ? "+" : "") + insights.score_delta);
            if (typeof insights.resolved === "number") smallStat(t(lang, "Behoben", "Resolved"), insights.resolved);
            if (typeof insights.new === "number") smallStat(t(lang, "Neu", "New"), insights.new);
            if (typeof insights.impact_eur === "number" && paid)
                smallStat(t(lang, "Modellierter Impact", "Modeled impact"),
                    insights.impact_eur.toLocaleString(lang === "de" ? "de-DE" : "en-US", {style:"currency",currency:"EUR"}));
            if (typeof insights.impact_delta_eur === "number" && paid)
                smallStat(t(lang, "Impact-Aenderung", "Impact change"),
                    insights.impact_delta_eur.toLocaleString(lang === "de" ? "de-DE" : "en-US", {style:"currency",currency:"EUR"}));
            if (insightKpis.children.length) insightPanel.appendChild(insightKpis);
            var riskAreas = Array.isArray(insights.risk_areas) ? insights.risk_areas : [];
            if (riskAreas.length) {
                insightPanel.appendChild(el("h4", "", t(lang, "Risikobereiche", "Risk areas")));
                var areas = el("div", "bcs-v2-areas");
                riskAreas.slice(0, 10).forEach(function (area) {
                    var areaRow = el("div", "bcs-v2-area");
                    areaRow.appendChild(el("strong", "", area.name));
                    areaRow.appendChild(el("span", "", String(area.findings || 0) + " " + t(lang, "Auffaelligkeiten", "findings")));
                    areas.appendChild(areaRow);
                });
                insightPanel.appendChild(areas);
            }
            var top = Array.isArray(insights.top_findings) ? insights.top_findings : [];
            if (top.length && tier !== "free-health") {
                insightPanel.appendChild(el("h4", "", t(lang, "Top-5 priorisierte Findings", "Top five priority findings")));
                var priorities = el("ol", "bcs-v2-priorities");
                top.slice(0, 5).forEach(function (entry) {
                    var item = el("li", "", entry.title);
                    if (entry.severity) item.appendChild(el("small", "", " - " + entry.severity));
                    priorities.appendChild(item);
                });
                insightPanel.appendChild(priorities);
            }
            var trend = Array.isArray(insights.trend) ? insights.trend : [];
            if (tier === "monitoring" && trend.length > 1) {
                insightPanel.appendChild(el("h4", "", t(lang, "Score-Verlauf", "Score trend")));
                var trends = el("div", "bcs-v2-trend");
                trend.forEach(function (point) {
                    var column = el("div", "bcs-v2-trend-col");
                    column.style.height = Math.max(5, percent(point.score)) + "%";
                    column.setAttribute("title", String(point.score) + "/100");
                    trends.appendChild(column);
                });
                insightPanel.appendChild(trends);
            }
            root.appendChild(insightPanel);
        }
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