#!/usr/bin/env python3
"""Build the US Ops HQ tracker (tracker.html) and chapter board (chapters.html).

Tracker tasks are the real live-phase lines from data.json with evidence-backed statuses. The chapter names and current assignments come from
the US CHAPTER INDEX sheet, tab "Chapter Assignments", snapshot saved in
chapters-src/assignments-2026-11-23.tsv (read 2026-11-23, read only).
Options A and B from round one live in history/tracker-v1/.
"""
import json, html, pathlib
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from hqnav import hqnav, HEAD as HQHEAD

HERE = pathlib.Path(__file__).parent

# Reporting lines (Nov 23 working session)
PEOPLE = [
    {"id": "mary", "name": "Mary", "role": "CEO", "reports": None, "tracker": False},
    {"id": "catherine", "name": "Catherine", "role": "Lead", "reports": "mary"},
    {"id": "whitney", "name": "Whitney", "role": "Coordinator", "reports": "catherine"},
    {"id": "sierra", "name": "Sierra", "role": "Coordinator", "reports": "catherine"},
    {"id": "alaysia", "name": "Alaysia", "role": "Intern", "reports": "whitney"},
    {"id": "lily", "name": "Lily", "role": "Intern", "reports": "whitney"},
    {"id": "nicole", "name": "Nicole", "role": "Intern", "reports": "sierra"},
    {"id": "aisling", "name": "Aisling", "role": "Intern", "reports": "sierra"},
    {"id": "josh", "name": "Josh", "role": "AI / COO", "reports": None},
]

# Real task lines from data.json for what's live in late Nov 2026: fall "Handoff + close",
# spring "Plan + recruit" and "All year". Owners follow the tier (Lead = Catherine,
# Coordinator = Sierra and/or Whitney, Intern = the four interns, AI / COO = Josh).
# Status: Done only with evidence; notes only where a real fact backs them.
COORDS = ["sierra", "whitney"]
INTERNS_ALL = ["alaysia", "lily", "nicole", "aisling"]
TIER_OWNER = {"L": ["catherine"], "C": COORDS, "I": INTERNS_ALL, "A": ["josh"]}
OWNER_PICK = {  # where the grid or the record points at one coordinator
    "g21": ["sierra"],   # interest calls: S27 replies go to Sierra's daily digest
    "g17": ["sierra"],   # chapter materials: Sierra's "review Chapter Hub resources" row
    "g35": ["whitney"],  # onboarding: Whitney aligns the newest intern's first priorities
}
STATUS = {  # id: (status, note, source)
    "g1": ("done", "Q4 and 2027 goals marked Complete in the team priorities sheet", "RYC team priorities sheet, rows due Nov 22"),
    "g3": ("doing", "Working session on Nov 23", ""),
    "g4": ("doing", "Chapter remap started Nov 23", ""),
    "g5": ("doing", "Draft red zone and pause rules written Nov 23", ""),
    "g6": ("doing", "Draft standards in the playbook", ""),
    "g11": ("doing", "Recap with owners after every weekly call, agreed Nov 22", "C-suite Connect 11/22"),
    "g13": ("doing", "", ""),
    "g93": ("doing", "", ""),
    "g54": ("doing", "Newsletter is an action item from the US Ops call", "team priorities sheet"),
    "g16": ("doing", "Recruiting form and role descriptions going to the chapter listserv", "C-suite Connect 11/22"),
    "g17": ("doing", "Chapter hub redesign with tech agreed Nov 22", "C-suite Connect 11/22"),
    "g20": ("doing", "Power 4 roster push on Nov 21", "S27 log 11/21"),
    "g21": ("doing", "", ""),
    "g22": ("doing", "One lead per school rule set Nov 22", "S27 log 11/22"),
    "g23": ("doing", "4 new chapters committed as of Nov 15", "Exec Connect 11/15"),
    "g88": ("doing", "Chapter remap started Nov 23", ""),
    "g35": ("doing", "Newest intern joined Nov 15; onboarding resources sent Nov 16", "team priorities sheet"),
    "g51": ("doing", "Program dev is working through the feedback form results", "team priorities sheet"),
    "g52": ("doing", "", ""),
    "g92": ("doing", "", ""),
    "g56": ("doing", "Runs daily; 46 of 50 DMs delivered on Nov 23", "S27 health card 11/23"),
    "g59": ("doing", "Spring 2027 status notes started in the chapter index", "US CHAPTER INDEX, Total chapters tab"),
    "g80": ("doing", "Leadership turnover planning underway", "Exec Connect 11/15"),
    "g81": ("doing", "Feedback ratings are in; low-support chapters get a call", "Exec Connect 11/15"),
    "g83": ("todo", "Planned for chapters that rated support 3 or below", "Exec Connect 11/15"),
    "g78": ("doing", "Recruiting form and role descriptions going to the chapter listserv", "C-suite Connect 11/22"),
    "g84": ("doing", "", ""),
    "g85": ("doing", "Chapters asked to fill in the status tracker weekly", "team priorities sheet"),
    "g87": ("doing", "App restructuring ideas shared with tech", "Exec Connect 11/15"),
    "g53": ("doing", "Tech is building parent check-in reminder emails", "Exec Connect 11/15"),
}
PHASE_DUE = {"close": "By mid-Dec", "plan": "Dec-Jan", "all": "Ongoing"}
PHASE_NAME = {"close": "Fall close", "plan": "Spring plan + recruit", "all": "All year"}


def real_tasks():
    d = json.loads((HERE / "data.json").read_text())
    out = []
    for g in d["steps"]:
        if g["phase"] not in PHASE_DUE:
            continue
        st, note, src = STATUS.get(g["id"], ("todo", "", ""))
        out.append({"id": g["id"], "text": g["short"], "owners": OWNER_PICK.get(g["id"], TIER_OWNER[g["tier"]]),
                    "tier": g["tier"], "phase": g["phase"], "due": PHASE_DUE[g["phase"]], "status": st,
                    "note": note, "src": src})
    order = {"close": 0, "plan": 1, "all": 2}
    out.sort(key=lambda t: (order[t["phase"]], "LCIA".index(t["tier"])))
    return out


# ---------------- chapters ----------------
INTERNS = ["alaysia", "lily", "nicole", "aisling"]
STEPS = ["Go/no-go", "Intern connected", "Location", "Dates", "Leadership team", "Signups", "Session one"]


