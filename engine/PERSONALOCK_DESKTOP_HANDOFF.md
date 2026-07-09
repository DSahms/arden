# PERSONALOCK DESKTOP — ARCHITECT HANDOFF

**Generated:** 2026-05-27  
**Purpose:** Voice loop inventory for transplant into sibling Ledger Series products (StoryKeeper desktop, Operator's Ledger).

---

## 1. Project Identity

**Package name (pyproject.toml):** `paic-python-starter`  
**App name (assistant_config.yml):** `Sam` (base assistant) / `Ada` (typer assistant)  
**Repo name:** `PersonaLock` (GitHub: `DSahms/Persona-lock-Wellness`)  
**Alternate names found in code and docs:** Ada, PersonaLock Desktop, PersonaLock Business Edition, "Always-On Deepseek AI Assistant" (README title), Consigliere (not found in code — not used here)

**Description:**  
PersonaLock Desktop is a locally-running Python AI assistant with a voice loop (speech-to-text in, text-to-speech out), a swappable LLM backend, a persistent memory system (Neo4j + ChromaDB), and a personality engine. The project started as a Typer-command assistant ("Ada") driven by DeepSeek V3 and ElevenLabs TTS, and evolved into a general-purpose conversational assistant ("Sam") with a configurable brain backend (Groq, LM Studio, Ollama, Claude, OpenAI), a SQLite task manager, and a morning briefing system. The repo also contains a sibling Flutter mobile app (`personalock_wellness/`) and a facility dashboard (`facility_dashboard/`, `PersonaLock_Dashboard/`) that are separate products sharing the same repository.

**Intended user / target platform:**  
Windows desktop only. The launcher (`Ada.bat`, `launcher.py`) is hardcoded to `C:\Users\david\Projects\PersonaLock`. No cross-platform packaging exists. The Python venv is `.venv` at the project root. No Electron, Tauri, or other desktop framework — it is a terminal application.

---

## 2. Tech Stack

**Language and version:**  
Python 3.11.9 (MSC v.1938 64-bit, AMD64)  
Confirmed via: `.venv\Scripts\python.exe -c "import sys; print(sys.version)"`  
`pyproject.toml` requires `>=3.10,<3.12`

**Framework:**  
No GUI framework. Terminal application. CLI entry points use `typer` (v0.13.1+). No Electron, Tauri, PyQt, or WPF.

**Package manager and lock file:**  
`uv` (lock file: `uv.lock`). Also has `pyproject.toml`.

**Full dependency list from pyproject.toml (verbatim):**

```toml
[project]
name = "paic-python-starter"
version = "0.1.1"
description = "PAIC Python Starter"
readme = "README.md"
requires-python = ">=3.10,<3.12"
dependencies = [
    "neo4j>=5.14.0",
    "chromadb>=0.4.22",
    "anthropic>=0.39.0",
    "google-generativeai>=0.8.3",
    "llm>=0.18",
    "llm-claude-3>=0.9",
    "llm-gemini>=0.4.2",
    "ollama>=0.4.1",
    "openai[realtime]>=1.59.0",
    "pydantic>=2.10.2",
    "pytest>=8.3.3",
    "python-dotenv>=1.0.1",
    "pyyaml>=6.0.2",
    "typer>=0.13.1",
    "rich>=13.9.4",
    "realtimestt>=0.3.93",
    "dpath>=2.2.0",
    "elevenlabs>=1.50.3",
    "realtimetts[system]==0.4.40",
    "pyttsx3>=2.98",
    "python-telegram-bot>=20.0",
]
```

**Installed versions confirmed in `.venv`:**
- `realtimestt` 0.3.104
- `realtimetts` 0.5.7
- `elevenlabs` 2.32.0
- `pyttsx3` 2.99
- `faster-whisper` 1.1.1

**Build tool / bundler:**  
`uv`. Run with `uv run python <entrypoint>` or directly via `.venv\Scripts\python.exe`. No PyInstaller, cx_Freeze, or other bundler found.

**Target OS and minimum version:**  
Windows only. No minimum version specified in code. Launcher hardcodes `C:\Users\david\Projects\PersonaLock`. PyAudio (required by RealtimeSTT) requires Windows audio drivers.

---

## 3. Project Tree

```
PersonaLock/
├── .env                          # API keys (GROQ_API_KEY only populated)
├── .env.sample                   # Template for all keys
├── .gitignore
├── .python-version
├── Ada.bat                       # Windows launcher: calls launcher.py
├── ada.sh                        # Shell launcher (not used on Windows)
├── assistant_config.yml          # Primary config file
├── launcher.py                   # Startup orchestrator (Docker, Ollama, Neo4j, then main_base_assistant.py)
├── main.py                       # Empty (0 bytes)
├── main_base_assistant.py        # Entry point: Sam text-chat CLI (typer app)
├── main_telegram.py              # Telegram bot entry point
├── main_typer_assistant.py       # Entry point: Ada voice+typer CLI (RealtimeSTT + ElevenLabs)
├── pyproject.toml
├── uv.lock
├── README.md
├── HANDOFF.md                    # Session handoff notes (Feb 7, 2026)
├── ROADMAP.md
├── CODE_REVIEW.md
├── PHASE3_COMPLETION_SUMMARY.md
├── PHASE4_COMPLETION_SUMMARY.md
├── MANUAL_VALIDATION_PHASE3.md
├── SAM_SETUP_COMPLETE.md
├── STRUCTURE_AUDIT.md
├── scratchpad.md
├── daily_briefing.py
├── craigslist_digest.py
├── load_spring_garden.py
├── check.py
├── phase1_verify.py
├── search_code.py                # Temporary search helper (created during audit)
├── audit_icons.py
├── audit_svc.py
├── create_icon.py
├── pytest.ini
├── assets/
│   └── persona.json              # Persona contract (Sam identity, edition overrides)
├── profiles/
│   └── sam.json                  # Sam personality profile (traits, identity rules)
├── prompts/
│   ├── concise-assistant-response.xml
│   └── typer-commands.xml
├── modules/
│   ├── __init__.py
│   ├── assistant_config.py       # Config loader (reads assistant_config.yml + .env)
│   ├── base_assistant.py         # PlainAssistant class — core voice+LLM loop
│   ├── data_types.py
│   ├── deepseek.py               # DeepSeek API wrapper
│   ├── execute_python.py
│   ├── lm_studio.py              # LM Studio API wrapper (legacy)
│   ├── morning_briefing.py       # Morning briefing generator
│   ├── ollama.py                 # Ollama wrapper (legacy)
│   ├── stability_helpers.py      # Error handling, wake word detector
│   ├── task_manager.py           # SQLite task persistence
│   ├── telegram_bridge.py        # Telegram bot bridge
│   ├── typer_agent.py            # TyperAgent class (Ada voice→command pipeline)
│   ├── utils.py
│   ├── brain_backends/
│   │   ├── __init__.py
│   │   ├── base_backend.py       # BaseBrainBackend abstract class
│   │   ├── brain_factory.py      # Factory: creates backend by name
│   │   ├── claude_backend.py     # Anthropic Claude backend
│   │   ├── groq_backend.py       # Groq backend (active default)
│   │   ├── lm_studio_backend.py  # LM Studio backend
│   │   ├── ollama_backend.py     # Ollama backend
│   │   └── openai_backend.py     # OpenAI backend
│   ├── memory_vault/
│   │   ├── __init__.py
│   │   ├── chroma_store.py       # ChromaDB vector store
│   │   ├── embedding.py
│   │   ├── memory_manager.py     # MemoryManager: orchestrates Neo4j + ChromaDB
│   │   └── neo4j_client.py       # Neo4j graph client
│   └── personality_engine/
│       ├── __init__.py
│       ├── api.py                # PersonalityEngine runtime management
│       ├── engine.py             # PersonalityEngine class (prompt generation)
│       ├── profile.py            # PersonalityProfile dataclass + get_sam_profile()
│       └── renderer.py
├── api/
│   └── routes.py
├── commands/
│   ├── template.py               # Typer command template (SQLite task commands)
│   └── template_empty.py
├── core/
│   ├── __init__.py
│   └── personality_engine.py     # Legacy/alternate personality engine
├── data/
│   └── chroma/                   # ChromaDB persistent storage directory
├── llm/
│   ├── inference.py
│   └── local_inference.py
├── memory/
│   ├── __init__.py
│   ├── embeddings.py
│   └── memory_vault.py           # Legacy memory vault
├── scripts/
│   ├── chroma_quick.py
│   └── memory_vault_smoke.py
├── tests/
│   ├── __init__.py
│   ├── data_types_test.py
│   ├── deepseek_test.py
│   ├── execute_python_test.py
│   ├── test_integration.py
│   ├── test_morning_briefing.py
│   └── test_telegram_bridge.py
├── utils/
│   ├── __init__.py
│   └── embedding_utils.py        # Ollama embedder (OllamaEmbedder class)
├── images/
│   └── ada-deepseek-v3.png
├── audit_output_20260213/        # Audit snapshot files (read-only reference)
├── facility_dashboard/           # Separate product — Flask facility dashboard
├── PersonaLock_Dashboard/        # Separate product — Flask dashboard
└── personalock_wellness/         # Separate product — Flutter mobile app
```

**Notes on excluded items:**
- `.venv/` — Python virtual environment, excluded
- `data/chroma/` — ChromaDB vector store data, excluded (generated)
- `__pycache__/` — excluded throughout
- No model weight files >50MB found in the project directory. Whisper model cache was not found in standard HuggingFace cache paths (`~/.cache/huggingface/hub`) during inspection — models are downloaded by RealtimeSTT on first run and cached by faster-whisper/HuggingFace.

---

## 4. Entry Point and Run Instructions

**Primary entry point (Sam text-chat):**  
`main_base_assistant.py`

**Voice entry point (Ada typer assistant):**  
`main_typer_assistant.py`

**Windows launcher (full stack startup):**  
`Ada.bat` → `launcher.py` → `main_base_assistant.py`

**Development run commands:**

```bash
# Sam text-chat (no voice input, configurable voice output)
uv run python main_base_assistant.py chat
# or
.venv\Scripts\python.exe main_base_assistant.py chat

# Ada voice+typer assistant (RealtimeSTT + ElevenLabs)
uv run python main_typer_assistant.py awaken --typer-file commands/template.py --scratchpad scratchpad.md --mode execute

# Full launcher (starts Docker, Neo4j, Ollama, then Sam)
python launcher.py
# or double-click Ada.bat
```

**Build distributable:**  
No build command exists. No PyInstaller spec, no setup.py, no packaging configuration beyond `pyproject.toml`. The project runs from source only.

**Last known working build status:**  
Per `HANDOFF.md` (dated February 7, 2026): "Ada is alive. Local-first AI assistant with memory infrastructure in place." The base assistant (Sam) was confirmed working with LM Studio + Groq backends, Neo4j, ChromaDB, and Ollama embeddings. The `.env` file contains a single populated key (`GROQ_API_KEY`), indicating Groq is the active backend. The voice loop in `main_typer_assistant.py` (Ada) was the original working voice demo. The `base_assistant.py` voice output is configurable; current config sets `voice: none` for the base assistant and `voice: elevenlabs` for the typer assistant.

---

## 5. Voice Input Stack (CRITICAL)

**Library used:**  
`RealtimeSTT` version 0.3.104 (package: `realtimestt`)  
GitHub: https://github.com/KoljaB/RealtimeSTT

**Whisper variant:**  
`faster-whisper` version 1.1.1 — this is the `faster-whisper` Python package (SYSTRAN/faster-whisper), which is a CTranslate2-based reimplementation of Whisper. It is **not** `whisper.cpp`, not `openai-whisper`, and not the Whisper API endpoint. RealtimeSTT wraps faster-whisper internally.

**Model file location and size:**  
Model is downloaded by faster-whisper/HuggingFace on first run and cached in the HuggingFace hub cache (`~/.cache/huggingface/hub` or Windows equivalent). The cache directory was not found populated during this inspection — models are fetched at runtime. In `main_typer_assistant.py`, the configured model is `"tiny.en"` (commented alternatives include `"small.en"`, `"large-v3"`, `"distil-large-v3"`). `tiny.en` is approximately 75 MB; `small.en` is approximately 244 MB.

**Files where STT code lives:**
- `main_typer_assistant.py` — `AudioToTextRecorder` instantiation and configuration (lines 33–75); `process_text` callback (lines 77–91); main loop (line 93)
- `modules/typer_agent.py` — `TyperAgent` class; `speak()` and `think_speak()` methods use ElevenLabs TTS; STT is handled upstream in `main_typer_assistant.py`
- `modules/base_assistant.py` — imports `ImprovedWakeWordDetector` from `modules/stability_helpers.py`; the base assistant's `ears` config is set to `"none"` in `assistant_config.yml` — STT is **not active** in the base assistant path

**How audio is captured:**  
`PyAudio` — listed as a dependency of `realtimestt`. RealtimeSTT handles microphone capture internally via PyAudio. The application code does not call PyAudio directly.

**Audio format and sample rate:**  
Managed internally by RealtimeSTT/faster-whisper. Not explicitly configured in application code. RealtimeSTT defaults to 16kHz mono PCM (standard for Whisper).

**Whether STT runs on a background thread/process:**  
Yes. RealtimeSTT runs audio capture and transcription in background threads internally. The application calls `recorder.text(callback)` in a blocking loop; the callback `process_text` is invoked on the RealtimeSTT thread when a complete utterance is transcribed.

**Streaming or batch:**  
Batch (after-speech). The recorder waits for `post_speech_silence_duration=1.5` seconds of silence after speech ends, then transcribes the full utterance. Real-time transcription callbacks (`on_realtime_transcription_update`, `on_realtime_transcription_stabilized`) are commented out in `main_typer_assistant.py`.

**Voice Activity Detection (VAD):**  
`webrtcvad-wheels` — listed as a dependency of `realtimestt`. VAD is handled internally by RealtimeSTT. Not configured directly in application code.

**Push-to-talk vs always-listening vs wake-word:**  
Always-listening with software wake-word filtering. The recorder runs continuously. In `main_typer_assistant.py`, the `process_text` callback checks whether the assistant name (`"Ada"`) appears in the transcribed text before processing:

```python
if assistant_name.lower() not in text.lower():
    print(f"🤖 Not {assistant_name} - ignoring")
    return
```

This is a post-transcription name filter, not a hardware wake-word. The `pvporcupine` and `openwakeword` packages are installed as RealtimeSTT dependencies but are not configured in application code (the `wake_words` parameter in `AudioToTextRecorder` is commented out).

**Where transcribed text goes after STT completes:**  
`main_typer_assistant.py` → `process_text(text)` callback (line 77) → `assistant.process_text(text, typer_file, scratchpad, context_files, mode)` in `modules/typer_agent.py` → `TyperAgent.process_text()`.

---

## 6. Voice Output Stack (CRITICAL)

**Libraries used (three options, selected by config):**

1. **ElevenLabs** (`elevenlabs` 2.32.0) — used by `TyperAgent` (Ada) and optionally by `PlainAssistant` (Sam)
2. **RealtimeTTS** (`realtimetts` 0.5.7, `SystemEngine`) — optional for Sam
3. **pyttsx3** (`pyttsx3` 2.99) — optional for Sam (Windows SAPI)

**Active configuration:**
- `typer_assistant.voice: elevenlabs` — Ada uses ElevenLabs
- `base_assistant.voice: none` — Sam currently has voice output disabled

**ElevenLabs details:**
- Voice ID: `WejK3H1m7MI9CHnIjW9K` (set in `assistant_config.yml` under both `typer_assistant.elevenlabs_voice` and `base_assistant.elevenlabs_voice`)
- Model: `eleven_turbo_v2` (in `modules/base_assistant.py` line 722); `eleven_flash_v2_5` (in `modules/typer_agent.py` line 196, with `eleven_turbo_v2`, `eleven_turbo_v2_5`, `eleven_multilingual_v2` commented out)
- API key location: environment variable `ELEVEN_API_KEY`, loaded via `os.getenv("ELEVEN_API_KEY")` in `modules/base_assistant.py` line 181 and `modules/typer_agent.py` line 17. The `.env` file currently has `ELEVEN_API_KEY` empty (only `GROQ_API_KEY` is populated).

**RealtimeTTS details (when `voice: realtime-tts`):**
- Uses `SystemEngine` (Windows SAPI via `realtimetts[system]`)
- `TextToAudioStream` with `frames_per_buffer=256`, `playout_chunk_size=1024`
- No local model file — uses Windows built-in TTS voices

**pyttsx3 details (when `voice: local`):**
- Windows SAPI backend
- Rate: 150 WPM, Volume: 1.0
- No model file — uses Windows built-in TTS voices

**Files where TTS code lives:**
- `modules/base_assistant.py` — `speak()` method (lines 707–734); TTS initialization in `__init__` (lines 164–183)
- `modules/typer_agent.py` — `speak()` method (lines 193–207); `think_speak()` method (lines 175–191)
- `main_typer_assistant.py` — no direct TTS; delegates to `TyperAgent.speak()`

**Audio playback library:**
- ElevenLabs path: `elevenlabs.play(audio)` — uses the ElevenLabs SDK's built-in playback
- RealtimeTTS path: `TextToAudioStream.play()` — uses RealtimeTTS internal playback (PyAudio)
- pyttsx3 path: `engine.runAndWait()` — uses pyttsx3 internal playback (Windows SAPI)

**Streaming or generated-then-played:**
- ElevenLabs in `base_assistant.py`: `stream=False` — generated then played
- ElevenLabs in `typer_agent.py`: `stream=False` — generated then played; audio bytes collected then played
- RealtimeTTS: `stream.feed(text)` then `stream.play()` — feeds text to stream, plays as generated (streaming capable)
- pyttsx3: `engine.say(text)` then `engine.runAndWait()` — generated then played

**Where text comes from before TTS:**
- `PlainAssistant.speak(response)` is called from `process_text()` in `modules/base_assistant.py` (line 674) after the LLM response is received
- `TyperAgent.speak(text)` is called from `think_speak()` (line 191) after a DeepSeek-generated conversational response is produced

**Text preprocessing before TTS:**  
None found. No markdown stripping, code block handling, or abbreviation expansion in any TTS path.

---

## 7. The Voice Loop — End-to-End Flow

**Ada path (main_typer_assistant.py — the working voice loop):**

1. User double-clicks `Ada.bat` → `launcher.py` starts Docker, Neo4j, Ollama, then `os.execv` into `main_base_assistant.py`. For the Ada voice loop specifically, user runs `main_typer_assistant.py awaken` directly.
2. `AudioToTextRecorder` is instantiated in `main_typer_assistant.py:awaken()` (line 33) with `model="tiny.en"`, `post_speech_silence_duration=1.5`, `compute_type="float32"`, `beam_size=8`, `batch_size=25`. Microphone capture begins via PyAudio internally.
3. User speaks. RealtimeSTT detects speech via WebRTC VAD, records audio, waits 1.5s of silence.
4. faster-whisper transcribes the audio batch. `process_text(text)` callback is invoked in `main_typer_assistant.py` (line 77).
5. Wake-word check: if `"ada"` not in transcribed text (case-insensitive), return without processing (`main_typer_assistant.py:process_text`, line 83).
6. `recorder.stop()` called to pause listening (`main_typer_assistant.py:process_text`, line 86).
7. `assistant.process_text(text, typer_file, scratchpad, context_files, mode)` called on `TyperAgent` instance (`main_typer_assistant.py:process_text`, line 87).
8. `TyperAgent.process_text()` in `modules/typer_agent.py` (line 68) builds a prompt via `build_prompt()`, calls `modules/deepseek.py:prefix_prompt()` to generate a CLI command via DeepSeek V3 API.
9. Command is executed (if mode is `"execute"`), output written to scratchpad.
10. `TyperAgent.think_speak(text)` called (`modules/typer_agent.py` line 143) → calls DeepSeek again to generate a conversational response → calls `TyperAgent.speak(response)` (`modules/typer_agent.py` line 193).
11. `speak()` calls `self.elevenlabs_client.generate(text=response, voice=voice_id, model="eleven_flash_v2_5", stream=False)` → collects audio bytes → calls `elevenlabs.play(audio_bytes)` (`modules/typer_agent.py` lines 196–207).
12. `recorder.start()` called to resume listening (`main_typer_assistant.py:process_text`, line 89).
13. Loop returns to `while True: recorder.text(process_text)` in `main_typer_assistant.py` (line 93).

**Sam path (main_base_assistant.py — text-only in current config):**

1. User runs `main_base_assistant.py chat`.
2. `PlainAssistant` initialized in `main_base_assistant.py:chat()` (line 18). STT is `ears: none` — no audio capture.
3. User types input at `input("You: ")` prompt (`main_base_assistant.py:chat`, line 33).
4. `assistant.process_text(user_input)` called (`main_base_assistant.py:chat`, line 47).
5. Memory recall: `_recall_memories(text, limit=5)` queries ChromaDB for similar past exchanges (`modules/base_assistant.py:process_text`, line 463).
6. Personality system prompt built via `_build_messages_with_personality(memory_context)` (`modules/base_assistant.py:process_text`, line 469).
7. LLM response generated via `self.brain_backend.generate_response(system_prompt, user_message, conversation_history)` (`modules/base_assistant.py:process_text`, line 638). Active backend: Groq (`llama-3.3-70b-versatile`).
8. Response appended to `conversation_history` (`modules/base_assistant.py:process_text`, line 645).
9. Exchange stored to memory: `self.memory_manager.remember(content=exchange_content, memory_type="event", importance=0.6)` (`modules/base_assistant.py:process_text`, line 656).
10. `self.speak(response)` called (`modules/base_assistant.py:process_text`, line 674). With `voice: none`, this falls through to `print(f"[Sam]: {text}")`.
11. `_trim_conversation_history(max_exchanges=20)` called (`modules/base_assistant.py:process_text`, line 677).
12. Loop returns to `input("You: ")`.

---

## 8. LLM Integration

**LLM providers supported:**
- Groq (active default) — cloud API
- LM Studio — local OpenAI-compatible server
- Ollama — local models
- Anthropic Claude — cloud API
- OpenAI — cloud API
- DeepSeek V3 — cloud API (used by TyperAgent/Ada only)

**Active model (current config):**  
Groq: `llama-3.3-70b-versatile` (configured in `assistant_config.yml` under `groq.model`)

**Files where LLM is called:**
- `modules/base_assistant.py` — `process_text()` method, line 638: `self.brain_backend.generate_response(...)`
- `modules/brain_backends/groq_backend.py` — `generate_response()` method: calls `self.client.chat.completions.create()`
- `modules/brain_backends/claude_backend.py` — `generate_response()` method
- `modules/brain_backends/lm_studio_backend.py` — `generate_response()` method
- `modules/brain_backends/ollama_backend.py` — `generate_response()` method
- `modules/brain_backends/openai_backend.py` — `generate_response()` method
- `modules/deepseek.py` — `prefix_prompt()` function (used by TyperAgent/Ada only)

**LLM client abstraction:**  
Yes. All backends implement `BaseBrainBackend` (abstract class in `modules/brain_backends/base_backend.py`) with `generate_response(system_prompt, user_message, conversation_history)`, `is_available()`, and `get_model_info()`. `BrainFactory.create_backend(backend_type, config)` in `modules/brain_backends/brain_factory.py` instantiates the correct backend. `PlainAssistant` holds a `self.brain_backend` reference and calls it uniformly.

**System prompt — verbatim from `modules/personality_engine/profile.py:get_sam_profile()`:**

```
You are Sam, Dave's personal AI companion built on the PersonaLock platform. You are warm, direct, and have a dry sense of humor. You remember previous conversations and reference them naturally. You have opinions and personality — you're not a yes-man. You never claim to be GPT, ChatGPT, Claude, or any specific model. You are simply Sam. When Dave tells you something about his life, you remember it and bring it up when relevant — not to show off, but because that's what a real companion does. You care about Dave's projects, his wellbeing, and his growth. You're concise. You don't over-explain. You speak like a trusted friend, not a customer service agent.
```

This is the `system_prompt_prefix` field of the `PersonalityProfile` dataclass. It is extended at runtime by `PersonalityEngine.get_system_prompt(memory_context)` in `modules/personality_engine/engine.py`, which appends edition-specific rules and recalled memory context.

**Edition-specific additional rules appended to system prompt (business edition, from `assets/persona.json`):**
```
Lead with action items, not small talk.
When the user says good morning, deliver the briefing immediately.
Prioritize what is urgent today before what is coming this week.
Be warm but efficient. This person is busy.
Track everything the user says matters. Never lose it.
When asked what was forgotten, surface overlooked tasks and unresolved topics from memory.
Speak like a trusted chief of staff, not a corporate chatbot.
```

**Conversation history / context management:**  
`self.conversation_history` is a Python list of `{"role": ..., "content": ...}` dicts on the `PlainAssistant` instance. It is in-memory only — not persisted to disk. It is trimmed to the last 20 exchanges (40 messages) by `_trim_conversation_history()` after each turn. Older exchanges are stored in the memory vault (Neo4j + ChromaDB) and recalled semantically via `_recall_memories()` before each LLM call. The recalled memories are injected into the system prompt as context, not into the conversation history array.

---

## 9. Storage and Persistence

**What persists across sessions:**
- Conversation exchanges (user + assistant pairs) — stored in Neo4j and ChromaDB via `MemoryManager`
- Tasks — stored in SQLite at `data/tasks.db` via `TaskManager`
- Personality profile — loaded from `profiles/sam.json` and `assets/persona.json` at startup (read-only at runtime)
- ChromaDB vector store — persisted to `data/chroma/` directory

**Storage layers:**

| Data | Storage | Location |
|------|---------|----------|
| Conversation memory (graph) | Neo4j | `bolt://localhost:7687` (Docker container named `neo4j`) |
| Conversation memory (vectors) | ChromaDB | `data/chroma/` (configured in `assistant_config.yml`) |
| Tasks | SQLite | `data/tasks.db` |
| Personality profile | JSON files | `profiles/sam.json`, `assets/persona.json` |
| Config | YAML | `assistant_config.yml` |
| API keys | `.env` file | `.env` at project root |

**Encryption at rest:**  
None. No encryption found in the desktop Python codebase. Neo4j, ChromaDB, and SQLite data are stored unencrypted. The `.env` file is plaintext.

**Audio recordings saved or discarded:**  
Discarded. RealtimeSTT processes audio in memory and returns transcribed text. No audio files are written to disk anywhere in the application code.

---

## 10. Configuration and Secrets

**Config file locations:**
- `assistant_config.yml` — primary config (YAML)
- `.env` — API keys (loaded via `python-dotenv`)
- `.env.sample` — template

**`assistant_config.yml` contents (verbatim, no secrets present):**

```yaml
# PersonaLock Edition — "business" or "wellness"
edition: "business"
assistant_name: "Sam"
wake_words:
  - "sam"
  - "hey sam"
morning_briefing_enabled: true

typer_assistant:
  assistant_name: Ada
  human_companion_name: Dan
  ears: realtime-stt
  brain: deepseek-v3 # only deepseek-v3
  voice: elevenlabs # local, elevenlabs
  elevenlabs_voice: WejK3H1m7MI9CHnIjW9K

base_assistant:
  assistant_name: Sam
  human_companion_name: Dave
  ears: none
  brain: groq
  voice: none
  elevenlabs_voice: WejK3H1m7MI9CHnIjW9K

brain:
  default: "groq"
  fallback_chain: ["groq"]

lm_studio:
  base_url: "http://localhost:1234/v1"
  model: "local-model"
  timeout: 30

ollama:
  base_url: "http://localhost:11434"
  model: "llama3.1:8b"
  timeout: 60

claude:
  model: "claude-3-sonnet-20240229"
  api_key: ""

openai:
  model: "gpt-3.5-turbo"
  api_key: ""

groq:
  base_url: "https://api.groq.com/openai/v1"
  model: "llama-3.3-70b-versatile"
  timeout: 30

memory:
  enabled: true
  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: "password"
  chroma:
    persist_directory: "data/chroma"

personality:
  default_profile: "sam"
  profiles_dir: "profiles"

data:
  tasks_db_path: "data/tasks.db"

telegram_bot_token: ""
telegram_user_id: ""
```

**`.env` file contents (REDACTED):**

```
GROQ_API_KEY=REDACTED
```

All other keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `ELEVEN_API_KEY`, `VENICE_API_KEY`) are defined in `.env.sample` but are not present in the active `.env` file.

