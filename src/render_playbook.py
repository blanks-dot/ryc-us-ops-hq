#!/usr/bin/env python3
"""Playbook tab v2: playbook.json + data.json -> playbook-a.html (guided tour),
playbook-b.html (by role), playbook-c.html (field guide). v1 backed up in history/playbook-v1/.
Design principles: playbook-research.md."""
import json, os, html
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from hqnav import hqnav, HEAD as HQHEAD
D = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(D, "playbook.json")))
G = json.load(open(os.path.join(D, "data.json")))
TIERS = {t["key"]: t for t in G["tiers"]}
ORDER = ["L", "C", "I", "A"]
PH = [p for p in G["phases"]]
TAGS = P["tags"]
e = lambda s: html.escape(str(s or ""))
CH = {c["k"]: c for c in P["story"]["chapters"]}
ROLE = {r["key"]: r for r in P["team"]["roles"]}
VIEWS = [("a", "Guided tour"), ("b", "By role"), ("c", "Field guide")]


def tag(s):
    return f'<span class="tag tag-{s}">{e(TAGS.get(s, s))}</span>' if s else ""


def items(lst, cls="list"):
    out = []
    for it in lst:
        src = f'<span class="src">{e(it["src"])}</span>' if it.get("src") else ""
        out.append(f'<li class="{"open" if it.get("s") else ""}"><span>{e(it["t"])}</span>{tag(it.get("s"))}{src}</li>')
    return f'<ul class="{cls}">' + "".join(out) + "</ul>"


def stats(big=False):
    c = CH["today"]
    return '<div class="stats' + (' big' if big else '') + '">' + "".join(
        f'<div class="stat"><b>{e(s["n"])}</b><span>{e(s["l"])}</span><small>{e(s["src"])}</small></div>'
        for s in c["stats"]) + "</div>"


def outcomes():
    c = CH["today"]
    rows = []
    for it in c["items"]:
        pct, rest = it["t"].split(" ", 1)
        rows.append(f'<div class="out"><b>{e(pct)}</b><span>{e(rest)}</span></div>')
    return '<div class="outs">' + "".join(rows) + f'</div><p class="cap">{e(c["items_src"])}</p>'


def values():
    return '<div class="values">' + "".join(
        f'<div class="val"><b>{e(v["k"])}</b><span>{e(v["t"])}</span></div>' for v in P["story"]["values"]) + "</div>"


def stories():
    s = P["story"]["stories"]
    return f'<div class="placeholder"><div><b>{e(s["title"])}</b> {tag(s["s"])}</div><span>{e(s["t"])}</span></div>'


def journey():
    st, nx, dr = CH["started"], CH["next"], CH["dream"]
    pts = [
        ("2018", "Founded", "Charlottesville, Virginia, by UVA student-athletes"),
        ("2024", "First big goal", "10,000 kids by 2035"),
        ("Fall 2026", "Today", f'{CH["today"]["stats"][0]["n"]} kids, 102 chapters running'),
        ("2027", "Next", "Grow sustainably, not by force"),
        ("2040", "The dream", "1 million kids"),
    ]
    return '<ol class="journey">' + "".join(
        f'<li class="{"now" if w == "Fall 2026" else ""}{" goal" if w == "2040" else ""}"><span class="yr">{e(w)}</span><b>{e(h)}</b><span class="d">{e(t)}</span></li>'
        for w, h, t in pts) + "</ol>"


def role_tile(k, n_owns=3, link=None):
    t, r = TIERS[k], ROLE[k]
    owns = "".join(f"<li>{e(x)}</li>" for x in r["owns"][:n_owns])
    href = f' href="{link}#{k.lower()}"' if link else ""
    tagn = "a" if link else "div"
    return (f'<{tagn} class="role role-{k}"{href}><div class="rh"><b>{e(t["label"])}</b></div>'
            f'<p>{e(t["role"])}</p><ul>{owns}</ul><span class="esc">{e(r["escalates"])}</span></{tagn}>')


def ladder():
    return ('<div class="ladder">'
            '<div class="rung"><b>Intern</b><span>owns their chapters, start to finish</span></div><i aria-hidden="true">&rarr;</i>'
            '<div class="rung"><b>Coordinator</b><span>runs the systems, unblocks interns</span></div><i aria-hidden="true">&rarr;</i>'
            '<div class="rung top"><b>Lead</b><span>final call on US Ops decisions</span></div></div>'
            '<p class="cap">Escalate one step up. Safety incidents go straight to the lead.</p>')


def meetings():
    return '<ul class="rhythm">' + "".join(
        f'<li><span class="when">{e(m["when"])}</span><span class="what">{e(m["t"])}{tag(m.get("s"))}</span><span class="who">{e(TIERS[m["who"]]["label"])}</span></li>'
        for m in P["tracking"]["meetings"]) + "</ul>"


def agenda():
    t = P["tracking"]
    return f'<div class="agenda"><h3 class="h3">{e(t["agenda_title"])} {tag(t.get("agenda_s"))}</h3>' + items(t["agenda"]) + '</div>'


def proposal():
    t = P["tracking"]
    return f'<h3 class="h3">{e(t["proposal_title"])} {tag(t.get("proposal_s"))}</h3>' + items(t["proposal"])


def gate():
    first = P["triggers"]["items"][0]["t"]
    checks = ["Safety basics in place", "Leadership trained", "Handoff done"]
    return ('<div class="gate"><div class="gh">Before session one: the gate</div>'
            + "".join(f'<div class="chk"><i aria-hidden="true"></i>{c}</div>' for c in checks)
            + '<div class="gr"><span class="go">Go live</span><span>or</span><span class="push">Push the start</span></div></div>')


def pause_rule():
    rows = []
    for x in P["triggers"]["items"]:
        if x.get("s") != "stake":
            continue
        head, _, body = x["t"].partition(": ")
        rows.append(f'<div class="sr"><b>{e(head)}</b><span>{e(body[0].upper() + body[1:])}</span></div>')
    return (f'<div class="stake"><div class="sk"><span>Triage and pause rules</span>{tag("stake")}</div>'
            + "".join(rows) + '<small>Draft. The US Ops team will adjust these and decide together.</small></div>')


def trig_rest(skip_flag=False):
    return [t for t in P["triggers"]["items"][1:] if t.get("s") != "stake" and not (skip_flag and "Flag struggling" in t["t"])]


# ---------------------------------------------------------------- shared shell
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">'

