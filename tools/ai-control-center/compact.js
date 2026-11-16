/* Compact, evidence-qualified dashboard. Task-time edits are intentional POSTs only. */
(function(){
"use strict";
const byId=id=>document.getElementById(id);
const node=(tag,value,cls)=>{const n=document.createElement(tag);if(value!==undefined)n.textContent=String(value);if(cls)n.className=cls;return n;};
const num=n=>typeof n==="number"&&Number.isFinite(n)?n.toLocaleString("de-DE",{maximumFractionDigits:1}):"–";
const hours=m=>typeof m==="number"?(m/60).toLocaleString("de-DE",{maximumFractionDigits:2})+" h":"–";
let latest=null;
function metric(title,value,description){
 const n=node("div",undefined,"compact-metric");
 n.append(node("span",title),node("strong",value),node("small",description));return n;
}
function td(text){return node("td",text);}
function sprintRow(s){
 const tr=document.createElement("tr");
 tr.append(td(s.sprint+(s.area==="saas"?" · SaaS":"")));
 const phase=document.createElement("td");phase.className="compact-phases";
 for(const [name,key] of [["Code","integrated"],["DEV","preview"],["Abnahme","accepted"]]){
   const x=node("div",undefined,"compact-mini");
   const pct=s.percent?.[key]??0;
   x.append(node("span",name),node("strong",num(pct)+" %"));
   const rail=node("div",undefined,"compact-rail"),fill=node("span",undefined,"compact-fill");
   fill.style.width=pct+"%";rail.append(fill);x.append(rail);phase.append(x);
 }
 tr.append(phase);
 tr.append(td(s.plan_hours===null?"Kein Excel-Wert":num(s.plan_hours)+" h"));
 const actual=document.createElement("td");
 const input=document.createElement("input");
 input.type="number";input.min="0";input.max="1000000";input.step="1";
 input.placeholder="Minuten";input.inputMode="numeric";
 input.value=s.actual_minutes===null?"":String(s.actual_minutes);
 input.className="compact-minutes";input.setAttribute("aria-label","Kumulierte Ist-Minuten "+s.sprint);
 const btn=node("button","Speichern","compact-save");btn.type="button";
 const note=node("small",s.actual_minutes===null?"Noch nicht erfasst":hours(s.actual_minutes)+" erfasst","compact-save-note");
 const label=document.createElement("div");label.className="compact-entry";
 label.append(input,btn);actual.append(label,note);tr.append(actual);
 const usage=s.budget_used_percent;
 const status=node("span",usage===null?"–":num(usage)+" %","compact-budget");
 if(usage!==null){status.classList.add(usage>100?"compact-over":"compact-under");}
 const statusCell=document.createElement("td");statusCell.append(status);
 statusCell.append(node("small",usage===null?"Ohne Ist-Zeit":"Budgetverbrauch, nicht Termin-Freigabe"));
 tr.append(statusCell);
 btn.addEventListener("click",async()=>{
   const v=input.value.trim();
   if(!/^\d+$/.test(v)||Number(v)>1000000){note.textContent="Bitte ganze Minuten eingeben.";return;}
   btn.disabled=true;note.textContent="Speichert …";
   try{
     const response=await fetch('/api/sprint-effort',{
       method:"POST",credentials:"same-origin",
       headers:{"Content-Type":"application/json","X-Requested-With":"BCSentinel-AI-PM"},
       body:JSON.stringify({area:s.area,sprint:s.sprint,minutes:Number(v),revision:s.time_revision||0})
     });
     const result=await response.json();
     if(!response.ok)throw Error(result.error||"HTTP "+response.status);
     note.textContent="Gespeichert · neue Revision "+result.revision;
     // Reload the snapshot without re-triggering form writes.
     const snapshotResponse=await fetch('/api/snapshot',{cache:"no-store"});
     if(!snapshotResponse.ok)throw Error("Speicherung erfolgt; Ansicht bitte aktualisieren.");
     const snapshot=await snapshotResponse.json();
     renderCompact(snapshot);
   }catch(e){note.textContent=e.message||"Speichern fehlgeschlagen";}
   finally{btn.disabled=false;}
 });
 return tr;
}
function renderCurrentProject(current){
 const priority=byId("compact-current-next"),domains=byId("compact-current-areas");
 if(!priority||!domains)return;
 priority.replaceChildren();domains.replaceChildren();
 if(!current||!Array.isArray(current.areas)){
   priority.append(node("p","Aktuelle Statusquelle nicht verfügbar – keine alten Versionszahlen als neu ausgeben."));
   return;
 }
 for(const task of (current.next||[]).slice(0,3)){
   const card=node("article",undefined,"compact-next-card");
   card.append(node("strong",task.title),node("p",task.action));
   priority.append(card);
 }
 const labels={code_candidate:"AL-Quellkandidat",source_partial:"Quellcode / Review teilweise",dev_verified:"DEV verifiziert",
   dev_verified_prior:"DEV zuletzt nachgewiesen",merged_source_controls:"Quellkontrollen integriert",
   editorial_complete:"Redaktionell vorbereitet",not_started:"Noch nicht freigegeben",unreconciled:"Einzelstatus ungeklärt"};
 for(const area of current.areas){
   const card=node("article",undefined,"compact-area-card");
   card.append(node("strong",area.name),node("small",labels[area.stage]||area.stage),
      node("p",area.evidence),node("p","Noch offen: "+area.remaining));
   const valid=(area.refs||[]).find(ref=>/^https:\/\/github\.com\/danielwauer-maker\/[\w-]+\/(pull|actions\/runs)\/\d+$/.test(ref));
   if(valid){const a=node("a","Nachweis auf GitHub");a.href=valid;a.target="_blank";a.rel="noopener noreferrer";card.append(a);}
   domains.append(card);
 }
 byId("compact-coverage-limit").textContent=current.coverage_note||"";
}
function renderCompact(snapshot){
 const p=snapshot?.evidence_progress;
 if(!p||!Array.isArray(p.sprints)){byId("compact-state").textContent="Projektfortschritt nicht verfügbar";return;}
 latest=snapshot;
 renderCurrentProject(snapshot.current_project);
 const rates=p.metrics?.phase_coverage_fiverr_percent||{};
 const stats=byId("compact-stats");stats.replaceChildren();
 const effort=p.effort||{};
 const comparable=effort.comparable_sprints||0;
 stats.append(
   metric("Integrierter Code",num(rates.integrated)+" %","Fiverr · Nachweisabdeckung"),
   metric("DEV / Preview",num(rates.preview)+" %","Fiverr · Nachweisabdeckung"),
   metric("Manuell abgenommen",num(rates.accepted)+" %","Fiverr · unabhängig bestätigt"),
   metric("Planstunden",num(p.timeline?.planned_fiverr_hours)+" h","Aus Excel · 61 Aufgaben"),
   metric("Ist-Zeit",hours(p.timeline?.actual_logged_hours===null?null:p.timeline.actual_logged_hours*60),comparable+" Sprint(s) mit Plan/Ist-Vergleich")
 );
 const plan=effort.comparable_plan_minutes;
 const used=effort.comparable_actual_minutes;
 const pct=effort.budget_used_percent;
 byId("compact-state").textContent="85 Aufgaben · "+p.sprints.length+" Sprintbereiche · GitHub "+
   (snapshot?.sprint_radar?.github?.state==="loaded"?"synchronisiert":"unvollständig")+
   " · Fiverr weiterhin NO-GO";
 const compare=byId("compact-comparison");
 compare.textContent=comparable
   ? "Soll/Ist für "+comparable+" erfasste Sprintbereiche: "+hours(plan)+" Soll / "+hours(used)+" Ist · "+
     num(pct)+" % Budgetverbrauch. Noch laufende Aufgaben können weitere Zeit benötigen."
   : "Noch keine Ist-Zeiten eingetragen. Bitte kumulierte Minuten pro Sprint erfassen.";
 const tbody=byId("compact-rows");tbody.replaceChildren();
 for(const s of p.sprints)tbody.append(sprintRow(s));
 const dated=[...(p.timeline?.events||[])].sort((a,b)=>b.date.localeCompare(a.date));
 const timeline=byId("compact-timeline");timeline.replaceChildren();
 for(const event of dated.slice(0,15)){
   const li=document.createElement("li");
   li.append(node("time",event.date));
   li.append(node("span",event.label));
   timeline.append(li);
 }
 if(!dated.length)timeline.append(node("li","Noch keine datierten Nachweise."));
 byId("compact-timeline-status").textContent=dated.length+
   " Ereignisse bekannt. Arbeitszeit wird nur über manuelle Minuteneingaben erfasst.";
}
window.renderCompact=renderCompact;
})();