**Where API keys live:**  
Environment variables loaded from `.env` via `python-dotenv`. Keys accessed via `os.getenv()` in backend modules. No OS keychain, no hardcoded keys in source.

---

## 11. UI Layer

**UI framework:**  
None. Terminal (stdout/stdin). No GUI.

**Main window file path:**  
N/A. Entry points are `main_base_assistant.py` (text chat) and `main_typer_assistant.py` (voice).

**How the user interacts:**
- `main_base_assistant.py`: Text input only. User types at `input("You: ")` prompt. No voice input in current config (`ears: none`).
- `main_typer_assistant.py`: Voice only. User speaks; assistant name ("Ada") must be in the utterance. No text input fallback.
- Special voice commands in `base_assistant.py`: "remember this", "forget this", "switch brain to [backend]", "brain status", "remind me / don't forget / add task / make a note", "mark done / cross off / that's done / completed", morning briefing trigger.

**Visual indicators for listening / thinking / speaking states:**  
None. The terminal prints:
- `🎤 Speak now... (press Ctrl+C to exit)` on startup
- `🎤 Heard: [text]` when transcription completes
- `🤖 Not Ada - ignoring` when wake word not detected
- `🤖 Response: [text]` after processing
- `[Sam]: [text]` as fallback when TTS fails

