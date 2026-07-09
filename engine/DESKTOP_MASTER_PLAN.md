# PersonaLock Desktop — Master Plan

**Product:** PersonaLock Desktop Edition — David's personal AI assistant  
**Tagline:** *Keep the soul. Change the brain.*  
**Workspace:** `D:\dev\PersonaLock\`  
**Created:** 2026-06-07  
**Status:** Building toward Janice finish line  

---

## FINISH LINE (agreed with Dave)

**Ship when:** Janice installs `PersonaLock_Setup.exe`, opens Sam, talks — **no Docker, no terminal, no Dave on the phone.**

Details: `docs/JANICE_EDITION.md`

| Edition | User | Brain | Memory | Package |
|---------|------|-------|--------|---------|
| **Dave** | David | Kobold + Gemma (M40) | Neo4j + Chroma | Dev stack |
| **Janice** | Consumer | Groq/Venice (cloud) | SQLite + Chroma | `PersonaLock_Setup.exe` |

Dave edition = build + dogfood. Janice edition = **finish line.**

---

## Executive Summary

PersonaLock Desktop is David's **local-first personal assistant**. Sam (the persona/soul) persists across sessions. Memories live on disk in a graph + vector vault. The LLM is a **swappable inference engine** — never the owner of identity or memory.

**This plan prioritizes:**
1. **Janice `PersonaLock_Setup.exe`** — the ship milestone
2. Daily-usable Sam on Dave's hardware (Tesla M40 + KoboldCpp)
3. Local soul (persona + memories + embeddings) — never cloud-stored
4. Swappable brains (Kobold default for Dave, cloud default for Janice)
5. Encryption at rest (Phase 4 — not skipped)
6. StoryKeeper interview merge — **explicitly out of scope**

**Autonomous work started while Dave is away:**
- `docker-compose.yml` for Neo4j
- `kobold` brain backend + config default flip
- `scripts/bootstrap.ps1` one-shot infra check
- `launcher.py` path + compose fixes

---

## Dave's Hardware Profile

| Component | Spec | Role in PersonaLock |
|-----------|------|---------------------|
| **GPU** | NVIDIA Tesla M40, 24GB VRAM, Maxwell, CUDA 11.7 | KoboldCpp inference + optional Whisper GPU |
| **LLM server** | KoboldCpp "Old PC" (~1.1.13), port **5001** | **Default brain** |
| **Model** | Gemma 4 12B (Unsloth fine-tune), Q5_K_XL | Chat brain — **text-only today** via KoboldCpp; `mmproj-F32.gguf` pending (~1–2 wks) for vision/audio multimodal |
| **Inference (verified)** | TTFT 0.05s · 10.58 tok/s gen · 198.83 tok/s prompt | Dave-reported KoboldCpp bench — not estimates |
| **Embeddings** | Ollama `nomic-embed-text` on CPU | Memory semantic search — keeps VRAM for chat |
| **STT (future)** | RealtimeSTT + faster-whisper on **CPU** | `small.en` + `int8` — VRAM reserved for Kobold only |
| **NOT used on M40** | LM Studio (CUDA 12 line) | Deprecated for this card |
| **Planned upgrade** | Tesla P40 24GB (~$125) | Drop-in Pascal swap, same power/shroud |

### Voice-to-text note (for agents reading Dave's messages)

When Dave's STT glues the article **"a"** to the next word (`AP40` = **a P40**, `ACAR` = **a car**), parse accordingly. Dave does not go back to fix transcripts.

---

## Architecture Principles (Non-Negotiable)

### What stays LOCAL forever
- Sam persona (`profiles/sam.json`, `assets/persona.json`)
- All memories (Neo4j graph + ChromaDB vectors)
- Embedding generation (Ollama `nomic-embed-text`)
- Conversation history substrate
- Encryption keys (Phase 4 — Windows DPAPI / Credential Manager)

### What is SWAPPABLE (inference only)
Cloud backends receive an **assembled prompt for one turn**. They do not store persona or memories.

| Backend | Type | Status |
|---------|------|--------|
| **kobold** | Local (KoboldCpp :5001) | ✅ Added — **default** |
| **ollama** | Local | ✅ Exists |
| **lm_studio** | Local | ✅ Exists (not used on M40) |
| **groq** | Cloud | ✅ Exists — fallback only |
| **claude** | Cloud | ✅ Exists |
| **openai** | Cloud | ✅ Exists |
| **venice** | Cloud | ✅ Added (optional — needs `VENICE_API_KEY`) |
| **gemini** | Cloud | ✅ Added (optional — needs `GEMINI_API_KEY`; NOT local Gemma) |

### Thinking mode (Qwen3)
**Keep OFF.** PersonaLock has no logic to strip `` blocks. Thinking ON would leak into memory and TTS.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PersonaLock Desktop                       │
│                                                              │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │ Sam Persona  │    │         Memory Vault             │   │
│  │ engine.py    │───▶│  Neo4j (graph) + Chroma (vector) │   │
│  │ persona.json │    │  Ollama nomic-embed-text (CPU)   │   │
│  └──────────────┘    └─────────────────────────────────┘   │
│         │                          │                        │
│         └──────────┬───────────────┘                        │
│                    ▼                                        │
│           PlainAssistant (base_assistant.py)                 │
│                    │                                        │
│         ┌──────────┴──────────┐                            │
│         ▼                     ▼                            │
│  ┌─────────────┐      ┌─────────────┐                     │
│  │ KoboldCpp   │      │ Cloud APIs  │  (optional override) │
│  │ :5001 M40   │      │ Groq/Claude │                     │
│  └─────────────┘      └─────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Active code path (use this)
```
main_base_assistant.py
  → modules/base_assistant.py (PlainAssistant)
    → modules/personality_engine/engine.py
    → modules/memory_vault/memory_manager.py
    → modules/brain_backends/brain_factory.py
