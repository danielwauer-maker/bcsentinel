/* Read-only project media catalog. Never claims branch assets are deployed. */
(function () {
"use strict";
const $=id=>document.getElementById(id);
let payload=null;
function node(tag,cls,content) {
  const e=document.createElement(tag);
  if(cls)e.className=cls;
  if(content!==undefined)e.textContent=String(content);
  return e;
}
function urlFor(a,kind) {
  const p=new URLSearchParams({repo:a.repo,ref:a.ref,path:a.path});
  return "/api/media/"+kind+"?"+p.toString();
}
function githubUrl(value) {
  try {
    const u=new URL(value);
    if(u.protocol==="https:"&&u.hostname==="github.com"&&
      /^\/danielwauer-maker\/(bcsentinel|bcsentinel-frontend)\/blob\//.test(u.pathname))
      return u.href;
  } catch {}
  return null;
}
function anchor(href,label) {
  const a=node("a",null,label);
  a.href=href;
  a.rel="noopener noreferrer";
  a.target="_blank";
  return a;
}
function tablePreview(box,a) {
  const btn=node("button",null,"Tabellenvorschau anzeigen");
  btn.type="button";
  btn.addEventListener("click",async()=>{
    btn.disabled=true;
    const out=node("div","preview-table","Lade erste 8 Zeilen und 8 Spalten …");
    box.appendChild(out);
    try {
      const res=await fetch(urlFor(a,"table"),{cache:"no-store"});
      if(!res.ok)throw Error("Vorschau nicht verfügbar (HTTP "+res.status+")");
      const data=await res.json();
      out.replaceChildren();
      for(const sheet of data.sheets||[]) {
        out.appendChild(node("strong",null,sheet.name));
        const tbl=node("table");
        for(const row of sheet.rows||[]) {
          const tr=node("tr");
          for(const val of row)tr.appendChild(node("td",null,val));
          tbl.appendChild(tr);
        }
        out.appendChild(tbl);
      }
      out.appendChild(node("p","tiny","Begrenzte Vorschau, nicht die vollständige Datei."));
    } catch(e){out.textContent=e.message}
    finally{btn.disabled=false}
  });
  box.appendChild(btn);
}
function renderCard(a) {
  const article=node("article","asset"),thumb=node("div","thumb");
  if(a.preview==="image"){
    const img=document.createElement("img");
    img.alt="Vorschau: "+a.filename;
    img.loading="lazy";
    img.src=urlFor(a,"asset");
    img.addEventListener("error",()=>{thumb.replaceChildren(node("span","tiny","Vorschau nicht verfügbar"))});
    thumb.appendChild(img);
  }else{
    thumb.appendChild(node("div","doc",
      a.category==="PDF"?"PDF":a.category==="Tabelle"?"XLS":"DOC"));
  }
  article.appendChild(thumb);
  const body=node("div","body");
  body.appendChild(node("strong",null,a.filename));
  body.appendChild(node("div","tiny",a.path));
  body.appendChild(node("span","pill",a.category));
  body.appendChild(node("span","pill",a.version_state==="branch_candidate"?"Nur Draft-Branch":"Repository main"));
  body.appendChild(node("div","tiny",a.source+" · "+(Number.isInteger(a.size)?(a.size/1024).toFixed(1)+" KiB":"Größe unbekannt")));
  const git=githubUrl(a.url);
  if(git) {
    const p=node("p");p.appendChild(anchor(git,"GitHub-Datei öffnen"));body.appendChild(p);
  }
  if(a.preview==="pdf") {
    const p=node("p");p.appendChild(anchor(urlFor(a,"asset"),"PDF im Browser öffnen"));body.appendChild(p);
  }
  if(a.preview==="table")tablePreview(body,a);
  const detail=node("details"),summary=node("summary",null,"Verwendungsstellen & Status");
  detail.appendChild(summary);
  if(a.usage_state==="verified_source"&&Array.isArray(a.usage)&&a.usage.length){
    detail.appendChild(node("p","tiny","Statische Quellcode-Dateireferenz nachgewiesen, nicht Deployment:"));
    const ul=node("ul","usage");
    for(const use of a.usage){
      const li=node("li");
      const safe=githubUrl(use.url);
      li.appendChild(safe?anchor(safe,use.path):node("span",null,use.path));
      ul.appendChild(li);
    }
    detail.appendChild(ul);
  }else detail.appendChild(node("p","tiny",a.usage_state==="scan_incomplete"?"Referenzsuche unvollständig; Verwendung unbekannt.":"Keine direkte statische Dateireferenz erkannt; dynamische Einbindungen bleiben möglich."));
  detail.appendChild(node("p","tiny","Blob-SHA: "+(a.sha||"nicht verfügbar")));
  body.appendChild(detail);
  article.appendChild(body);
  return article;
}
function display() {
  if(!payload)return;
  const search=$("search").value.trim().toLocaleLowerCase("de-DE");
  const cat=$("category").value,src=$("source").value;
  const items=payload.assets.filter(a=>
    (cat==="all"||a.category===cat)&&
    (src==="all"||a.source===src)&&
    [a.filename,a.path,a.source,...(a.usage||[]).map(u=>u.path)].join(" ").toLocaleLowerCase("de-DE").includes(search)
  );
  const root=$("assets");root.replaceChildren();
  for(const item of items)root.appendChild(renderCard(item));
  $("status").textContent=items.length+" von "+payload.count+" Dateien · "+
    payload.sources.length+" GitHub-Quellen · "+(payload.errors.length?"Teilweise unvollständig":"Inventar geladen");
  if(!items.length)root.appendChild(node("p","muted","Keine Dateien gefunden. Filter ändern oder Quellstatus prüfen."));
}
async function load() {
  $("refresh").disabled=true;
  $("status").textContent="GitHub-Inventar wird geladen …";
  try {
    const r=await fetch("/api/media",{cache:"no-store"});
    if(!r.ok)throw Error("GitHub-Daten nicht verfügbar (HTTP "+r.status+")");
    const data=await r.json();
    if(!Array.isArray(data.assets)||!Array.isArray(data.sources))throw Error("Unvollständiges Antwortformat");
    payload=data;
    const old=$("source").value;
    $("source").replaceChildren(new Option("Alle Branches","all"));
    for(const s of data.sources)$("source").appendChild(new Option(s.source,s.source));
    if([...$("source").options].some(o=>o.value===old))$("source").value=old;
    const sources=$("sources");sources.replaceChildren();
    for(const s of data.sources) {
      const div=node("div","source-state");
      div.appendChild(node("strong",null,s.source+" · "+s.ref));
      div.appendChild(node("span","tiny"," · GitHub tree "+s.tree_sha.slice(0,12)+" · abgefragt "+s.observed_at));
      const c=s.coverage||{};
      div.appendChild(node("div","tiny","Statische Referenzsuche: "+(c.source_scanned??0)+"/"+(c.source_candidates??0)+" Quellcodedateien geprüft"+(c.limited?" · TEILABDECKUNG":"")+" · kein Nachweis eines Live-Deployments"));
      sources.appendChild(div);
    }
    for(const e of data.errors) sources.appendChild(node("p","error",e.source+": "+e.reason));
    display();
  }catch(e) {
    payload=null;
    $("assets").replaceChildren();
    $("status").textContent=e.message;
    $("status").classList.add("error");
  } finally{$("refresh").disabled=false}
}
for(const id of ["search","category","source"]) $(id).addEventListener(id==="search"?"input":"change",display);
$("refresh").addEventListener("click",load);
load();
})();
