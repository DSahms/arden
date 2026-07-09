# personalock Desktop — Claude Memory Export

> Tagging key: **FACT** = stated in a project file or directly confirmed in conversation · **RECOLLECTION** = remembered from past conversation, not necessarily written into any file · **OPEN** = unresolved, unverified, or in-flight.

---

## Executive Summary

- **FACT** — PersonaLock is a local-first, Windows-native desktop application that acts as a *stateful wrapper* around any LLM. Its one defining idea: decouple AI **identity** (personality + memory) from AI **inference** (the LLM). The LLM is swappable; the persona and memory are not. Tagline: *"Keep the soul. Change the brain."*
- **FACT** — It is a desktop project only. No APK, no mobile, no web app. This has been asked and confirmed more than once.
- **FACT** — Built by **David** (solo founder/developer), using **Cline** (VS Code AI coding extension) driven by the **Anthropic API**, plus direct Claude chat sessions.
- **FACT** — Phase 1 (Foundation) is the last state reflected in the canonical project files: the assistant "Ada" launches, listens, responds, and runs locally. Phase 2 (memory persistence) is marked as the next step in those files.
- **RECOLLECTION** — In a Feb 2026 session, work was reported as far ahead of the files: Phases 1–4 described as complete (~"67% done," Phase 5 partially done). The current project files do **not** reflect that progress. This is the single biggest open discrepancy in the project (see Contradictions).
- **RECOLLECTION** — The project carries real personal weight for David: Ada was first brought to life "on a bad day that turned into a win." The brand is meant to carry that meaning without being heavy about it.

---

## Product Identity

### What it is
- **FACT** — A persistent, personalized AI companion + productivity assistant that retains memory, keeps a stable personality across sessions, and is hosted locally for privacy and independence.
- **FACT** — Core promise: continuity. "You say 'I hate mornings' today; next week it answers 'Afternoon — you mentioned you hate mornings.'" The assistant remembers, knows you, and the underlying brain doesn't matter.
- **FACT** — Explicitly NOT: a session-resetting chatbot, a cloud-dependent service, a personality-less generic assistant, or a tool locked to one LLM vendor.

### The three-tier naming hierarchy (current)
- **RECOLLECTION** — This structure was worked out in a branding conversation (Feb 1, 2026) and lives mostly in chat, not in the project files:
  - **PersonaLock** — the *company / parent brand*. Wordmark-first. "PersonaLock, makers of Ada." Designed so it survives any product pivot (companion → identity security → memory platform) without looking dated.
  - **Ada** — the *indie-dev product*. Public-facing, the open-source-able engine, the thing that responds to the wake word. Can have its own smaller sub-brand later.
  - **Sam** — short for **Samantha**. David's *private personal companion* persona — the "soul." Warm, direct, dry humor, memory continuity. Sam lives *inside* Ada but is not Ada. Others could clone Ada and build their own "Sam."
- **FACT** — In code this already maps cleanly: the base assistant launches as **Ada** (wake word), while the Personality Engine profile is **Sam**.

### Sam's persona spec
- **FACT** — Traits (0.0–1.0): warmth 0.8, directness 0.7, humor 0.6, formality 0.3, empathy 0.9, patience 0.8.
- **FACT** — System-prompt rules: warm + direct, dry humor, references past conversations naturally, has opinions but isn't pushy, concise but warm, and **never** claims to be GPT/ChatGPT/Claude or any specific model — "simply Sam."
- **FACT** — Greeting: "Hey! What are we working on?" · conversation_style: "friendly_direct."

### Brand direction (from chat, not in files)
- **RECOLLECTION** — Vibe: warm not cold; quiet confidence ("it just knows you"); privacy as a feature not a disclaimer; intimate but not creepy (lean into trust/ownership, not surveillance).
- **RECOLLECTION** — Color palette: deep navy / dark slate base + warm amber / soft gold accent (not neon, not clinical blue).
- **RECOLLECTION** — Wordmark approach: keep "PersonaLock" as the logo itself, exploiting the natural **Persona + Lock** split. Candidate treatments: weight contrast (light "Persona," bold "Lock"); a stylized capital **L** hinting at a lock shackle; the **O** in "Lock" as a subtle keyhole. One subtle letterform tweak, otherwise a single clean typeface.
- **RECOLLECTION** — Font shortlist discussed: Rajdhani, Exo 2, Inter.
- **RECOLLECTION** — Catchphrase candidates; Claude's pick was *"The AI that remembers."* Others floated: "Your AI. Your data. Your rules.", "Stays local. Stays loyal.", "Finally, an AI that knows you.", "Lock it in.", "Identity, persistent.", "Portable AI identity — persistent memory and personality that survives any brain swap."

### Inspirations / lineage
- **FACT** — Forked from **disler/always-on-ai-assistant** (GitHub) as the working foundation.
- **FACT** — Design philosophy influenced by the open-source "always-on" assistant ecosystem, specifically the **Ozark's Assistant / Ada** project (lightweight, persistent, voice-controlled, local hosting, modular personality profiles, pluggable memory). PersonaLock extends it with richer long-term memory retrieval and a deeper personality engine.

