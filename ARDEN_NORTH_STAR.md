# Arden Desktop — North Star

**Read this first** when starting any Arden or Consigliere session in Cursor.  
**Founder context:** `D:\dev\DAVE.md` · **Portfolio agent rules:** `D:\dev\AGENTS.md`  
**Emotional / ethical spine (Witness, covenant, listen mode):** `ARDEN_COVENANT.md` — **read before personal or intake work so context is not lost.**  
**Powered by Rémanence** · AI Integration and Consulting LLC  
**Last updated:** 2026-06-17 (Phase 6 Consigliere v1 + Covenant doc)

**Companion docs:** `ARDEN_PROJECT_OVERVIEW.md` (what exists on disk) · `BRITTANY_SHIP.md` (consumer ship) · `engine/` (code)

---

## One sentence

**Arden is a persona-locked personal companion that knows you through intentional intake — not a generic chatbot, not a memoir app, not an agent that runs loops.**

Chat is how it speaks. **Tactical knowledge is the product.**

---

## What we are building

| Layer | Role |
|-------|------|
| **Soul** | Persona, voice, local memory, structured facts about the person |
| **Brain** | Swappable inference — Venice (default consumer), Groq backup, Kobold local (Dave / Advanced) |
| **Intake** | StoryKeeper-*craft* questions — companion domains, not memoir chapters |
| **Chat** | Daily surface — streaming, sessions, remember/recall |
| **Sources** | **RAG** — chat with your documents (PDFs, bills, exports). Same brain as chat. |
| **Skills** (later) | Email draft, export, calendar glance — utilities, not the moat |

**Consigliere** (Dave personal, then business) uses the **same rail** — richer intake domains, stronger proactive care, optional hardware SKU for business. Not a fork.

---

## What this is NOT

Do not drift here:

- **Not NotebookLM / Open Notebook** — use Google’s product when you want Google’s product. **Not integrated into Arden.**
- **Not a memoir app merge** — no book deliverable from intake.
- **Not a coding agent** — not Cursor, not loops, not "go fix my repo."
- **Not generic setup** — name + API key alone is not the value. (Do not call intake **"onboarding"** on screen — it sounds like homework.)
- **Not auto-pilot** — no sending email, no sanctions, no medical advice without explicit user-stated facts and human judgment.
- **Not NURA Connect** — separate product, separate guardrails. Arden is personal desk; NURA is facility/mobile.

---

## The moat — tactical knowledge (SAM)

A great executive assistant knows **constraints**, not just tasks:

- Who matters (Mom, spouse, brother-in-law who supplies your cheese)
- What you must not do (triggers, jealousy, addiction history — **user stated**, never inferred)
- Dates that matter (anniversaries, appointments, med changes — **confirmed facts**)
- Routines (insulin, meetings, recovery)

**Intake produces structured facts + high-importance memories.**  
It does **not** produce a printed book.

Example (business / Consigliere): meeting at Hard Rock + known gambling history → **speak up before**, not spreadsheet trivia after.

Example (personal): "Did you take your insulin?" — only from **opt-in health facts**, not hallucination.

---

## Get-to-know-you intake (Phase 2 — the work ahead)

**Words matter:** Never label this **"onboarding"** in the UI. Use **"Help me know you"** / **"Get to know you"** / **"Continue getting to know you"**. Install gets you running; intake is optional depth you can always come back to.

### Three options at install (A · B · C)

User picks based on **time on hand** and **confidence in the app** — not a wall, not guilt.

| Option | Button copy (plain) | What happens |
|--------|---------------------|--------------|
| **A** | **Get started** / skip for now | App opens. Chat works. No intake. They can add knowledge later from chat or settings. |
| **B** | **Quick get-to-know-you** (~few minutes) | Speed-dating basics: birth dates, key people, a handful of tactical facts. Enough to feel personal. |
| **C** | **Help me know you** (save & continue) | **In-depth intake.** Saves progress; quit anytime; resume when time or trust allows. |

