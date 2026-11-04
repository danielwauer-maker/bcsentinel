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
        button.appendChild(el("span", "bcs-v2-chevron", panelState[id] ? "\u2303" : "\u2304"));
        var detail = el("div", "bcs-v2-disclosure-body");
        detail.hidden = !panelState[id];
        detail.appendChild(contents);
        button.addEventListener("click", function () {
            panelState[id] = !panelState[id];
            button.setAttribute("aria-expanded", panelState[id] ? "true" : "false");
            detail.hidden = !panelState[id];
            button.lastChild.textContent = panelState[id] ? "\u2303" : "\u2304";
        });
        section.appendChild(button);
        section.appendChild(detail);
        return section;
    }
    function detailField(caption, value) {
        var field = el("div", "bcs-v2-detail-field");
        field.appendChild(el("small", "", caption));
        field.appendChild(el("strong", "", value || "\u2014"));
        return field;
    }

    function mountainArtwork() {
        // Packaged vector landscape: no external requests, no third-party imagery.
        var ns = "http://www.w3.org/2000/svg";
        var svg = document.createElementNS(ns, "svg");
        svg.setAttribute("viewBox", "0 0 720 190");
        svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
        svg.setAttribute("class", "bcs-v3-mountains");
        svg.setAttribute("aria-hidden", "true");
        function path(d, fill, opacity) {
            var p = document.createElementNS(ns, "path");
            p.setAttribute("d", d);
            p.setAttribute("fill", fill);
            if (opacity !== undefined) p.setAttribute("opacity", opacity);
            svg.appendChild(p);
        }
        path("M0 160 L70 112 L115 132 L202 70 L256 117 L338 41 L413 110 L506 19 L592 92 L641 48 L720 132 L720 190 L0 190Z", "#1d5790", ".73");
        path("M0 185 L128 125 L208 163 L335 66 L424 145 L516 31 L607 124 L700 68 L720 101 L720 190 Z", "#0b365d", ".92");
        path("M194 75 L202 70 L230 96 L212 89 Z M326 78 L338 41 L374 81 L347 67 Z M495 51 L506 19 L540 54 L518 44 Z M632 59 L641 48 L664 75 L646 65 Z", "#91dbff", ".96");
        path("M0 190 L35 153 L76 178 L110 148 L148 179 L214 130 L244 185 L292 146 L360 180 L420 133 L474 177 L531 117 L585 180 L628 126 L690 170 L720 154 L720 190Z", "#061e34");
        for (var i = 0; i < 22; i++) {
            var x = 20 + i * 33;
            var height = 17 + (i * 7) % 28;
            path("M" + x + " 190 L" + (x + 8) + " " + (189 - height) +
                 " L" + (x + 17) + " 190 Z", "#021526", ".87");
        }
        return svg;
    }

    function metaItem(icon, caption, value, tone) {
        var cell = el("div", "bcs-v3-meta-item " + (tone || ""));
        cell.appendChild(el("span", "bcs-v3-meta-icon", icon));
        var labels = el("span", "bcs-v3-meta-copy");
        labels.appendChild(el("small", "", caption));
        labels.appendChild(el("strong", "", value || "-"));
        cell.appendChild(labels);
        return cell;
    }

    function sectionCard(title, icon) {
        var card = el("section", "bcs-v3-card");
        var heading = el("h3", "bcs-v3-card-title");
        heading.appendChild(el("span", "bcs-v3-title-icon", icon));
        heading.appendChild(el("span", "", title));
        card.appendChild(heading);
        return card;
    }

    function scoreGauge(score) {
        var gauge = el("div", "bcs-v3-gauge");
        gauge.style.background = "conic-gradient(#d98e04 0 " + percent(score) +
            "%, #e5eaf0 " + percent(score) + "% 100%)";
        var inside = el("div", "bcs-v3-gauge-inner");
        inside.appendChild(el("strong", "", String(percent(score))));
        inside.appendChild(el("small", "", "von 100"));
        gauge.appendChild(inside);
        return gauge;
    }

    function freeDashboard(data, insights, lang) {
        // All displayed values are derived from the authenticated Free report.
        var free = el("div", "bcs-v3-free");
        var score = percent(insights.score);
        var top = el("div", "bcs-v3-top-grid");
        var scoreCard = sectionCard("Data Health Score", "\u25c9");
        var scoreContent = el("div", "bcs-v3-score-content");
        scoreContent.appendChild(scoreGauge(score));
        var scoreCopy = el("div", "bcs-v3-score-copy");
        scoreCopy.appendChild(el("strong", "bcs-v3-risk-caption",
            score < 60 ? t(lang, "Kritischer Verbesserungsbedarf", "Critical improvement needed") :
            score < 80 ? t(lang, "Verbesserungsbedarf", "Improvement needed") :
            t(lang, "Guter Datenzustand", "Good data health")));
        scoreCopy.appendChild(el("p", "", score < 60 ?
            t(lang, "Ihre Datenqualit\u00e4t weist erhebliches Verbesserungspotenzial auf.",
              "Your data quality has significant room for improvement.") :
            t(lang, "Der vorl\u00e4ufige Score bewertet den erkannten Standard-Scope.",
              "This preliminary score covers the detected standard scope.")));
        scoreContent.appendChild(scoreCopy);
        scoreCard.appendChild(scoreContent);
        top.appendChild(scoreCard);

        var scope = sectionCard(t(lang, "Scan Scope", "Scan scope"), "\u25c8");
        var scopeItems = el("div", "bcs-v3-scope-grid");
        [
            [count(insights.affected_records, lang), t(lang, "Betroffene\nDatens\u00e4tze", "Affected\nrecords"), "\u25a4"],
            [count(insights.checks, lang), t(lang, "Checks\ndurchgef\u00fchrt", "Checks\nexecuted"), "\u2315"],
            [count(insights.modules_analyzed, lang), t(lang, "Bereiche\nanalysiert", "Areas\nanalyzed"), "\u25c7"],
            [count(insights.findings, lang), t(lang, "Findings\ngesamt", "Findings\ntotal"), "\u26a0"]
        ].forEach(function (entry) {
            var item = el("div", "bcs-v3-scope-item");
            item.appendChild(el("span", "bcs-v3-scope-icon", entry[2]));
            item.appendChild(el("strong", "", entry[0]));
            item.appendChild(el("span", "bcs-v3-scope-label", entry[1]));
            scopeItems.appendChild(item);
        });
        scope.appendChild(scopeItems);
        top.appendChild(scope);
        free.appendChild(top);

        var analysis = el("div", "bcs-v3-analysis-grid");
        var severity = sectionCard(t(lang, "Schweregrad-Verteilung der Findings", "Finding severity distribution"), "\u25a6");
        var sev = insights.severity || {};
        var levels = [
            ["critical", t(lang,"Kritisch","Critical"), "#cf3a3a"],
            ["high", t(lang,"Hoch","High"), "#ff921f"],
            ["medium", t(lang,"Mittel","Medium"), "#f6b900"],
            ["low", t(lang,"Niedrig","Low"), "#11a36a"],
            ["info", "Info", "#9aaabc"]
        ];
        var total = levels.reduce(function (sum, level) { return sum + Math.max(0, Number(sev[level[0]]) || 0); }, 0);
        var segments = el("div", "bcs-v3-severity-bar");
        levels.forEach(function (level) {
            var value = Math.max(0, Number(sev[level[0]]) || 0);
            if (total <= 0 || value <= 0) return;
            var segment = el("span", "", Math.round(value / total * 100) + "%");
            segment.style.width = (value / total * 100) + "%";
            segment.style.background = level[2];
            segment.setAttribute("title", level[1] + ": " + count(value, lang));
            segments.appendChild(segment);
        });
        severity.appendChild(segments);
        var severityList = el("div", "bcs-v3-severity-list");
        levels.forEach(function (level) {
            var item = el("div", "bcs-v3-severity-item");
            var label = el("span", "");
            var dot = el("i", "bcs-v3-dot");
            dot.style.background = level[2];
            label.appendChild(dot);
            label.appendChild(el("span", "", level[1]));
            item.appendChild(label);
            item.appendChild(el("strong", "", count(sev[level[0]], lang)));
            severityList.appendChild(item);
        });
        severity.appendChild(severityList);
        analysis.appendChild(severity);

        var risks = sectionCard(t(lang, "Top-Risikobereiche (aggregiert)", "Top risk areas (aggregate)"), "\u26a0");
        var table = el("div", "bcs-v3-risk-table");
        var head = el("div", "bcs-v3-risk-row bcs-v3-risk-head");
        [ "#", t(lang,"Bereich","Area"), t(lang,"H\u00f6chster Schweregrad","Highest severity"),
            "Findings", t(lang,"Betroffene Datens\u00e4tze","Affected records") ].forEach(function (title) {
            head.appendChild(el("span","",title));
        });
        table.appendChild(head);
        var areas = Array.isArray(insights.risk_areas) ? insights.risk_areas.slice(0,5) : [];
        areas.forEach(function (area, index) {
            var row = el("div", "bcs-v3-risk-row");
            row.appendChild(el("span", "", String(index + 1)));
            row.appendChild(el("strong", "", area.name));
            var severityText = String(area.severity || "info").toLowerCase();
            var severityCaption = {critical:"Kritisch",high:"Hoch",medium:"Mittel",low:"Niedrig",info:"Info"}[severityText] || severityText;
            var severityPill = el("span", "bcs-v3-risk-pill " + severityText, lang === "de" ? severityCaption : severityText);
            row.appendChild(severityPill);
            row.appendChild(el("strong", "", count(area.findings, lang)));
            row.appendChild(el("span", "", count(area.affected_records,lang)));
            table.appendChild(row);
        });
        risks.appendChild(table);
        analysis.appendChild(risks);
        free.appendChild(analysis);

        var impact = el("section", "bcs-v3-card bcs-v3-impact");
        var impactPreview = el("div", "bcs-v3-impact-left");
        impactPreview.appendChild(el("h3", "bcs-v3-card-title", t(lang,"Business Impact (Vorschau)","Business impact (preview)")));
        var band = String(insights.impact_band || "").toLowerCase();
        var bandLabels = [["low",t(lang,"Niedrig","Low")],["medium",t(lang,"Mittel","Medium")],
                          ["high",t(lang,"Hoch","High")],["very high",t(lang,"Sehr hoch","Very high")]];
        var bandBar = el("div","bcs-v3-impact-scale");
        bandLabels.forEach(function (option) {
            var key = option[0];
            var active = (key === "high" && (band === "hoch" || band === "high")) ||
                         (key === "medium" && (band === "mittel" || band === "medium")) ||
                         (key === "low" && (band === "niedrig" || band === "low")) ||
                         (key === "very high" && (band === "sehr hoch" || band === "very high"));
            bandBar.appendChild(el("span", active ? "active" : "", option[1]));
        });
        impactPreview.appendChild(bandBar);
        impact.appendChild(impactPreview);
        var impactCopy = el("div", "bcs-v3-impact-right");
        impactCopy.appendChild(el("strong", "", t(lang,"Business Impact: ","Business impact: ") + (insights.impact_band || "-")));
        impactCopy.appendChild(el("p", "", t(lang,
            "Die detaillierte finanzielle Bewertung mit modelliertem Verlust und potenziellen Einsparungen ist im Full Assessment enthalten.",
            "Detailed modeled losses and potential savings are included in the Full Assessment.")));
        impact.appendChild(impactCopy);
        free.appendChild(impact);

        var upsell = el("section","bcs-v3-upsell");
        upsell.appendChild(el("h3","", t(lang,"Weitere Analysedetails im Assessment","More analysis details in Assessment")));
        var benefits = el("div","bcs-v3-upsell-grid");
        [
            ["\u2315",t(lang,"Detaillierte Findings","Detailed findings"),t(lang,"Beschreibung und Kontext erkannter Datenqualit\u00e4tsprobleme.","Descriptions and context of findings"),"table"],
            ["\u25a5",t(lang,"Modellierter finanzieller Impact","Modeled financial impact"),t(lang,"Quantifizierte finanzielle Auswirkungen und Einsparpotenziale.","Financial impact and savings potential"),"bars"],
            ["\u25ce",t(lang,"Priorisierte Ma\u00dfnahmen & Roadmap","Prioritized actions & roadmap"),t(lang,"Konkrete Empfehlungen mit Priorisierung und Umsetzungsplan.","Actionable recommendations and plan"),"roadmap"]
        ].forEach(function (benefit) {
            var card = el("div","bcs-v3-benefit");
            var lead = el("div","bcs-v3-benefit-heading");
            lead.appendChild(el("span","",benefit[0]));
            var copy = el("div","");
            copy.appendChild(el("strong","",benefit[1]));
            copy.appendChild(el("p","",benefit[2]));
            lead.appendChild(copy);
            card.appendChild(lead);
            var preview = el("div","bcs-v3-preview "+ benefit[3]);
            for(var n=0;n<8;n++) {
                var mark=el("span","");
                mark.style.height=(12+(n*19)%34)+"px";
                preview.appendChild(mark);
            }
            preview.appendChild(el("span","bcs-v3-lock","\uD83D\uDD12"));
            card.appendChild(preview);
            benefits.appendChild(card);
        });
        upsell.appendChild(benefits);
        free.appendChild(upsell);
        return free;
    }

    function render() {
        if (!root) return;
        root.replaceChildren();
        var data = payload || {};
        var lang = String(data.language || "en").toLowerCase() === "de" ? "de" : "en";
        var status = String(data.status || "queued").toLowerCase();
        if (!data.runId) {
            root.appendChild(el("div", "bcs-v2-empty", t(lang, "Kein Scan ausgew\u00e4hlt", "No scan selected")));
            return;
        }
        var completed = status === "completed";
        var insights = data.insights && data.insights.tier === data.accessTier ? data.insights : null;
        var tier = insights ? insights.tier : "unavailable";
        var paid = data.canViewFullScores === true &&
            (tier === "assessment" || tier === "validation" || tier === "monitoring");
        var statusLabels = {
            completed: t(lang, "Abgeschlossen", "Completed"),
            running: t(lang, "Wird ausgef\u00fchrt", "Running"),
            failed: t(lang, "Fehlgeschlagen", "Failed"),
            queued: t(lang, "In Warteschlange", "Queued"),
            canceled: t(lang, "Abgebrochen", "Canceled")
        };
        var header = el("header", "bcs-v2-hero");
        var brand = el("div", "bcs-v2-brand");
        brand.appendChild(identityIcon());
        var name = el("div", "bcs-v2-brand-copy");
        name.appendChild(el("div", "bcs-v2-wordmark", "BCSentinel"));
        name.appendChild(el("div", "bcs-v2-claim", "Clean Data \u2013 Higher Impact"));
        brand.appendChild(name);
        header.appendChild(brand);
        var descriptor = el("div", "bcs-v2-heading");
        descriptor.appendChild(el("strong", "", "Scan Monitor"));
        descriptor.appendChild(el("span", "", data.runId));
        header.appendChild(descriptor);
        // Deliberately no completion badge in the dark hero: the scan state is
        // displayed exactly once in the white metadata bar below.
        var heroContext = el("p", "bcs-v3-hero-context", t(lang,
            "Kompakte Bewertung Ihrer Business-Central-Datenqualit\\u00e4t, identifizierter Risikobereiche und des modellierten Business Impacts.",
            "Concise overview of Business Central data quality, identified risks and modeled business impact."));
        header.appendChild(heroContext);
        header.appendChild(mountainArtwork());
        root.appendChild(header);
        var meta = el("div","bcs-v3-meta");
        meta.appendChild(metaItem("▥",t(lang,"Firma","Company"), data.companyName));
        meta.appendChild(metaItem("◈",t(lang,"BC-Umgebung","BC environment"),data.environmentName));
        meta.appendChild(metaItem("▦",t(lang,"Scan-Datum","Scan date"),data.startedAt));
        meta.appendChild(metaItem("▤",t(lang,"Run-ID","Run ID"),data.runId));
        meta.appendChild(metaItem(completed ? "✓" : status === "failed" ? "!" : "▶",
            t(lang,"Status","Status"),statusLabels[status] || status,
            completed ? "done" : status === "failed" ? "error" : "active"));
        root.appendChild(meta);

        if (completed && tier === "free-health" && insights) {
            root.appendChild(freeDashboard(data, insights, lang));
        } else {
        var kpis = el("div", "bcs-v2-kpis");
        var scoreAvailable = completed && insights && typeof insights.score === "number";
        var score = scoreAvailable ? percent(insights.score) : null;
        var scope = tier === "free-health" || tier === "quick-assessment";
        var scoreHint = scoreAvailable ? (scope ?
            t(lang, "Vorl\u00e4ufiger Scope-Score", "Preliminary scope score") :
            (score < 60 ? t(lang, "Kritisch", "Critical") : score < 80 ?
             t(lang, "Erh\u00f6ht", "Elevated") : t(lang, "Gut", "Good"))) :
            t(lang, "Vorschau nicht verf\u00fcgbar", "Preview unavailable");
        kpis.appendChild(metric("Data Health Score", scoreAvailable ? score + "/100" : "-",
            scoreHint, scoreAvailable && score < 60 ? "critical" : "restricted", "01"));
        var checks = insights && typeof insights.checks === "number" ? insights.checks : data.checks;
        var modules = Array.isArray(data.modules) ? data.modules : [];
        kpis.appendChild(metric(t(lang, "Pr\u00fcfungen", "Checks"),
            count(checks, lang), modules.length + " " + t(lang, "Module", "modules"), "checks", "02"));
        var findings = completed && insights && typeof insights.findings === "number"
            ? count(insights.findings, lang) : "-";
        kpis.appendChild(metric(t(lang, "Auff\u00e4lligkeiten", "Findings"), findings,
            scope ? t(lang, "Im erkannten Standard-Scope", "Within the detected standard scope") :
            t(lang, "Findings, nicht Datens\u00e4tze", "Findings, not affected records"), "issues", "03"));
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
        scorePanel.appendChild(el("p", "bcs-v2-subtitle", t(lang, "Datenqualit\u00e4t je Modul (0\u2013100 Punkte)", "Data quality by module (0\u2013100)")));
        modules.forEach(function (module) {
            progressPanel.appendChild(moduleItem(String(module.name || ""), module.progress, "progress"));
            if (paid && completed && Object.prototype.hasOwnProperty.call(module, "score"))
                scorePanel.appendChild(moduleItem(String(module.name || ""), module.score, "score"));
        });
        if (!paid) {
            var gate = el("div", "bcs-v2-locked");
            gate.appendChild(el("strong", "", t(lang, "Detaillierte Modul-Scores", "Detailed module scores")));
            gate.appendChild(el("p", "", tier === "unavailable" ?
                t(lang, "Die Berechtigungspr\u00fcfung ist derzeit nicht verf\u00fcgbar. Ihr Scanfortschritt bleibt sichtbar.",
                      "Entitlement check unavailable. Your scan progress remains visible.") :
                t(lang, "Volle Modul-Scores sind im Full Assessment, Validation oder Monitoring verf\u00fcgbar.",
                      "Full module scores are available with Full Assessment, Validation or Monitoring.")));
            scorePanel.appendChild(gate);
        } else if (!completed) {
            scorePanel.appendChild(el("p", "bcs-v2-locked", t(lang, "Modul-Scores nach Scanabschluss verf\u00fcgbar.", "Module scores available after scan completion.")));
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
                smallStat(t(lang, "Betroffene Datens\u00e4tze", "Affected records"), count(insights.affected_records, lang));
            if (insights.impact_band) smallStat("Business Impact Band", insights.impact_band);
            if (typeof insights.score_delta === "number")
                smallStat(t(lang, "Score-\u00c4nderung", "Score change"), (insights.score_delta > 0 ? "+" : "") + insights.score_delta);
            if (typeof insights.resolved === "number") smallStat(t(lang, "Behoben", "Resolved"), insights.resolved);
            if (typeof insights.new === "number") smallStat(t(lang, "Neu", "New"), insights.new);
            if (typeof insights.impact_eur === "number" && paid)
                smallStat(t(lang, "Modellierter Impact", "Modeled impact"),
                    insights.impact_eur.toLocaleString(lang === "de" ? "de-DE" : "en-US", {style:"currency",currency:"EUR"}));
            if (typeof insights.impact_delta_eur === "number" && paid)
                smallStat(t(lang, "Impact-\u00c4nderung", "Impact change"),
                    insights.impact_delta_eur.toLocaleString(lang === "de" ? "de-DE" : "en-US", {style:"currency",currency:"EUR"}));
            if (insightKpis.children.length) insightPanel.appendChild(insightKpis);
            var riskAreas = Array.isArray(insights.risk_areas) ? insights.risk_areas : [];
            if (riskAreas.length) {
                insightPanel.appendChild(el("h4", "", t(lang, "Risikobereiche", "Risk areas")));
                var areas = el("div", "bcs-v2-areas");
                riskAreas.slice(0, 10).forEach(function (area) {
                    var areaRow = el("div", "bcs-v2-area");
                    areaRow.appendChild(el("strong", "", area.name));
                    areaRow.appendChild(el("span", "", String(area.findings || 0) + " " + t(lang, "Auff\u00e4lligkeiten", "findings")));
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

        }
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