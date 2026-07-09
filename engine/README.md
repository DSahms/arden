# PersonaLock Desktop Edition

**Keep the soul. Change the brain.**

A local-first personal AI assistant. Sam (persona + memory) persists on your machine. The LLM backend is swappable — local KoboldCpp by default, cloud optional.

## Quick start

**Prerequisites:** Docker Desktop, Neo4j (via compose), Ollama (`nomic-embed-text`), KoboldCpp on port 5001.

```powershell
cd D:\dev\PersonaLock
.\scripts\bootstrap.ps1
python main_base_assistant.py chat          # terminal (Dave)
python main_gui_assistant.py chat           # window (Janice)
```

Say `brain status` to confirm the active backend.

## Architecture

| Layer | What | Where |
|-------|------|-------|
| **Soul** | Sam persona, edition rules | `profiles/`, `assets/persona.json` |
| **Memory** | Graph + semantic recall | Neo4j + ChromaDB + Ollama embeddings |
| **Brain** | Inference (swappable) | KoboldCpp, Ollama, Groq, Claude, OpenAI, Venice, Gemini |
| **Shell** | Text chat CLI | `main_base_assistant.py` |

Persona and memories **never** live in the cloud. Cloud backends only receive the assembled prompt for one turn.

## Default stack (Dave's M40)

- **Brain:** Gemma 4 12B via KoboldCpp (`http://127.0.0.1:5001/v1`)
- **Embeddings:** Ollama `nomic-embed-text` on CPU
- **STT (future):** CPU-first Whisper — VRAM reserved for inference

See `DESKTOP_MASTER_PLAN.md` for the full roadmap.  
**Ship target:** `docs/JANICE_EDITION.md` → `PersonaLock_Setup.exe`

## Configuration

- `assistant_config.yml` — brain, memory, persona, STT settings
- `.env` — API keys for optional cloud backends (copy from `.env.sample`)

## Commands (in chat)

| Command | Action |
|---------|--------|
| `brain status` | Show active backend |
| `switch brain to kobold` | Swap inference backend |
| `remember this` | Mark last exchange important |
| `forget this` | Delete last stored memory |

## Entry points

| Script | Purpose |
|--------|---------|
| `main_base_assistant.py chat` | **Sam** — text assistant (primary) |
| `launcher.py` | Full stack: Docker → Neo4j → Ollama → Sam |
| `main_typer_assistant.py awaken` | **Ada** — voice + Typer commands (legacy path) |

## Tests

```powershell
python test_brain_backends.py
python test_memory_pipeline.py
```

## Legacy code

The `api/`, `memory/`, `core/`, and `llm/` directories are a **deprecated** parallel stack. Active code lives in `modules/`. See `DEPRECATED.md`.

## Naming

- **PersonaLock** — parent brand
- **Sam** — persona / soul (base assistant)
- **Ada** — voice shell (Typer assistant)
