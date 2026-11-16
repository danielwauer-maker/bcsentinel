/* AI-PM 2.5: source-backed stage coverage and honest duration accounting.
   All nodes are textContent based. No approval, storage or network writes. */
(function(){
"use strict";
const el=id=>document.getElementById(id);
const txt=(tag,value,cls)=>{const n=document.createElement(tag);n.textContent=String(value);if(cls)n.className=cls;return n;};
const names={draft:"Draft / Codekandidat",integrated:"Im Repo integriert",preview:"DEV / Preview",technical:"Technisch attestiert",accepted:"Manuell abgenommen"};
const order=["draft","integrated","preview","technical","accepted"];
let current=null;
const hours=v=>typeof v==="number"&&Number.isFinite(v)?v.toLocaleString("de-DE",{maximumFractionDigits:1})+" h":"nicht erfasst";
function phaseBar(key,count,total){
  const wrap=txt("div","","ephase");
  const pct=total?Math.round(count/total*1000)/10:0;
  const head=txt("div","","ephase-head");
  head.append(txt("span",names[key]),txt("strong",pct.toLocaleString("de-DE")+" % · "+count+"/"+total));
  const track=txt("div","","ephase-track"),fill=txt("span","","ephase-fill ephase-"+key);
  fill.style.width=pct+"%";track.append(fill);wrap.append(head,track);
  return wrap;
}
function render(){
  if(!current)return;
  const select=el("evidence-category"),category=select.value;
  const groups=current.sprints.filter(s=>category==="all"||s.area===category);
  const list=el("evidence-sprints");list.replaceChildren();
  for(const sprint of groups){
    const section=txt("details","","evidence-sprint");
    const heading=txt("summary","");
    const name=txt("strong",sprint.sprint+(sprint.area==="saas"?" · SaaS":""));
    const meta=txt("span",sprint.tasks+" Aufgaben · Plan: "+hours(sprint.plan_hours)+" · Ist: "+hours(sprint.actual_hours));
    heading.append(name,meta);section.append(heading);
    const lead=txt("p","Nachweisabdeckung "+sprint.reviewed+"/"+sprint.tasks+" Aufgaben einzeln geprüft. Nicht geprüfte Aufgaben werden nicht als fertig gezählt.","evidence-note");
    section.append(lead);
    const bars=txt("div","","evidence-phase-grid");
    for(const k of order)bars.append(phaseBar(k,sprint.counts[k]||0,sprint.tasks));
    section.append(bars);
    const table=txt("div","","evidence-task-list");
    for(const t of sprint.tasks_detail){
      const div=txt("div","","evidence-task");
      const badges=order.filter(k=>t.evidence[k]).map(k=>names[k]).join(" · ")||"Ohne aktuellen Einzelnachweis";
      div.append(txt("strong",t.id+" · "+t.title),
                 txt("small",badges+" | Plan: "+hours(t.plan_hours)+" | Ist: "+hours(t.actual_hours)));
      if(t.next_action)div.append(txt("small","Noch offen: "+t.next_action));
      table.append(div);
    }
    section.append(table);list.append(section);
  }
  el("evidence-showing").textContent=groups.length+" Sprintbereiche · "+groups.reduce((a,g)=>a+g.tasks,0)+" Aufgaben";
}
function renderTimeline(source){
  const t=source.timeline||{};
  el("evidence-planned-hours").textContent=hours(t.planned_fiverr_hours);
  el("evidence-actual-hours").textContent=hours(t.actual_logged_hours);
  el("evidence-time-note").textContent="Plan: verifizierte Excel-Stunden (Fiverr). Ist: keine geprüften Zeiterfassungen. PR-Durchlaufzeit in Kalendertagen ist keine Arbeitszeit.";
  const events=(t.events||[]).slice().reverse();
  const list=el("evidence-timeline");list.replaceChildren();
  for(const event of events){
    const div=txt("div","","evidence-event");
    div.append(txt("time",event.date));
    const detail=txt("div","");
    const link=event.url&&/^https:\/\/github\.com\/danielwauer-maker\/(bcsentinel|bcsentinel-frontend)\/pull\/\d+$/.test(event.url);
    if(link){const a=txt("a",event.label);a.href=event.url;a.target="_blank";a.rel="noopener noreferrer";detail.append(a);}
    else detail.append(txt("strong",event.label));
    detail.append(txt("small",event.area+" · "+(event.kind==="merge"?"Merge":event.kind==="draft"?"Draft":"DEV-Nachweis")+
      (typeof event.lead_calendar_days==="number"?" · PR-Durchlaufzeit: "+event.lead_calendar_days+" Kalendertage":"")));
    div.append(detail);list.append(div);
  }
  if(!events.length)list.append(txt("p","Keine eindeutig datierten Einzelereignisse verfügbar."));
  el("evidence-event-count").textContent=String(t.event_count||0)+" datierte Nachweise";
}
function renderEvidenceProgress(snapshot){
  const source=snapshot?.evidence_progress;
  if(!source?.sprints){el("evidence-progress-state").textContent="Daten nicht verfügbar";return;}
  current=source;
  const metrics=source.metrics?.phase_coverage_fiverr_percent||{};
  const box=el("evidence-overall");box.replaceChildren();
  for(const phase of order){
    const card=txt("article","","evidence-score");
    const value=metrics[phase];
    card.append(txt("span",names[phase]),txt("strong",typeof value==="number"?value.toLocaleString("de-DE")+" %":"–"));
    box.append(card);
  }
  const area=el("evidence-category"),previous=area.value;
  area.replaceChildren(new Option("Alle Kategorien","all"));
  for(const label of [...new Set(source.sprints.map(s=>s.area))].sort())area.append(new Option(label==="fiverr"?"Fiverr – alle Sprints":"SaaS / Stripe",label));
  if([...area.options].some(o=>o.value===previous))area.value=previous;
  el("evidence-progress-state").textContent=source.state==="loaded"?"Quellen vollständig geladen":"Teilweise Quellenlücke – keine fehlenden Nachweise als erledigt gezählt";
  el("evidence-method").textContent=source.warning;
  render();renderTimeline(source);
}
el("evidence-category")?.addEventListener("change",render);
window.renderEvidenceProgress=renderEvidenceProgress;
})();