def load_chapters():
    states = {}
    for line in (HERE / "chapters-src" / "states-2026-11-23.tsv").read_text().splitlines():
        if line.strip():
            n, st = (line.split("\t") + [""])[:2]
            states[n.strip()] = {"IO": "ID"}.get(st.strip(), st.strip())  # sheet typo: Caldwell, IO
    rows = []
    for line in (HERE / "chapters-src" / "assignments-2026-11-23.tsv").read_text().splitlines():
        if not line.strip():
            continue
        name, cohort, f26, l1, l2 = (line.split("\t") + [""] * 5)[:5]
        rows.append({"name": name.strip(), "cohort": cohort.strip(), "f26": f26.strip(),
                     "l1": l1.strip(), "l2": l2.strip(), "state": states.get(name.strip(), "")})
    return rows


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800'
         '&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">')

CSS = r"""
:root{--ink:#091f77;--ink2:#4f5f9e;--ink3:#6573aa;--pink:#e03870;--pinkbg:#fdf0f4;--line:#dbdae5;--line2:#e9e9ef;--bg:#f6f6f9;--fd:'Bricolage Grotesque',system-ui,sans-serif;--fb:'DM Sans',system-ui,sans-serif}
*{box-sizing:border-box}html,body{margin:0}body{background:var(--bg);color:var(--ink);font:15px/1.45 var(--fb);-webkit-font-smoothing:antialiased}
button,input,select,textarea{font:inherit;color:inherit}
header.top{position:sticky;top:0;z-index:30;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:12px 24px}
header.top h1{font:800 22px/1.1 var(--fd);letter-spacing:-.02em;margin:0}
header.top .sub{font-size:13px;color:var(--ink2);margin-top:3px;max-width:680px}
.tagx{display:inline-block;font:700 10.5px/1 var(--fb);letter-spacing:.06em;text-transform:uppercase;padding:4px 7px;border-radius:6px;background:#ebebf2;color:var(--ink2);margin-left:6px;vertical-align:2px}
.tagx.pk{background:var(--pinkbg);color:#b01f52}
nav.sw{margin-left:auto;display:flex;gap:3px;background:#ebebf2;border-radius:999px;padding:4px;flex-wrap:wrap}
nav.sw a{color:var(--ink);text-decoration:none;padding:7px 15px;border-radius:999px;font-weight:600;font-size:14px;white-space:nowrap}
nav.sw a:hover{background:#dedeea}nav.sw a.on{background:var(--ink);color:#fff}
main{padding:22px 24px 48px;max-width:1520px;margin:0 auto}
h2{font:800 20px/1.15 var(--fd);letter-spacing:-.015em;margin:0}h3{font:700 16px/1.2 var(--fd);margin:0}
.muted{color:var(--ink2)}.small{font-size:13px}
.card{background:#fff;border:1px solid var(--line);border-radius:14px}
.pill{display:inline-flex;align-items:center;gap:5px;font:600 12px/1 var(--fb);padding:5px 9px;border-radius:999px;white-space:nowrap;border:1px solid transparent}
.st-todo{background:#f0f0f5;color:var(--ink2)}.st-doing{background:#fff;color:var(--ink);border-color:#b9bfd9}
.st-blocked{background:var(--pinkbg);color:#b01f52;border-color:#f3afc6}.st-done{background:var(--ink);color:#fff}
.who{display:inline-block;font:600 12px/1 var(--fb);padding:5px 8px;border-radius:7px;background:#eef0f7;color:var(--ink);white-space:nowrap}
.due{font-size:13px;color:var(--ink2);white-space:nowrap}.due.over{color:#b01f52;font-weight:600}
.btn{border:0;background:var(--ink);color:#fff;font-weight:600;font-size:14px;padding:9px 15px;border-radius:999px;cursor:pointer}
.btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line)}
.btn:focus-visible,button:focus-visible,a:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--pink);outline-offset:2px}
.toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:var(--ink);color:#fff;padding:10px 16px;border-radius:999px;font-size:14px;opacity:0;transition:opacity .2s;pointer-events:none;z-index:50}.toast.on{opacity:1}
@media (max-width:900px){header.top{padding:10px 14px;gap:10px}nav.sw{margin-left:0;width:100%;justify-content:space-between}nav.sw a{padding:6px 10px;font-size:13px}main{padding:16px 14px 40px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

NAV = [("./", "Tasks", "tasks"), ("playbook-a.html", "Playbook", "playbook"),
       ("tracker.html", "Tracker", "tracker"), ("chapters.html", "Chapters", "chapters")]


def nav(cur):
    return hqnav(cur)


HSUB = {'tracker': "Every US Ops task has an owner and a deadline, so we stay accountable. Success means finishing on time, or flagging early and working with the team to get it done. Silent failures, misses nobody knew about, come up in the weekly meeting so they don't happen again.", 'chapters': 'Who looks after each chapter'}


def shell(cur, title, h1, sub, css, body, data, js):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>{FONTS}<style>{CSS}{css}</style>{HQHEAD}</head>
<body><header class="top"><div><h1>{h1}</h1><div class="sub">{HSUB.get(cur, "")}</div></div>{nav(cur)}</header>
<main>{body}</main><div class="toast" role="status" aria-live="polite"></div>
<script id="d" type="application/json">{json.dumps(data)}</script>
<script>{COMMON_JS}{js}</script></body></html>"""


COMMON_JS = r"""
const D=JSON.parse(document.getElementById('d').textContent);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function load(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function toast(m){const t=document.querySelector('.toast');t.textContent=m;t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('on'),1600)}
"""

