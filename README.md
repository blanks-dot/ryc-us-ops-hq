# US Ops HQ

Run Your City's US Ops home: an overview page, the task grid, the playbook, the tracker and the chapter list.

| Page | File |
|---|---|
| Overview (start here: why we do this, how the tabs fit, where things live) | `index.html` |
| Playbook | `playbook-a.html` (also `playbook.html`) |
| Tasks (every task, by role and season) | `tasks.html` |
| Tracker | `tracker.html` |
| Chapters | `chapters.html` |

Plain static HTML, no build step. Live at https://blanks-dot.github.io/ryc-us-ops-hq/ (GitHub Pages, updates a minute after each push to `main`). Original version: https://us-ops-hq.vercel.app. **Working on it (people or agents): read `AGENTS.md`** for local live-reload setup and the PR flow.

`src/` has the data and the scripts that first generated the pages. jtan regenerates from them, so if you change the design in the HTML, say so in the PR and jtan will carry it back into the scripts.

Tracker and chapter edits made in the browser save only to that browser (localStorage) for now.