```

### Legacy path (deprecate, do not extend)
```
api/routes.py → memory/ → core/ → llm/
```
Fence with `_legacy/` move in Phase 1. Do not delete until smoke tests pass.

---

## Current State Audit (2026-06-07)

### ✅ Working
- Sam text chat loop (`main_base_assistant.py chat`)
- Personality engine + edition overrides (`assets/persona.json`)
- Memory vault code (Neo4j + Chroma + Ollama embeddings)
- Brain factory with kobold, ollama, lm_studio, groq, claude, openai
- Task manager (SQLite `data/tasks.db`)
- Morning briefing (`daily_briefing.py`)
- Ollama `nomic-embed-text` installed
- KoboldCpp responding on `:5001`

### ⚠️ Needs attention
- Neo4j container did not exist — `docker-compose.yml` added (spin up on return)
- Default was Groq (cloud) — **flipped to kobold**
- No encryption at rest
- "Forget this" may be stubbed — verify + wire delete
- `launcher.py` had wrong path — **fixed** to `D:\dev\PersonaLock`
- Duplicate broken `modules/personality_engine/api.py`
- README still describes original Ada/DeepSeek fork
- STT on base path: `ears: none`

### ❌ Out of scope (this plan)
- StoryKeeper interview merge
- Wellness Flutter features
- Ledger Core as runtime dependency (adopt later)
- GUI / dashboard

---

## Phase Breakdown

### Phase 0 — Infrastructure Bootstrap ⏳ IN PROGRESS

**Goal:** `python main_base_assistant.py chat` works with Kobold brain + memory.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 0.1 | `docker-compose.yml` for Neo4j | Agent | ✅ Done |
| 0.2 | `kobold` backend + config default | Agent | ✅ Done |
| 0.3 | `launcher.py` path + compose fix | Agent | ✅ Done |
| 0.4 | `scripts/bootstrap.ps1` | Agent | ✅ Done |
| 0.5 | `docker compose up -d` (Neo4j running) | Agent | ✅ Done |
| 0.6 | Smoke: `test_brain_backends.py` | Agent | ⬜ Pending |
| 0.7 | Smoke: `test_memory_pipeline.py` | Agent | ⬜ Pending |
| 0.8 | Smoke: live chat with Sam | Dave + Agent | ⬜ Pending (Dave — when back from writing) |

**Dave's 2-minute checklist on return:**
```powershell
cd D:\dev\PersonaLock
.\scripts\bootstrap.ps1
python main_base_assistant.py chat
```

**Exit criteria:** Sam responds via KoboldCpp, recalls a injected memory, Neo4j browser shows nodes at `http://localhost:7474`.

