"use strict";
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const path = require("node:path");

class Element {
    constructor(tag) {
        this.tagName = tag;
        this.children = [];
        this.attributes = {};
        this.style = {};
        this.hidden = false;
        this.className = "";
        this.handlers = {};
        this._text = "";
    }
    set textContent(value) { this._text = String(value); this.children = []; }
    get textContent() { return this._text + this.children.map(e => e.textContent).join(""); }
    get lastChild() { return this.children[this.children.length - 1]; }
    appendChild(element) { this.children.push(element); return element; }
    replaceChildren(...children) { this.children = children; this._text = ""; }
    setAttribute(k, v) { this.attributes[k] = String(v); }
    addEventListener(event, fn) { this.handlers[event] = fn; }
}
const host = new Element("div");
const document = {
    body: new Element("body"),
    createElement: tag => new Element(tag),
    createElementNS: (_ns, tag) => new Element(tag),
    getElementById: id => id === "controlAddIn" ? host : null,
};
const emitted = [];
const window = { Microsoft: { Dynamics: { NAV: { InvokeExtensibilityMethod: (event) => emitted.push(event) } } } };
const script = fs.readFileSync(path.join(__dirname, "..", "bc-extension/app/src/controladdin/js/scanvisual.js"), "utf8");
vm.runInNewContext(script, { window, document, Number, String, Object }, { filename: "scanvisual.js" });
window.BCSentinelScanVisualInit();
assert.deepEqual(emitted, ["ControlReady"]);

function show(value) {
    window.SetScanData(JSON.stringify(value));
    return host.textContent;
}
const modules = [
    {name:"System",progress:100,score:50},
    {name:"Inventory",progress:100,score:27}
];
const base = {
    runId:"RUN_TEST_001",status:"completed",progress:100,
    checks:202,score:47,issues:95,
    language:"de",companyName:"CRONUS DE",environmentName:"Sandbox",startedAt:"04.11.2026 11:37",currentModule:"All modules completed",
    currentStep:"Scan completed",modules,events:"Scan started | Scan completed"
};
let rendered = show({...base, accessTier:"free-health",canViewFullScores:false,
    insights:{tier:"free-health",score:40,checks:202,findings:72,affected_records:1250,
              impact_band:"Hoch",modules_analyzed:10,severity:{critical:0,high:17,medium:35,low:20,info:0},
              risk_areas:[{name:"Inventory",findings:25,severity:"high",affected_records:3200}]}});
assert.match(rendered,/BCSentinel/);
assert.match(rendered,/202/);
assert.match(rendered,/durchgef\u00fchrt/);
assert.match(rendered,/Schweregrad-Verteilung der Findings/);
assert.match(rendered,/Weitere Analysedetails im Assessment/);
assert.match(rendered,/CRONUS DE/);
assert.match(rendered,/Sandbox/);
assert.match(rendered,/Abgeschlossen/);
// Visual-polish contract: no placeholder typography icons or shallow landscapes.
const root = host.children[0];
function flattenElements(element, accum) {
    accum.push(element);
    (element.children || []).forEach(function (child) { flattenElements(child, accum); });
    return accum;
}
const allVisualNodes = flattenElements(root, []);
const svgIcons = allVisualNodes.filter(function (node) {
    return node.tagName === "svg" && (node.attributes["class"] || "").includes("bcs-v3-");
});
assert.ok(svgIcons.length >= 12, "Free dashboard uses SVG for metadata, scope, and headings");
const alpine = allVisualNodes.find(function (node) {
    return node.tagName === "svg" && node.attributes["class"] === "bcs-v3-mountains";
});
assert.ok(alpine, "Detailed mountain artwork exists");
assert.ok(alpine.children.length > 100, "Alpine SVG has multiple mountain and forest layers");
assert.ok(!allVisualNodes.some(function (node) {
    return node.tagName === "span" && ["▥","◈","▦","▤","◉","⌕","⚠","🔒"].includes(node._text);
}), "Placeholder symbol spans and emoji are removed");
// Status belongs only in the white metadata strip, not in the mountain hero.
const visualRoot = host.children[0];
const brandHero = visualRoot.children.find(e => e.className === "bcs-v2-hero");
const scanMeta = visualRoot.children.find(e => e.className === "bcs-v3-meta");
assert.ok(brandHero, "Dark branded header is present");
assert.ok(scanMeta, "White scan metadata strip is present");
assert.doesNotMatch(brandHero.textContent,/Abgeschlossen/, "No duplicate completion badge in the hero");
assert.match(scanMeta.textContent,/Abgeschlossen/, "Completion status stays in scan metadata");
assert.ok(brandHero.children.some(e => e.attributes.class === "bcs-v3-mountains"),
          "Right-side mountain artwork stays in the branded header");