**Critical product rule — C includes B:** If they choose **C**, they automatically get everything **B** would cover first (brief layer), then depth. The user **never** picks B then C. They never see "step 1 of 2." One path: basics woven in, then go deep.

They may start at **A, B, or C** only — any entry point is valid.

### Confidence grows over time

- Someone on **A** may later tap **Quick get-to-know-you** or **Help me know you** when the app earns trust.
- Someone on **C** may quit mid-session — **partial knowledge is kept** — and finish later when they see what the companion offers (SAM moment).
- **Always in the UI:** a permanent, findable way to **continue getting to know you** (Settings + gentle nudge when knowledge is thin — not nagging on day one).

Nudge when thin (after they’ve used chat): *"I'm still light on a few things — a few minutes so I can show up better for you?"*

### Domains (craft these — ~4–8, not 11 memoir chapters)

Start set to spec:

1. **People** — who matters, relationships, loyalty constraints  
2. **Health & routines** — opt-in; meds, appointments, reminders (supportive, not clinical)  
3. **Dates & milestones** — grief, anniversaries, hard days  
4. **Triggers & recovery** — opt-in; places, patterns (Consigliere/business packs expand here)  
5. **Work & obligations** — schedule reality, not spreadsheets  
6. **Preferences** — how they want to be spoken to, what annoys them  

**Engine:** `ledger_core/interview` prompts + one-question flow + resume sessions.  
**Output:** structured fact schema + episodic memory — not narrative prose for a book.

### Brittany vs Dave vs Consigliere

| | Brittany (consumer) | Dave | Consigliere / business |
|---|---------------------|------|-------------------------|
| Ship bar | Install → chat + Venice works | Full lab | Same core + domain packs |
| Intake | Skippable; gentle depth | Full SAM | Triggers, meetings, accountability |
| Brain | Venice, Groq; Kobold hidden until local | Kobold when cooled | Cloud OK; hardware optional |
| Privacy pitch | Local soul + keys on PC | Same | Device-bound; less "privacy" marketing |

**Brittany v1 is shipped** (chat, memory, persona, portable exe). Get-to-know-you intake is **Phase 2 on top**, not a blocker to what shipped.

### Context deepening — life goes on (Phase 3b, future)

Intake is not the only way to learn. As the user lives in chat, the companion may **gently ask one follow-up** when a decision or decline is worth understanding — not to nag, but to know *why*, not just *what*.

**Example:** User declines a birthday party invitation. Storing *"declined party"* is weak. Storing *"avoids Chuck E. Cheese / noisy kid venues"* or *"conflict with that family"* or *"doesn't do public crowds"* makes future advice humane and accurate.

**Rules (non-negotiable):**

| Rule | Why |
|------|-----|
| **One question, not an interview** | Dig a little — don't interrogate |
| **Always skippable** | "Rather not say" / skip — no guilt, no repeat that session |
| **Confirm before storing** | *"Should I remember you prefer to skip kid-heavy venues?"* |
| **Never infer the reason** | Ask or skip; don't guess Chuck E. Cheese |
| **Opt-in tone** | Curious friend, not parole officer |
| **Tied to decisions & boundaries** | Invites, habits, avoids — not every chat turn |

This is how the companion becomes your **closest individual** over time — reasons and constraints, not a log of events.

---

## Trust — non-negotiable behavior

These are product rules, not model hope:

1. **Say "I don't know"** when a fact is not in intake or confirmed memory — never invent life details.
2. **No sycophantic correction** — if the user is right (or sarcastic), do not fabricate errors to please them.
3. **Confirm before storing** — *"Should I remember that you buy cheese from Carl?"*
4. **Separate lanes** — facts (database) · suggestions (labeled) · math/layout (show work or calculator).
5. **User-visible "What I know about you"** — edit, delete, export. Trust dies when the system pretends it listened (see Gemini song conflation — one betrayal = years lost).

**Prompt quality > model choice** — NURA Connect and StoryKeeper proved this. Arden intake questions are **baked in**, not improvised each session.