### Target audience
- **FACT** — Technical decision-makers (there is a "Technical Decision Maker Segment" strategy doc), and the indie/developer audience for the Ada layer.

---

## Architecture

- **FACT** — Flow: `User Input → PersonaLock Wrapper (inject persona + memory) → swappable LLM backend → response with Sam's personality + memory context.`
- **FACT** — Four swappable components:
  - **Ears (STT)** — RealtimeSTT / Whisper / cloud APIs.
  - **Memory (State)** — *always local.* Neo4j (graph: facts, bios, relationships, projects, preferences, goals) + ChromaDB (semantic/vector search). SQLite named as an option.
  - **Brain (LLM)** — local or cloud: LM Studio, Ollama, Claude, OpenAI, DeepSeek.
  - **Voice (TTS)** — Piper / pyttsx3 / ElevenLabs.
- **FACT** — Detailed-summary architecture also frames it as five tiers: Persona Layer, Memory Vault, Interaction Layer (incl. OpenAI Realtime API compatibility), Execution Layer (run tasks/call tools), Local Hosting Layer (local-first, fall back to APIs only for heavy tasks).

### Confirmed running stack (Phase 1)
- **FACT** — Local LLM: **DeepSeek Coder 7B** via **LM Studio** on `localhost:1234`.
- **FACT** — Graph memory: **Neo4j** (`localhost:7474`, bolt `7687`).
- **FACT** — Vector: **ChromaDB** (embedded mode) with **Ollama** `nomic-embed-text` embeddings.
- **FACT** — Language/framework: **Python + FastAPI**.
- **FACT** — Voice in/out: **RealtimeSTT** / **pyttsx3** (RealtimeTTS SystemEngine).
- **FACT** — Tooling: **Cline** in VS Code, on the **Anthropic API**, using a Claude Sonnet 4.5 model string.
- **FACT** — Dependencies installed: realtimestt, realtimetts, pyttsx3, dpath, elevenlabs, anthropic, ollama, openai, chromadb, neo4j, typer, pydantic, rich.

### Planned brain-swapping layer (Phase 4 design)
- **FACT** — Abstract base backend + concrete backends for LM Studio, Ollama, Claude, OpenAI, plus a factory with a fallback chain (default `lm_studio`, fallback to `ollama`). Voice/text commands planned: "switch brain," "brain status." Principle: Sam's identity persists across every backend.

### Components engineered on top of the fork
- **FACT** — Memory Vault (graph + embeddings) — built and working.
- **FACT/OPEN** — Personality Engine (Sam profile + engine) — fully specified in the autonomous Cline prompts; the canonical handoff still marks the engine module as referenced-but-not-yet-created.

---

## Decisions

- **FACT** — Desktop-only, local-first, privacy-first. No mobile/web/APK.
- **FACT** — Decouple state from brain: personality + memory live outside the LLM so model swaps don't reset identity. ("Soul is local, brain is flexible.")
- **FACT** — Modularity over monoliths: every component swappable to balance privacy/cost/performance.
- **RECOLLECTION** — Brand as a **wordmark**, not an icon — chosen deliberately because David's prior companies led with the company name as the logo, and a wordmark survives a pivot where a lock/fingerprint icon would not.
- **RECOLLECTION** — "PersonaLock, makers of Ada" parent/product structure (Apple→iPhone, Google→Gmail analogy). PersonaLock wordmark first; Ada gets its own identity later; Sam's quiet sub-identity much later.
- **FACT** — Cline workflow decision: **one fully-specified task per session** (cline_prompt_v2), because v1 failed — Phase 2 items were manual tests not code, specs were too vague to implement under a "don't ask questions" rule, and reading three context files up front burned the context window. Handoff doc is the single source of truth Cline reads each session.
- **FACT** — Autonomous Cline prompts authored for Phase 3 (Personality Engine), Phase 4 (Brain Swapping), Phase 5 (Polish & Stability), runnable via the Claude API with minimal user input.
- **FACT** — ADHD-aware coding conventions baked into the prompts: heavy comments, clear names, small functions, docstrings, logical separation.
- **RECOLLECTION** — API budget decision point: David funded the Anthropic account with **$35** to drive Cline.

---

## Contradictions & Stale Names