BASE = r"""
/* Layout: white sticky header + calm paper surfaces; navy carries structure, pink is the one accent, blue supports */
:root{
 --ink:#091f77;--ink2:#4a5893;--ink3:#8a93bd;
 --paper:#ffffff;--mist:#f5f5f9;--line:#e3e2ec;
 --pink:#e03870;--pinkwash:#fdeef3;--blue:#3870e0;--bluewash:#eef3fd;
 --fd:'Bricolage Grotesque',ui-sans-serif,system-ui,sans-serif;--fb:'DM Sans',ui-sans-serif,system-ui,sans-serif;
 color-scheme:light}
*{box-sizing:border-box}html,body{margin:0}[hidden]{display:none!important}
body{background:var(--mist);color:var(--ink);font:16px/1.55 var(--fb);-webkit-font-smoothing:antialiased}
a{color:inherit}
:focus-visible{outline:3px solid var(--blue);outline-offset:2px;border-radius:6px}
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--paper);border-bottom:1px solid var(--line);
 display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding-block:12px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}
header.top h1{font:800 22px/1.1 var(--fd);letter-spacing:-.02em;margin:0;color:var(--ink)}
header.top .sub{font-size:13px;color:var(--ink2);margin-top:2px}
nav.sw{margin-left:auto;display:flex;gap:4px;background:#ebebf2;border-radius:999px;padding:4px;flex-wrap:wrap}
nav.sw a{color:var(--ink);text-decoration:none;padding:7px 14px;border-radius:999px;font-weight:600;font-size:14px;white-space:nowrap}
nav.sw a:hover{background:#dedeea}
nav.sw a.on{background:var(--ink);color:#fff}
nav.sw a.tasks{border-right:1px solid #d3d3e0;border-radius:999px 0 0 999px;margin-right:2px}
.tag{display:inline-block;vertical-align:2px;margin-left:6px;font:700 11px/1 var(--fb);letter-spacing:.04em;text-transform:uppercase;padding:4px 7px;border-radius:999px;white-space:nowrap}
.tag-tbd{color:var(--pink);background:var(--pinkwash)}
.tag-fill{color:var(--blue);background:var(--bluewash)}
.tag-draft{color:var(--ink2);background:#ececf3}
.tag-new{color:var(--ink);background:#e6fbe9}
.tag-stake{color:#fff;background:var(--pink)}
.tag-pdraft{color:var(--blue);background:var(--bluewash);border:1px solid #c5d4f6}
.agenda{background:var(--paper);border:1px dashed #b9c8ee;border-radius:16px;padding:16px 18px;margin-top:22px}
.tag-proposal{color:var(--blue);background:var(--bluewash);border:1px solid #c5d4f6}
.src{display:block;font-size:12.5px;color:var(--ink3);margin-top:2px}
.cap{font-size:13px;color:var(--ink3);margin:.6em 0 0}
.list{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.list li{position:relative;padding-left:22px}
.list li::before{content:"";position:absolute;left:2px;top:.62em;width:8px;height:8px;border-radius:50%;background:var(--ink)}
.list li.open::before{background:transparent;border:2px solid var(--pink);width:9px;height:9px;left:1px}
.eyebrow{font:700 13px/1 var(--fb);letter-spacing:.12em;text-transform:uppercase;color:var(--pink)}
h2.big{font:800 clamp(34px,4.2vw,58px)/1.02 var(--fd);letter-spacing:-.03em;margin:.35em 0 .3em;text-wrap:balance}
.lede{font-size:19px;line-height:1.5;color:var(--ink2);max-width:34em;margin:0}
.h3{font:700 19px/1.25 var(--fd);margin:0 0 12px;letter-spacing:-.01em}
.stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.stat{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:18px 20px}
.stat b{display:block;font:800 40px/1 var(--fd);letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.stat span{display:block;margin-top:8px;font-weight:600;line-height:1.35}
.stat small{display:block;margin-top:6px;font-size:12px;color:var(--ink3)}
.outs{display:grid;gap:12px}
.out{display:grid;grid-template-columns:72px 1fr;gap:14px;align-items:baseline}
.out b{font:800 30px/1 var(--fd);color:var(--pink);font-variant-numeric:tabular-nums}
.values{display:grid;gap:14px}
.val{display:grid;grid-template-columns:96px 1fr;gap:16px;align-items:baseline;padding-bottom:14px;border-bottom:1px solid var(--line)}
.val:last-child{border-bottom:0;padding-bottom:0}
.val b{font:800 28px/1 var(--fd);letter-spacing:-.02em}
.val span{font-size:17px;color:var(--ink2)}
.placeholder{border:2px dashed #c9cde3;border-radius:16px;padding:16px 18px;display:grid;gap:4px;color:var(--ink2)}
.placeholder b{color:var(--ink)}
.journey{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;position:relative}
.journey::before{content:"";position:absolute;left:8px;right:8px;top:9px;height:3px;background:linear-gradient(90deg,var(--line),var(--ink3) 50%,var(--pink))}
.journey li{position:relative;padding:30px 14px 0 0}
.journey li::before{content:"";position:absolute;left:0;top:2px;width:17px;height:17px;border-radius:50%;background:var(--paper);border:3px solid var(--ink3)}
.journey li.now::before{background:var(--ink);border-color:var(--ink)}
.journey li.goal::before{background:var(--pink);border-color:var(--pink)}
.journey .yr{display:block;font:700 13px/1 var(--fb);letter-spacing:.08em;text-transform:uppercase;color:var(--ink3)}
.journey li.goal .yr{color:var(--pink)}
.journey b{display:block;font:700 18px/1.2 var(--fd);margin:6px 0 4px}
.journey .d{display:block;font-size:14.5px;line-height:1.4;color:var(--ink2)}
.role{display:flex;flex-direction:column;gap:10px;background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:20px;text-decoration:none;color:var(--ink)}
.role .rh b{font:800 22px/1.1 var(--fd);letter-spacing:-.02em}
.role p{margin:0;color:var(--ink2);font-size:15px;line-height:1.45}
.role ul{margin:0;padding-left:18px;display:grid;gap:6px;font-size:15px}
.role .esc{margin-top:auto;font-size:13.5px;font-weight:600;color:var(--blue)}
.role-A{background:#f2f2f7}
.owner{display:flex;gap:14px;align-items:flex-start;background:var(--paper);border:1px solid var(--line);border-left:0;border-radius:16px;padding:16px 18px;font-size:16.5px}
.owner b{font:800 15px/1.4 var(--fd);color:var(--pink);white-space:nowrap}
.ladder{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}
.ladder .rung{flex:1 1 150px;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.ladder .rung b{display:block;font:800 19px/1.1 var(--fd)}
.ladder .rung span{display:block;font-size:14px;color:var(--ink2);margin-top:4px}
.ladder .rung.top{background:var(--ink);border-color:var(--ink);color:#fff}
.ladder .rung.top span{color:#c9cfee}
.ladder i{align-self:center;font-style:normal;font:800 22px var(--fd);color:var(--ink3)}
.gate{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:18px 20px;display:grid;gap:10px}
.gate .gh{font:700 17px/1.2 var(--fd)}
.chk{display:flex;gap:10px;align-items:center;font-size:16px}
.chk i{width:20px;height:20px;border-radius:6px;border:2px solid var(--ink);display:inline-block;flex:none;position:relative}
.chk i::after{content:"";position:absolute;left:5px;top:1px;width:5px;height:10px;border:solid var(--ink);border-width:0 2.5px 2.5px 0;transform:rotate(45deg)}
.gr{display:flex;gap:10px;align-items:center;margin-top:4px;font-size:14px;color:var(--ink2)}
.gr .go,.gr .push{font-weight:700;padding:6px 12px;border-radius:999px}
.gr .go{background:var(--ink);color:#fff}.gr .push{background:#ececf3;color:var(--ink)}
.stake{background:var(--paper);border:2px solid var(--pink);border-radius:18px;padding:18px 20px;display:grid;gap:8px}
.stake .sk{display:flex;align-items:center;gap:8px;font:700 17px/1.2 var(--fd)}.stake .sk .tag{margin-left:0;order:2}
.stake .sr{display:grid;grid-template-columns:88px minmax(0,1fr);gap:12px;font-size:16px;line-height:1.5;padding:8px 0;border-top:1px solid var(--line)}.stake .sr b{font:800 16px/1.5 var(--fd);color:var(--pink)}.stake small{font-size:13.5px;color:var(--ink2)}
.rhythm{list-style:none;margin:0;padding:0;display:grid;gap:0}
.rhythm li{display:grid;grid-template-columns:130px minmax(0,1fr) auto;gap:14px;align-items:baseline;padding:11px 0;border-bottom:1px solid var(--line)}
.rhythm li:last-child{border-bottom:0}
.rhythm .when{font:700 12.5px/1.2 var(--fb);letter-spacing:.06em;text-transform:uppercase;color:var(--ink3)}
.rhythm .who{font-size:13px;font-weight:700;color:var(--blue);white-space:nowrap}
@media (max-width:760px){.journey{grid-template-columns:1fr;gap:18px}.journey::before{left:7px;right:auto;top:8px;bottom:8px;width:3px;height:auto;background:linear-gradient(180deg,var(--line),var(--pink))}.journey li{padding:0 0 0 30px}
 .rhythm li{grid-template-columns:1fr}.stats{grid-template-columns:1fr 1fr}header.top{gap:10px}header.top .sub{display:none}nav.sw{margin-left:0;flex-wrap:nowrap;width:100%;justify-content:space-between}nav.sw a{padding:7px 11px}nav.sw .vn{display:none}
 .nav .hint{display:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""


def shell(view, title_tail, css, body, js=""):
    sw = '<a class="tasks" href="./">Tasks</a>' + "".join(
        f'<a href="playbook-{k}.html" class="{"on" if k == view else ""}">Option {k.upper()}<span class="vn">: {e(n)}</span></a>' for k, n in VIEWS)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Playbook</title>{FONTS}<style>{BASE}{css}</style></head><body>
<header class="top"><div><h1>Playbook</h1><div class="sub">{e(title_tail)}</div></div><nav class="sw" aria-label="Views">{sw}</nav></header>
{body}
<script>(()=>{{const h=document.querySelector('header.top'),f=()=>document.documentElement.style.setProperty('--hh',h.offsetHeight+'px');f();addEventListener('resize',f)}})();{js}</script></body></html>"""