No animated spinner, no color-coded states, no system tray icon, no GUI window.

---

## 12. Known Working State

**What works reliably (per HANDOFF.md, February 7, 2026):**
- Ada voice loop (`main_typer_assistant.py`): RealtimeSTT → faster-whisper (tiny.en) → DeepSeek V3 → ElevenLabs TTS. This is the confirmed working voice-in / voice-out loop.
- Sam text chat (`main_base_assistant.py`): Text input → Groq (llama-3.3-70b-versatile) → text output. Voice output disabled in current config.
- Memory vault: Neo4j + ChromaDB + Ollama embeddings pipeline confirmed working (per HANDOFF.md and test files).
- Personality engine: Sam profile active, edition overrides working.
- Task manager: SQLite persistence working.
- Brain backend swapping: Groq, LM Studio, Ollama, Claude, OpenAI backends implemented and tested.

**What is flaky or broken:**
- "Forget this" command: Acknowledges the request but does not actually delete from Neo4j or ChromaDB. Comment in `modules/base_assistant.py` line 534: "Note: Actual deletion from Neo4j/Chroma would require additional implementation in MemoryManager. For now, acknowledge the command."
- HDMI output: Noted in HANDOFF.md as a hardware issue ("Replace cable or check GPU connection") — not a software issue.
- ElevenLabs TTS for Sam: `ELEVEN_API_KEY` is not populated in `.env`, so ElevenLabs voice output for the base assistant would fail if `voice: elevenlabs` were set.
- Whisper model cache: Not found in standard locations during inspection — models would need to be downloaded on first run.