- **OPEN** — **Phase status conflict.** Project files (HANDOFF/ROADMAP, dated Jan 27, 2026) say Phase 1 complete / Phase 2 next. A Feb 12, 2026 session, however, treated Phases 1–4 as complete and Phase 5 as partly done. May 31 and June 3, 2026 summaries again describe Phase 1 done / Phase 2 next. Either the Feb work was lost/never merged, or the folder was re-seeded with the older files. **Unverified which is true** — needs a check of what's actually running.
- **FACT** — **"GPT-5 mini"** — a dead identity. Before the Personality Engine, Ada wrongly self-identified as "GPT-5 mini." Killing this is the explicit point of the Sam profile.
- **FACT** — **Module-file naming drift.** The roadmap/handoff describe the engine file as `api.py`; the autonomous Cline prompts build it as `engine.py`. Same class (`PersonalityEngine`), inconsistent filename across docs.
- **FACT** — **Name spelling drift.** "PersonaLock" (canonical) vs "Personalock" vs "Personal lock" (one marketing-strategy file is literally titled "Personal_lock_..."). Your own request used "Personalock desktop." Recommend locking the canonical casing as **PersonaLock**.
- **RECOLLECTION** — **"Klein" vs "Cline."** Voice transcription has rendered the tool **Cline** as "Klein" in at least one session. Same tool.
- **FACT** — **Corrupted emoji in ROADMAP.md.** The file contains mojibake (e.g. `âœ…`, `ðŸ"²`) where check/box emoji should be — a UTF-8/encoding artifact, cosmetic but real.
- **FACT** — **Marketing/strategy PDFs are effectively empty.** LinkedIn Campaign Plan, Marketing Strategy, Strategic Marketing Plan, Technical Decision Maker Segment — content did not extract; they read as blank/older stubs.
- **FACT** — **"Ada" vs "Sam" in prose.** Docs sometimes say "Ada remembers/has identity" and sometimes "Sam." Per the agreed hierarchy, Ada = product shell/wake word, Sam = the persona speaking. Worth normalizing in writing.

---

## Open Threads

- **OPEN** — Phase 2 not verified: complete a full exchange, confirm it persists to Neo4j, restart, and confirm Ada recalls it; confirm ChromaDB semantic retrieval surfaces relevant memories into the prompt.
- **OPEN** — Whether the Feb "Phases 3–4 complete" state actually exists in the codebase today (see Contradictions).
- **OPEN** — Personality Engine: confirm the module exists, is wired into the system prompt, and that "Who are you?" returns "Sam," not a model name.
- **OPEN** — Known runtime issues from live sessions:
  - Exit/quit got stuck in a loop; clean shutdown still needs work (multiple Ctrl+C reported).
  - Unicode emoji logging crash on exit (Windows `cp1252` charmap can't encode the wave emoji).
  - `ffmpeg`/`avconv` not found warning from pydub.
  - HDMI/display hardware issue (screen cutting out ~every 10 seconds) — environmental, not code.
- **OPEN** — Phase 5 polish: graceful error handling system, recovery strategies, fuzzy/multi-trigger wake-word detection, user-facing error messages written in Sam's voice.
- **OPEN** — Phase 6 (future): multi-persona support (formal advisor, creative partner, etc.), voice command to switch personas, per-persona voice, shared vs. isolated memory.
- **OPEN** — Brand execution: pick a final wordmark direction, produce SVG mockups, decide on Sam's eventual soft sub-identity, choose the final catchphrase.
- **OPEN** — Fill the empty marketing PDFs with real content (LinkedIn campaign, strategy, technical-decision-maker segment).
- **OPEN** — "Remember this" / "forget this" explicit commands appeared checked-off in one Feb roadmap snapshot but are not in the canonical roadmap — status unconfirmed.

---

## Only in Claude (not saved to a file yet)

These are things established in conversation that, as far as the project files show, were never written down:

- **RECOLLECTION** — The full **PersonaLock → Ada → Sam** three-tier brand hierarchy and its rationale. The files mention Ada and Sam, but the deliberate company/product/companion split lives only in the Feb 1, 2026 branding conversation.
- **RECOLLECTION** — **Sam = Samantha.** The meaning behind the name is not in any file.
- **RECOLLECTION** — "**PersonaLock, makers of Ada**" naming structure and the pivot-proofing logic behind choosing a wordmark.
- **RECOLLECTION** — The entire brand vibe spec: color palette (navy/slate + amber/gold), the five logo concept directions, the font shortlist, and all the catchphrase candidates.
- **RECOLLECTION** — **Founder context:** David has run other companies before and habitually leads branding with the company name as the logo; he came to Claude specifically because of shared history on this project. He has **ADHD** (drives the formatting/code conventions). Phase 5 notes also reference **potential health concerns**, used as a reason to prioritize reliability and clean shutdown.
- **RECOLLECTION** — The **origin story**: Ada first came alive on "a bad day that turned into a win" — used as emotional weight the brand should quietly carry. ("Against all the odds, we accomplished something.")
- **RECOLLECTION** — **Setup specifics:** funded the Anthropic account with $35, generated an API key, configured Cline with Anthropic + a Claude Sonnet 4.5 model string, and cloned disler/always-on-ai-assistant directly into a fresh project folder to start from a working base.
- **RECOLLECTION** — The reasoning behind the Cline-prompt redesign (why v1 deadlocked) is captured in a file, but the lived experience that triggered it — Cline stalling on manual-test "tasks" — came out of working sessions.

---

*Compiled from this project's files and Claude's recollection of prior project conversations. Items marked RECOLLECTION/OPEN should be confirmed against the live build before being treated as ground truth.*
