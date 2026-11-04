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
    language:"de",currentModule:"All modules completed",
    currentStep:"Scan completed",modules,events:"Scan started | Scan completed"
};
let rendered = show({...base, accessTier:"free-health",canViewFullScores:false});
assert.match(rendered,/BCSentinel/);
assert.match(rendered,/202/);
assert.match(rendered,/Prüfungen/);
assert.match(rendered,/Detail-Scores geschützt/);
assert.doesNotMatch(rendered,/47\/100/);
assert.doesNotMatch(rendered,/27\/100/);
assert.doesNotMatch(rendered,/(^|\D)95(\D|$)/);

rendered = show({...base,accessTier:"quick-assessment",canViewFullScores:false});
assert.doesNotMatch(rendered,/47\/100/);
assert.doesNotMatch(rendered,/27\/100/);

rendered = show({...base,accessTier:"assessment",canViewFullScores:true});
assert.match(rendered,/47\/100/);
assert.match(rendered,/95/);
assert.match(rendered,/27\/100/);
assert.match(rendered,/Findings, keine Datensätze/);

const buttons = [];
function traverse(e) {
    if(e.tagName === "button") buttons.push(e);
    e.children.forEach(traverse);
}
traverse(host);
assert.equal(buttons.length, 2, "Two accessible disclosure buttons are present");
buttons[0].handlers.click();
assert.equal(buttons[0].attributes["aria-expanded"], "true");
assert.match(host.textContent,/Startzeit/);

rendered = show({...base,accessTier:"free-health",canViewFullScores:true});
assert.doesNotMatch(rendered,/47\/100/, "Never trust a mismatched disclosure flag");
assert.doesNotMatch(rendered,/27\/100/);
console.log("Scan visual UI tests: PASS (Free, Quick, Assessment, disclosure and denied-tier mismatch)");