# ---------------------------------------------------------------- A: guided tour
def view_a():
    rules = P["rules"]["items"]
    trig = P["triggers"]["items"]
    steps = [
        ("why", "Why we're here", P["story"]["brand_line"],
         f'<p class="lede">{e(P["story"]["mission"])}</p><p class="tagline">{e(P["story"]["tagline"])}</p>',
         values() + f'<p class="cap" style="margin-top:18px">{e(CH["started"]["items"][0]["t"])}</p>' + '<div style="margin-top:18px">' + stories() + '</div>'),
        ("today", "Where we are today", "Look how far we've come",
         '<p class="lede">Fall 2026. Every number here is a kid, a volunteer or a chapter we get to support.</p>',
         stats() + '<div style="margin-top:22px">' + outcomes() + '</div>'),
        ("next", "Where we're going", "1 million kids by 2040",
         f'<p class="lede">The dream: every kid is introduced to sport. Next year we grow by making the chapters we have strong.</p><p class="cap">{e(CH["dream"]["items"][1].get("src"))}</p>',
         journey() + '<div style="margin-top:30px">' + items(CH["next"]["items"][1:]) + '</div>'),
        ("roles", "How US Ops works", "Four roles. One owner for every task",
         f'<div class="owner"><b>Owner</b><span>Make it happen, pull in anyone you need, never let it slip silently</span></div>',
         '<div class="roles4">' + "".join(role_tile(k) for k in ORDER) + '</div><p class="cap">Every task, by role and season, is on the <a href="tasks.html">task grid</a>.</p>'),
        ("decide", "How we decide", "The owner decides and tells everyone affected",
         '<p class="lede">Input is welcome. Silence is not.</p>' + '<div style="margin-top:22px">' + ladder() + '</div>',
         items([r for r in rules if "owner decides" not in r["t"] and "escalate" not in r["t"]])),
        ("struggle", "When a chapter struggles", "Catch it early. Decide in the open",
         '<p class="lede">Flag struggling chapters and wins every week, so each gets support or recognition.</p>' + '<div style="margin-top:22px">' + gate() + '</div>',
         pause_rule() + '<div style="margin-top:24px">' + items(trig_rest(True)) + '</div>'),
        ("follow", "How we follow up", "Nothing closes silently",
         '<h3 class="h3">Our rhythm</h3>' + meetings() + agenda(),
         proposal() + f'<h3 class="h3" style="margin-top:26px">{e(P["team"]["standards_title"])}</h3>' + items(P["team"]["standards"])),
    ]
    rail = "".join(f'<a href="#{k}" data-i="{i}"><span class="n">{i+1}</span><span class="t">{e(lbl)}</span></a>' for i, (k, lbl, *_ ) in enumerate(steps))
    secs = "".join(
        f'<section class="step" id="s-{k}" data-k="{k}" {"" if i == 0 else "hidden"} aria-label="{e(lbl)}"><div class="l"><div class="eyebrow">Step {i+1} of {len(steps)} &middot; {e(lbl)}</div><h2 class="big">{e(head)}</h2>{left}</div><div class="r">{right}</div></section>'
        for i, (k, lbl, head, left, right) in enumerate(steps))
    css = r"""
.rail{display:flex;gap:6px;flex-wrap:wrap;padding-block:14px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px));background:var(--paper);border-bottom:1px solid var(--line);position:sticky;top:calc(env(safe-area-inset-top,0px) + var(--hh,71px));z-index:15}
.rail a{display:flex;gap:8px;align-items:center;text-decoration:none;color:var(--ink2);padding:6px 12px 6px 6px;border-radius:999px;font-weight:600;font-size:14.5px}
.rail a .n{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#ececf3;font:800 13px var(--fd);color:var(--ink2)}
.rail a.done .n{background:var(--ink3);color:#fff}
.rail a.on{background:var(--ink);color:#fff}.rail a.on .n{background:var(--pink);color:#fff}
main.tour{max-width:1240px;margin:0 auto;padding-block:44px 120px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}
.step{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:56px;align-items:start}
.step .l{position:sticky;top:150px}
.tagline{font:800 22px/1 var(--fd);color:var(--pink);margin:22px 0 0}
.roles4{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.step .owner{margin-top:20px}
.step .l .h3{margin-top:8px}
.nav{position:fixed;left:0;right:0;bottom:0;background:var(--paper);border-top:1px solid var(--line);display:flex;align-items:center;gap:12px;padding-block:12px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px));padding-bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:20}
.nav button{font:700 15px var(--fb);border-radius:999px;padding:11px 20px;cursor:pointer;border:0}
.nav .prev{background:#ececf3;color:var(--ink)}.nav .next{background:var(--ink);color:#fff;margin-left:auto}
.nav .next b{color:#ffc2d6;font-weight:700}
.nav .hint{font-size:13px;color:var(--ink3)}
.nav button[disabled]{opacity:.35;cursor:default}
@media (max-width:900px){.step{grid-template-columns:1fr;gap:28px}.step .l{position:static}.rail{position:static}.rail a .t{display:none}.rail a.on .t{display:inline}.roles4{grid-template-columns:1fr}}
"""
    body = f'<div class="rail" role="tablist" aria-label="Playbook steps">{rail}</div><main class="tour">{secs}</main>' \
           f'<div class="nav"><button class="prev" type="button" id="prev">Back</button><span class="hint">Use the arrow keys to move between steps</span><button class="next" type="button" id="next">Next</button></div>'
    names = json.dumps([s[1] for s in steps])
    keys = json.dumps([s[0] for s in steps])
    js = f"""
const K={keys},N={names};let cur=0;
const secs=[...document.querySelectorAll('.step')],rail=[...document.querySelectorAll('.rail a')],prev=document.getElementById('prev'),next=document.getElementById('next');
function go(i,push){{cur=Math.max(0,Math.min(K.length-1,i));secs.forEach((s,j)=>s.hidden=j!==cur);rail.forEach((a,j)=>{{a.classList.toggle('on',j===cur);a.classList.toggle('done',j<cur);a.setAttribute('aria-selected',j===cur)}});
 prev.disabled=cur===0;next.innerHTML=cur===K.length-1?'Back to the start':'Next: <b>'+N[cur+1]+'</b>';if(push!==false&&location.hash!=='#'+K[cur])history.replaceState(null,'','#'+K[cur]);window.scrollTo({{top:0}})}}
rail.forEach((a,j)=>a.onclick=ev=>{{ev.preventDefault();go(j)}});
prev.onclick=()=>go(cur-1);next.onclick=()=>go(cur===K.length-1?0:cur+1);
document.addEventListener('keydown',ev=>{{if(ev.target.closest('input,textarea'))return;if(ev.key==='ArrowRight')go(cur+1);if(ev.key==='ArrowLeft')go(cur-1)}});
function fromHash(){{const i=K.indexOf(location.hash.slice(1));go(i<0?0:i,false)}}
window.addEventListener('hashchange',fromHash);fromHash();
"""
    return shell("a", "A guided tour for anyone joining US Ops. Seven short steps, from why we're here to how we follow up.", css, body, js)


