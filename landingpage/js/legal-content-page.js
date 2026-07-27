/* LP-GL-11A — shared renderer for legal pages. */
(function(){
  const page=()=>document.body.dataset.legalPage||'';
  const esc=(v)=>String(v??'');
  function render(payload){
    const t=payload?.page,root=document.getElementById('legalPageRoot');if(!t||!root)return;
    document.title=t.metaTitle;const meta=document.querySelector('meta[name="description"]');if(meta)meta.content=t.metaDescription;
    const toc=(t.sections||[]).map(s=>`<a href="#${esc(s.id)}">${esc(s.title)}</a>`).join('');
    const sections=(t.sections||[]).map(s=>`<section class="legal-section" id="${esc(s.id)}"><h2>${esc(s.title)}</h2>${(s.paragraphs||[]).map(p=>`<p>${p}</p>`).join('')}${s.items?.length?`<ul>${s.items.map(i=>`<li>${i}</li>`).join('')}</ul>`:''}${s.note?`<div class="legal-note">${s.note}</div>`:''}</section>`).join('');
    root.innerHTML=`<div class="legal-page"><div class="legal-container"><section class="legal-hero"><div><p class="legal-eyebrow">${esc(t.eyebrow)}</p><h1>${esc(t.title)}</h1><p class="legal-lead">${esc(t.lead)}</p></div><aside class="legal-meta"><strong>${esc(t.updatedLabel)}</strong><span>${esc(t.updated)}</span></aside></section>${t.notice?`<div class="legal-note" style="margin-bottom:28px">${t.notice}</div>`:''}<div class="legal-layout"><nav class="legal-toc" aria-label="${esc(t.tocAria)}"><strong>${esc(t.tocTitle)}</strong>${toc}</nav><main class="legal-content">${sections}</main></div></div></div>`;
  }
  async function load(){const bundle=page();if(!bundle||!window.BCSentinelContent)return;const payload=await window.BCSentinelContent.loadBundle(bundle,document.documentElement.lang==='en'?'en':'de');render(payload)}
  function init(){load().catch(()=>{});new MutationObserver(m=>{if(m.some(x=>x.attributeName==='lang'))load().catch(()=>{})}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']})}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();