# ---------------- tracker ----------------
T_CSS = r"""
.row{grid-template-columns:26px minmax(0,1fr) 190px 126px 112px 44px!important}
.edt{border:0;background:none;color:var(--ink3);font:600 13px var(--fb);cursor:pointer;padding:6px 4px;border-radius:8px}
.edt:hover{color:var(--ink);background:#eef0f7}
#edlg{border:0;border-radius:20px;padding:0;width:min(520px,92vw);box-shadow:0 20px 60px rgba(9,31,119,.25)}
#edlg::backdrop{background:rgba(9,31,119,.35)}
#edlg input[type=text],#edlg input[type=date],#edlg select{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:14px;background:#fff;margin-top:4px}
.eown{border:0;padding:0;margin:0}.eown legend{font-weight:600;font-size:14px;margin-bottom:6px}
#eowners{display:flex;flex-wrap:wrap;gap:6px 16px}
.ck{display:inline-flex!important;align-items:center;gap:6px;font-weight:500!important;font-size:14px}
.erow{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.danger{color:var(--pink)!important}
@media (max-width:620px){.row{grid-template-columns:26px minmax(0,1fr)!important}.row>.ws,.row>.sts,.row>.due,.row>.edt{grid-column:2;justify-self:start}.erow{grid-template-columns:1fr}}

.ag-pre{background:#f5f5f9;border-radius:14px;padding:12px 14px;margin:4px 0 8px}
.ag-pre-h{font:700 13px/1.2 var(--fb);color:var(--ink3);margin-bottom:6px}
.ag-pre-r{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:14px;font-size:13.5px;padding:3px 0;color:var(--ink2)}
.ag-pre-r b{color:var(--ink);font-weight:700}
.ag-pre-r .od{color:var(--pink);font-weight:700}

.ag-step.blk .ag-n{background:#eef0f7!important;color:var(--ink)!important}
.ag-step{border-top:0!important;padding:10px 0!important}
.ci-top{margin-bottom:12px}
.ci-top .ci-btn{margin-top:0}

.row{grid-template-columns:26px minmax(0,1fr) 190px 126px 112px!important}
.due{position:relative;display:inline-flex;align-items:center;font:600 13px/1.2 var(--fb);color:var(--ink2);white-space:nowrap;cursor:pointer}
.due span{border-bottom:1px dashed #c3c8df;padding-bottom:1px}
.due:hover span{color:var(--ink);border-bottom-color:var(--ink)}
.due input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%}
.due.late{color:var(--pink)}.due.late span{border-bottom-color:var(--pink)}
.due.rec{cursor:default;color:var(--ink3)}
.add{margin:0 0 16px!important;background:#fff;border-radius:14px;padding:10px;box-shadow:0 1px 2px rgba(9,31,119,.05),0 8px 22px rgba(9,31,119,.06);align-items:center}
.add input,.add select{border-color:transparent!important;background:#f5f5f9!important}
.adue{display:inline-flex;align-items:center;gap:6px;font:600 13.5px var(--fb);color:var(--ink2)}
.mom{margin-top:16px;padding:18px 18px 14px}
.mom h2{font:800 20px/1.2 var(--fd);margin:0}
.mom ul{list-style:none;margin:12px 0 0;padding:0;display:grid;gap:0}
.agenda{max-height:calc(100vh - 100px);overflow-y:auto;scrollbar-width:thin}
@media (max-width:1000px){.agenda{max-height:none;overflow:visible}}
.mom li{display:grid;grid-template-columns:96px minmax(0,1fr) 20px;gap:10px;align-items:baseline;padding:8px 0;border-top:1px solid #ececf3;font-size:14px}
.mom li b{font:700 13.5px var(--fb);color:var(--ink);white-space:nowrap}
.mom li.past{opacity:.45}
.mom .x{border:0;background:none;color:var(--ink3);cursor:pointer;font-size:16px;line-height:1;padding:0;opacity:0}
.mom li:hover .x{opacity:1}
.addm{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
.addm input{border:0;background:#f5f5f9;border-radius:10px;padding:8px 10px;font-size:13.5px;min-width:0}
.addm input[type=text]{flex:1;min-width:120px}
@media (max-width:620px){.row{grid-template-columns:26px minmax(0,1fr)!important}.row>.due{grid-column:2}}

.lay{display:grid;grid-template-columns:minmax(0,1fr) 370px;gap:20px}
.fbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.fbar select{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;font-weight:600;font-size:14px;max-width:100%}
.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 12px;font-weight:600;font-size:13.5px;cursor:pointer;color:var(--ink)}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}.chip b{font-weight:700;margin-left:4px;opacity:.75}
.tidy{margin-left:auto}.tidy[disabled]{opacity:.45;cursor:default}
.grp{margin-bottom:16px}.grp-h{display:flex;align-items:baseline;gap:8px;margin:0 0 8px 4px}.grp-h h3{font-size:15px}.grp-h span{font-size:12.5px;color:var(--ink3)}
.list{background:#fff;border:1px solid var(--line);border-radius:14px}
.row{display:grid;grid-template-columns:26px minmax(0,1fr) 200px 112px;gap:12px;align-items:center;padding:10px 14px;border-top:1px solid var(--line2)}
.row:first-child{border-top:0}
.ws{display:flex;flex-wrap:wrap;gap:4px}
.cb{width:20px;height:20px;border-radius:6px;border:2px solid #b9bfd9;background:#fff;cursor:pointer;display:grid;place-items:center;padding:0}
.cb.on{background:var(--ink);border-color:var(--ink)}.cb.on::after{content:'';width:9px;height:5px;border:2px solid #fff;border-top:0;border-right:0;transform:rotate(-45deg) translate(1px,-1px)}
.row .tx{font-weight:600;font-size:14.5px}.row .tx small{display:block;font-weight:500;color:var(--ink3);font-size:12.5px;margin-top:2px}
.row.isdone .tx{color:var(--ink3);text-decoration:line-through;text-decoration-color:#b9bfd9}
.row.changed{background:#fafafe}.row.changed.isdone{opacity:.65}
.sts{appearance:none;-webkit-appearance:none;font:600 12px/1 var(--fb);padding:6px 24px 6px 10px;border-radius:999px;border:1px solid transparent;cursor:pointer;background-image:linear-gradient(45deg,transparent 50%,currentColor 50%),linear-gradient(135deg,currentColor 50%,transparent 50%);background-position:calc(100% - 13px) 50%,calc(100% - 9px) 50%;background-size:4px 4px;background-repeat:no-repeat;justify-self:start}
.sts.st-todo{background-color:#f0f0f5;color:var(--ink2)}.sts.st-doing{background-color:#fff;color:var(--ink);border-color:#b9bfd9}.sts.st-blocked{background-color:var(--pinkbg);color:#b01f52;border-color:#f3afc6}.sts.st-done{background-color:var(--ink);color:#fff}
.add{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}.add input,.add select{border:1px solid var(--line);border-radius:10px;padding:9px 11px;font-size:14px;background:#fff}.add input[type=text]{flex:1;min-width:180px}
.empty{padding:16px;color:var(--ink3);font-size:14px}
.agenda{position:sticky;top:86px;align-self:start}.agenda .card{padding:18px 18px 14px}
.ag-h{display:flex;align-items:center;gap:8px}.ag-h .btn{margin-left:auto;padding:7px 12px;font-size:13px}
.ag-step{display:grid;grid-template-columns:28px 1fr;gap:10px;padding:12px 0;border-top:1px solid var(--line2)}.ag-step:first-of-type{border-top:0}
.ag-n{width:26px;height:26px;border-radius:50%;background:#eef0f7;color:var(--ink);display:grid;place-items:center;font:700 13px/1 var(--fd)}
.ag-step.blk .ag-n{background:var(--pink);color:#fff}
.ag-t{font-weight:700;font-size:14.5px}.ag-t small{font-weight:500;color:var(--ink2);margin-left:6px;font-size:12.5px}
.ag-step ul{margin:6px 0 0;padding:0;list-style:none}.ag-step li{font-size:13.5px;padding:3px 0;display:flex;gap:7px;align-items:baseline}
.ag-step li .who{font-size:12.5px;color:var(--ink3);background:none;padding:0}.ag-empty{font-size:13px;color:var(--ink3);margin-top:4px}
.dot{width:7px;height:7px;border-radius:50%;background:var(--ink3);flex:none;transform:translateY(-1px)}.dot.p{background:var(--pink)}
.ci-btn{width:100%;margin-top:12px;background:var(--pink)}.posted{font-size:12.5px;color:var(--ink2);margin-top:6px;text-align:center}
dialog{border:0;border-radius:16px;padding:0;max-width:520px;width:calc(100% - 28px);color:var(--ink);box-shadow:0 20px 60px rgba(9,31,119,.25)}dialog::backdrop{background:rgba(9,31,119,.3)}
.dlg{padding:22px}.dlg label{display:block;font-weight:700;font-size:14px;margin:14px 0 6px}.dlg label small{font-weight:500;color:var(--ink2)}
.dlg textarea,.dlg select{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:14px;background:#fff}.dlg textarea{min-height:64px;resize:vertical}.dlg .rw{display:flex;gap:10px;justify-content:flex-end;margin-top:18px}
@media (max-width:1000px){.lay{grid-template-columns:1fr}.agenda{position:static}}
@media (max-width:620px){.row{grid-template-columns:26px minmax(0,1fr);row-gap:6px}.row>.ws,.row>.sts{grid-column:2}.tidy{margin-left:0}}
"""
T_BODY = r"""
<div class="lay">
<section aria-label="Tasks">
  <div class="fbar">
    <select id="me" aria-label="Whose tasks"></select>
    <select id="ph" aria-label="Phase"><option value="">All phases</option><option value="close">Fall close (by mid-Dec)</option><option value="plan">Spring plan + recruit (Dec-Jan)</option><option value="all">All year</option></select>
    <span id="chips"></span>
  </div>
  <form class="add" id="add"><input type="text" id="atx" placeholder="Add a task" aria-label="New task"><select id="awho" aria-label="Owner"></select><label class="adue">Due <input type="date" id="adue" aria-label="Deadline"></label><select id="aph" aria-label="Phase"><option value="close">Fall close</option><option value="plan" selected>Spring plan + recruit</option><option value="all">All year</option></select><button class="btn">Add task</button></form>
  <div id="groups"></div>
</section>
<aside class="agenda" aria-label="This week's meeting"><div class="ci-top"><button class="btn ci-btn" id="post">Post your weekly check-in</button><div class="posted" id="posted"></div></div><div class="card">
  <div class="ag-h"><h2>Weekly meeting</h2><button class="btn ghost" id="copy">Copy agenda</button></div>
  <div id="ag" style="margin-top:8px"></div>
</div>
<div class="card mom"><h2>Key moments</h2><div class="muted small" style="margin-top:3px">Season dates everyone works toward</div><ul id="moms"></ul>
<form id="addm" class="addm"><input type="date" id="mdt" aria-label="Date" required><input type="text" id="mtx" placeholder="Add a moment" aria-label="Moment" required><button class="btn">Add</button></form></div>
</aside>
</div>
<dialog id="edlg"><form class="dlg" method="dialog"><h2>Edit task</h2>
<label>Task<input type="text" id="etx" required></label>
<label>Note <small>optional</small><input type="text" id="enote"></label>
<fieldset class="eown"><legend>Owners</legend><div id="eowners"></div></fieldset>
<div class="erow"><label>Deadline<input type="date" id="edue"></label><label>Phase<select id="eph"><option value="close">Fall close</option><option value="plan">Spring plan + recruit</option><option value="all">All year</option></select></label></div>
<div class="rw"><button class="btn ghost danger" value="del" formnovalidate>Delete task</button><span style="flex:1"></span><button class="btn ghost" value="cancel" formnovalidate>Cancel</button><button class="btn" value="ok">Save</button></div></form></dialog>
<dialog id="dlg"><form class="dlg" method="dialog"><h2>Your weekly check-in</h2><p class="muted small" style="margin:4px 0 0">Three short answers before the meeting. Specific beats general.</p>
<label>Who are you?<select id="fwho"></select></label><label>What got done? <small>one per line</small><textarea id="fdone"></textarea></label>
<label>What are you working on now? <small>one per line</small><textarea id="fnow"></textarea></label><label>Anything blocked or at risk? <small>leave blank if not</small><textarea id="fblk"></textarea></label>
<div class="rw"><button class="btn ghost" value="cancel" formnovalidate>Cancel</button><button class="btn" value="ok">Post</button></div></form></dialog>
"""
T_JS = r"""
const P=Object.fromEntries(D.people.map(p=>[p.id,p]));
const ST={todo:'Not started',doing:'In progress',blocked:'Blocked',done:'Done'};const ORD=['todo','doing','blocked','done'];
const PH={close:'Fall close',plan:'Spring plan + recruit',all:'All year'};const PHD={close:'by mid-Dec',plan:'Dec-Jan',all:'ongoing'};
const nm=id=>P[id]?P[id].name:id;const ws=t=>`<span class="ws">${t.owners.map(o=>`<span class="who">${esc(nm(o))}</span>`).join('')}</span>`;
const KEY='usops-tracker-v3';let S=load(KEY)||{st:{},extra:[],ci:{},ch:{}};S.ci=S.ci||{};S.ch=S.ch||{};S.due=S.due||{};S.mom=S.mom||[];S.momx=S.momx||[];let F='',me='',ph='';
const DUE0={g14:'2026-12-15',g15:'2026-12-15',g16:'2026-12-15',g49:'2026-12-15',g51:'2026-12-15',g80:'2026-12-15',g81:'2026-12-15',g83:'2026-12-15',g78:'2026-12-15',g97:'2026-12-15',g1:'2026-11-22',g2:'2026-12-01',g3:'2026-12-01',g4:'2026-12-15',g5:'2026-12-01',g6:'2026-12-01',g17:'2027-01-01',g21:'2026-12-15',g23:'2026-12-15',g88:'2026-12-19',g32:'2026-12-15',g25:'2027-01-15',g58:'2027-01-01',g59:'2026-12-15',g20:'2026-12-01',g22:'2026-12-01',g56:'2026-12-15'};
const REC={g11:'Weekly',g54:'Each season'};
const MOM0=[['2026-12-15','Chapters confirmed'],['2027-01-01','Outreach starts'],['2027-01-04','Chapter kickoff call (first week of Jan)'],['2027-01-10','Locations and session dates set (Jan 17 fallback)'],['2027-02-01','Parent kickoff (early Feb)'],['2027-02-21','Earliest season start']];
const TODAY=new Date().toISOString().slice(0,10);const dueOf=t=>S.due[t.id]??t.due0??DUE0[t.id]??'';
const MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];const fmt=d=>{if(!d)return'';const [y,m,dd]=d.split('-');return MON[+m-1]+' '+(+dd)+(y!==TODAY.slice(0,4)?', '+y:'')};
const late=t=>{const d=dueOf(t);return d&&d<TODAY&&st(t)!=='done'};
S.ed=S.ed||{};S.del=S.del||[];
const all=()=>D.tasks.concat(S.extra).filter(t=>!S.del.includes(t.id)).map(t=>S.ed[t.id]?{...t,...S.ed[t.id]}:t);const st=t=>S.st[t.id]||t.status;
let G={};const snap=()=>{G={};all().forEach(t=>G[t.id]=st(t))};snap();const gs=t=>G[t.id]||st(t);
const team=id=>[id,...D.people.filter(p=>p.reports===id).flatMap(p=>team(p.id))];
function scopeO(owners){if(!me)return true;const [k,id]=me.split(':');const set=k==='p'?[id]:team(id);return owners.some(o=>set.includes(o))}
const scope=t=>(!ph||t.phase===ph)&&scopeO(t.owners);
const FL={doing:['In progress',t=>gs(t)==='doing'],todo:['Not started',t=>gs(t)==='todo'],blocked:['Blocked',t=>gs(t)==='blocked'],done:['Done',t=>gs(t)==='done']};
function draw(){
 const base=all().filter(scope);
 document.getElementById('chips').innerHTML=Object.entries(FL).map(([k,[l,f]])=>`<button class="chip${F===k?' on':''}" data-f="${k}" aria-pressed="${F===k}">${l}<b>${base.filter(f).length}</b></button>`).join(' ');
 const ts=F?base.filter(FL[F][1]):base;
 const out=['close','plan','all'].map(p=>{const r=ts.filter(t=>t.phase===p).sort((a,b)=>(gs(a)==='done')-(gs(b)==='done')||(dueOf(a)||'9').localeCompare(dueOf(b)||'9'));if(!r.length)return'';
  return `<div class="grp"><div class="grp-h"><h3>${PH[p]}</h3><span>${PHD[p]}, ${r.length} task${r.length===1?'':'s'}</span></div><div class="list">${r.map(t=>{const s=st(t);
   return `<div class="row${s==='done'?' isdone':''}${s!==gs(t)?' changed':''}"><button class="cb${s==='done'?' on':''}" data-cb="${t.id}" aria-label="Mark done: ${esc(t.text)}"></button>
   <div class="tx">${esc(t.text)}${t.note?`<small>${esc(t.note)}</small>`:''}</div>${ws(t)}${t.phase==='all'&&!dueOf(t)?`<span class="due rec">${esc(REC[t.id]||'Ongoing')}</span>`:`<label class="due${late(t)?' late':''}"><span>${late(t)?'Overdue ':'Due '}${esc(fmt(dueOf(t))||'not set')}</span><input type="date" data-due="${t.id}" value="${esc(dueOf(t))}" aria-label="Deadline for ${esc(t.text)}"></label>`}
   <select class="sts st-${s}" data-t="${t.id}" aria-label="Status of ${esc(t.text)}">${ORD.map(o=>`<option value="${o}"${o===s?' selected':''}>${ST[o]}</option>`).join('')}</select><button class="edt" data-ed="${t.id}" aria-label="Edit ${esc(t.text)}">Edit</button></div>`}).join('')}</div></div>`}).join('');
 document.getElementById('groups').innerHTML=out||'<div class="list empty">Nothing here.</div>';
 const A=all().filter(scope),done=A.filter(t=>S.ch[t.id]&&st(t)==='done'),open=A.filter(t=>st(t)==='doing'),blk=A.filter(t=>st(t)==='blocked'),miss=A.filter(t=>late(t)&&st(t)!=='blocked');
 const CI=Object.entries(S.ci).filter(([pid])=>scopeO([pid]));
 const ciL=(k,p)=>CI.flatMap(([pid,c])=>c[k].map(x=>`<li><span class="dot${p?' p':''}"></span><span style="flex:1">${esc(x)}</span><span class="who">${esc(nm(pid))}</span></li>`)).join('');
 const L=(a,n,p)=>a.slice(0,n).map(t=>`<li><span class="dot${p?' p':''}"></span><span style="flex:1">${esc(t.text)}</span><span class="who">${esc(t.owners.map(nm).join(', '))}</span></li>`).join('')+(a.length>n?`<li class="muted">+ ${a.length-n} more</li>`:'');
 const groups=[['catherine','Catherine'],['whitney',"Whitney's team"],['sierra',"Sierra's team"]].map(([id,l])=>{const set=id==='catherine'?['catherine']:team(id);const my=A.filter(t=>t.owners.some(o=>set.includes(o)));return {l,id,d:my.filter(t=>st(t)==='done').length,o:my.filter(t=>st(t)==='doing').length,od:my.filter(late).length}});
 const nci=Object.keys(S.ci).length;document.getElementById('posted').textContent=nci?`${nci} of ${D.people.filter(p=>p.tracker!==false).length} check-ins posted this week`:'No check-ins posted yet this week';
 document.getElementById('ag').innerHTML=`
 <div class="ag-pre"><div class="ag-pre-h">Read before the call</div>${groups.map(g=>`<div class="ag-pre-r"><b>${esc(g.l)}</b><span>${g.d} done</span><span class="${g.od?'od':''}">${g.od} overdue</span></div>`).join('')}</div>
 <div class="ag-step"><span class="ag-n">1</span><div><div class="ag-t">One win <small>0-3 min</small></div><div class="ag-empty">A chapter or teammate shout-out, led by a different person each week</div></div></div>
 <div class="ag-step"><span class="ag-n">2</span><div><div class="ag-t">Overdue and blocked <small>3-15 min</small></div>${blk.length||miss.length||CI.some(([,c])=>c.blk.length)?`<ul>${L(miss.map(t=>({...t,text:t.text+' (due '+fmt(dueOf(t))+')'})),8,1)}${L(blk,8,1)}${ciL('blk',1)}</ul><div class="ag-empty">Owner gives a new date or names what they need</div>`:'<div class="ag-empty">Nothing overdue or blocked</div>'}</div></div>
 <div class="ag-step"><span class="ag-n">3</span><div><div class="ag-t">One decision <small>15-25 min</small></div><div class="ag-empty">One topic picked in advance, framed as a question, led by whoever raised it</div></div></div>
 <div class="ag-step"><span class="ag-n">4</span><div><div class="ag-t">Commitments <small>25-30 min</small></div><div class="ag-empty">Each person says what they own next week. Update the Tracker live</div></div></div>`;
 window._ag=['US Ops weekly meeting (30 min)','Read before the call:',...groups.map(g=>'   - '+g.l+': '+g.d+' done, '+g.od+' overdue'),'1. One win (0-3 min)','2. Overdue and blocked (3-15 min)',...miss.map(t=>'   - '+t.text+', due '+fmt(dueOf(t))+' ('+t.owners.map(nm).join(', ')+')'),...blk.map(t=>'   - Blocked: '+t.text+' ('+t.owners.map(nm).join(', ')+')'),...CI.flatMap(([pid,c])=>c.blk.map(x=>'   - '+x+' ('+nm(pid)+')')),'3. One decision (15-25 min)','4. Commitments: what each person owns next week (25-30 min)'].join('\n');
 const M=MOM0.filter(m=>!S.momx.includes(m[0]+m[1])).map(m=>({d:m[0],t:m[1],k:m[0]+m[1]})).concat(S.mom.map(m=>({d:m.d,t:m.t,k:m.k,own:1}))).sort((a,b)=>a.d.localeCompare(b.d));
 document.getElementById('moms').innerHTML=M.map(m=>`<li class="${m.d<TODAY?'past':''}"><b>${esc(fmt(m.d))}</b><span>${esc(m.t)}</span><button class="x" data-mx="${esc(m.k)}" aria-label="Remove ${esc(m.t)}">&times;</button></li>`).join('')||'<li class="muted">No moments yet</li>';
}
function setSt(id,v){S.st[id]=v;S.ch[id]=true;save(KEY,S);snap();draw()}
document.addEventListener('click',e=>{const c=e.target.closest('.chip');if(c){F=F===c.dataset.f?'':c.dataset.f;draw();return}
 const b=e.target.closest('.cb');if(b){const t=all().find(x=>x.id===b.dataset.cb);setSt(t.id,st(t)==='done'?'doing':'done');toast(st(t)==='done'?'Done':'Reopened')}});
document.addEventListener('change',e=>{const di=e.target.closest('input[data-due]');if(di){S.due[di.dataset.due]=di.value;save(KEY,S);draw();toast(di.value?'Deadline set to '+fmt(di.value):'Deadline cleared');return}});
document.addEventListener('click',e=>{const x=e.target.closest('[data-mx]');if(!x)return;const k=x.dataset.mx;const i=S.mom.findIndex(m=>m.k===k);if(i>-1)S.mom.splice(i,1);else S.momx.push(k);save(KEY,S);draw();toast('Moment removed')});
const edlg=document.getElementById('edlg');let EID=null;
document.addEventListener('click',e=>{const b=e.target.closest('[data-ed]');if(!b)return;EID=b.dataset.ed;const t=all().find(x=>x.id===EID);
 document.getElementById('etx').value=t.text;document.getElementById('enote').value=t.note||'';document.getElementById('edue').value=dueOf(t);document.getElementById('eph').value=t.phase;
 document.getElementById('eowners').innerHTML=tracked.map(p=>`<label class="ck"><input type="checkbox" value="${p.id}"${t.owners.includes(p.id)?' checked':''}> ${esc(p.name)}</label>`).join('');edlg.showModal()});
edlg.addEventListener('close',()=>{const v=edlg.returnValue;if(!EID)return;
 if(v==='del'){if(!S.del.includes(EID))S.del.push(EID);save(KEY,S);draw();toast('Task deleted')}
 else if(v==='ok'){const tx=document.getElementById('etx').value.trim();const ow=[...document.querySelectorAll('#eowners input:checked')].map(i=>i.value);
  if(tx){S.ed[EID]={text:tx,note:document.getElementById('enote').value.trim(),owners:ow.length?ow:all().find(x=>x.id===EID).owners,phase:document.getElementById('eph').value};S.due[EID]=document.getElementById('edue').value;save(KEY,S);snap();draw();toast('Task updated')}}
 EID=null});
document.getElementById('addm').onsubmit=e=>{e.preventDefault();const d=document.getElementById('mdt').value,t=document.getElementById('mtx').value.trim();if(!d||!t)return;S.mom.push({d,t,k:'m'+Date.now()});save(KEY,S);document.getElementById('mtx').value='';document.getElementById('mdt').value='';draw();toast('Moment added')};
document.addEventListener('change',e=>{const s=e.target.closest('select.sts');if(s){setSt(s.dataset.t,s.value);toast('Status: '+ST[s.value])}});
const tracked=D.people.filter(p=>p.tracker!==false);
const lab=p=>`${p.name} (${p.role}${p.reports&&P[p.reports]?', reports to '+P[p.reports].name:''})`;
document.getElementById('me').innerHTML='<option value="">Everyone</option><optgroup label="Teams"><option value="t:catherine">Catherine\'s team (all of US Ops)</option><option value="t:whitney">Whitney\'s team: Whitney, Alaysia, Lily</option><option value="t:sierra">Sierra\'s team: Sierra, Nicole, Aisling</option></optgroup><optgroup label="People">'+tracked.map(p=>`<option value="p:${p.id}">${esc(lab(p))}</option>`).join('')+'</optgroup>';
const opts=tracked.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('');document.getElementById('awho').innerHTML=opts;document.getElementById('fwho').innerHTML=opts;
document.getElementById('me').onchange=e=>{me=e.target.value;draw()};document.getElementById('ph').onchange=e=>{ph=e.target.value;draw()};
document.getElementById('add').onsubmit=e=>{e.preventDefault();const v=document.getElementById('atx').value.trim();if(!v)return;const p=document.getElementById('aph').value;const t={id:'x'+Date.now(),text:v,owners:[document.getElementById('awho').value],phase:p,due:'',due0:document.getElementById('adue').value,status:'todo',note:''};document.getElementById('adue').value='';S.extra.push(t);G[t.id]='todo';save(KEY,S);document.getElementById('atx').value='';draw();toast('Task added')};
document.getElementById('copy').onclick=async()=>{try{await navigator.clipboard.writeText(window._ag);toast('Agenda copied')}catch(e){toast('Copy not allowed here')}};
const dlg=document.getElementById('dlg');const sp=id=>document.getElementById(id).value.split('\n').map(x=>x.trim()).filter(Boolean);
function fillCI(pid){const c=S.ci[pid]||{done:[],now:[],blk:[]};document.getElementById('fdone').value=c.done.join('\n');document.getElementById('fnow').value=c.now.join('\n');document.getElementById('fblk').value=c.blk.join('\n')}
document.getElementById('post').onclick=()=>{fillCI(document.getElementById('fwho').value);dlg.showModal()};document.getElementById('fwho').onchange=e=>fillCI(e.target.value);
dlg.addEventListener('close',()=>{if(dlg.returnValue!=='ok')return;S.ci[document.getElementById('fwho').value]={done:sp('fdone'),now:sp('fnow'),blk:sp('fblk')};save(KEY,S);draw();toast('Check-in posted. It is on the agenda')});
document.addEventListener('input',e=>{const n=e.target.closest('input.nt');if(!n)return;const v=n.value.trim();if(v)S.notes[n.dataset.n]=v;else delete S.notes[n.dataset.n];save(KEY,S)});
draw();
"""

