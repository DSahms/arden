# Arden Desktop — Master Plan

**Product:** Arden Desktop — personal AI desk  
**Company:** AI Integration and Consulting LLC · **Powered by Rémanence**  
**Tagline:** *Keep the soul. Change the brain.*  
**Workspace:** `D:\dev\Arden\` (engine code migrates from `D:\dev\PersonaLock\`)  
**Created:** 2026-06-09  
**Status:** Phase 2–3 — forest sanctuary theme (splash-sampled), session persistence, Notebooks panel

---

## Executive decisions (Dave, 2026-06-09)

| Decision | Value |
|----------|--------|
| Product name | **Arden Desktop** |
| Companion name | **Arden** (replaces Sam on desktop) |
| Legacy | PersonaLock Desktop → deprecated brand; code migrates |
| Public app | **NURA Connect** unchanged (facility/mobile) |
| Notebook layer | **Open Notebook** (`D:\dev\Arden\open-notebook\`) — integrated, not merged |
| Corporate line | Powered by **Rémanence** |

---

## What Arden Desktop is

One desk (one chrome package):

| Tab / module | Engine | Purpose |
|--------------|--------|---------|
| **Arden** (chat) | PersonaLock Python stack | Companion, Chroma + Neo4j/SQLite memory, persona |
| **Notebooks** | Open Notebook (Docker) | NotebookLM-style research, sources, podcasts |
| **Router (Kairos)** | Shared config | One chosen LLM provider per session rules |

Cursor remains primary builder/agent. Arden is memory + research + talk.

---

## API strategy — one wallet

**Goal:** Fund **one primary cloud API** (e.g. Anthropic) for chat intelligence.

| Layer | Anthropic only? | Notes |
|-------|-----------------|-------|
| Arden chat | ✅ Yes | `claude` backend in `brain_factory.py` |
| Open Notebook **chat** | ✅ Yes | Configure Anthropic in Open Notebook Settings |
| Open Notebook **embeddings** | ❌ No | Anthropic does not supply embeddings in Open Notebook — use **Ollama local** (`nomic-embed-text`, already on Dave stack) or cheap embed API |
| Open Notebook **podcasts** | ❌ Optional extra | TTS/STT needs ElevenLabs, OpenAI, Google, or Deepgram — skip until needed |
| Dave at home | $0 chat | Kobold/Gemma on M40 — same memory, swap brain |

**Practical setup:** Anthropic for LLM + Ollama for embeddings = **one paid API** for daily use.

---

## Open Notebook vs NotebookLM — honest gap

**Open Notebook matches or beats NotebookLM on:**
- Self-hosted privacy
- Multi-provider (not locked to Google)
- Doc chat with citations
- Multi-speaker podcasts (1–4 speakers)
- PDF / video / audio / web / Office ingest

**NotebookLM Studio features Open Notebook does NOT natively match (today):**
- Slide decks (Presenter / Detailed)
- Infographics (visual single-page)
- Mind maps (Studio panel)
- Video overview
- Flashcards / Quiz studio

Open Notebook outputs **notes, summaries, transformations (text), podcasts** — not Google's Nano Banana slide/infographic pipeline. For slides, you may still use NotebookLM occasionally OR add a future Arden transformation.

Dave's call: Open Notebook is **key** for doc chat + podcasts + privacy; not a 100% Studio clone.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Arden Desktop UI (new shell — Phase 1)                     │
│  Sidebar · streaming chat · backend picker · tabs           │
├──────────────────────┬──────────────────────────────────────┤
│  Arden Chat          │  Notebooks (Open Notebook UI embed)  │
│  PersonaLock engine  │  Docker :8502 UI / :5055 API         │
│  persona + memory    │  SurrealDB + Esperanto providers     │
├──────────────────────┴──────────────────────────────────────┤
│  Kairos router — local Kobold vs cloud Anthropic rules      │
└─────────────────────────────────────────────────────────────┘
```

**Separate processes, one interface.** Connect the dots, don't merge git repos.

---

## Phases