assert.match(rendered,/40von 100/);
assert.match(rendered,/72/);
assert.match(rendered,/Inventory/);
assert.doesNotMatch(rendered,/47\/100/);
assert.doesNotMatch(rendered,/27\/100/);
assert.doesNotMatch(rendered,/(^|\D)95(\D|$)/);

rendered = show({...base,accessTier:"quick-assessment",canViewFullScores:false,
    insights:{tier:"quick-assessment",score:40,findings:72,
              top_findings:[{rank:1,title:"Duplicate inventory references",severity:"high"}]}});
assert.match(rendered,/Duplicate inventory references/);
assert.doesNotMatch(rendered,/47\/100/);
assert.doesNotMatch(rendered,/27\/100/);

rendered = show({...base,accessTier:"assessment",canViewFullScores:true,
    insights:{tier:"assessment",score:47,checks:202,findings:95,impact_eur:30000,
              top_findings:[{rank:1,title:"Missing customer attributes",severity:"high"}]}});
assert.match(rendered,/47\/100/);
assert.match(rendered,/95/);
assert.match(rendered,/27\/100/);
assert.match(rendered,/Findings, nicht Datens\u00e4tze/);
assert.match(rendered,/Missing customer attributes/);

rendered = show({...base,accessTier:"validation",canViewFullScores:true,
    insights:{tier:"validation",score:62,findings:51,score_delta:15,resolved:12,new:1}});
assert.match(rendered,/62\/100/);
assert.match(rendered,/Score-\u00c4nderung/);

rendered = show({...base,accessTier:"monitoring",canViewFullScores:true,
    insights:{tier:"monitoring",score:67,findings:40,trend:[{score:52},{score:61},{score:67}]}});
assert.match(rendered,/67\/100/);
assert.match(rendered,/Score-Verlauf/);

// Re-render the Free view before checking its single diagnostics disclosure.
rendered = show({...base,accessTier:"free-health",canViewFullScores:false,
    insights:{tier:"free-health",score:40,checks:202,findings:72,
              severity:{critical:0,high:17,medium:35,low:20,info:0},
              risk_areas:[],impact_band:"Hoch",affected_records:8846,modules_analyzed:10}});
const buttons = [];
function traverse(e) {
    if(e.tagName === "button") buttons.push(e);
    e.children.forEach(traverse);
}
traverse(host);
assert.equal(buttons.length, 1, "Free dashboard retains only the diagnostics disclosure");
buttons[0].handlers.click();
assert.equal(buttons[0].attributes["aria-expanded"], "true");
assert.match(host.textContent,/Scan started/);

rendered = show({...base,accessTier:"free-health",canViewFullScores:true,
    insights:{tier:"free-health",score:40,findings:72}});
assert.doesNotMatch(rendered,/47\/100/, "Never trust mismatched disclosure flag");
assert.doesNotMatch(rendered,/27\/100/);

rendered = show({...base,accessTier:"free-health",canViewFullScores:false});
assert.doesNotMatch(rendered,/47\/100/);
assert.doesNotMatch(rendered,/95/);
console.log("Scan visual UI tests: PASS (five product tiers, safe fallback, details and disclosure)");
