"""Shared top nav for every US Ops HQ page. Same order and look on all five pages (styles in hq.css)."""
HOME_SVG = ('<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M3 9.2 10 3.5l7 5.7V16a1 1 0 0 1-1 1h-3.5v-4.5h-5V17H4a1 1 0 0 1-1-1z"/></svg>')
PAGES = [("./", "Overview", "home"), ("playbook-a.html", "Playbook", "playbook"), ("tasks.html", "Tasks", "tasks"),
         ("tracker.html", "Tracker", "tracker"), ("chapters.html", "Chapters", "chapters")]
HEAD = '<link rel="icon" href="data:,"><link rel="stylesheet" href="hq.css"><script src="hq.js" defer></script>'


def hqnav(cur):
    out = []
    for href, label, key in PAGES:
        cls = " ".join(c for c in ("home" if key == "home" else "", "on" if key == cur else "") if c)
        inner = f"{HOME_SVG}<span>{label}</span>" if key == "home" else label
        out.append(f'<a{f" class=\"{cls}\"" if cls else ""} href="{href}"' + (' aria-current="page"' if key == cur else "") + f">{inner}</a>")
    return '<nav class="hqnav" aria-label="US Ops HQ pages">' + "".join(out) + "</nav>"
