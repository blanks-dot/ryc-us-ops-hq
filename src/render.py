#!/usr/bin/env python3
"""Swimlane process flow: data.json -> tasks.html + history snapshot; bumps version.txt."""
import json, os, html, shutil
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from hqnav import hqnav, HEAD as HQHEAD
D = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(D, "data.json")))
vf = os.path.join(D, "version.txt")
v = (int(open(vf).read().strip()) if os.path.exists(vf) else 0) + 1
PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">%BASE%<title>Tasks</title>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">
<style>
:root{--pink:#e03870;--pink4:#f9d7e2;--blue:#3870e0;--blue4:#d7e2f9;--navy:#091f77;--navy2:#4f5f9e;--navy3:#969fc5;--gray:#dbdae5;--gray3:#e9e9ef;--gray4:#f0f0f5;--gray5:#f8f8fa;
--fd:'Bricolage Grotesque',system-ui,sans-serif;--fb:'DM Sans',system-ui,sans-serif}
*{box-sizing:border-box}html,body{margin:0}body{background:var(--gray5);color:var(--navy);font:12.5px/1.3 var(--fb)}
header{background:#fff;color:var(--navy);border-bottom:1px solid var(--gray);padding:9px 16px 9px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
h1{font:800 19px/1.1 var(--fd);letter-spacing:-.02em;margin:0}.sub{opacity:.75;font-size:12px;margin-top:2px}
.tools{margin-left:auto;display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.chip{border:0;padding:4px 2px;cursor:pointer;font-weight:600;font-size:12.5px;background:transparent;color:var(--navy)}.chip b{color:var(--pink);margin-left:3px}
.chip.on{text-decoration:underline;text-decoration-color:var(--pink);text-decoration-thickness:2px;text-underline-offset:4px}.chip .k{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}
input.q{border:1px solid var(--gray);border-radius:999px;padding:5px 12px;font:inherit;width:130px;color:var(--navy)}
.views{display:flex;gap:4px;background:var(--gray3);border-radius:999px;padding:3px;margin-left:8px}.views a{color:var(--navy);text-decoration:none;padding:5px 12px;border-radius:999px;font-weight:600;font-size:12px}.views a.on{background:var(--navy);color:#fff}
.ver{font:11px ui-monospace,Menlo,monospace;opacity:.6;margin-left:8px}.ver a{color:#fff;text-decoration:none;padding:0 3px}
.grid{display:grid;grid-template-columns:calc(var(--fs,12px)*9.6) repeat(5,minmax(0,1fr)) minmax(0,.8fr);gap:5px;padding:7px 12px 4px}
.tl0{}.tl{display:flex;align-items:stretch}.tl span{flex:1;display:flex;align-items:center;color:var(--navy);font:700 calc(var(--fs,12px)*.85) var(--fd);padding:4px 6px 4px 20px;margin-right:-6px;clip-path:polygon(0 0,calc(100% - 12px) 0,100% 50%,calc(100% - 12px) 100%,0 100%,12px 50%)}.tl span:first-child{padding-left:10px;clip-path:polygon(0 0,calc(100% - 12px) 0,100% 50%,calc(100% - 12px) 100%,0 100%)}.tlo{display:flex;align-items:center;justify-content:center;color:var(--pink);color:var(--navy);font:700 calc(var(--fs,12px)*.86) var(--fd)}
.ph{background:#fff;border-radius:9px;padding:5px 9px;box-shadow:0 1px 3px rgba(9,31,119,.08);position:sticky;top:0;z-index:2}
.ph b{font:800 calc(var(--fs,12px)*1.4) var(--fd);letter-spacing:-.01em;display:block}.ph .goal{display:block;font-size:calc(var(--fs,12px)*.85);line-height:1.25;color:var(--navy2);margin-top:2px}.ph small{display:block;color:var(--navy2);font-size:calc(var(--fs,12px)*.85);font-weight:600}
.tier{background:var(--navy);color:#fff;border-radius:11px;padding:9px 10px}
.tier b{font:800 calc(var(--fs,12px)*1.4) var(--fd);display:block;letter-spacing:-.01em}.tier .who{font-weight:700;margin-top:2px;font-size:calc(var(--fs,12px)*.85);line-height:1.25}.tier .role{opacity:.75;font-size:calc(var(--fs,12px)*.85);margin-top:5px;line-height:1.3}
.tier .n{display:inline-block;margin-top:6px;background:rgba(255,255,255,.14);border-radius:999px;padding:2px 9px;font-size:calc(var(--fs,12px)*.9)}
.cell{background:#fff;border-radius:11px;padding:7px 5px;border:1px solid var(--gray3);display:flex;flex-direction:column;gap:4px}
.cell.all{background:#fff}.tier.ai{background:var(--gray);color:var(--navy)}
.t{display:flex;gap:6px;align-items:flex-start;padding:2px 6px;border-radius:6px;cursor:pointer;line-height:1.32;font-size:var(--fs,12px);color:#1d2c6e}
.t:hover,.t.sel{background:var(--blue4)}.t .dt{flex:none;width:calc(var(--fs,12px)*.42);height:calc(var(--fs,12px)*.42);border-radius:50%;margin-top:calc(var(--fs,12px)*.45);background:var(--navy3)}.t .dt.d{background:none;box-shadow:inset 0 0 0 1.5px var(--blue)}.t .x{flex:1;overflow-wrap:anywhere}.t.idea .x{font-style:italic;color:var(--navy2)}
.t .m{flex:none;display:flex;gap:2px;padding-top:1px}.t .m i{width:var(--fs,12px);height:var(--fs,12px);border-radius:50%;font:700 calc(var(--fs,12px)*.7)/var(--fs,12px) var(--fb);color:#fff;text-align:center;font-style:normal}
.m .r{background:var(--pink)}.m .n{background:var(--navy);border-radius:4px!important}.t .dt.ch{background:var(--pink);width:calc(var(--fs,12px)*.62);height:calc(var(--fs,12px)*.62);margin-top:calc(var(--fs,12px)*.34)}.t .dt.d.ch{box-shadow:inset 0 0 0 2px var(--navy)}.own{font-size:calc(var(--fs,12px)*.85);line-height:1.3;color:var(--navy2);padding:3px 4px;align-self:end}#tip{position:fixed;z-index:20;max-width:380px;background:var(--navy);color:#fff;border-radius:9px;padding:9px 11px;font-size:12.5px;line-height:1.35;pointer-events:none;box-shadow:0 6px 22px rgba(9,31,119,.3);display:none}#tip .tr{color:#f9d7e2;margin-top:5px}#tip .tc{color:#d7e2f9;margin-top:5px}#tip p{margin:0 0 4px}#dr textarea,#dr input.nm{width:100%;border:1px solid var(--gray);border-radius:8px;padding:7px 9px;font:inherit;color:var(--navy);margin-top:5px}#dr textarea{min-height:64px;resize:vertical}#dr .btn{margin-top:6px;border:0;background:var(--pink);color:#fff;border-radius:999px;padding:6px 14px;font-weight:700;cursor:pointer}#dr .note{background:var(--gray4);border-radius:8px;padding:7px 9px;margin-top:6px}#dr .note small{color:var(--navy2);display:block;margin-bottom:2px}#dr .note .del{float:right;border:0;background:none;color:var(--navy3);cursor:pointer}.m .c{background:var(--blue)}.m .dc{background:#a8ffb2;color:var(--navy)!important}
.t.dim{opacity:.13}
.foot{padding:2px 14px 8px;color:var(--navy2);font-size:11.5px;display:flex;gap:16px;flex-wrap:wrap}
.foot i{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:-1px;margin-right:4px}
#dr{position:fixed;top:0;right:0;height:100vh;width:380px;background:#fff;box-shadow:-8px 0 30px rgba(9,31,119,.18);padding:20px 22px;overflow:auto;transform:translateX(105%);transition:transform .18s;z-index:10}
#dr.open{transform:none}#dr .close{position:absolute;top:12px;right:14px;border:0;background:var(--gray4);border-radius:999px;width:28px;height:28px;cursor:pointer;color:var(--navy);font-size:15px}
#dr h2{font:700 17px/1.25 var(--fd);margin:6px 30px 4px 0}#dr .k{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--navy2);margin-top:14px;font-weight:700}
#dr .box{padding:8px 10px;border-radius:8px;margin-top:5px}.rb{background:var(--pink4)}.cb{background:var(--blue4)}
#dr ol,#dr ul{padding-left:18px;margin:6px 0}#dr li{margin:4px 0}#dr a{color:var(--blue)}
@media (prefers-reduced-motion:reduce){#dr{transition:none}}
#dr input.nm{width:100%;border:1px solid var(--gray);border-radius:8px;padding:6px 8px;font:inherit;color:var(--navy);margin-top:6px}
.own{font-style:italic}

/* Calmer view: neutral season ribbon, Now marker, fewer dots, role + now controls */
body{background:#f5f5f9}
.tl span{background:#e9e9ef!important;color:var(--navy2)!important}
.tl span.now{background:var(--navy)!important;color:#fff!important}
.ph{box-shadow:none;border:1.5px solid transparent}
.ph.now{border-color:var(--navy)}
.ph.now b::after{content:"Now";margin-left:8px;font:700 calc(var(--fs,12px)*.8)/1 var(--fb);color:var(--pink);vertical-align:middle}
.chip{border:0;padding:6px 12px;border-radius:999px;box-shadow:inset 0 0 0 1.5px var(--gray);font:600 12.5px/1 var(--fb)}.chip .k{display:none}.chip.on{background:var(--navy);color:#fff;text-decoration:none;box-shadow:none}.chip:hover{background:#dedeea}.chip.on:hover{background:var(--navy)}
.cell{border:0;box-shadow:0 1px 2px rgba(9,31,119,.06);gap:3px;padding:8px 5px}
.t .dt{background:#b9bfd9}
.t .dt.ch{background:var(--pink)}
.fade{opacity:.35}
.tbar{background:#fff;border-bottom:1px solid #ececf3;padding:10px 24px}
.tbar .tools{margin-left:0;justify-content:flex-start}
.grid{gap:10px!important;padding:16px 24px 24px!important}
.ph{position:static!important;padding:10px 12px!important;border-radius:14px!important}
.cell{border-radius:14px!important;padding:10px 8px!important;gap:5px!important}
.tier{border-radius:14px!important;padding:12px!important}
.t{padding:3px 6px!important;line-height:1.38!important}
.own{padding:6px 4px!important}
.tools{gap:10px}
.seg{display:flex;gap:2px;background:#e9e9ef;border-radius:999px;padding:3px}
.seg button,.nowt{border:0;background:transparent;font:600 12.5px/1 var(--fb);color:var(--navy);padding:6px 11px;border-radius:999px;cursor:pointer;white-space:nowrap}
.seg button:hover,.nowt:hover{background:#dedeea}
.seg button.on{background:#fff;box-shadow:0 1px 3px rgba(9,31,119,.15)}
.nowt{box-shadow:inset 0 0 0 1.5px var(--gray)}
.nowt.on{background:var(--navy);color:#fff;box-shadow:none}
@media (max-width:760px){.seg{overflow-x:auto;max-width:100%}}
.phonehint{display:none}
@media (max-width:760px){.gscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}.gscroll .grid{min-width:1000px}.phonehint{display:block;margin:8px 16px 0;font-size:13px;color:var(--navy2)}.phonehint a{color:var(--navy);font-weight:700}header .tools{width:100%}}
</style>%HQHEAD%</head><body>
<header><div><h1>Tasks</h1><div class="sub">Every task, by role and season</div></div>%HQNAV%
</header><div class="tbar"><div class="tools" id="tools"></div></div>
<p class="phonehint">Built for a laptop. On a phone, swipe the grid sideways, or use the <a href="tracker.html">Tracker</a> for this week's work</p><div class="gscroll"><div class="grid" id="grid"></div></div>
<div id="dr" role="dialog" aria-label="Task detail"></div>
<script id="paint-data" type="application/json">%DATA%</script>
<script>
const V=%VER%,LATEST=%LATEST%,D=JSON.parse(document.getElementById('paint-data').textContent);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const F={risk:['Current challenges','var(--pink)',s=>s.risk]};
const NOWM={plan:[11,12,5,6],setup:[12,1,6,7],prep:[1,2,7,8],season:[3,4,9,10],close:[4,5,6,10,11,12]};const MON=new Date().getMonth()+1;const NOW=k=>k==='all'||(NOWM[k]||[]).includes(MON);
const RK='usops-tasks-view';let VW=(()=>{try{return JSON.parse(localStorage.getItem(RK)||'{}')}catch(e){return {}}})();const saveVW=()=>{try{localStorage.setItem(RK,JSON.stringify(VW))}catch(e){}};
const VIS=()=>VW.role?1:D.tiers.length;
let filt=null,q='';
const NK='usops-notes-v1';const NS=()=>{try{return JSON.parse(localStorage.getItem(NK)||'{}')}catch(e){return {}}};const nn=id=>(NS()[id]||[]).length;
const ok=s=>(!filt||F[filt][2](s))&&(!q||(s.short+' '+s.full+' '+(s.risk||'')+' '+(s.conflict||'')).toLowerCase().includes(q));
const row=s=>`<div class="t ${s.idea?'idea':''} ${ok(s)?'':'dim'}" data-id="${esc(s.id)}" tabindex="0"><span class="dt ${s.risk?'ch':''}"></span><span class="x">${esc(s.short)}</span>${nn(s.id)?`<span class="m">${nn(s.id)?`<i class="n" title="Notes">${nn(s.id)}</i>`:''}</span>`:''}</div>`;
function draw(){
 const _sp=D.phases.filter(p=>p.key!=='all'),_tc=["#f9d7e2", "#f3afc6", "#ec88a9", "#e6608d", "#e03870"];let h=`<div class="tl0"></div><div class="tl" style="grid-column:span ${_sp.length}">${_sp.map((p,i)=>`<span class="${NOW(p.key)?'now':''}" style="background:${_tc[i%_tc.length]};color:${i>=3?'#fff':'var(--navy)'}">${esc(p.when)}</span>`).join('')}</div>`+(D.phases.some(p=>p.key==='all')?`<div class="tlo">&#8635; ${esc(D.phases.find(p=>p.key==='all').when)}</div>`:'')+`<div class="own"></div>`+D.phases.map(p=>`<div class="ph ${NOW(p.key)&&p.key!=='all'?'now':''} ${VW.now&&!NOW(p.key)?'fade':''}" data-ph="${p.key}"><b>${esc(p.label)}</b><span class="goal">${esc(p.goal||"")}</span></div>`).join('');
 for(const t of D.tiers){const n=D.steps.filter(s=>s.tier===t.key).length;
  if(VW.role&&VW.role!==t.key)continue;
  h+=`<div class="tier ${t.key==='A'||t.key==='P'?'ai':''}"><b>${esc(t.label)}</b><div class="who">${esc(t.who)}</div><div class="role">${esc(t.role)}</div></div>`;
  for(const p of D.phases)h+=`<div class="cell ${p.key==='all'?'all':''} ${VW.now&&!NOW(p.key)?'fade':''}">${D.steps.filter(s=>s.tier===t.key&&s.phase===p.key).map(row).join('')}</div>`}
 const g=document.getElementById('grid');g.innerHTML=h;
 g.querySelectorAll('.t').forEach(e=>{e.onclick=()=>{tip.style.display='none';if(cur===e.dataset.id&&dr.classList.contains('open'))closeDr();else show(e.dataset.id)};e.onmouseenter=ev=>tipOn(e.dataset.id,ev);e.onmousemove=tipMove;e.onmouseleave=()=>{clearTimeout(tt);tip.style.display='none'};e.onkeydown=ev=>{if(ev.key==='Enter')show(e.dataset.id)}});
 document.getElementById('tools').innerHTML=`<div class="seg" role="group" aria-label="Show role">`+[['','Everyone']].concat(D.tiers.map(t=>[t.key,t.label])).map(([k,l])=>`<button class="${(VW.role||'')===k?'on':''}" data-role="${k}">${esc(l)}</button>`).join('')+`</div><button class="nowt ${VW.now?'on':''}" aria-pressed="${!!VW.now}">Now only</button>`+Object.entries(F).map(([k,[n,c]])=>`<span class="chip ${filt===k?'on':''}" data-f="${k}"><span class="k" style="background:${c}"></span>${n}</span>`).join('')+
  `<input class="q" placeholder="Search" value="${esc(q)}" aria-label="Search tasks">`;
 document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{filt=filt===c.dataset.f?null:c.dataset.f;draw()});
 document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{VW.role=b.dataset.role;saveVW();draw();fit()});
 document.querySelector('.nowt').onclick=()=>{VW.now=!VW.now;saveVW();draw()};
 const qi=document.querySelector('input.q');qi.oninput=()=>{q=qi.value.toLowerCase();const p=qi.selectionStart;draw();const n=document.querySelector('input.q');n.focus();n.setSelectionRange(p,p)};
 nav();
}
const dr=document.getElementById('dr');let cur=null;const tip=document.createElement('div');tip.id='tip';document.body.appendChild(tip);let tt;
function tipMove(ev){const w=tip.offsetWidth,h=tip.offsetHeight;let x=ev.clientX+14,y=ev.clientY+16;if(x+w>innerWidth-8)x=ev.clientX-w-14;if(y+h>innerHeight-8)y=ev.clientY-h-12;tip.style.left=x+'px';tip.style.top=y+'px'}
function tipOn(id,ev){clearTimeout(tt);tt=setTimeout(()=>{const s=D.steps.find(x=>x.id===id);tip.innerHTML=s.parts.map(q=>`<p>${esc(q.full)}</p>${q.risk?`<div class="tr">Current challenge: ${esc(q.risk)}</div>`:''}${q.conflict?`<div class="tc">Conflicting guidance: ${esc(q.conflict)}</div>`:''}${q.decision?`<div class="tc" style="color:#a8ffb2">Decided: ${esc(q.decision)}</div>`:''}`).join('<hr style="border:0;border-top:1px solid rgba(255,255,255,.2);margin:6px 0">');tip.style.display='block';tipMove(ev)},250)}
function closeDr(){dr.classList.remove('open');cur=null;document.querySelectorAll('.t.sel').forEach(x=>x.classList.remove('sel'))}
function open(h){dr.innerHTML='<button class="close" aria-label="Close">&times;</button>'+h;dr.classList.add('open');dr.querySelector('.close').onclick=closeDr}
function show(id){cur=id;const s=D.steps.find(x=>x.id===id),t=D.tiers.find(x=>x.key===s.tier),p=D.phases.find(x=>x.key===s.phase);
 document.querySelectorAll('.t').forEach(e=>e.classList.toggle('sel',e.dataset.id===id));
 open(`<div class="k" style="margin-top:0">${esc(t.label)}, ${esc(p.label)}</div><h2>${esc(s.short)}</h2>${s.parts.length>1?`<div style="color:var(--navy2)">Combines ${s.parts.length} tasks</div>`:''}`+
 s.parts.map(q=>`<div class="k">${q.num?'Task #'+q.num:'From the Key problems doc'}${q.when?', '+esc(q.when):''}</div><div>${esc(q.full)}</div>
 ${q.risk?`<div class="box rb">${esc(q.risk)}</div>`:''}${q.conflict?`<div class="box cb">${esc(q.conflict)}</div>`:''}${q.decision?`<div class="box" style="background:#deffe1"><b>Decided:</b> ${esc(q.decision)}</div>`:''}<div style="color:var(--navy3);font-size:11px;margin-top:3px">${esc(q.src)}</div>`).join('')+notesHtml(id));wireNotes(id)}
function notesHtml(id){const L=NS()[id]||[];return `<div class="k">Notes</div>${L.map((n,i)=>`<div class="note"><button class="del" data-i="${i}" aria-label="Delete note">&times;</button><small>${n.who&&n.who!=='Anonymous'?`<b>${esc(n.who)}</b> &middot; `:''}${esc(n.at)}</small>${esc(n.text)}</div>`).join('')||'<div style="color:var(--navy3);margin-top:4px">No notes yet.</div>'}<input class="nm" placeholder="Your name" aria-label="Your name" value="${esc(localStorage.getItem('usops-name')||'')}"><textarea placeholder="Add a note or suggested change" aria-label="Note"></textarea><button class="btn">Add note</button>`}
function wireNotes(id){const b=dr.querySelector('.btn');b.onclick=()=>{const t=dr.querySelector('textarea').value.trim(),w=(dr.querySelector('.nm').value.trim()||'Anonymous');localStorage.setItem('usops-name',w==='Anonymous'?'':w);if(!t)return;const S=NS();(S[id]=S[id]||[]).push({who:w,text:t,at:new Date().toLocaleString([], {month:'short',day:'numeric',hour:'numeric',minute:'2-digit'})});localStorage.setItem(NK,JSON.stringify(S));draw();show(id)};
 dr.querySelectorAll('.del').forEach(x=>x.onclick=()=>{const S=NS();S[id].splice(+x.dataset.i,1);localStorage.setItem(NK,JSON.stringify(S));draw();show(id)})}
const _i=document.getElementById('info');if(_i)_i.onclick=e=>{e.preventDefault();open(`<h2>Design principles</h2><ol>${D.principles.map(p=>`<li>${esc(p)}</li>`).join('')}</ol>
 <div class="k">Conflicts to resolve</div><ul>${D.steps.filter(s=>s.conflict).map(s=>`<li><a href="#" data-go="${esc(s.id)}">${esc(s.short)}</a></li>`).join('')}</ul>
 <div class="k">Where the work lives</div><ul>${D.links.map(([t,u])=>`<li><a href="${esc(u)}" target="_blank">${esc(t)}</a></li>`).join('')}</ul>`);
 dr.querySelectorAll('[data-go]').forEach(a=>a.onclick=e=>{e.preventDefault();show(a.dataset.go)})};
let T=V;function nav(){const p=document.getElementById('prev'),n=document.getElementById('next'),of=document.getElementById('of');if(!p)return;p.href=V>1?`history/v${V-1}.html`:'#';of.textContent='/'+T;n.href=V<T?(V+1===T?'tasks.html':`history/v${V+1}.html`):'#'}

function fit(){const g=document.getElementById('grid'),de=document.documentElement;if(innerWidth<760){g.style.setProperty('--fs','12px');g.style.height='';g.style.gridTemplateRows='';return}let lo=9,hi=VW.role?16:17;g.style.height='';g.style.gridTemplateRows='';
 for(let k=0;k<14;k++){const m=(lo+hi)/2;g.style.setProperty('--fs',m+'px');
  if(de.scrollHeight<=innerHeight&&de.scrollWidth<=innerWidth)lo=m;else hi=m}
 if(lo<13.5){g.style.setProperty('--fs','13.5px');g.style.height='';g.style.gridTemplateRows='';return}g.style.setProperty('--fs',lo+'px');g.style.gridTemplateRows=`auto auto repeat(${VIS()},1fr)`;g.style.height=(innerHeight-g.getBoundingClientRect().top-2)+'px';if(VW.role){g.style.height='';g.style.gridTemplateRows=''}}
let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(fit,80)});
draw();fit();document.fonts&&document.fonts.ready.then(fit);
async function poll(){try{const r=await fetch('version.txt?'+Date.now(),{cache:'no-store'});T=parseInt(await r.text());nav();if(LATEST&&T>V)location.reload();}catch(e){}setTimeout(poll,1200);}poll();

document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();const q=document.querySelector('input.q');if(q){q.focus();q.select()}}});
</script></body></html>"""
def page(latest):
    return (PAGE.replace("%BASE%", "" if latest else '<base href="../">').replace("%TITLE%", html.escape(data["title"])).replace("%HQNAV%", hqnav("tasks")).replace("%HQHEAD%", HQHEAD)
        .replace("%SUB%", html.escape(data["subtitle"])).replace("%VER%", str(v)).replace("%LATEST%", "true" if latest else "false")
        .replace("%DATA%", json.dumps(data).replace("</", "<\\/")))
open(os.path.join(D, "history", f"v{v}.html"), "w").write(page(False))
shutil.copy(os.path.join(D, "data.json"), os.path.join(D, "history", f"v{v}.json"))
open(os.path.join(D, "tasks.html"), "w").write(page(True)); open(vf, "w").write(str(v)); print("rendered v", v)

import subprocess, sys
subprocess.run([sys.executable, os.path.join(D, "render_alts.py")], check=True)