# ---------------------------------------------------------------- B: by role
def view_b():
    steps_by = {}
    for s in G["steps"]:
        steps_by.setdefault(s["tier"], {}).setdefault(s["phase"], []).append(s["short"])
    meet_by = {}
    for m in P["tracking"]["meetings"]:
        meet_by.setdefault(m["who"], []).append(m)

    def season(k):
        rows = []
        for p in PH:
            lst = steps_by.get(k, {}).get(p["key"], [])
            if not lst:
                continue
            rows.append(f'<div class="ph"><div class="pl"><b>{e(p["label"])}</b><small>{e(p["when"])}</small></div><ul>' + "".join(f"<li>{e(x)}</li>" for x in lst) + "</ul></div>")
        return "".join(rows)

    def rhythm(k):
        ms = meet_by.get(k, [])
        if not ms:
            return '<p class="muted">No standing meetings. Join the weekly US Ops call.</p>'
        return '<ul class="list">' + "".join(f'<li class="{"open" if m.get("s") else ""}"><span>{e(m["t"])}</span>{tag(m.get("s"))}<span class="src">{e(m["when"])}</span></li>' for m in ms) + "</ul>"

    cards = '<button class="pick all" type="button" data-k="everyone" aria-controls="p-everyone"><b>Everyone</b><span>Why we\'re here, how we decide, and the standards we all keep</span><small>Start here if you\'re new</small></button>' + "".join(
        f'<button class="pick" type="button" data-k="{k.lower()}" aria-controls="p-{k.lower()}"><b>{e(TIERS[k]["label"])}</b><span>{e(TIERS[k]["role"])}</span><small>{sum(len(v) for v in steps_by.get(k, {}).values())} tasks on the grid</small></button>'
        for k in ORDER)

    panels = []
    for k in ORDER:
        t, r = TIERS[k], ROLE[k]
        panels.append(f'''<section class="panel" id="p-{k.lower()}" hidden>
<div class="ptop"><div><div class="eyebrow">Your role</div><h2 class="big">{e(t["label"])}</h2><p class="lede">{e(t["role"])}</p></div>
<div class="goto"><span>When you're stuck</span><b>{e(r["escalates"])}</b></div></div>
<div class="cols">
<div class="col"><h3 class="h3">What you own</h3><ul class="list">{"".join(f"<li><span>{e(x)}</span></li>" for x in r["owns"])}</ul>
<h3 class="h3" style="margin-top:28px">Your rhythm</h3>{rhythm(k)}</div>
<div class="col wide"><h3 class="h3">Your season, step by step</h3><div class="season">{season(k)}</div></div>
</div></section>''')
    rules = P["rules"]["items"]
    panels.append(f'''<section class="panel" id="p-everyone" hidden>
<div class="ptop"><div><div class="eyebrow">For everyone on US Ops</div><h2 class="big">{e(P["story"]["brand_line"])}</h2><p class="lede">The dream: every kid is introduced to sport. 1 million kids by 2040.</p></div>
<div class="goto"><span>Owner means</span><b>Make it happen, pull in anyone you need, never let it slip silently</b></div></div>
<div class="cols three">
<div class="col"><h3 class="h3">Where we are, Fall 2026</h3>{stats()}</div>
<div class="col"><h3 class="h3">How we decide</h3>{items(rules)}</div>
<div class="col"><h3 class="h3">{e(P["team"]["standards_title"])}</h3>{items(P["team"]["standards"])}<div style="margin-top:20px">{stories()}</div></div>
</div>
<div class="cols even rowsep">
<div class="col"><h3 class="h3">When chapters struggle</h3>{gate()}<div style="margin-top:16px">{pause_rule()}</div><div style="margin-top:20px">{items(trig_rest())}</div></div>
<div class="col"><h3 class="h3">Meetings and follow-up</h3>{meetings()}{agenda()}<div style="margin-top:26px">{proposal()}</div></div>
</div></section>''')
    css = r"""
main.roles{max-width:1320px;margin:0 auto;padding-block:30px 80px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}
.intro{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:16px}
.intro h2{font:800 30px/1.1 var(--fd);letter-spacing:-.02em;margin:0}
.intro p{margin:0;color:var(--ink2)}
.picker{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.pick{all:unset;box-sizing:border-box;cursor:pointer;background:var(--paper);border:2px solid var(--line);border-radius:18px;padding:16px 18px;display:flex;flex-direction:column;gap:6px;min-width:0}
.pick b{font:800 21px/1.1 var(--fd);letter-spacing:-.02em}
.pick span{font-size:14px;line-height:1.4;color:var(--ink2)}
.pick small{margin-top:auto;padding-top:6px;font-size:12.5px;font-weight:700;color:var(--ink3)}
.pick:hover{border-color:var(--ink3)}
.pick.on{border-color:var(--ink);background:var(--ink)}
.pick.on b,.pick.on span{color:#fff}.pick.on small{color:#ffc2d6}
.pick.all{background:var(--pinkwash);border-color:#f6cddb}
.pick.all.on{background:var(--ink);border-color:var(--ink)}
.panel{margin-top:30px;background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:34px 36px}
.ptop{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:32px;align-items:end;padding-bottom:26px;border-bottom:1px solid var(--line)}
.ptop h2.big{margin:.25em 0 .2em}
.goto{background:var(--mist);border-radius:16px;padding:16px 18px;display:grid;gap:4px}
.goto span{font:700 12px/1 var(--fb);letter-spacing:.1em;text-transform:uppercase;color:var(--ink3)}
.goto b{font:700 17px/1.35 var(--fd)}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:40px;margin-top:28px}
.cols.three{grid-template-columns:repeat(3,minmax(0,1fr))}
.cols.even{grid-template-columns:repeat(2,minmax(0,1fr))}.rowsep{padding-top:30px;border-top:1px solid var(--line)}
.cols.three .stats{grid-template-columns:1fr 1fr}.cols.three .stat b{font-size:30px}
.season{display:grid;gap:0}
.ph{display:grid;grid-template-columns:150px minmax(0,1fr);gap:18px;padding:13px 0;border-bottom:1px solid var(--line)}
.ph:last-child{border-bottom:0}
.ph .pl b{display:block;font:700 16px/1.2 var(--fd)}
.ph .pl small{display:block;font-size:12.5px;color:var(--ink3);margin-top:3px}
.ph ul{margin:0;padding-left:18px;display:grid;gap:5px;font-size:15.5px}
.muted{color:var(--ink2);margin:0}
@media (max-width:1000px){.picker{grid-template-columns:repeat(2,minmax(0,1fr))}.ptop,.cols,.cols.three,.cols.even{grid-template-columns:1fr}.panel{padding:22px}.ph{grid-template-columns:1fr;gap:6px}}
"""
    body = f'<main class="roles"><div class="intro"><h2>Find your role</h2><p>Pick a role to see what you own, your season and who to go to.</p></div><div class="picker" role="tablist">{cards}</div>{"".join(panels)}</main>'
    js = """
const picks=[...document.querySelectorAll('.pick')];
function show(k,push){const ok=picks.some(p=>p.dataset.k===k);k=ok?k:'everyone';
 picks.forEach(p=>{p.classList.toggle('on',p.dataset.k===k);p.setAttribute('aria-selected',p.dataset.k===k)});
 document.querySelectorAll('.panel').forEach(s=>s.hidden=s.id!=='p-'+k);
 if(push!==false)history.replaceState(null,'','#'+k)}
picks.forEach(p=>p.onclick=()=>show(p.dataset.k));
window.addEventListener('hashchange',()=>show(location.hash.slice(1),false));show(location.hash.slice(1)||'everyone',false);
"""
    return shell("b", "Start from your role: what you own, your season, your rhythm and who to go to.", css, body, js)