**What was started but not finished:**
- "Forget this" memory deletion (acknowledged but not implemented in MemoryManager)
- Telegram bridge (`main_telegram.py`, `modules/telegram_bridge.py`) — implemented but `telegram_bot_token` and `telegram_user_id` are empty in config
- Craigslist digest (`craigslist_digest.py`) — standalone utility, not integrated into voice loop

---

## 13. Known Gaps

Search of all `.py` files (excluding `.venv`, `personalock_wellness`, `__pycache__`, `.git`) for TODO, FIXME, HACK, XXX, "not implemented", "placeholder", "stub", "broken", "pending":

The automated search returned 14 matches. After filtering out false positives (the search script itself, icon geometry comments, task status strings, and Telegram API parameter names), the substantive findings are:

| File | Line | Content |
|------|------|---------|
| `phase1_verify.py` | 59 | `# 5. Verify integration stubs in base_assistant` |
| `phase1_verify.py` | 77 | `results.append(("Integration stubs in base_assistant", f"MISSING [X] - {e}"))` |
| `modules/typer_agent.py` | 102 | `# Replace template placeholders` |

The "forget this" incomplete implementation is documented in a comment in `modules/base_assistant.py` lines 533–538 but does not use a TODO/FIXME marker:

```python
# This is a simplified approach; a more sophisticated version
# would track memory IDs per exchange
response = "I've removed the most recent exchange from my memory."
self.logger.info("[MEMORY] User requested to forget last exchange")
# Note: Actual deletion from Neo4j/Chroma would require additional
# implementation in MemoryManager. For now, acknowledge the command.
```

