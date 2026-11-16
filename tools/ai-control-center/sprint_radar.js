/* Read-only sprint radar. Never promotes PR observations into manual release approval. */
(function () {
"use strict";
const el = id => document.getElementById(id);
const put = (id, value) => { const n=el(id); if(n) n.textContent=String(value); };
const node=(tag,className,text)=>{const n=document.createElement(tag);if(className)n.className=className;if(text!==undefined)n.textContent=String(text);return n;};
let last=null;
function renderCard(item) {
  const card=node("article","radar-item");
  const top=node("div","radar-top");
  top.append(node("strong",null,item.id+" · "+item.title));
  top.append(node("span","radar-tag",item.label));
  card.append(top);
  card.append(node("p","radar-next","Nächster Schritt: "+item.next_action));
  if(item.detail)card.append(node("p","radar-detail",item.detail));
  const links=node("div","radar-refs");
  for(const pr of item.prs||[]){
    if(!/^https:\/\/github\.com\/danielwauer-maker\/(bcsentinel|bcsentinel-frontend)\/pull\/\d+$/.test(pr.url||"")) continue;
    const a=node("a",null,"PR #"+pr.number+" · "+pr.state);
    a.href=pr.url; a.target="_blank";a.rel="noopener noreferrer";links.append(a);
  }
  if(links.children.length)card.append(links);
  if((item.unresolved_pr_refs||[]).length)card.append(node("small",null,"Weitere PR-Referenzen außerhalb des aktuellen GitHub-Beobachtungsfensters; Status unbekannt."));
  return card;
}
function renderBoard() {
  const data=last;
  if(!data)return;
  const area=el("radar-area").value,kind=el("radar-stage").value;
  const items=(data.items||[]).filter(item=>(area==="all"||item.area===area)&&(kind==="all"||item.category===kind));
  const container=el("radar-items");container.replaceChildren();
  for(const item of items)container.append(renderCard(item));
  if(!items.length)container.append(node("p",null,"Keine Einträge in dieser Auswahl; keine automatische Freigabe ableitbar."));
  put("radar-showing",items.length+" von "+(data.items||[]).length+" kuratierten Aufgaben · "+data.inventory.other_fiverr_unreviewed+" weitere Fiverr-Aufgaben noch nicht einzeln reconciliert");
}
function renderRadar(snapshot) {
  const data=snapshot?.sprint_radar;
  last=data?.items?data:null;
  if(!last){put("radar-freshness","Radar nicht verfügbar – Quellenstand unbekannt.");return;}
  const gh=data.github||{};
  const observed=gh.observed_at?new Date(gh.observed_at).toLocaleString("de-DE"):"Unbekannt";
  put("radar-freshness",(gh.state==="loaded"?"GitHub-Metadaten geprüft: ":"GitHub teilweise nicht verfügbar: ")+observed+" · Sprint-Evidence: "+(data.source_date||"unbekannt")+" · PR ≠ BC-Abnahme");
  put("radar-count-next",data.counts.next||0);
  put("radar-count-waiting",data.counts.waiting||0);
  put("radar-count-implementation",data.counts.in_progress||0);
  put("radar-count-unreviewed",data.inventory.other_fiverr_unreviewed||0);
  const next=el("radar-priority");next.replaceChildren();
  for(const item of (data.next||[]).slice(0,3))next.append(renderCard(item));
  if(!next.children.length)next.append(node("p",null,"Keine verifizierte nächste Aufgabe."));
  const milestone=el("radar-milestones");milestone.replaceChildren();
  for(const m of data.milestones||[]){
    const item=node("div","radar-milestone");
    item.append(node("strong",null,m.name),node("span",null,m.state==="dev_verified"?"DEV-Nachweis vorhanden":m.state==="not_executed"?"Runtime ausstehend":"Nicht verifiziert"),node("small",null,"Noch offen: "+m.remaining));
    milestone.append(item);
  }
  const select=el("radar-area"),current=select.value;
  select.replaceChildren(new Option("Alle Bereiche","all"));
  for(const name of [...new Set((data.items||[]).map(x=>x.area))].sort())select.append(new Option(name,name));
  if([...select.options].some(o=>o.value===current))select.value=current;
  renderBoard();
}
el("radar-stage")?.addEventListener("change",renderBoard);
el("radar-area")?.addEventListener("change",renderBoard);
window.renderSprintRadar=renderRadar;
})();