---

### Phase 1 — Consolidate & Document (Est. 2–3 days)

**Goal:** One truth. Any agent can cold-start from docs alone.

| # | Task | Files |
|---|------|-------|
| 1.1 | Rewrite `README.md` for PersonaLock Desktop | `README.md` |
| 1.2 | Mark legacy stack deprecated | `api/`, `memory/`, `core/` → `_legacy/` or `DEPRECATED.md` |
| 1.3 | Fix/remove broken `personality_engine/api.py` | `modules/personality_engine/` |
| 1.4 | Align `ROADMAP.md` with actual code state | `ROADMAP.md` |
| 1.5 | Add `.env.sample` entries for all backends | `.env.sample` |
| 1.6 | Update module READMEs (remove "scaffold" language) | `modules/*/README.md` |

**Exit criteria:** New session reads README + this file only; no confusion about Ada vs Sam vs PersonaLock.

**Naming clarity (canonical):**
- **PersonaLock** — parent brand
- **Sam** — persona/soul (base assistant, text)
- **Ada** — voice shell (Typer path, `main_typer_assistant.py`)

---

### Phase 2 — Complete Backend Roster (Est. 2 days)

**Goal:** All 7 backends swappable at runtime.

| # | Task | Source |
|---|------|--------|
| 2.1 | Port `VeniceBackend` | `ledger_core/src/ledger_core/brain/venice.py` |
| 2.2 | Add `GeminiBackend` | New — `google-generativeai` already in pyproject.toml |
| 2.3 | Config blocks + `.env` keys | `assistant_config.yml` |
| 2.4 | Tests for venice + gemini | `test_brain_backends.py` |
| 2.5 | Update switch-brain help text | `base_assistant.py` ✅ partial |

**Exit criteria:** `"switch brain to venice"` works; all backends in `test_brain_backends.py` pass.

---

### Phase 3 — Memory Hardening (Est. 3 days)

**Goal:** Memory commands are trustworthy.

| # | Task | Detail |
|---|------|--------|
| 3.1 | Wire "forget this" | ✅ `_last_memory_id` + `forget()` / `forget_most_recent()` |
| 3.2 | Verify "remember this" | importance=0.9, correct typing |
| 3.3 | Memory type taxonomy | fact, preference, goal, event |
| 3.4 | Session continuity | Conversation nodes link across restarts |
| 3.5 | Auto-extraction (optional) | Post-turn local Ollama: "did Sam learn anything?" |
| 3.6 | Memory status command | "what do you remember about X?" |

**Exit criteria:** Remember → visible in Neo4j browser. Forget → gone from both stores.

---

### Phase 4 — Encryption at Rest (Est. 4–5 days)

**Goal:** Raw disk files not readable plaintext.

| # | Task | Approach |
|---|------|----------|
| 4.1 | API keys → Windows Credential Manager | Replace plaintext `.env` |
| 4.2 | Chroma document encryption | Encrypt before write, decrypt on read |
| 4.3 | Neo4j sensitive field encryption | Application-layer for PII fields |
| 4.4 | SQLite tasks.db encryption | SQLCipher or field-level |
| 4.5 | Key storage | Windows DPAPI via `keyring` package |
| 4.6 | Backup strategy | Encrypted export only |

**Reference donors:** Wellness `storage_service.dart` patterns, Ledger Core Phase 6 spec.

**Exit criteria:** Pull power plug, reboot, Sam works; hex-dump of Chroma/Neo4j data dirs shows no plaintext user content.

---

### Phase 5 — Voice + Daily Driver (Est. 5+ days)

**Goal:** Wake word → Sam speaks with memory, local brain, encrypted storage.