# ---------------------------------------------------------------- C: field guide
def view_c():
    rules = P["rules"]["items"]
    trig = P["triggers"]["items"]
    toc = [("story", "Our story"), ("roles", "How US Ops works"), ("decide", "How we decide"), ("struggle", "When chapters struggle"), ("follow", "Meetings and follow-up")]
    body = f'''<section class="hero"><div class="in">
<div class="eyebrow">The US Ops field guide</div>
<h2 class="mega">{e(P["story"]["brand_line"])}</h2>
<div class="dream"><div><span>The dream</span><b>Every kid is introduced to sport</b></div><div><span>By 2040</span><b>1 million kids</b><small>{e(CH["dream"]["items"][1].get("src"))}</small></div><div><span>Together we can</span><b>{e(P["story"]["values"][0]["k"])} &middot; {e(P["story"]["values"][1]["k"])} &middot; {e(P["story"]["values"][2]["k"])}</b></div></div>
</div></section>
<div class="band"><div class="in">{stats(big=True)}</div></div>
<nav class="toc" aria-label="Sections"><div class="in">{"".join(f'<a href="#{k}">{e(n)}</a>' for k, n in toc)}</div></nav>
<main class="guide">
<section id="story" class="sec"><div class="sh"><div class="eyebrow">Our story</div><h2 class="h2">From one campus to a national network</h2></div>
{journey()}
<div class="two" style="margin-top:34px"><div><h3 class="h3">What families tell us</h3>{outcomes()}</div><div><h3 class="h3">Our mission</h3><p class="mission">{e(P["story"]["mission"])}</p><div style="margin-top:18px">{stories()}</div></div></div></section>
<section id="roles" class="sec"><div class="sh"><div class="eyebrow">How US Ops works</div><h2 class="h2">Four roles. One owner for every task</h2></div>
<div class="owner"><b>Owner</b><span>Make it happen, pull in anyone you need, never let it slip silently</span></div>
<div class="roles4">{"".join(role_tile(k, 4) for k in ORDER)}</div>
<p class="cap">Every task, by role and season, is on the <a href="tasks.html">task grid</a>.</p></section>
<section id="decide" class="sec"><div class="sh"><div class="eyebrow">How we decide</div><h2 class="h2">The owner decides and tells everyone affected</h2></div>
<div class="two"><div>{ladder()}</div><div>{items([r for r in rules if "escalate" not in r["t"]])}</div></div></section>
<section id="struggle" class="sec"><div class="sh"><div class="eyebrow">When chapters struggle</div><h2 class="h2">Catch it early. Decide in the open</h2></div>
<div class="two"><div>{gate()}<div style="margin-top:18px">{pause_rule()}</div></div><div>{items(trig_rest())}</div></div></section>
<section id="follow" class="sec"><div class="sh"><div class="eyebrow">Meetings and follow-up</div><h2 class="h2">Nothing closes silently</h2></div>
<div class="two"><div><h3 class="h3">Our rhythm</h3>{meetings()}{agenda()}</div><div>{proposal()}<h3 class="h3" style="margin-top:26px">{e(P["team"]["standards_title"])}</h3>{items(P["team"]["standards"])}</div></div></section>
</main>'''
    css = r"""
.in{max-width:1240px;margin:0 auto;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}
.hero{background:var(--ink);color:#fff;padding-block:52px 44px}
.hero .eyebrow{color:#ff9fbf}
.mega{font:800 clamp(40px,5.4vw,76px)/.98 var(--fd);letter-spacing:-.035em;margin:.3em 0 .5em;max-width:15ch;text-wrap:balance}
.dream{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;border-top:1px solid rgba(255,255,255,.22)}
.dream>div{padding:18px 22px 0 0}
.dream>div+div{padding-left:22px;border-left:1px solid rgba(255,255,255,.22)}
.dream span{display:block;font:700 12.5px/1 var(--fb);letter-spacing:.12em;text-transform:uppercase;color:#b8c0ea}
.dream b{display:block;font:700 24px/1.2 var(--fd);margin-top:8px}
.dream small{display:block;font-size:12px;color:#b8c0ea;margin-top:4px}
.band{background:var(--paper);border-bottom:1px solid var(--line);padding-block:26px}
.stats.big{grid-template-columns:repeat(4,minmax(0,1fr))}
.stats.big .stat{border:0;padding:0 0 0 18px;border-left:3px solid var(--line);border-radius:0}
.stats.big .stat:first-child{border-left-color:var(--pink)}
.stats.big .stat b{font-size:46px}
.toc{position:sticky;top:calc(env(safe-area-inset-top,0px) + var(--hh,71px));z-index:15;background:rgba(245,245,249,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.toc .in{display:flex;gap:6px;flex-wrap:wrap;padding-block:10px}
.toc a{text-decoration:none;font-weight:600;font-size:14.5px;padding:7px 13px;border-radius:999px;color:var(--ink2)}
.toc a:hover,.toc a.on{background:var(--paper);color:var(--ink);box-shadow:0 0 0 1px var(--line)}
main.guide{max-width:1240px;margin:0 auto;padding-block:10px 90px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}
.sec{padding-block:56px 8px;scroll-margin-top:130px}
.sec+.sec{border-top:1px solid var(--line)}
.sh{margin-bottom:26px}
.h2{font:800 clamp(28px,3vw,40px)/1.08 var(--fd);letter-spacing:-.025em;margin:.35em 0 0;max-width:22ch;text-wrap:balance}
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:48px;align-items:start}
.mission{font-size:17px;line-height:1.6;color:var(--ink2);margin:0;max-width:38em}
.roles4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:18px}
@media (max-width:980px){.two{grid-template-columns:1fr;gap:28px}.roles4{grid-template-columns:repeat(2,minmax(0,1fr))}.stats.big{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:22px}.dream{grid-template-columns:1fr}.dream>div+div{padding-left:0;border-left:0}}
@media (max-width:560px){.roles4{grid-template-columns:1fr}.toc .in{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}.toc a{white-space:nowrap}.sec{scroll-margin-top:150px}}
"""
    js = """
const links=[...document.querySelectorAll('.toc a')],secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const io=new IntersectionObserver(es=>{es.forEach(en=>{if(en.isIntersecting){links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+en.target.id))}})},{rootMargin:'-40% 0px -55% 0px'});
secs.forEach(s=>s&&io.observe(s));
"""
    return shell("c", "One scrolling page: the dream up top, then how US Ops works, decides and follows up.", css, body, js)


# ---------------------------------------------------------------- FINAL playbook (Nov 23, 20:01)
# Field guide (C) as the base, left section nav from A. Two goals: motivate and set expectations.
# No draft labels; "to decide" lines and the stories placeholder are left out. Mary does the visual design next.
DECK = "2026 Q4 RYC Board Meeting deck (Nov 22, 2026)"
TARGETS = [  # Q4 board deck, slides 9, 10 and 16 (short labels)
    ("120", "chapters running in fall"),
    ("30", "new chapters, 15 a season"),
    ("22,000", "registrations"),
    ("95%", "of chapters keep running"),
    ("90%", "of sessions delivered"),
    ("5", "learning sites on what brings kids back"),
]
CSUITE = [("Mary", "CEO"), ("Josh", "COO / CFO, runs the automated work"), ("Owayne", "CTO"), ("Callie", "International")]
TEAMS = [("Whitney", ["Alaysia", "Lily"]), ("Sierra", ["Nicole", "Aisling"])]  # reporting lines, Nov 23 call


def plain(lst, drop=()):
    out = [f'<li><span>{e(it["t"])}</span></li>' for it in lst
           if it.get("s") not in ("tbd", "fill") and not any(d in it["t"] for d in drop)]
    return '<ul class="list">' + "".join(out) + "</ul>"


def chips(k, cls=""):
    return '<div class="chips">' + "".join(
        f'<span class="chip {cls}">{e(n.strip())}</span>' for n in TIERS[k]["who"].split(",")) + "</div>"


def org():
    teams = "".join(
        f'<div class="o-col"><div class="o-node"><b>{e(c)}</b><span>Coordinator</span></div><div class="o-v" aria-hidden="true"></div>'
        + '<div class="o-ints">' + "".join(f'<div class="o-int"><b>{e(n)}</b><span>Intern</span></div>' for n in ins) + '</div></div>'
        for c, ins in TEAMS)
    return f"""<div class="otree">
<div class="o-node top"><b>{e(TIERS["L"]["who"])}</b><span>US Ops lead</span></div><div class="o-v" aria-hidden="true"></div>
<div class="o-row">{teams}</div></div>"""


def decide_flow():
    steps = [("Intern", "Owns their chapters start to finish. Escalates to the coordinator."),
             ("Coordinator", "Runs the systems and unblocks interns. Escalates to the lead."),
             ("Lead", "Makes the final call. Anything that goes to all chapters goes through the lead.")]
    out = []
    for n, (h, t) in enumerate(steps):
        if n:
            out.append('<div class="df-arrow" aria-hidden="true">&rarr;</div>')
        out.append(f'<div class="df-step{" last" if n == 2 else ""}"><b>{e(h)}</b><span>{e(t)}</span></div>')
    return '<div class="dflow">' + "".join(out) + '</div><p class="note">Safety incidents skip the line: chapters alert the lead right away.</p>'


def role_card(k):
    t, r = TIERS[k], ROLE[k]
    who = "Automated work" if k == "A" else t["who"]
    return (f'<div class="rc"><h4><b>{e(t["label"])}</b><span>{e(who)}</span></h4><p>{e(t["role"])}</p><ul>'
            + "".join(f"<li>{e(x)}</li>" for x in r["owns"][:5]) + f'</ul><p class="rc-esc">{e(r["escalates"])}</p></div>')


def triage():
    rows = [("Red zone", "A chapter with under 30 signups, or any parent complaint in the past month. Its owner steps in with extra support right away: a call with the chapter leads and a plan to get back on track."),
            ("Pause", "A chapter that misses 2 key deadlines (choosing a location, setting the leadership team, selecting session dates), after being reminded 3+ times before each. Its owner meets with the chapter to push the season back, given the missed deadlines.")]
    return ('<div class="stake">' + "".join(f'<div class="sr"><b>{e(h)}</b><span>{e(b)}</span></div>' for h, b in rows) + '</div>')


def rhythm_plain():
    return '<ul class="rhythm">' + "".join(
        f'<li><span class="when">{e(m["when"])}</span><span class="what">{e(m["t"])}</span><span class="who">{e(TIERS[m["who"]]["label"])}</span></li>'
        for m in sorted(P["tracking"]["meetings"], key=lambda m: m["when"] == "As needed")) + "</ul>"