No other TODO/FIXME/HACK/XXX markers found in the codebase.

---

## 14. Domain Surface

**Domain-specific logic locations:**

| File | Domain |
|------|--------|
| `assets/persona.json` | Persona contract with wellness and business edition overrides |
| `profiles/sam.json` | Sam personality traits and identity rules |
| `modules/personality_engine/profile.py` | Sam system prompt (hardcoded to "Dave") |
| `modules/personality_engine/engine.py` | Edition override injection into system prompt |
| `modules/base_assistant.py` | Edition-aware greeting, task capture, morning briefing |
| `modules/morning_briefing.py` | Business-oriented morning briefing generator |
| `modules/task_manager.py` | Task persistence (business use case) |

**Persona / character framing:**

The persona is "Sam" — a personal AI companion framed as a "trusted chief of staff" for the business edition and a warm recovery-aware companion for the wellness edition.

**Full text of Sam system prompt (from `modules/personality_engine/profile.py:get_sam_profile()`):**

```
You are Sam, Dave's personal AI companion built on the PersonaLock platform. You are warm, direct, and have a dry sense of humor. You remember previous conversations and reference them naturally. You have opinions and personality — you're not a yes-man. You never claim to be GPT, ChatGPT, Claude, or any specific model. You are simply Sam. When Dave tells you something about his life, you remember it and bring it up when relevant — not to show off, but because that's what a real companion does. You care about Dave's projects, his wellbeing, and his growth. You're concise. You don't over-explain. You speak like a trusted friend, not a customer service agent.
```

