# Instructions for an agent working on US Ops HQ

This repo is Run Your City's US Ops HQ: five static pages, no build step.

| Page | File |
|---|---|
| Overview (start here: why we do this, how the tabs fit, where things live) | `index.html` |
| Playbook | `playbook-a.html` (keep `playbook.html` an identical copy) |
| Tasks (every task, by role and season) | `tasks.html` |
| Tracker | `tracker.html` |
| Chapters | `chapters.html` |

The live site is https://us-ops-hq.vercel.app. Vercel deploys `main` automatically.

## 1. Run it locally with live reload

```bash
git clone https://github.com/josheiland/us-ops-hq.git
cd us-ops-hq
npx --yes live-server --port=5173 --no-browser
```

Open http://localhost:5173. Every saved edit reloads the browser.
No Node? `python3 -m http.server 5173` also works, but you have to refresh by hand.

## 2. Make changes on a branch

```bash
git checkout -b mary/<short-topic>
# edit the HTML/CSS, check it at localhost:5173
git add -A && git commit -m "<what changed>"
git push -u origin mary/<short-topic>
gh pr create --fill
```

**Always open a pull request. Never push to `main`.** Vercel only deploys commits from Josh's account, so Josh (or his agent, jtan) merges the PR and the merge goes live within a minute. Each PR also gets a Vercel preview, but the preview link only opens for Josh's Vercel account.

## 3. House rules

- **RYC brand.**
  - Navy `#091f77` for text and structure, pink `#e03870` for one accent per view, light gray `#dbdae5` / `#f0f0f5` for surfaces.
  - Bricolage Grotesque (700/800) for headings, DM Sans for body.
  - No Poppins.
- **No em dashes, no middle dots (·), no diamond bullets.** No trailing periods on one-phrase labels.
- **Don't change the wording without asking.** It was finalized with the team on 11/23. Visual and layout changes are fine.
- **People.**
  - Names appear only in the org chart, role cards, tracker and chapters.
  - No blame or performance notes anywhere.
- **Check before every PR:** desktop (about 1500x980) and phone (about 400 wide). There should be no sideways scroll, no console errors, and the sticky header must stay readable.
- **Keep the top switcher the same on all five pages:** Overview | Playbook | Tasks | Tracker | Chapters. It is built by `src/hqnav.py` and styled by `hq.css`.
- **Design system.** `hq.css` holds the shared rules (nav, dropdowns, labels as plain text); `pb.css` holds the Playbook's design pass. Only things you can click look like buttons; labels, names and statuses are plain text. Cards sit on soft shadows, not outlines.
- **Photos** live in `img/`, cropped close on the kids. `banner-tracker.jpg` and `banner-chapters.jpg` are the photo banners on those pages. Every photo on the site is used once. `hq.js` sizes dropdowns so their arrow sits right after the text. Tab previews on the overview are in `img/tabs/`; retake them if a tab changes a lot.

## 4. How the pages were generated

`src/` has the data (`data.json`, `playbook.json`, `chapters-src/`) and the Python scripts that first rendered the pages. jtan may regenerate a page from them. If your PR changes the design directly in the HTML, say so in the PR description, so jtan carries it into the scripts instead of overwriting it.

Tracker and chapter edits made in the browser save to that browser only (localStorage). There's no shared database yet.
