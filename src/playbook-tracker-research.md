---
title: US Ops tracker research
type: research
created: 2026-11-23
tags: [paint, ryc, us-ops, tracker]
related:
  - "[[Workbench/paint/2026-11-23-us-ops-process-flow/2026-11-23-us-ops-process-flow]]"
---

# How a small, part-time, distributed team should track work

Question: how should a team of about 8 to 12 part-time volunteers (one lead, coordinators and interns, spread across schools and time zones) track priorities and tasks, and run a weekly async update plus a 30-minute meeting?

Caveat: most sources are practitioner and vendor blogs, not formal studies. They are a starting point, not proof.

## What the existing sheet does ("RYC team priorities", read 2026-11-23, read only)

- **Tabs:** Team Dashboard, Team Priorities, Team, plus Marketing and International tabs.
- **Team Priorities columns:** Team member (with role), Category, Task, Due date, Days left, Status, Notes.
  - Status values: In progress, Complete, Incomplete, Deprioritized.
  - "ongoing; weekly" is used as a due date.
- **Team Dashboard:** the vision, the North Star, impact status, and "Bi-weekly Priorities", which counts completed items and overdue days per person.
- **What works:**
  - one row per task with one owner;
  - due dates with an automatic days-left count;
  - dated running notes;
  - one place everyone already knows.
- **What doesn't:**
  - Category is free text and isn't tied to a few team priorities.
  - Recurring work and one-off tasks are mixed together.
  - Finished rows pile up.
  - There is no "blocked" status and no "what's next".
  - The weekly check-in lives somewhere else.
  - A per-person overdue count reads like a scoreboard.

## Principles

1. **A few team priorities, each with one owner.** Keep 3 to 5 outcomes for the season, and give every priority and every task exactly one directly responsible person, even when many people help. Shared ownership slows follow-through, and over time the "organized one" becomes a single point of failure. ([DRI doc](https://docs.google.com/document/d/1I4jBy1XryEdknFoDCMUY93PEn0rR-oOOx6yiLSiaa38/export?format=pdf), [One task, one assignee](https://productive.io/blog/one-task-one-assignee-apple-method/), [Shared ownership slows progress](https://aligntoday.com/blog/shared-ownership-slows-progress/), [Todoist: unclear accountability](https://www.todoist.com/inspiration/team-accountability))
2. **Async status, live decisions.** Collect done / doing / blocked in writing before the meeting so the 30 minutes go to blockers and decisions, not status. This matters most for people with classes and jobs on different schedules. ([Basecamp check-ins](https://basecamp.com/learn/beyond-the-basics/automatic-check-ins), [G2: async stand-ups](https://learn.g2.com/asynchronous-standup-meetings), [Built In](https://builtin.com/operations/replace-daily-stand-ups))
3. **Ask on a fixed schedule, with the same three questions.** For example, "what got done, what's next, what's blocked" every week at the same time. Answers stay in one searchable place. ([Basecamp check-ins](https://basecamp.com/learn/beyond-the-basics/automatic-check-ins), [Loom/Atlassian weekly updates](https://www.atlassian.com/blog/loom/weekly-updates))
4. **Make the updates get read: the meeting is built from them.** The known failure of async updates is that nobody reads them. The fix is to make the check-ins the agenda, so skipping one is visible in the meeting itself. ([Honeycomb: stand-ups are dead](https://www.honeycomb.io/blog/standup-meetings-are-dead), [Anti-patterns of distributed stand-ups](https://medium.com/catch-blog/5-anti-patterns-of-distributed-team-stand-ups-af259886716c))
5. **Blockers first and in plain sight.** A blocked item should look different and should jump to the meeting's blocker slot automatically, so help arrives the same week. ([G2](https://learn.g2.com/asynchronous-standup-meetings), [Parabol](https://www.parabol.co/?p=8059))
6. **Specific, short updates.** "Sent the form reminder to the remaining chapters" beats "worked on forms". ([ClickUp: async stand-ups](https://clickup.com/blog/async-standup/))
7. **Show progress toward something that matters.** Volunteers stay when they can see their work counts. Tie tasks to the priorities and celebrate what got done; don't rank people. ([MSU Extension](https://www.canr.msu.edu/news/why-strong-volunteer-management-matters), [U.S. Chamber](https://www.uschamber.com/chambers-of-commerce/empower-volunteers-to-lead-and-drive-organizational-success), [Journal of Accountancy](https://www.journalofaccountancy.com/news/2020/jan/how-to-improve-nonprofit-volunteer-retention-22493.html))
8. **See what's stuck, not just what's late.** Basecamp's hill charts separate "still figuring it out" from "just doing it". A simple Not started / In progress / Blocked / Done status gives a lighter version of the same thing. ([Hill Charts](https://basecamp.com/hill-charts))
9. **Separate recurring duties from projects.** "Answer us-ops@" is a standing duty, not a task that is ever done. Keep it in its own short list so the task list only holds things that can finish. (Inference from the sheet's "ongoing; weekly" rows; no source.)

## How the three mockups use this

- **A, Weekly check-in:** principles 2 to 6. Each person's done / now / blocked card builds the meeting agenda.
- **B, Priorities:** principles 1, 7, 8 and 9. This is closest to the existing sheet, regrouped under 4 priorities.
- **C, Task list:** principles 1, 4, 5 and 9. One list where changing a task's status also writes the agenda, so nobody posts twice.