### Phase 0 — Foundation
- [x] `D:\dev\Arden\` created
- [x] Open Notebook cloned
- [x] `ARDEN_DESKTOP.md` (this file)
- [x] `CONTINUE_POLICY.md` — autonomous march rules
- [x] Docker smoke-test Open Notebook (2026-06-09 — API healthy, UI :8502)

### Phase 1 — Rebrand engine
- [x] Copy/adapt `PersonaLock\` Python engine → `Arden\engine\`
- [x] Rename Sam → Arden in persona, prompts, GUI strings (runtime paths)
- [x] Rename PersonaLock Desktop → Arden Desktop in packaging (`packaging/arden.spec`, `Arden.bat`)
- [x] App icon / exe build (`scripts/build_arden_consumer.ps1` → `dist/Arden/Arden.exe`)
- [x] Brittany portable zip (`scripts/package_for_brittany.ps1` → `release/Arden-Portable.zip`)
- [x] Keep NURA Connect repo untouched

### Phase 2 — UI shell
- [x] Sidebar layout (sessions, New chat, Notebooks, Rémanence footer)
- [x] Forest sanctuary theme sampled from splash #4 (`arden_theme.py`)
- [x] Shared widgets — cards, sanctuary input, paned chrome (`arden_widgets.py`)
- [x] Brain dropdown (Venice / Groq consumer; + Kobold etc. Dave edition)
- [x] Tagged chat transcript (user vs Arden colors)
- [x] Unified tab chrome — Chat | Notebooks in one window (`notebooks_panel.py`)
- [x] Sidebar neural-tree glyph + gold rule accents (`arden_decor.py`)
- [x] Splash image + progress bar + Rémanence tagline (`splash.py`)
- [x] Word-stream reply animation (pseudo-stream)
- [x] Thinking status pulse
- [x] Sidebar session persistence (`session_store.py` → `%LOCALAPPDATA%\Arden\sessions.json`)
- [x] Double-click session rename in sidebar
- [x] Forest-themed first-run wizard (`first_run.py`)
- [x] In-app Settings dialog (API keys, forest chrome)
- [x] **Kobold streaming** — local SSE tokens when KoboldCpp is running

### Phase 3 — Open Notebook integration
- [x] Native Windows launcher (`start-open-notebook-native.bat`, setup script)
- [x] Venice + Ollama + Kobold wire script (`docker/wire_open_notebook_providers.py`)
- [x] **Notebooks** tab + sidebar shortcut + health polling + launch stack
- [x] Unified forest theme on Notebooks panel (Phase 2 shell match)
- [x] **WebView2 in-app embed** (`notebooks_embed.py` + `wryview` — optional `pip install wryview`)
- [x] Package wryview in consumer exe (`collect_all('wryview')` in `arden.spec`)

### Studio gap (slides / infographics / quiz cards)
NotebookLM **Studio visuals** are not in Open Notebook or AnythingLLM. Path later:
- Open Notebook **transformations** → export text/outline → future Rémanence slide step or occasional NotebookLM for visuals only.
- **Not** a reason to swap stacks — Arden memory + Open Notebook research stay.

### Phase 4 — Polish
- [ ] Brittany edition path (optional) — consumer exe, no Docker; Brittany = first outside-dev tester
- [ ] Encryption at rest (from PersonaLock Phase 4)

---

## Folder layout (target)

```
D:\dev\Arden\
├── ARDEN_DESKTOP.md          ← this file
├── open-notebook\            ← upstream clone (MIT)
├── engine\                   ← migrated from PersonaLock (Phase 1)
├── shell\                    ← new UI (Phase 2)
└── docker\                   ← compose for Open Notebook + Neo4j
```

PersonaLock repo remains until migration complete; NURA Connect stays in `personalock_wellness\`.

---

## Policy split (unchanged)

| Product | Guardrails |
|---------|------------|
| NURA Connect | Required — facility/public |
| Arden Desktop | None — personal workstation |

Do not port NURA red-team rules to Arden.

---

*AI Integration and Consulting LLC · Powered by Rémanence*