# ---------------- chapters table ----------------
C_CSS = r""".nt{width:100%;min-width:180px;border:1px solid transparent;border-radius:8px;padding:5px 8px;background:transparent;font-size:13.5px;color:var(--ink)}.nt:hover{border-color:var(--line)}.nt:focus{border-color:var(--ink);background:#fff;outline:none}.nt::placeholder{color:#b3b8d4}

.tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.tools input[type=search]{border:1px solid var(--line);border-radius:999px;padding:8px 14px;font-size:14px;min-width:220px;background:#fff}
.tools select{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;font-weight:600;font-size:14px}
.tools .sp1{margin-left:auto}
.sum{font-size:13px;color:var(--ink2);margin:0 0 10px 2px}.sum b{color:var(--ink)}
.tw{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:auto}
table{width:100%;border-collapse:collapse;font-size:14px}
th{position:sticky;top:0;background:#fafafc;z-index:1;font:700 11.5px/1 var(--fb);letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);text-align:left;padding:0;border-bottom:1px solid var(--line);white-space:nowrap}
th button{all:unset;cursor:pointer;display:block;padding:11px 12px}th button:hover{color:var(--ink)}th button:focus-visible{outline:2px solid var(--pink)}
th .ar{margin-left:4px;opacity:.8}
td{padding:7px 12px;border-bottom:1px solid var(--line2);vertical-align:middle}
tr:last-child td{border-bottom:0}tr:hover td{background:#fafafe}
td.nm{font-weight:600}td.nm small{font-weight:500;color:var(--ink3);margin-left:6px}
td select{border:1px solid var(--line);border-radius:8px;padding:4px 6px;background:#fff;font-size:13.5px;font-weight:600;color:var(--ink)}
tr.moved td select{border-color:var(--pink);background:var(--pinkbg)}
.stt{font:600 12px/1 var(--fb);padding:4px 8px;border-radius:999px;white-space:nowrap}
.s-running{background:#eef0f7;color:var(--ink)}.s-hold{background:var(--pinkbg);color:#b01f52}.s-not{background:#f0f0f5;color:var(--ink3)}.s-new{background:var(--ink);color:#fff}
.pg{display:flex;align-items:center;gap:3px}.pg button{width:14px;height:14px;border-radius:4px;border:1.5px solid #b9bfd9;background:#fff;padding:0;cursor:pointer}
.pg button.on{background:var(--ink);border-color:var(--ink)}.pg span{font-size:12px;color:var(--ink2);margin-left:6px;min-width:26px}
.legend{font-size:12px;color:var(--ink3);margin:10px 2px 0}
.addc{display:flex;gap:6px}.addc input{border:1px solid var(--line);border-radius:999px;padding:8px 12px;font-size:14px;min-width:170px}
@media (max-width:760px){.tools input[type=search]{min-width:0;flex:1}.tools .sp1{margin-left:0}
 table,tbody,tr,td{display:block}thead{display:none}tr{padding:8px 4px;border-bottom:1px solid var(--line2)}td{border:0;padding:3px 10px}
 td[data-l]::before{content:attr(data-l);display:inline-block;width:92px;font-size:11.5px;color:var(--ink3);text-transform:uppercase;letter-spacing:.05em}}
"""
C_BODY = r"""
<div class="tools">
  <input type="search" id="q" placeholder="Search chapters or states" aria-label="Search">
  <select id="fo" aria-label="Owner"><option value="">All owners</option></select>
  <select id="fc" aria-label="Coordinator"><option value="">All coordinators</option></select>
  <select id="fs" aria-label="Status"><option value="">All statuses</option><option value="running">Running</option><option value="hold">On hold</option><option value="not">Not running</option><option value="new">New (Spring 2027)</option></select>
  <span class="sp1"></span>
  <form class="addc" id="addc"><input id="addn" placeholder="Add a new chapter" aria-label="New chapter name"><button class="btn">Add</button></form>
  <button class="btn ghost" id="reset">Reset owners</button><button class="btn" id="copy">Copy as list</button>
</div>
<p class="sum" id="sum"></p>
<div class="tw"><table><thead><tr id="hd"></tr></thead><tbody id="tb"></tbody></table></div>
<p class="legend" id="legend"></p>
"""
C_JS = r"""
const KEY='usops-chapters-v2';let S=load(KEY)||{own:{},steps:{},added:[]};S.notes=S.notes||{};
const INT={alaysia:'Alaysia',lily:'Lily',nicole:'Nicole',aisling:'Aisling'};const INT_CO={alaysia:'Whitney',lily:'Whitney',nicole:'Sierra',aisling:'Sierra'};
const SL={running:'Running',hold:'On hold',not:'Not running',new:'New (Spring 2027)'};
const PLAN=D.plan||{};const base=D.chapters.map(c=>{const l1=c.l1.toLowerCase().trim();const p=INT[l1]?'':(PLAN[c.name]||'');const intern=INT[l1]?l1:p;
 return {...c,short:c.name.replace(/^Run /,''),owner0:intern,co0:INT[l1]?(c.l2||INT_CO[l1]):p?INT_CO[p]:(['Catherine','Sierra','Whitney'].includes(c.l1)?c.l1:''),
  status:c.f26==='Yes'?'running':c.f26==='TBD'?'hold':'not'}});
const rows=()=>base.concat(S.added.map(a=>({...a,short:a.name.replace(/^Run /,''),owner0:'',co0:'',status:'new',state:'',cohort:'Spring 2027'})));
const own=c=>c.name in S.own?S.own[c.name]:c.owner0;const co=c=>c.name in S.own?(S.own[c.name]?INT_CO[S.own[c.name]]:c.co0):c.co0;
const prog=c=>(S.steps[c.name]||[]).length;
let sortK='short',dir=1;
const COLS=[['short','Chapter'],['state','State'],['owner','Owner (intern)'],['co','Coordinator'],['status','Status'],['notes','Notes']];
const key=(c,k)=>k==='owner'?(own(c)?INT[own(c)]:'~'):k==='co'?(co(c)||'~'):k==='notes'?((S.notes[c.name]||'').toLowerCase()||'~'):k==='status'?['running','hold','new','not'].indexOf(c.status):(c[k]||'~');
function draw(){
 const q=document.getElementById('q').value.trim().toLowerCase(),fo=document.getElementById('fo').value,fc=document.getElementById('fc').value,fs=document.getElementById('fs').value;
 let r=rows().filter(c=>(!q||(c.short+' '+c.state).toLowerCase().includes(q))&&(!fo||(fo==='none'?!own(c):own(c)===fo))&&(!fc||(fc==='none'?!co(c):co(c)===fc))&&(!fs||c.status===fs));
 r.sort((a,b)=>{const x=key(a,sortK),y=key(b,sortK);return (x<y?-1:x>y?1:0)*dir||a.short.localeCompare(b.short)});
 document.getElementById('hd').innerHTML=COLS.map(([k,l])=>`<th scope="col" aria-sort="${sortK===k?(dir>0?'ascending':'descending'):'none'}"><button data-k="${k}">${l}<span class="ar">${sortK===k?(dir>0?'↑':'↓'):''}</span></button></th>`).join('');
 document.getElementById('tb').innerHTML=r.map(c=>{const o=own(c),st=S.steps[c.name]||[];const moved=c.name in S.own&&S.own[c.name]!==c.owner0;
  return `<tr class="${moved?'moved':''}"><td class="nm" data-l="Chapter">${esc(c.short)}<small>${c.cohort?'('+esc(c.cohort==='Never'?'never launched':c.cohort)+')':''}</small></td><td data-l="State">${esc(c.state||'')}</td>
  <td data-l="Owner"><select data-o="${esc(c.name)}" aria-label="Owner of ${esc(c.name)}"><option value="">Unassigned</option>${Object.entries(INT).map(([k,v])=>`<option value="${k}"${o===k?' selected':''}>${v}</option>`).join('')}</select></td>
  <td data-l="Coordinator">${esc(co(c)||'')}</td><td data-l="Status"><span class="stt s-${c.status}">${SL[c.status]}</span></td>
  <td data-l="Notes" class="ntd"><input class="nt" data-n="${esc(c.name)}" value="${esc(S.notes[c.name]||'')}" placeholder="Add a note" aria-label="Notes for ${esc(c.name)}"></td></tr>`}).join('');
 const R=rows(),cnt=k=>R.filter(c=>own(c)===k).length;
 document.getElementById('sum').innerHTML=`<b>${r.length}</b> of ${R.length} chapters shown. Owners: `+Object.entries(INT).map(([k,v])=>`${v} <b>${cnt(k)}</b>`).join(', ')+`, unassigned <b>${R.filter(c=>!own(c)&&c.status!=='not').length}</b> (plus ${R.filter(c=>c.status==='not').length} not running)`;
}
document.getElementById('legend').textContent='Dates in brackets are the season each chapter started. Notes save in this browser only. Each intern holds 25 returning chapters; Alaysia and Aisling also hold the 7 on-hold chapters. New chapters go to the intern with the fewest new ones, aiming for 5 each. Owner changes save in this browser only. Coordinator follows the intern.';
document.getElementById('fo').innerHTML+=Object.entries(INT).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')+'<option value="none">Unassigned</option>';
document.getElementById('fc').innerHTML+=['Whitney','Sierra','Catherine'].map(v=>`<option>${v}</option>`).join('')+'<option value="none">None</option>';
['q','fo','fc','fs'].forEach(id=>document.getElementById(id).addEventListener('input',draw));
document.addEventListener('click',e=>{const h=e.target.closest('th button');if(h){const k=h.dataset.k;if(sortK===k)dir=-dir;else{sortK=k;dir=1}draw();return}
 const b=e.target.closest('.pg button');if(b){const n=b.dataset.p,i=+b.dataset.i,a=S.steps[n]||[];S.steps[n]=a.includes(i)?a.filter(x=>x!==i):a.concat(i);save(KEY,S);draw()}});
document.addEventListener('change',e=>{const s=e.target.closest('select[data-o]');if(!s)return;S.own[s.dataset.o]=s.value;save(KEY,S);draw();toast(s.dataset.o.replace(/^Run /,'')+': '+(s.value?INT[s.value]:'Unassigned'))});
document.getElementById('addc').onsubmit=e=>{e.preventDefault();let v=document.getElementById('addn').value.trim();if(!v)return;if(!/^Run /.test(v))v='Run '+v;S.added.push({name:v});const nc={};Object.keys(INT).forEach(k=>nc[k]=0);S.added.forEach(a=>{const o=S.own[a.name];if(o in nc)nc[o]++});const pick=Object.keys(INT).sort((a,b)=>nc[a]-nc[b])[0];S.own[v]=pick;save(KEY,S);document.getElementById('addn').value='';document.getElementById('fs').value='new';draw();toast('Added and assigned to '+INT[pick])};
document.getElementById('reset').onclick=()=>{S.own={};save(KEY,S);draw();toast('Owners back to the sheet')};
document.getElementById('copy').onclick=async()=>{const R=rows();const g=k=>R.filter(c=>own(c)===k).map(c=>'   - '+c.name).join('\n');
 const txt=['Chapter owners (proposed)',...Object.entries(INT).map(([k,v])=>`${v} (with ${INT_CO[k]}): ${R.filter(c=>own(c)===k).length}\n`+g(k)),'Unassigned: '+R.filter(c=>!own(c)&&c.status!=='not').length+'\n'+R.filter(c=>!own(c)&&c.status!=='not').map(c=>'   - '+c.name+(c.co0?' (held by '+c.co0+')':'')).join('\n')].join('\n\n');
 try{await navigator.clipboard.writeText(txt);toast('Copied')}catch(x){toast('Copy not allowed here')}};
draw();
"""

