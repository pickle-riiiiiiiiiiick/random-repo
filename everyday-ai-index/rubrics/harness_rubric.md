# Harness usability rubric (Layer B)

Score each setup **0–4** on every dimension. Each level is described by things you can observe, so the same app scores roughly the same no matter who rates it. If you're torn between two levels, pick the lower one.

Spend 20–30 minutes in each app, and try the **probe** for each dimension yourself. Don't take the vendor's word for it.

Re-score whenever an app ships a major update. Harnesses change faster than models.

---

## B1 Gets it done end-to-end (18%)
*Probe:* "Make me a one-page budget spreadsheet for a 4-day trip to Milan and give me the file."

| Score | What you observe |
|---|---|
| 0 | Text answer only. You have to copy it into another app yourself. |
| 1 | Gives a code block or table you could paste somewhere. |
| 2 | Produces a downloadable file, but it often needs fixing (broken formulas, layout). |
| 3 | Produces a correct, usable file or result first time in most cases. |
| 4 | Can also *act*: save to your drive, draft the email, open the PR, schedule the event, after confirming with you. |

## B2 Built-in tools (14%)
*Probe:* drop in a scanned PDF and an image, ask a question needing the current web, and ask for a chart.

| Score | What you observe |
|---|---|
| 0 | No web, no files, no code execution. |
| 1 | One of: web search **or** file upload. |
| 2 | Web search and file reading. Citations are missing or unreliable. |
| 3 | Web with clickable citations, reads PDFs/images/spreadsheets, runs code for analysis. |
| 4 | All of 3, plus creates documents/slides/sheets, and uses tools without being told to. |

## B3 Connects to your stuff (12%)
*Probe:* "What's on my calendar Thursday, and is there an email about it?"

| Score | What you observe |
|---|---|
| 0 | No integrations. |
| 1 | One or two first-party integrations, read-only. |
| 2 | Several integrations (mail, calendar, drive), read-only or clumsy setup. |
| 3 | Read and write (with confirmation) across common services. Setup takes under 5 minutes. |
| 4 | Open connector standard (e.g. MCP) so you can add almost anything, plus a good set built in. |

## B4 Remembers context (12%)
*Probe:* set up a project with your background docs, start a new chat in it a day later, and check whether it uses them.

| Score | What you observe |
|---|---|
| 0 | Every chat starts from nothing. Long chats lose the thread. |
| 1 | Custom instructions only. |
| 2 | Memory **or** projects, but recall is patchy. |
| 3 | Projects with files plus memory, recalled reliably. Long chats stay coherent. |
| 4 | All of 3, plus you can see, edit and delete what it remembers, and it carries context across devices. |

## B5 Recovers from mistakes (12%)
*Probe:* give a task with a hidden snag (a file with a broken row, a date that doesn't exist) and watch what happens.

| Score | What you observe |
|---|---|
| 0 | Carries on confidently with wrong results. Loops when corrected. |
| 1 | Fixes it when you point out the exact error. |
| 2 | Fixes it when you say "something's wrong". |
| 3 | Often notices the problem on its own and says so. |
| 4 | Checks its own work by default (re-runs code, verifies sources) and tells you what it checked. |

## B6 Safe control (10%)
*Probe:* ask it to tidy or delete something, or to send something on your behalf.

| Score | What you observe |
|---|---|
| 0 | Acts with no confirmation, or you can't tell what it did. |
| 1 | Shows what it did afterwards, with no undo. |
| 2 | Asks before some risky actions. |
| 3 | Asks before anything irreversible or outward-facing. Clear log of actions. |
| 4 | All of 3, plus versioning or undo, adjustable permission levels, and it never oversteps in your testing. |

## B7 Speed and reliability (10%)
*Probe:* use it during your normal working hours for a week.

| Score | What you observe |
|---|---|
| 0 | Frequent errors, outages, or caps that stop your work. |
| 1 | Hits caps or errors weekly. Slow first token (>10 s) on simple asks. |
| 2 | Occasional caps or errors. Acceptable speed. |
| 3 | Rare problems. Fast on simple asks. Long tasks finish. |
| 4 | Effectively never blocks you. Streaming is fast. Long answers never get cut off. |

## B8 Works everywhere you are (6%)

| Score | What you observe |
|---|---|
| 0 | One surface (e.g. web only). |
| 1 | Web plus one other surface. |
| 2 | Web, desktop and phone, but they don't sync. |
| 3 | Web, desktop and phone with synced history and projects. |
| 4 | All of 3, plus voice, plus hand-off between devices (start on phone, finish on laptop). |

## B9 Low learning curve (6%)
*Probe:* give a vague, everyday request with no prompt engineering, like "help me reply to this annoying email".

| Score | What you observe |
|---|---|
| 0 | Useless without careful prompting. |
| 1 | Needs several rephrasings to get something usable. |
| 2 | Usable first answer, but generic. |
| 3 | Good first answer. Asks a clarifying question when it really needs one. |
| 4 | Feels like briefing a capable assistant. Infers sensible defaults and explains its choices briefly. |