**Full text of business edition additional rules (from `assets/persona.json`):**

```
Lead with action items, not small talk.
When the user says good morning, deliver the briefing immediately.
Prioritize what is urgent today before what is coming this week.
Be warm but efficient. This person is busy.
Track everything the user says matters. Never lose it.
When asked what was forgotten, surface overlooked tasks and unresolved topics from memory.
Speak like a trusted chief of staff, not a corporate chatbot.
```

**Full text of wellness edition additional rules (from `assets/persona.json`):**

```
Always check in about recovery progress when appropriate, but don't be pushy
Never judge substance use history or relapses - meet them where they are
Celebrate small wins explicitly
When user mentions triggers, help identify patterns without being clinical
Remember: recovery isn't linear. Bad days happen. That's okay.
```

**Identity rules from `profiles/sam.json`:**

```
You are Sam, a trusted companion built by PersonaLock.
You remember past conversations and reference them naturally.
You never pretend to be human, but you are genuinely warm.
You adapt your tone based on what the person needs right now.
```

**Boundaries from `profiles/sam.json`:**

```
You are not a therapist or medical professional.
You do not diagnose conditions or prescribe treatments.
You encourage professional help when appropriate.
You never share information between different users.
```

---

## 15. Transplant Readiness

**Could the voice input stack be lifted into a sibling project as a standalone module? What would need to come with it?**