def journey_final():
    pts = [("2018", "Founded", "Charlottesville, Virginia, by UVA student-athletes"),
           ("Fall 2024", "First expansion cohort", "From 1 to 10 chapters"),
           ("Fall 2026", "Today", "19,757 kids, 106 chapters"),
           ("2027", "Next", "120 chapters, 22,000 registrations"),
           ("2040", "The dream", "1,000,000 kids reached")]
    return '<ol class="journey">' + "".join(
        f'<li class="{"now" if w == "Fall 2026" else ""}{" goal" if w == "2040" else ""}"><span class="yr">{e(w)}</span><b>{e(h)}</b><span class="d">{e(t)}</span></li>'
        for w, h, t in pts) + "</ol>"


def stats_final():
    S = [("19,757", "kids so far"), ("106", "chapters in the network"), ("38 + DC", "states"), ("2,472", "volunteers")]
    return '<div class="stats big">' + "".join(f'<div class="stat"><b>{e(n)}</b><span>{e(l)}</span></div>' for n, l in S) + "</div>"


def outcomes_final():
    O = [("89%", "of kids more interested in sports and being active"), ("86%", "of kids grew in confidence"), ("96%", "of kids felt welcomed and that they belonged")]
    return '<div class="outs">' + "".join(f'<div class="out" style="--p:{e(n)}"><b>{e(n)}</b><span>{e(l)}</span><i class="bar" aria-hidden="true"></i></div>' for n, l in O) + "</div>"


AGENDA = [('24 hrs before', "Everyone posts their check-in in the Tracker: what got done, what you're working on now, any roadblocks or risks. The lead reads them before the call"),
          ('0-3 min', 'One win: a chapter or teammate shout-out, led by a different person each week'),
          ('3-15 min', 'Overdue and blocked: only the items flagged in the Tracker. The owner gives a new date or names what they need'),
          ('15-25 min', 'One decision: a single topic picked in advance and framed as a question, led by whoever raised it'),
          ('25-30 min', 'Commitments: each person says what they own next week. The Tracker is updated live'),
          ('After', 'Recap posted, with an owner and a date on every action item')]


def agenda_final():
    return '<ol class="agenda2">' + "".join(
        f'<li><span class="num">{i+1}</span><span class="tc">{e(t)}</span><span class="tx">{e(x)}</span></li>' for i, (t, x) in enumerate(AGENDA)) + "</ol>"


def sub(id_, title, html_):
    return f'<div class="sub" id="{id_}"><h3 class="h3">{e(title)}</h3>{html_}</div>'


