/* AI-PM 2.2 – concise read-only executive view built from existing snapshot.
   No writes, no synthetic approvals and no invented delivery dates. */
(function () {
  "use strict";
  const byId = id => document.getElementById(id);
  const set = (id, value) => { const node=byId(id); if(node) node.textContent=String(value); };
  const pct = value => Number.isFinite(value) && value>=0 && value<=1
    ? (value*100).toLocaleString("de-DE",{maximumFractionDigits:1})+" %" : "Nicht verfügbar";
  const count = value => Number.isInteger(value) && value>=0 ? String(value) : "–";
  const LIMIT = 5;

  function renderExecutive(snapshot) {
    const ready = snapshot?.fiverr_readiness || {};
    const insights = snapshot?.pm_insights || {};
    const brief = snapshot?.ai_pm_brief || {};
    const plan = snapshot?.blocker_plan || {};
    const repos = Array.isArray(snapshot?.repositories) ? snapshot.repositories : [];
    set("exec-status", "NICHT FREIGEGEBEN");
    set("exec-progress", ready.state==="loaded" ? pct(ready.technical_fraction) : "Nicht verfügbar");
    set("exec-progress-source", "Fiverr · technisch markierte Planstunden, keine unabhängige Abnahme");
    set("exec-gates", ready.state==="loaded" ? pct(ready.gate_fraction) : "Nicht verfügbar");
    set("exec-gates-source", "Fiverr · historische Excel-Häkchen, keine unabhängige Abnahme");
    set("exec-estimate", ready.state==="loaded" ? pct(ready.legacy_estimate_fraction) : "Nicht verfügbar");
    set("exec-estimate-source", "Historische qualitative Gesamtprojektschätzung · kein technischer Fortschritt");
    set("exec-p0", insights.state==="loaded" ? count(insights.risk_summary?.p0_open_criteria) : "–");
    set("exec-p0-source", "Offene P0-Prüfkriterien im kuratierten Teilumfang");
    const stamp = snapshot?.generated_at_utc;
    const date = typeof stamp==="string" ? new Date(stamp) : null;
    set("exec-asof", date && !Number.isNaN(date.getTime())
      ? "Snapshot: "+date.toLocaleString("de-DE")
      : "Snapshotzeit unbekannt");
    // Source review date is not a runtime observation timestamp or a release approval.
    const reviewed = snapshot?.sprint_evidence?.reviewed_at;
    const known = typeof reviewed==="string" && /^\d{4}-\d{2}-\d{2}$/.test(reviewed);
    set("exec-evidence-asof", known
      ? "Sprint-Evidence: Reviewstand "+reviewed+" · kein aktueller Server-Snapshot"
      : "Sprint-Evidence: Reviewstand nicht verfügbar");

    set("exec-source-state", repos.length===2 && repos.every(r=>r.state==="loaded" && r.pr_state==="loaded")
      ? "GitHub-Metadaten verfügbar · kein CI-/BC-Abnahmenachweis"
      : "GitHub-Daten unvollständig oder nicht verfügbar");
    const recommendation = brief.state==="loaded" ? brief.recommendation : null;
    set("exec-primary", recommendation?.next_action || "Keine verifizierte Handlungsempfehlung verfügbar");
    set("exec-primary-title", recommendation?.task_id
      ? "Sprint "+recommendation.task_id+" · manueller Review" : "Manueller Review");
    const list = byId("exec-next");
    if(list) {
      list.replaceChildren();
      const tasks = plan.state==="loaded" && Array.isArray(plan.items)
        ? plan.items.filter(t=>t.priority==="P0").slice(0,LIMIT) : [];
      if(tasks.length) {
        for(const task of tasks) {
          const li=document.createElement("li");
          const strong=document.createElement("strong");
          strong.textContent=task.id+" · "+task.title;
          const detail=document.createElement("span");
          detail.textContent=task.next_check || "Manueller Evidence-Review erforderlich";
          li.append(strong,detail);
          list.appendChild(li);
        }
      } else {
        const li=document.createElement("li");
        li.textContent="Keine kuratierten P0-Aufgaben geladen – Priorität nicht ableitbar.";
        list.appendChild(li);
      }
    }
    set("exec-scope", plan.state==="loaded"
      ? "Kuratiertes Teilmodell: "+count(plan.modeled_tasks)+" Reviews; Reihenfolge ist eine Planungshypothese."
      : "Keine belastbare Priorisierung ohne kuratierte Evidence.");
  }
  window.renderExecutive=renderExecutive;
})();