---

## Brains (keep the soul, change the engine)

```
SOUL (persona + tactical facts + sessions)  →  always local, always yours
BRAIN (Venice / Groq / Kobold)               →  dropdown, reload keys from .env
```

- Consumer default: **Venice** — good privacy/cost balance, not "fully encrypted."  
- Local Kobold: **Advanced → Local brain** when hardware allows — not required for Brittany.  
- Switching must work: `which brain` / status bar shows **active** backend, not just dropdown label.

---

---

## Sources — chat with your documents (RAG)

**One line:** Drop files → ask questions → answers from **your** files, using whatever brain is selected.

**Examples:** PDF phone bill → *"When is electric due and how much?"* Email export → *"What did they say about the deadline?"* Manuscript → *"Is Agawa Canyon in chapter 3?"*

**Uses:** Active brain (Venice / Groq / Kobold). RAG retrieves chunks; LLM answers with snippets/citations.

**Not in scope:** NotebookLM, Open Notebook, podcasts, slides, SurrealDB, second-server research stack.

**Brittany:** Local files under user data dir (e.g. `%LOCALAPPDATA%\Arden\sources\` — path TBD in build).

**Honest scope:** Ingest PDF/txt → chunk → embed → retrieve → prompt with context. Not trivial, but **much smaller** than Open Notebook.

---

## Roadmap order (stay true)

| Phase | Focus | Status |
|-------|--------|--------|
| **1** | Brittany chat ship — Venice, memory, persona, portable install | **Done** |
| **2** | Get-to-know-you intake (A/B/C) + structured facts + **"What I know about you"** + finish-later in UI | **Shipped v1** |
| **3** | Proactive surface — dates, reminders, gentle check-ins from **stored facts only** | **Shipped v1** |
| **3b** | **Context deepening** — optional "why?" after decisions (skippable); stores reasons, not just events | **Shipped v1** |
| **4** | **Sources** — RAG chat over user files (PDF, bills, email exports). Same brain dropdown (Venice/Groq/Kobold). | **Shipped v1** |
| **5** | Utilities — export (.docx), email draft to clipboard, calendar read-only | **Shipped v1** |
| **6** | Consigliere business edition — domain packs, briefing, tasks, accountability | **Shipped v1** (hardware SKU doc only) |

**Scrapped:** Open Notebook embed, native stack launcher, `open-notebook/` integration path for Arden ship. MIT credit stays in legal notices only if code remains in repo; **not a product feature.**

Do **not** jump to email OAuth or agent loops before intake + facts exist.

---

## Anti-patterns (when you feel us drifting)

- Merging StoryKeeper app into Arden  
- Building NotebookLM / Open Notebook inside Arden  
- Generic 2-minute setup as the whole product  
- UI copy that says **"onboarding"** instead of **help me know you**
- Inferring addiction, meds, relationships, or **why someone skipped a party** from chat vibe  
- Auto-sending email or auto-violating anything  
- Spreadsheets-as-assistant (anyone can crunch CSVs; nobody knows the person)  
- Overclaiming geofence/verification (graded signal + human-in-the-loop — borrow language from NURA court work when relevant)

---

## Cursor session ritual

When opening Arden work:

```text
Read @D:\dev\arden\ARDEN_NORTH_STAR.md — stay true to vision.
Then @ARDEN_PROJECT_OVERVIEW.md for disk truth.
Task: [one thing]. Do not redo: [list].
```

When Dave drifts topic — that's fine. Pull back with: *"Current task: Phase 2 intake domain X."*

---

## The line we keep repeating

> **StoryKeeper proved the questions. NURA proved the prompts. Arden/Consigliere uses the same hands — different chapters. Get-to-know-you intake is the product; chat is how it shows up for you. Install first — A, B, or C — always a path back to finish.**

---

*If this doc conflicts with a old plan that says "StoryKeeper merge — out of scope," **this doc wins.** That meant don't merge the memoir app. It did **not** mean don't use interview craft for companion intake.*