REDIRECT = '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=tracker.html"><title>Moved</title><a href="tracker.html">The tracker moved here</a>'

if __name__ == "__main__":
    tasks = real_tasks()
    (HERE / "tracker.html").write_text(shell(
        "tracker", "Tracker", 'Tracker',
        "Every US Ops task has an owner and a deadline, so we stay accountable. Success means finishing on time, or flagging early "
        "and working with the team to get it done. Silent failures, misses nobody knew about, come up in the weekly meeting so they don't happen again.",
        T_CSS, T_BODY, {"people": PEOPLE, "tasks": tasks}, T_JS))
    chapters = load_chapters()
    PLAN = {n: o.lower() for n, o in (l.split("\t") for l in (HERE / "chapters-src" / "remap-2026-11-23.tsv").read_text().splitlines() if l.strip())}
    (HERE / "chapters.html").write_text(shell(
        "chapters", "Chapters", 'Chapters', "",
        C_CSS, C_BODY, {"chapters": chapters, "plan": PLAN, "steps": STEPS}, C_JS))
    for k in "abc":  # old option links land on the one tracker; originals are in history/tracker-v1/
        (HERE / f"tracker-{k}.html").write_text(REDIRECT)
    from collections import Counter
    print("tasks", len(tasks), Counter(t["status"] for t in tasks), "| chapters", len(chapters))