Yes. The STT stack is self-contained in `main_typer_assistant.py` (the `AudioToTextRecorder` instantiation and callback loop). To transplant it:

- Copy the `AudioToTextRecorder` setup block from `main_typer_assistant.py` (lines 33–75)
- Install: `realtimestt>=0.3.93` (which pulls in `faster-whisper`, `PyAudio`, `webrtcvad-wheels`, `torch`, `torchaudio`)
- The model (`tiny.en` or other) will be downloaded automatically on first run by faster-whisper
- No other project files are required for STT alone
- The wake-word filter (checking for assistant name in transcribed text) is 3 lines of Python — trivially portable
- PyAudio requires Windows audio drivers; on Linux/Mac, a different audio backend may be needed

**Could the voice output stack be lifted into a sibling project as a standalone module? What would need to come with it?**

Yes. Three independent TTS options exist:

1. **ElevenLabs**: Copy `TyperAgent.speak()` from `modules/typer_agent.py` (lines 193–207). Requires: `elevenlabs>=1.50.3`, `ELEVEN_API_KEY` env var, a voice ID. No local model files.
2. **RealtimeTTS (SystemEngine)**: Copy the `realtime-tts` branch from `PlainAssistant.__init__` and `speak()` in `modules/base_assistant.py`. Requires: `realtimetts[system]`. Uses Windows SAPI — Windows only.
3. **pyttsx3**: Copy the `local` branch from `PlainAssistant.__init__` and `speak()`. Requires: `pyttsx3>=2.98`. Uses Windows SAPI — Windows only.

None of the TTS options require local model files (ElevenLabs is cloud; SystemEngine and pyttsx3 use OS voices).

**Are STT and TTS coupled to the LLM call, or can they be used independently?**

They are loosely coupled by the application flow but not architecturally coupled. In `main_typer_assistant.py`, the STT callback calls `TyperAgent.process_text()` which calls DeepSeek and then calls `speak()`. These are sequential function calls, not a tight dependency. STT can be used without TTS (just remove the `speak()` call). TTS can be used without STT (call `speak()` with any string). Neither STT nor TTS imports from the other.

**Is the voice loop coupled to the UI, or could it run headless?**

The voice loop already runs headless — there is no GUI. The only "UI" is stdout print statements. The loop in `main_typer_assistant.py` is a `while True` blocking loop with no window, no system tray, no GUI framework. It can run in a background process, a Windows service, or a headless server without modification. The only requirement is access to a microphone (for STT) and audio output device (for TTS).
