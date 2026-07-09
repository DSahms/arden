# Arden Desktop — Complete Project Overview

**AI Integration and Consulting LLC · Powered by Rémanence**  
**Tagline:** *Keep the soul. Change the brain.*  
**Last updated:** June 2026  
**Status:** Consumer edition shippable; Sources/RAG tab replaces Open Notebook (scrapped June 2026)  
**Vision (read first):** [`ARDEN_NORTH_STAR.md`](ARDEN_NORTH_STAR.md)

---

## Table of contents

1. [What this product is](#what-this-product-is)
2. [How it fits in your product family](#how-it-fits-in-your-product-family)
3. [The core idea — soul vs brain](#the-core-idea--soul-vs-brain)
4. [Visual identity and “screenshots in words”](#visual-identity-and-screenshots-in-words)
5. [Architecture — how everything connects](#architecture--how-everything-connects)
6. [What works today (June 2026)](#what-works-today-june-2026)
7. [The chat experience — feature by feature](#the-chat-experience--feature-by-feature)
8. [Memory and personality (the “soul”)](#memory-and-personality-the-soul)
9. [Brains — swap without reinstalling](#brains--swap-without-reinstalling)
10. [Sources — document RAG](#sources--document-rag)
11. [Voice, mic, and accessibility](#voice-mic-and-accessibility)
12. [Onboarding and settings](#onboarding-and-settings)
13. [Packaging, install, and ship paths](#packaging-install-and-ship-paths)
14. [Quality assurance — the ship loop](#quality-assurance--the-ship-loop)
15. [Data on disk — where everything lives](#data-on-disk--where-everything-lives)
16. [Dave edition vs Brittany (consumer) edition](#dave-edition-vs-brittany-consumer-edition)
17. [Roadmap — what comes next](#roadmap--what-comes-next)
18. [Honest gaps vs NURA Connect](#honest-gaps-vs-nura-connect)
19. [Key file map](#key-file-map)

---

## What this product is

**Arden Desktop** is a personal AI workstation for your desk — not a facility app, not a mobile journey, not a chatbot in a browser tab you forget.

It is one forest-green window that combines:

| Layer | What it does |
|-------|----------------|
| **Companion chat** | Talk to an AI that remembers you, has a name and personality you choose, and replies with live streaming text |
| **Swappable brains** | Same companion, different inference engine — local Kobold on port 5001, Venice cloud, Groq cloud, and more on Dave’s build |
| **Local memory** | Conversations and facts stored on *your* machine under `%LOCALAPPDATA%\Arden\` |
| **Sources** | Second tab — chat with your PDFs/bills/exports (RAG; wiring in progress) |
| **Sessions** | Multiple named chats in the sidebar, persisted across restarts |

The product name on the box is **Arden Desktop**. The companion’s name defaults to **Arden** but the user can rename it to anything during onboarding or in Settings — Sam, Ada, Rhema, whatever.

Corporate line everywhere: **Powered by Rémanence**.

---

## How it fits in your product family

| Product | Role | Relationship to Arden |
|---------|------|------------------------|
| **NURA Connect** | Facility/mobile wellness app | **Separate.** Do not merge code or guardrails. NURA is the gold standard for guided mobile onboarding; Arden is the personal desk. |
| **NURA tablet demo** (`nura.html`) | Pitch / facility shell | Inspiration for polish; not the same codebase |
| **StoryKeeper** | Autobiography / book vertical | Separate Flutter app |
| **Daily Bread** | Offline scripture app | Separate; no shared engine |
| **PersonaLock Desktop** | Legacy brand | Deprecated; engine migrated into `D:\dev\Arden\engine\` — Chroma + hash embeddings for **memory recall** |

**Policy split (locked):**

- **NURA Connect** — guardrails required (facility/public).
- **Arden Desktop** — personal workstation; no NURA red-team rules ported here.

---

## The core idea — soul vs brain

This is the product’s signature feature and the reason the Brain dropdown exists.

```
┌─────────────────────────────────────────────────────────┐
│  SOUL (persistent on your PC)                           │
│  · Persona / personality (warmth, humor, rules)         │
│  · Memory vault (SQLite + optional Chroma)              │
│  · Session history                                      │
│  · Your name, companion name                            │
│  · Edition voice (consumer = plain friend)              │
├─────────────────────────────────────────────────────────┤
│  BRAIN (swappable per message or per session)           │
│  · kobold  → KoboldCpp localhost:5001 (Dave, $0)        │
│  · venice  → Venice.ai Llama 3.3 70B (privacy cloud)    │
│  · groq    → Groq free tier (backup cloud)              │
│  · claude, ollama, lm_studio → Dave/dev builds          │
└─────────────────────────────────────────────────────────┘
```

**Keep the soul. Change the brain.**  
A user never goes back into setup to switch APIs. They pick from the dropdown next to “Speak replies” and send. Same forest, same memories, different inference.

---

## Visual identity and “screenshots in words”

Arden’s look is **forest sanctuary** — sampled from splash image #4 (Dave’s chosen reference). It is deliberately distinct from NURA’s mobile gilt aesthetic while sharing Rémanence DNA.

### Color palette (from `arden_theme.py`)

| Name | Hex | Use |
|------|-----|-----|
| Forest Deep | `#182d25` | Main background, window chrome |
| Forest Sidebar | `#1a3228` | Left session rail |
| Forest Panel | `#243d32` | Chat header, cards, dialogs |
| Forest Elevated | `#2d4a3a` | Buttons, hover states |
| Gilt | `#dbb874` | Titles, accents, rules, tree glyph |
| Cream | `#d4d0bc` | Primary readable text |
| Cream Soft | `#b8c4bc` | Taglines, muted labels |

### Typography

- **UI:** Segoe UI (Windows-native, clean)
- **Display titles:** Segoe UI 20pt bold, gilt
- **Quotes:** Georgia italic — *“Where nothing is forgotten, and nothing leaves the forest.”*

### Splash screen (`splash.py` + `assets/splash.png`)

On launch you see:

1. **Full-bleed forest image** (splash #4) when the asset is bundled, OR a painted fallback with forest bands, firefly dots, and a neural-tree glyph
2. **ARDEN DESKTOP** in gilt
3. Tagline: *All remembered. Deeply encrypted. Never-leaving.*
4. Serif quote centered on the image
5. Gilt progress bar — “LOADING . . .”
6. Window icon derived from splash art for taskbar consistency

### Main window layout (1120×780, resizable)

Picture this as the “screenshot” of the shipped app:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Sidebar 220px]  │  [Main panel]                                         │
│                  │                                                        │
│  🌲 Neural tree  │  Arden          Brain: venice · Memory: sqlite        │
│  ARDEN           │  ─────────────────────────────────────────────────    │
│  tagline         │  [ Chat ]  [ Sources ]                               │
│  ─── gilt rule   │  ─────────────────────────────────────────────────    │
│  + New chat      │                                                        │
│  Sources         │  ┌────────────────────────────────────────────────┐   │
│  Settings        │  │  Chat transcript (read-only, color-tagged)      │   │
│                  │  │  You                                            │   │
│  SESSIONS        │  │  hello                                          │   │
│  · Chat 3        │  │                                                 │   │
│  · Chat 2        │  │  Arden                                          │   │
│  · This convo    │  │  Hey Dave. What's on your mind?                 │   │
│                  │  └────────────────────────────────────────────────┘   │
│  Keep the soul.  │  ☐ Speak replies    Brain: [kobold ▼]                  │
│  Change the brain│  ─────────────────────────────────────────────────    │
│  Powered by      │  [Mic]  [ Type your message here............... ] [Send]│
│  Rémanence       │                                                        │
└──────────────────────────────────────────────────────────────────────────┘
```

### Decorative elements (`arden_decor.py`)

- **Neural-network tree** — sidebar and splash; gilt nodes on forest canvas
- **Gold horizontal rules** — section separators
- **Status pulse** — “Arden is thinking…” with animated dots while waiting for inference
- **Sanctuary input frame** — inset panel around the message bar (forest card treatment)

### Dialogs (first-run + Settings)

Forest-themed modals — not stock Windows gray boxes:

- Dark forest panel body, gilt field labels
- Entries on sidebar-colored inputs with gilt focus border
- “Begin” / “Save” accent buttons
- Same tagline and quote as splash for brand continuity

---

## Architecture — how everything connects

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Arden Desktop (single Tk window)                     │
│  modules/gui/chat_app.py — ChatApp shell                                │
├────────────────────────────┬────────────────────────────────────────────┤
│  CHAT TAB                  │  SOURCES TAB                                │
│  · Streaming transcript    │  · Add PDFs / txt (RAG — wiring in progress)  │
│  · Brain dropdown          │  · Ask questions grounded in your files       │
│  · Mic / Send / Escape     │  · Same brain as chat                         │
│  · Session sidebar         │                                               │
├────────────────────────────┴────────────────────────────────────────────┤
│  PlainAssistant (modules/base_assistant.py)                             │
│  · PersonalityEngine ← assets/persona.json + profiles/                  │
│  · MemoryManager ← SQLite (consumer) or Neo4j (dev) + Chroma optional   │
│  · BrainFactory ← venice | groq | kobold | claude | ollama | …         │
│  · TaskManager, MorningBriefing (business edition hooks)                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Consumer bootstrap (modules/consumer_bootstrap.py)                     │
│  · %LOCALAPPDATA%\Arden\ — config, .env, sessions, memory DB, chroma    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Design principle:** Separate processes, one interface. Connect the dots; do not merge git repos.

---

## What works today (June 2026)

### Fully working (verified by acceptance harness)

| Capability | Notes |
|------------|-------|
| Forest-themed GUI shell | Chat + Sources tabs, sidebar, gilt chrome |
| Live token streaming | Venice, Groq, Kobold SSE — words appear as generated |
| Brain dropdown | **kobold · venice · groq** (consumer); auto-prioritizes kobold when :5001 is up |
| Input bar, Send, Mic button | Fixed and acceptance-tested |
| Escape cancels “thinking” | Unlocks UI if wait hangs |
| Session persistence | `sessions.json`, double-click rename |
| First-run wizard | Companion name, your name, Venice/Groq keys |
| Settings | Rename companion + your name; update API keys |
| SQLite memory | Background-thread safe; hash embeddings (no Ollama required on consumer) |
| Personality / consumer edition | Plain-spoken friend rules from `persona.json` |
| Splash + window icon | Image or canvas fallback |
| Portable zip + Install-Arden.ps1 | Brittany path — no Docker, no terminal |
| Built exe smoke + acceptance | `Arden.exe smoke-test` / `acceptance-test` exit 0 |
| Dave local Kobold | `http://127.0.0.1:5001/v1` — probed at startup |

### Working with caveats

| Capability | Caveat |
|------------|--------|
| Groq brain | Key may be invalid on a given machine; Venice or kobold recommended |
| Speak replies | Uses local `pyttsx3` TTS when enabled; can slow tests |
| Mic | Google Web Speech API — needs internet; push-to-talk |
| Chroma semantic recall | Optional; consumer uses lightweight hash embedder |
| Neo4j memory | Dave dev stack only; consumer uses SQLite |

### Recently fixed (ship loop June 2026)

- Streaming UI crash (`bad text index "stream"`) — left app stuck on “thinking”
- Input bar never rendering — code was inside wrong function
- Echo filter blocking repeated “hello” after failed attempts
- Brain/API key precedence and post-settings reconnect

---

## The chat experience — feature by feature

### Sending messages

1. Type in the bottom **sanctuary input** (not the transcript — transcript is read-only)
2. **Enter** or **Send**
3. Status line pulses: “Arden is thinking…”
4. Reply **streams** token-by-token in the transcript
5. Input unlocks when done; **Escape** cancels early

### Chat transcript

- **You** — user name tag + body (distinct color tags)
- **Arden** (or custom companion name) — assistant tag + streamed body
- Scroll follows new text
- Clicking transcript focuses input bar (when not busy)

### Sessions sidebar

- **+ New chat** — fresh thread, clears assistant conversation history for that session, shows greeting
- **List of sessions** — persisted titles
- **Double-click** session title to rename inline
- Switching sessions reloads transcript + syncs `conversation_history` for memory context

### Tabs

- **Chat** — primary companion (always default after send)
- **Notebooks** — research layer (see below)

### Greeting

Consumer edition greeting from persona: *“Hey! Good to see you. What's on your mind?”* — personalized to *“Hey {your name}…”* when your name is set in onboarding/Settings.

---

## Memory and personality (the “soul”)

### Personality engine

- Profile: `engine/assets/persona.json` + `engine/profiles/`
- **Traits:** warmth, directness, humor, formality, empathy, patience (0–1 scales)
- **Edition overrides:** `consumer`, `business`, `wellness` — different voice and rules
- **Identity contract:** Never claims to be GPT/Claude; always identifies as your chosen companion name on Arden Desktop — Powered by Rémanence
- **User identity:** `apply_user_identity()` rewrites system prompt with your name and companion name

### Memory vault

| Backend | Who uses it | Storage |
|---------|-------------|---------|
| **SQLite** | Consumer / Brittany | `%LOCALAPPDATA%\Arden\consumer_memory.db` |
| **Chroma** | Optional semantic search | `%LOCALAPPDATA%\Arden\chroma\` |
| **Neo4j** | Dave full dev stack | Docker bolt://localhost:7687 |

**What gets remembered:**

- Full user+assistant exchanges (importance ~0.6)
- “Remember this” command — marks last exchange high importance
- “Forget this” — removes recent memory
- “What do you remember about X?” — direct recall query
- Background writes — do not block GUI thread

**Embeddings (consumer):** Hash-based lightweight embedder — no Ollama required for Brittany clean install.

---

## Brains — swap without reinstalling

### Consumer dropdown (bottom bar)

| Brain | Type | Requires | Speed | Privacy |
|-------|------|----------|-------|---------|
| **kobold** | Local | KoboldCpp on :5001 | Slower, always there (Dave) | 100% local |
| **venice** | Cloud | API key in Settings | Fast | Privacy-oriented cloud |
| **groq** | Cloud | API key in Settings | Fast | Groq infrastructure |

Switching brains mid-chat appends a line: *“Switched to {brain}. Same soul — different brain.”*

### All backends in codebase (`brain_factory.py`)

**Built-in:** kobold, lm_studio, ollama, groq  
**Optional (if packages installed):** claude, openai, venice, gemini

### Fallback chain (consumer config)

`kobold → venice → groq` — first available at startup wins (Dave with Kobold running starts local).

### Inference features

- Streaming SSE for all three consumer brains
- 120s worker timeout, 60s API timeout (Venice/Groq)
- Friendly in-chat errors (invalid key, Kobold not running, timeout)
- Voice echo guard — only ignores mic input that matches last **assistant** reply (not repeated user typing)

---

## Sources — document RAG

**Purpose:** NotebookLM-style *doc chat* without external stacks — upload PDFs/txt, ask questions, answers grounded in your files.

**Status (June 2026):** Tab renamed **Sources**; placeholder UI in `sources_panel.py`. Open Notebook integration **removed**.

**Already on disk from PersonaLock → Arden:**

- `ChromaStore` + `MemoryManager` — `%LOCALAPPDATA%\Arden\chroma\`
- Hash embedder on consumer (no Ollama required); Ollama optional on Dave
- Collection today: **`memories`** (chat remember/recall)

**Still to build (~days, not weeks):**

- Second Chroma collection (or namespace) for **documents**
- PDF/txt ingest + chunk
- Sources chat UI wired to same brain dropdown as Chat
- Snippet citations in answers

**Not in scope:** NotebookLM, Open Notebook, podcasts, slides, SurrealDB, WebView2 embed, second server.

---

## Voice, mic, and accessibility

| Feature | Implementation | Default |
|---------|----------------|---------|
| **Speak replies** | `pyttsx3` local TTS via `voice_io.py` | Off unless config enables |
| **Mic** | `speech_recognition` + Google Web Speech | Push-to-talk; fills input bar |
| **Escape** | Cancels thinking state | Always bound |

Voice is optional — Brittany can use type-only with zero setup.

---

## Onboarding and settings

### First run (`first_run.py` — shown once)

Marker file: `%LOCALAPPDATA%\Arden\.first_run_done`

Collects:

1. **Assistant name** (default: Arden — user can type anything)
2. **What should they call you?**
3. **Venice API key** (recommended)
4. **Groq API key** (optional backup)

Forest-themed wizard — not system dialogs.

### Settings (sidebar, any time)

- Assistant name (rename companion)
- Your name
- Venice + Groq API keys
- Note: **Brain** is chosen in Chat tab dropdown, not Settings

### API key storage

`%LOCALAPPDATA%\Arden\.env` — never committed to git; loaded on every bootstrap.

---

## Packaging, install, and ship paths

### Dave development launch

```powershell
D:\dev\Arden\engine\Arden.bat
```

Sets `PERSONALOCK_EDITION=consumer`, runs `python main_gui_assistant.py chat`.

### Build consumer exe

```powershell
cd D:\dev\Arden\engine
.\scripts\build_arden_consumer.ps1
# Output: dist\Arden\Arden.exe
```

PyInstaller spec: `packaging/arden.spec` — bundles Chroma, wryview, Pillow, forest GUI modules, consumer config template.

### Brittany portable package

```powershell
.\scripts\package_for_brittany.ps1
# Output: release\Arden-Portable.zip
```

Zip contains:

- `Arden.exe` + `_internal` runtime
- `Install-Arden.ps1` — copies to `%LOCALAPPDATA%\Arden\App\`, desktop shortcut
- `Uninstall-Arden.ps1`
- `README-FOR-BRITTANY.txt`
- `THIRD_PARTY_NOTICES.txt`

### Install flow (Brittany)

1. Unzip `Arden-Portable.zip`
2. Double-click `Install-Arden.ps1`
3. Desktop shortcut **Arden**
4. First run wizard → name + API key
5. Chat

No Docker. No Neo4j. No command line after install.

---

## Quality assurance — the ship loop

Automated acceptance suite: `modules/arden_acceptance.py`

```powershell
cd D:\dev\Arden\engine
python main_gui_assistant.py acceptance-test
# or: dist\Arden\Arden.exe acceptance-test
```

**Tests include:**

- Bootstrap + config + API keys present
- Session store read/write
- SQLite memory background thread
- Tk stream marks (streaming UI)
- Venice inference + streaming
- Groq key status (warn if invalid)
- Echo filter (repeat hello allowed)
- Full `process_text` flow
- Chat queue → busy state clears
- Brain dropdown lists kobold/venice/groq + input bar exists
- Companion rename persistence
- Kobold port 5001 probe
- Brain switch Venice + Kobold

Results written to:

- `%LOCALAPPDATA%\Arden\acceptance-last.txt`
- `%LOCALAPPDATA%\Arden\ship-ready.txt` (after ship loop)

**Philosophy:** Human-out-of-the-loop for verification; human-in-the-loop only for taste and ship approval.

---

## Data on disk — where everything lives

All consumer data under **`%LOCALAPPDATA%\Arden\`**:

| Path | Contents |
|------|----------|
| `.env` | Venice + Groq API keys |
| `user.json` | Your name, assistant name |
| `assistant_config.runtime.yml` | Generated paths (memory DB, chroma, tasks) |
| `sessions.json` | Chat session list + messages |
| `consumer_memory.db` | SQLite memory graph |
| `chroma\` | Vector store (if used) |
| `tasks.db` | Task manager (business edition hooks) |
| `logs\` | Session logs |
| `.first_run_done` | Onboarding complete marker |
| `acceptance-last.txt` | Last harness result |
| `ship-ready.txt` | Last ship loop summary |

**Memories survive uninstall** unless user deletes the whole `Arden` folder (`Uninstall-Arden.ps1` removes app binaries only).

---

## Dave edition vs Brittany (consumer) edition

| Feature | Dave | Brittany |
|---------|------|----------|
| Kobold :5001 in dropdown | ✅ | ✅ offered; works if they run Kobold |
| Venice / Groq cloud | ✅ | ✅ primary path |
| Sources tab | ✅ placeholder | ✅ placeholder |
| Neo4j memory | ✅ optional dev | ❌ SQLite only |
| Claude / full backend set | ✅ dev config | ❌ consumer brains only |
| Morning briefing / tasks | ✅ hooks exist | Disabled consumer |
| NURA guardrails | ❌ not ported | ❌ not ported |

---

## Roadmap — what comes next

### Phase 4 — Sources RAG (next after intake)

- [ ] PDF/txt ingest + document collection in Chroma
- [ ] Sources chat wired to active brain
- [ ] Citation snippets in answers

### Polish (ongoing)

- [ ] Brittany clean-machine test (outside dev) — first non-Dave user
- [ ] Encryption at rest (from PersonaLock Phase 4)
- [ ] Rebuild portable zip after each fix batch (automated ship loop)

### Kairos router (planned)

Shared config rules: when to use local Kobold vs cloud Anthropic/Venice per session context — “right moment, right brain.”

### Possible enhancements

- Groq key refresh flow in Settings (detect 401, prompt replace)
- Brain dropdown friendly labels (“Local”, “Venice Cloud”, “Groq Cloud”)
- Telegram bridge (code exists in engine; not consumer-facing yet)
- Full Chroma + Ollama embeddings on power-user install
- Business edition morning briefing in GUI
- Wellness edition persona toggle (consumer uses consumer rules today)

---

## Honest gaps vs NURA Connect

### vs NURA Connect

NURA is a **finished mobile journey** — onboarding, mood, crisis, facility sync, elegant Flutter UI. Arden will not look or behave identically because it is a **desk tool** with more knobs. The right comparison is not “clone NURA” but **“never needs Dave on the phone.”**

### Known consumer limitations today

- Groq key quality varies by user
- Sources RAG not wired yet (tab is placeholder)
- TTS/Mic are optional and network-dependent for speech recognition
- No mobile app — desktop only (Windows consumer exe)

---

## Key file map

```
D:\dev\Arden\
├── ARDEN_DESKTOP.md              Master plan + phases
├── ARDEN_PROJECT_OVERVIEW.md     This document
├── BRITTANY_SHIP.md              Ship checklist for outside tester
├── CONTINUE_POLICY.md            Autonomous agent rules
├── engine\
│   ├── Arden.bat                 Dev launch
│   ├── main_gui_assistant.py     Entry: chat | smoke-test | acceptance-test
│   ├── assistant_config.consumer.yml
│   ├── assets\
│   │   ├── splash.png            Forest splash #4
│   │   └── persona.json          Soul contract
│   ├── modules\
│   │   ├── gui\
│   │   │   ├── chat_app.py       Main shell
│   │   │   ├── first_run.py      Onboarding + Settings
│   │   │   ├── arden_theme.py    Colors + fonts
│   │   │   ├── arden_decor.py    Tree glyph, pulse
│   │   │   ├── session_store.py  Sidebar sessions
│   │   │   ├── sources_panel.py  Sources tab (RAG)
│   │   │   └── splash.py
│   │   ├── base_assistant.py     PlainAssistant
│   │   ├── consumer_bootstrap.py
│   │   ├── arden_acceptance.py   Ship harness
│   │   └── brain_backends\       kobold, venice, groq, …
│   ├── packaging\arden.spec        PyInstaller
│   ├── scripts\
│   │   ├── build_arden_consumer.ps1
│   │   └── package_for_brittany.ps1
│   └── release\
│       └── Arden-Portable.zip    Ship artifact
```

---

## One-sentence pitch

**Arden Desktop** is your personal AI desk — forest-green, remembers everything on your machine, lets you rename your companion and swap brains with one dropdown, and optionally opens a research layer for documents and podcasts — **Powered by Rémanence**.

---

*AI Integration and Consulting LLC · Powered by Rémanence*  
*Keep the soul. Change the brain.*