| # | Task | Detail |
|---|------|--------|
| 5.1 | Enable STT on base path | `ears: realtime-stt` in config |
| 5.2 | Whisper CPU tune (Dave preference) | `small.en`, `device: cpu`, `compute_type: int8` — GPU only if CPU too slow |
| 5.3 | TTS | `pyttsx3` local default; ElevenLabs optional |
| 5.4 | Unified launcher | `launcher.py` or `Sam.bat` |
| 5.5 | Morning briefing in wake flow | Already partially wired |
| 5.6 | State indicators | listening / thinking / speaking (console) |

**VRAM budget (M40 24GB):**
- Qwen3 30B Q4_K_S: ~18–20 GB
- Whisper on CPU: ~0 VRAM (Gemma 12B keeps most of the 24GB)
- Headroom: ample — STT stays off GPU unless CPU latency becomes a problem

**Exit criteria:** Say "hey sam" → transcribed → Kobold response → pyttsx3 speaks → memory stored.

---

### Phase 6 — Polish & Ledger Core Adoption (Ongoing)

**Goal:** Desktop stays canonical; ledger_core catches up.

| # | Task | When |
|---|------|------|
| 6.1 | Adopt ledger_core `brain/` package | After ledger Phase 4 memory lands |
| 6.2 | Adopt `VoiceLoop` from ledger_core | After Phase 3 verification |
| 6.3 | Corpus export schema | Vendor-survivable backup |
| 6.4 | PyInstaller / Windows installer | Optional packaging |
| 6.5 | P40 migration notes | Document CUDA 11 Kobold settings |

### Phase 7 — House Nodes (ESP32, post-Janice)

**TLDR:** One Sam brain on Dave's PC. ESP32 puck in each room = ears + mouth only.

```
PC (PersonaLock server — memory + Gemma/Kobold)
  ↑ WiFi
Kitchen / Bedroom / Office ESP32 clients (Open Interpreter 01 Light pattern)
```

| # | Task |
|---|------|
| 7.1 | PersonaLock HTTP/WebSocket server mode |
| 7.2 | ESP32 client firmware (mic → server, server → speaker) |
| 7.3 | Wake word on nodes or push-to-talk |
| 7.4 | Google Nest pucks — speakers only if at all, not mic nodes |

**Not the finish line.** Janice `.exe` ships first.

---

## Autonomous Execution Plan (Agent)

When Dave approves this plan, the agent executes **without asking** within these bounds:

### Agent CAN do autonomously
- All Phase 0–3 implementation tasks
- Write/update code, configs, tests, docs in `D:\dev\PersonaLock\`
- Run `docker compose`, `pytest`, smoke scripts
- Port backends from `ledger_core` (read-only donor)
- Fix bugs found by tests

### Agent MUST ask Dave first
- Delete legacy code (move to `_legacy/` is OK; delete is not)
- Change Sam's persona traits or `persona.json` content
- Commit to git or push
- Install new system packages
- Change KoboldCpp model or fine-tune
- Anything that sends data to cloud services for testing

### Agent execution order (post-approval)
```
Phase 0 complete → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
```
Each phase ends with a short status update in this file's **Progress Log** section.

---

## Review Checklist (Dave — when you return)

1. **Read this file** — especially Phase 0 checklist
2. **Run bootstrap:**
   ```powershell
   cd D:\dev\PersonaLock
   .\scripts\bootstrap.ps1
   ```
3. **Talk to Sam:**
   ```powershell
   python main_base_assistant.py chat
   ```
4. **Confirm Kobold is the brain** — say `brain status`
5. **Approve / adjust** phase priorities
6. **Say "go autonomous"** — agent executes Phase 0 completion → Phase 1+

### Quick decisions needed from Dave
| Question | Default if no answer |
|----------|---------------------|
| Default brain? | **kobold** (already set) |
| Cloud fallback? | groq (keep in chain) |
| StoryKeeper merge? | **No** (locked) |
| Encryption priority? | Phase 4 — don't skip |
| Voice in Phase 5? | Yes, after memory hardening |

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Neo4j auth mismatch | compose uses `neo4j/password` — matches `assistant_config.yml` |
| Kobold 30B slow on long prompts | 120s timeout; trim memory recall token budget |
| M40 thermals | Already running cool — monitor under Whisper+Kobold concurrent |
| Doc/code drift | Phase 1 doc consolidation |
| Legacy stack confusion | Fence in Phase 1 |
| STT "a" prefix parsing | Agent convention documented above |
| NextDNS blocks Venice | Whitelist `api.venice.ai` when Venice backend added |

---

## Progress Log

| Date | Agent | Action |
|------|-------|--------|
| 2026-06-07 | Cursor | Created `DESKTOP_MASTER_PLAN.md` |
| 2026-06-07 | Cursor | Added `docker-compose.yml`, `kobold_backend.py` |
| 2026-06-07 | Cursor | Flipped config default groq → kobold |
| 2026-06-07 | Cursor | Fixed `launcher.py` paths, added `bootstrap.ps1` |
| 2026-06-07 | Cursor | Updated brain switch commands to include kobold + groq |
| 2026-06-07 | Cursor | `docker compose up -d` — Neo4j container running |
| 2026-06-07 | Dave | Swapped Kobold model: Qwen3 30B → Gemma 4 12B multimodal (Unsloth) |
| 2026-06-07 | Cursor | Updated `assistant_config.yml` kobold model ID + 90s timeout |
| 2026-06-07 | Dave | Gemma 4 12B text-only on KoboldCpp; mmproj multimodal pending KoboldCpp update |
| 2026-06-07 | Cursor | Wired forget-this, Venice/Gemini backends, README, DEPRECATED.md |
| 2026-06-07 | Dave + Cursor | Finish line locked: `PersonaLock_Setup.exe` for Janice |
| 2026-06-07 | Cursor | `assistant_config.consumer.yml`, `docs/JANICE_EDITION.md`, PyInstaller skeleton |
| 2026-06-07 | Cursor | `consumer` persona edition in `persona.json`, `PERSONALOCK_CONFIG` env support |
| 2026-06-07 | Cursor | SQLite memory backend — Janice path no longer requires Neo4j/Docker |
| 2026-06-07 | Cursor | GUI chat window + first-run wizard + NSIS installer skeleton |
| 2026-06-07 | Cursor | PyInstaller build OK — `release/PersonaLock-Portable.zip` shippable to Janice |

---

## File Map (key paths)

```
D:\dev\PersonaLock\
├── DESKTOP_MASTER_PLAN.md      ← THIS FILE
├── docker-compose.yml          ← Neo4j
├── assistant_config.yml        ← brain + memory config
├── main_base_assistant.py      ← entry: Sam chat
├── launcher.py                 ← full stack launcher
├── scripts/bootstrap.ps1       ← infra check
├── modules/
│   ├── base_assistant.py       ← orchestrator
│   ├── brain_backends/
│   │   ├── kobold_backend.py   ← NEW
│   │   └── brain_factory.py
│   ├── memory_vault/
│   └── personality_engine/
├── assets/persona.json
├── profiles/sam.json
└── data/
    ├── chroma/                 ← vector store
    └── tasks.db                ← SQLite tasks
```

---

## What Success Looks Like

**Short term (this week):** Dave opens laptop, runs bootstrap, talks to Sam. Sam knows him. Nothing touched the cloud. Neo4j shows growing memory graph.

**Medium term (this month):** Encryption on disk. All backends swappable. Memory forget works. README tells the truth.

**Long term:** Wake word Sam on the M40 (or P40). Gemma multimodal (mmproj) for music/images + local soul. PersonaLock Desktop is the daily driver — Ledger Series and Wellness are products that *lift from* this, not the other way around.

### Multimodal roadmap (Gemma 4 + KoboldCpp)
- **Now:** Text-only inference — Sam chat, memory, persona fully usable
- **Soon:** `mmproj-F32.gguf` lands → vision/audio ingest via KoboldCpp
- **Music lane:** FLAC library → (future) multimodal Gemma and/or CPU Whisper → memory vault
- **VRAM policy:** Keep Whisper on CPU; reserve M40 VRAM for Gemma inference

---

*Go cut the grass. The plan will be here when you get back.*
