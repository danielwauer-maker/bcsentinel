/* AI-PM 2.2 desktop triage: read-only presentation of source observations.
   Never maps PRs to approvals or schedules, never performs network writes. */
(function(){
"use strict";
const byId=id=>document.getElementById(id);
let current=null;
function clean(value){return String(value??"").trim().toLocaleLowerCase("de-DE")}
function githubUrl(value){
  if(typeof value!=="string")return null;
  try{
    const url=new URL(value);
    if(url.protocol!=="https:"||url.hostname!=="github.com"||url.username||url.password||url.port)return null;
    if(!/^\/(danielwauer-maker)\/(bcsentinel|bcsentinel-frontend)\/(pull|issues)\/\d+(?:\/)?$/.test(url.pathname))return null;
    if(url.search||url.hash)return null;
    return url.href;
  }catch{return null}
}
function empty(container,message){
  const p=document.createElement("p");p.className="sub";p.textContent=message;container.appendChild(p);
}
function addLink(parent,url,label){
  const safe=githubUrl(url);if(!safe)return;
  const a=document.createElement("a");a.href=safe;a.target="_blank";a.rel="noopener noreferrer";a.textContent=label;parent.appendChild(a);
}
function item(container,title,subtitle,links){
  const article=document.createElement("article");article.className="exec-triage-item";
  const h=document.createElement("strong");h.textContent=title;article.appendChild(h);
  const p=document.createElement("p");p.textContent=subtitle;article.appendChild(p);
  if(links.length){const foot=document.createElement("div");foot.className="exec-triage-links";
    for(const [href,label] of links)addLink(foot,href,label);
    article.appendChild(foot);
  }
  container.appendChild(article);
}
function display(data){
  const query=clean(byId("exec-triage-search")?.value);
  const kind=byId("exec-triage-kind")?.value||"all";
  const chosen=byId("exec-triage-limit")?.value||"10";
  const limit=chosen==="all"?Number.MAX_SAFE_INTEGER:Number(chosen)||10;
  const evidence=data?.sprint_evidence||{};
  const works=Array.isArray(evidence.work_items)?evidence.work_items:[];
  const unique=new Map();
  for(const task of works){
    if(!task||typeof task.id!=="string")continue;
    const key=clean(task.id);
    const old=unique.get(key);
    if(old){ // Multiple observations: keep all distinct source URLs, without implying a newer status.
      const refs=[...new Set([...(old.refs||[]),...(Array.isArray(task.refs)?task.refs:[])])];
      old.refs=refs;
    }else unique.set(key,{...task,refs:Array.isArray(task.refs)?task.refs:[]});
  }
  const work=[...unique.values()].filter(t=>
    clean([t.id,t.title,t.status,t.detail,...t.refs].join(" ")).includes(query));
  const wr=byId("exec-work-list"),pr=byId("exec-pr-items");
  if(!wr||!pr)return;
  wr.replaceChildren();pr.replaceChildren();
  byId("exec-work-panel").hidden=kind==="prs";
  byId("exec-pr-panel").hidden=kind==="work";
  byId("exec-work-count").textContent=work.length+" passende Aufgaben · "+unique.size+" inventarisiert";
  if(!work.length)empty(wr,works.length?"Keine passenden kuratierten Aufgaben.":"Keine kuratierte Aufgaben-Evidence verfügbar.");
  for(const task of work.slice(0,limit)){
    const refs=[...new Set(task.refs)].filter(githubUrl);
    item(wr,task.id+" · "+(task.title||"Sprint-Evidence"),
      (task.status||"Status offen")+" · "+(task.detail||"Keine weitere Information"),refs.map((url,i)=>[url,"Quelle "+(i+1)]));
  }
  const repos=Array.isArray(data?.repositories)?data.repositories:[];
  const sourceOk=repos.length===2&&repos.every(r=>r.state==="loaded"&&r.pr_state==="loaded");
  const prs=new Map();
  for(const r of repos){
    if(!Array.isArray(r.open_prs))continue;
    for(const p of r.open_prs){
      if(!p||!Number.isInteger(p.number))continue;
      const key=String(r.repo)+"#"+p.number;
      if(!prs.has(key))prs.set(key,{...p,repo:r.repo});
    }
  }
  const entries=[...prs.values()].filter(p=>
    clean([p.repo,p.number,"#"+p.number,p.title,p.draft?"Draft":"Offen"].join(" ")).includes(query));
  entries.sort((a,b)=>{
    const ad=Date.parse(a.updated_at||"")||0,bd=Date.parse(b.updated_at||"")||0;
    return bd-ad||(a.repo||"").localeCompare(b.repo||"")||a.number-b.number;
  });
  byId("exec-pr-count").textContent=entries.length+" passende PRs · "+prs.size+" eindeutig";
  if(!entries.length)empty(pr,sourceOk?"Keine passenden offenen Pull Requests.":"Quellen unvollständig – keine vollständige PR-Aussage möglich.");
  for(const p of entries.slice(0,limit)){
    let date="Änderungszeit unbekannt";
    if(p.updated_at&&Number.isFinite(Date.parse(p.updated_at)))date=new Date(p.updated_at).toLocaleString("de-DE");
    item(pr,"#"+p.number+" · "+(p.title||"Ohne Titel"),(p.repo||"Repository unbekannt")+
      " · "+(p.draft?"Draft":"Offen")+" · Stand "+date,
      githubUrl(p.url)?[[p.url,"PR öffnen"]]:[]);
  }
  byId("exec-pr-freshness").textContent=sourceOk
    ?"GitHub-PR-Metadaten geladen · Zeitpunkt ist PR-Update, kein CI-/BC-Nachweis."
    :"GitHub-Quelle unvollständig · angezeigte PRs sind möglicherweise nicht vollständig.";
}
window.renderTriage=function(data){current=data;display(data)};
for(const id of ["exec-triage-search","exec-triage-kind","exec-triage-limit"]){
  const el=byId(id);
  if(el)el.addEventListener(id==="exec-triage-search"?"input":"change",()=>{if(current)display(current)});
}
})();