def view_final():
    st, tk = P["story"], P["tracking"]
    trig, rules = P["triggers"]["items"], P["rules"]["items"]
    S = []  # (id, nav label, eyebrow, heading, [(sub id, sub label)], body)

    S.append(("why", "Why we're here", "1. Why we're here", None, [("today", "Where we are today"), ("going", "Where we're going")],
        f'''<div class="hero">
<h2 class="mega">{e(st["brand_line"])}</h2>
<p class="mis">{e(st["mission"])}</p>
<div class="dream"><div><span>The dream</span><b>Every kid is introduced to sport</b></div><div><span>By 2040</span><b>1,000,000 kids reached</b></div><div><span>Our tagline</span><b>{e(st["tagline"])}</b></div></div></div>
<div class="vals3">''' + "".join(f'<div class="v"><b>{e(v["k"])}</b><span>{e(v["t"])}</span></div>' for v in st["values"]) + '</div>'
        + '<div class="sub tight" id="today"><div class="row2"><div><h4 class="h4">Where we are today</h4>' + stats_final() + '<p class="src-note">Kids and volunteers from the live site counter, Nov 15, 2026. Chapters from the app, Oct 29, 2026: 106 in the network, 102 running this fall. States from the live site, Nov 2026.</p></div>'
        + f'<div><h4 class="h4">What families tell us</h4>{outcomes_final()}<p class="src-note">From about 900 parent and caregiver survey responses, as of June 2026.</p></div></div></div>'
        + '<div class="sub tight" id="going"><h4 class="h4">Where we\'re going</h4>' + journey_final()
        + '<h4 class="h4" style="margin-top:22px">2027 targets</h4><div class="targets">'
        + "".join(f'<div class="tg"><b>{e(n)}</b><span>{e(l)}</span></div>' for n, l in TARGETS) + '</div>'
        + '<p class="note">We grow only while 95% of chapters keep running and 90% of sessions happen. If either slips, we slow launches. Stronger chapters before more chapters: help every chapter reach 30+ kids, the one real predictor of a chapter lasting.</p></div>'))

    S.append(("expect", "Expectations and standards", "2. Expectations, accountability and standards", "What we expect of each other",
        [("standards", "Team standards"), ("meeting", "The weekly meeting"), ("tracking", "How we track work"), ("rhythm", "Our meeting rhythm")],
        '<div class="owner"><b>Owner</b><span>Make it happen, pull in anyone you need, never let it slip silently</span></div>'
        + sub("standards", "Team standards", '<div class="std">' + "".join(
            f'<div class="s"><i aria-hidden="true">{i+1}</i><span>{e(x["t"])}</span></div>' for i, x in enumerate(P["team"]["standards"])) + '</div>')
        + sub("meeting", "The weekly US Ops meeting, 30 minutes", agenda_final())
        + sub("tracking", "How we track work", plain(tk["proposal"]))
        + sub("rhythm", "Our meeting rhythm", rhythm_plain())
        + sub("good", "What good looks like", '<ul class="list">' + "".join(f"<li><span>{e(x)}</span></li>" for x in G["principles"]) + "</ul>")))

    S.append(("roles", "Roles and who's who", "3. Roles and who's who", "Four roles. One owner for every task",
        [("org", "Who's who"), ("cards", "What each role owns"), ("decide", "How we decide")],
        sub("org", "Who's who", org())
        + sub("cards", "What each role owns", '<div class="rcs">' + "".join(role_card(k) for k in ORDER) + '</div><p class="cap">Every task, by role and season, is on the <a href="tasks.html">task grid</a>.</p>')
        + sub("decide", "How we decide", decide_flow() + f'<div style="margin-top:20px">{plain(rules, drop=("escalate", "safety incident", "goes to all chapters"))}</div>')))

    S.append(("struggle", "When a chapter struggles", "4. When a chapter struggles", "Catch it early. Decide in the open",
        [("gate", "Before session one"), ("redzone", "Red zone and pause"), ("other", "Other chapter rules")],
        sub("gate", "Before session one: the gate", gate())
        + sub("redzone", "Red zone and pause", triage())
        + sub("other", "Other chapter rules", plain(trig[1:], drop=("Red zone", "misses 2 key deadlines", "insurance invoice")))))

    side = "".join(
        f'<a class="top1" href="#{k}"><span class="n">{i+1}</span><span class="t">{e(lbl)}</span></a>'
        + '<div class="subs">' + "".join(f'<a href="#{sid}">{e(sl)}</a>' for sid, sl in subs) + '</div>'
        for i, (k, lbl, _, _, subs, _) in enumerate(S))
    secs = "".join(
        f'<section id="{k}" class="sec">' + (f'<div class="sh"><h2 class="h2">{e(h)}</h2></div>' if h else '') + body + '</section>'
        for k, _, eb, h, _, body in S)
    body = f'<div class="wrap"><nav class="side" aria-label="Playbook sections"><div class="sidein">{side}<a class="grid" href="tasks.html">Open the task grid &rarr;</a></div></nav><main class="final">{secs}</main></div>'
    css = r"""
.wrap{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:250px minmax(0,1fr);gap:44px;padding-block:22px 80px;padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}
.side{position:sticky;top:calc(env(safe-area-inset-top,0px) + var(--hh,71px) + 24px);align-self:start;max-height:calc(100vh - var(--hh,71px) - 48px);overflow-y:auto}
.sidein{display:flex;flex-direction:column;gap:2px}
.side a{text-decoration:none;color:var(--ink2);border-radius:12px}
.side a.top1{display:flex;gap:10px;align-items:center;padding:9px 12px;font-weight:700;font-size:15px;line-height:1.25;color:var(--ink)}
.side a.top1 .n{flex:none;width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#e6e6ef;font:800 12.5px var(--fd)}
.side a.top1.on{background:var(--ink);color:#fff}.side a.top1.on .n{background:var(--pink);color:#fff}
.subs{display:flex;flex-direction:column;margin:2px 0 10px 48px;border-left:2px solid var(--line)}
.subs a{padding:5px 12px;font-size:14px;font-weight:500;border-radius:0 8px 8px 0;margin-left:-2px;border-left:2px solid transparent}
.subs a:hover{color:var(--ink);background:#ebebf2}.subs a.on{color:var(--ink);font-weight:700;border-left-color:var(--pink)}
.side a.grid{margin-top:8px;color:var(--blue);font-size:14px;font-weight:600;padding:8px 12px}
main.final{min-width:0}
.sec{padding-block:0 36px}
.sec+.sec{border-top:2px solid var(--line);padding-top:34px}
.sec,.sub{scroll-margin-top:calc(var(--hh,71px) + 20px)}
.sub{margin-top:28px}
.sub>.h3{font-size:22px;margin-bottom:12px}
.h4{font:700 17px/1.25 var(--fd);margin:0 0 12px}
.hero{background:var(--ink);color:#fff;border-radius:22px;padding:28px 34px 24px}
.hero .eyebrow{color:var(--pink)}
.mega{font:800 clamp(28px,3vw,44px)/1.05 var(--fd);letter-spacing:-.03em;margin:.3em 0 .35em;text-wrap:balance}
.mis{font-size:16.5px;line-height:1.55;color:#d3d8f3;max-width:52em;margin:0 0 18px}
.vchips{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}.vchips span{font:700 16px/1 var(--fd);padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.14)}
.dream{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid rgba(255,255,255,.22)}
.dream>div{padding:14px 22px 0 0}.dream>div+div{padding-left:22px;border-left:1px solid rgba(255,255,255,.22)}
.dream span{display:block;font:700 12.5px/1 var(--fb);letter-spacing:.12em;text-transform:uppercase;color:#b8c0ea}
.dream b{display:block;font:700 20px/1.2 var(--fd);margin-top:8px}
.vals3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;margin-top:26px}
.vals3 .v{padding:4px 0}
.vals3 b{display:block;font:800 34px/1 var(--fd);letter-spacing:-.025em;color:var(--ink)}
.vals3 span{display:block;margin-top:8px;font-size:16px;color:var(--ink2)}
.sh{margin-bottom:10px}
.h2{font:800 clamp(28px,3vw,42px)/1.08 var(--fd);letter-spacing:-.025em;margin:.35em 0 0;max-width:26ch;text-wrap:balance}
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:44px;align-items:start}
.stats.big{grid-template-columns:repeat(4,minmax(0,1fr))}
.stats.big .stat{border:0;padding:0 0 0 18px;border-left:3px solid var(--line);border-radius:0;background:none}
.stats.big .stat:first-child{border-left-color:var(--pink)}
.stats.big .stat b{font-size:42px}
.targets{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.targets .tg{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:18px 20px}
.targets .tg:first-child{background:var(--ink);border-color:var(--ink);color:#fff}
.targets b{display:block;font:800 42px/1 var(--fd);letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.targets span{display:block;margin-top:10px;font-weight:600;line-height:1.35}
.targets .tg:first-child span{color:#d3d8f3}
.cap{max-width:62em;margin-top:14px}
main.final .journey{grid-template-columns:repeat(5,minmax(0,1fr))}
@media (max-width:760px){main.final .journey{grid-template-columns:1fr}}
.note{margin:14px 0 0;font-size:15px;color:var(--ink2);max-width:62em}
.owner{margin-top:18px}
.std{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.std .s{display:flex;gap:14px;align-items:flex-start;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:16px 18px;font-size:16.5px;font-weight:600;line-height:1.4}
.std i{font:800 14px/1 var(--fd);font-style:normal;color:#fff;background:var(--ink);width:28px;height:28px;border-radius:50%;display:grid;place-items:center;flex:none}
.org{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:28px;display:flex;flex-direction:column;align-items:center;min-width:0}
.lvl{width:100%;display:flex;flex-direction:column;align-items:center;gap:10px}
.lvlname{font:700 12px/1 var(--fb);letter-spacing:.12em;text-transform:uppercase;color:var(--ink3)}
.csrow{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,440px) minmax(0,1fr);gap:20px;width:100%;align-items:end;margin-top:10px}.csrow .ceo{grid-column:2;display:flex;justify-content:center}.csrow .others{grid-column:3;display:flex;flex-wrap:wrap;gap:8px}.csrow .others .cs{min-width:0;flex:1 1 90px;padding:10px 12px}.csrow .ceo .cs{min-width:0}
.cs{min-width:120px;text-align:center;background:var(--mist);border-radius:14px;padding:12px 16px}
.cs b{display:block;font:800 18px/1.1 var(--fd)}.cs span{display:block;font-size:13.5px;color:var(--ink2);margin-top:3px}
.cs.us{background:var(--ink);color:#fff}.cs.us span{color:#c9cfee}
.stem{width:3px;height:24px;background:var(--line);margin:6px 0}.stem.short{height:18px;margin:4px auto}
.node{background:var(--paper);border:1.5px solid var(--line);border-radius:16px;padding:14px 18px;display:grid;gap:8px;max-width:440px;width:100%}
.node b{font:800 19px/1.1 var(--fd)}.node>span{font-size:14px;color:var(--ink2);line-height:1.4}
.node.lead{background:var(--ink);border-color:var(--ink);color:#fff}.node.lead>span{color:#c9cfee}
.node.ai{background:#f2f2f7;border-style:dashed}
.leadrow{margin-top:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,440px) minmax(0,1fr);gap:20px;width:100%;align-items:center}.leadrow .lead{grid-column:2}.leadrow .ai{grid-column:3;max-width:300px}
.orgnote{margin:18px 0 0;font-size:14px;color:var(--ink2);text-align:center}
.branch{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;width:100%;max-width:900px;padding-top:20px;border-top:3px solid var(--line)}
.branch .col{display:flex;flex-direction:column;align-items:center}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:13.5px;font-weight:600;padding:4px 10px;border-radius:999px;background:var(--bluewash);color:var(--ink)}
.chip.inv{background:rgba(255,255,255,.16);color:#fff}
.roles4{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.role .rh{display:grid;gap:8px}
.stake{background:var(--paper);border:2px solid var(--pink);border-radius:18px;padding:8px 20px}
.stake .sr{display:grid;grid-template-columns:100px minmax(0,1fr);gap:14px;font-size:16.5px;line-height:1.5;padding:12px 0}
.stake .sr+.sr{border-top:1px solid var(--line)}
.stake .sr b{font:800 17px/1.5 var(--fd);color:var(--pink)}
.gate{max-width:560px}
.sub .gate .gh{display:none}
.stake .sr:first-child{border-top:0}
.hero{padding:22px 30px 18px}
.mega{font-size:clamp(26px,2.5vw,38px);margin:0 0 .3em}
.mis{font-size:15px;line-height:1.5;margin:0 0 14px}
.dream>div{padding-top:10px}.dream b{font-size:18px;margin-top:5px}.dream span{font-size:11.5px}
.vals3{gap:24px;margin-top:16px}.vals3 b{font-size:26px}.vals3 span{font-size:15px;margin-top:4px}
.sub.tight{margin-top:20px}
.row2{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:36px;align-items:start}
.stats.big .stat b{font-size:32px}.stats.big .stat{padding-left:14px}.stats.big .stat span{margin-top:4px;font-size:14px}
.outs{gap:6px}.out{grid-template-columns:56px 1fr;gap:10px}.out b{font-size:22px}.out span{font-size:14.5px}
main.final .journey li{padding-top:26px}main.final .journey b{font-size:16px;margin:4px 0 2px}main.final .journey .d{font-size:13.5px}
.targets{grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}
.targets .tg{padding:12px 14px;border-radius:14px}.targets b{font-size:30px}.targets span{font-size:13.5px;margin-top:6px}
.note{font-size:14px;margin-top:10px}
.std{grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}.std .s{font-size:14.5px;padding:14px;gap:10px}
.agenda2{list-style:none;margin:0;padding:0;display:grid;gap:8px;max-width:860px}
.agenda2 li{display:grid;grid-template-columns:28px 92px minmax(0,1fr);gap:12px;align-items:center;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:10px 14px}
.agenda2 .num{width:28px;height:28px;border-radius:50%;background:var(--ink);color:#fff;display:grid;place-items:center;font:800 13px var(--fd)}
.agenda2 .tc{justify-self:start;font:700 12.5px/1 var(--fb);letter-spacing:.04em;text-transform:uppercase;color:var(--blue);background:var(--bluewash);padding:6px 10px;border-radius:999px;white-space:nowrap}
.agenda2 .tx{font-size:15.5px;line-height:1.4}
@media (max-width:1100px){.row2{grid-template-columns:1fr}.targets{grid-template-columns:repeat(3,minmax(0,1fr))}.std{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){.targets{grid-template-columns:1fr 1fr}.std{grid-template-columns:1fr}.agenda2 li{grid-template-columns:28px minmax(0,1fr)}.agenda2 .tx{grid-column:2}}
.cs.lead2{background:var(--ink);color:#fff;min-width:200px}.cs.lead2 span{color:#c9cfee}
.branch{display:grid;grid-template-columns:repeat(2,minmax(0,320px));justify-content:center;gap:24px;width:100%;padding-top:18px;border-top:3px solid var(--line);max-width:700px}
.team{background:var(--mist);border-radius:14px;padding:12px 14px;display:grid;gap:8px;text-align:center}
.team .tl b{display:block;font:800 18px/1.1 var(--fd)}.team .tl span{font-size:13.5px;color:var(--ink2)}
.team .ti{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;align-items:center}.team .ti small{width:100%;font-size:12.5px;color:var(--ink3)}
.csrow .others .cs:first-child{flex-basis:100%}
.std{grid-template-columns:repeat(3,minmax(0,1fr))}
.csline{display:flex;flex-wrap:wrap;gap:6px 22px;align-items:baseline;margin:0 0 22px;font-size:15.5px;color:var(--ink2)}
.csline .lab{font:700 12px/1 var(--fb);letter-spacing:.12em;text-transform:uppercase;color:var(--ink3)}.csline b{color:var(--ink);font-family:var(--fd)}
.otree{display:flex;flex-direction:column;align-items:center}
.o-node{display:grid;gap:2px;text-align:center;padding:10px 18px;border:1.5px solid var(--line);border-radius:12px;background:var(--paper);min-width:170px}
.o-node b{font:800 18px/1.1 var(--fd)}.o-node span{font-size:13.5px;color:var(--ink2)}.o-node em{font-style:normal;font-size:14.5px;font-weight:600;margin-top:6px;color:var(--ink)}
.o-node.top{background:var(--ink);border-color:var(--ink);color:#fff}.o-node.top span{color:#c9cfee}
.o-v{width:2px;height:20px;background:var(--ink3)}
.o-row{display:flex;gap:40px;justify-content:center;padding-top:20px;border-top:2px solid var(--ink3);position:relative}
.o-key{font-size:13px;color:var(--ink3);margin:12px 0 0}
.rcs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px}
.rc{border-top:3px solid var(--ink);padding-top:12px}
.rc h4{margin:0;display:grid;gap:2px}.rc h4 b{font:800 20px/1.1 var(--fd)}.rc h4 span{font-size:14px;font-weight:600;color:var(--blue)}
.rc p{margin:8px 0;font-size:14.5px;color:var(--ink2);line-height:1.4}
.rc ul{margin:0;padding-left:16px;display:grid;gap:4px;font-size:14.5px;line-height:1.35}
.rc .rc-esc{font-size:13.5px;font-weight:600;color:var(--ink);margin-top:10px}
@media (max-width:1100px){.rcs{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){.rcs{grid-template-columns:1fr}.o-row{gap:12px}.o-node{min-width:0}}
.o-row{display:flex;gap:56px;justify-content:center;padding-top:20px;border-top:2px solid var(--ink3)}
.o-col{display:flex;flex-direction:column;align-items:center}
.o-ints{display:flex;gap:10px;padding-top:14px;border-top:2px solid var(--line)}
.o-int{display:grid;gap:2px;text-align:center;padding:8px 14px;border-radius:10px;background:var(--bluewash);min-width:96px}
.o-int b{font:700 16px/1.1 var(--fd)}.o-int span{font-size:12.5px;color:var(--ink2)}
.dflow{display:grid;grid-template-columns:minmax(0,1fr) 36px minmax(0,1fr) 36px minmax(0,1fr);align-items:stretch}
.df-step{background:var(--paper);border:1.5px solid var(--line);border-radius:14px;padding:14px 16px;display:grid;gap:6px;align-content:start}
.df-step b{font:800 19px/1.1 var(--fd)}.df-step span{font-size:15px;line-height:1.4;color:var(--ink2)}
.df-step.last{background:var(--ink);border-color:var(--ink);color:#fff}.df-step.last span{color:#d3d8f3}
.df-arrow{display:grid;place-items:center;font:800 22px var(--fd);color:var(--ink3)}
@media (max-width:760px){.dflow{grid-template-columns:1fr}.df-arrow{transform:rotate(90deg);height:30px}.o-row{gap:16px}.o-int{min-width:0;padding:6px 10px}}
@media (max-width:1100px){.two{grid-template-columns:1fr;gap:28px}.targets{grid-template-columns:repeat(2,minmax(0,1fr))}.stats.big{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:22px}}
@media (max-width:900px){
 .wrap{grid-template-columns:minmax(0,1fr);gap:0;padding-top:0;overflow-x:clip}.side{min-width:0}
 .side{top:calc(env(safe-area-inset-top,0px) + var(--hh,71px));z-index:15;max-height:none;overflow:visible;margin-left:calc(-1*max(24px,env(safe-area-inset-left,0px)));margin-right:calc(-1*max(24px,env(safe-area-inset-right,0px)));background:rgba(245,245,249,.96);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
 .sidein{flex-direction:row;overflow-x:auto;scrollbar-width:none;padding:8px max(16px,env(safe-area-inset-left,0px));gap:4px}
 .subs,.side a.grid{display:none}.side a.top1{white-space:nowrap;padding:7px 12px 7px 7px;font-size:14px}
 .sec,.sub{scroll-margin-top:calc(var(--hh,71px) + 64px)}.sec:first-child{padding-top:20px}
 .hero{padding:22px 18px;border-radius:18px}.dream,.vals3{grid-template-columns:1fr}.dream>div+div{padding-left:0;border-left:0}
 .roles4,.branch{grid-template-columns:1fr}.cs.lead2{min-width:0}.leadrow{grid-template-columns:1fr}.leadrow .lead,.leadrow .ai{grid-column:auto;max-width:none}.org{padding:18px}.cs{min-width:0;flex:1 1 120px}}
@media (max-width:560px){.targets{grid-template-columns:1fr 1fr}.targets b{font-size:32px}.stats.big .stat b{font-size:32px}.stake .sr{grid-template-columns:1fr;gap:2px}}
"""
    js = """
const tops=[...document.querySelectorAll('.side a.top1')],subs=[...document.querySelectorAll('.subs a')],all=[...tops,...subs];
function mark(id){
 const el=document.getElementById(id);if(!el)return;const sec=el.closest('.sec');
 tops.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+sec.id));
 subs.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+id));
 const a=tops.find(a=>a.classList.contains('on'));if(a&&a.parentElement.scrollWidth>a.parentElement.clientWidth)a.parentElement.scrollTo({left:a.offsetLeft-16,behavior:'smooth'})}
const io=new IntersectionObserver(es=>{es.forEach(en=>{if(en.isIntersecting)mark(en.target.id)})},{rootMargin:'-25% 0px -65% 0px'});
document.querySelectorAll('.sec,.sub').forEach(s=>io.observe(s));
all.forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();const id=a.getAttribute('href').slice(1);document.getElementById(id).scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});history.replaceState(null,'','#'+id);mark(id)}));
mark(location.hash.slice(1)||'why');if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
"""
    sw = hqnav("playbook")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Playbook</title>{FONTS}<style>{BASE}{css}</style>{HQHEAD}<link rel="stylesheet" href="pb.css"></head><body>
<header class="top"><div><h1>Playbook</h1><div class="sub">Why we're here, what we expect of each other, and how we work</div></div>{sw}</header>
{body}
<script>(()=>{{const h=document.querySelector('header.top'),f=()=>document.documentElement.style.setProperty('--hh',h.offsetHeight+'px');f();addEventListener('resize',f)}})();{js}</script></body></html>"""


open(os.path.join(D, "playbook-a.html"), "w").write(view_final())
print("wrote final playbook-a.html (v2 options are in history/playbook-v2/)")
