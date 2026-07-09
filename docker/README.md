# Arden Docker services

## Open Notebook (Notebooks tab)

### Dave — native Windows (preferred, no Docker)

One-time setup (~20 min when you have time):

```powershell
D:\dev\Arden\scripts\setup_open_notebook_native.ps1
```

Daily start — double-click:

```
D:\dev\Arden\start-open-notebook-native.bat
```

Then wire Venice + Ollama:

```powershell
python D:\dev\Arden\docker\wire_open_notebook_providers.py
```

UI: http://127.0.0.1:8502

### Docker (dev smoke test only)

```powershell
cd D:\dev\Arden\open-notebook
docker compose up -d
```

Stop when done:

```powershell
cd D:\dev\Arden\open-notebook
docker compose down
```

| Service | URL |
|---------|-----|
| Web UI | http://localhost:8502 |
| REST API | http://localhost:5055 |
| Health | http://localhost:5055/health |
| SurrealDB | localhost:8000 (internal) |

Smoke test (2026-06-09): API `{"status":"healthy"}`, UI on :8502.

---

## Venice AI — Open Notebook setup (one wallet for demos)

Venice is already the default for **NURA Connect** and **Arden Desktop** chat. Wire the same key into Open Notebook so doc chat and notebooks use your existing balance (~975 credits left as of 2026-06-09).

### Where the key lives

Copy from either file (same value):

- `D:\dev\Arden\engine\.env` → `VENICE_API_KEY=...`
- `D:\dev\PersonaLock\.env` → `VENICE_API_KEY=...`

Do not commit these files. Regenerate at [venice.ai](https://venice.ai) if the key stops working.

### Automated wiring (recommended)

Dave's Venice key is read from `D:\dev\Arden\engine\.env`. Re-run anytime after a fresh Open Notebook database:

```powershell
cd D:\dev\Arden\docker
python wire_open_notebook_providers.py
```

This creates:

- **Venice AI (Dave)** — OpenAI Compatible, chat model `llama-3.3-70b`
- **Ollama local (Dave)** — embeddings `nomic-embed-text` via `host.docker.internal:11434`
- Default chat + embedding slots in Settings

Wired 2026-06-09: Venice test passed (88 models), Ollama test passed.

### Click-by-click (Web UI — manual fallback)

1. Open **http://localhost:8502** (Docker must be running).
2. Go to **Settings** (gear) → **API Keys** (or **Credentials**).
3. Click **Add Credential**.
4. Choose provider: **OpenAI Compatible** (Venice uses an OpenAI-style API).
5. Fill in:
   - **API Key** — paste `VENICE_API_KEY` from `.env` above
   - **Base URL** — `https://api.venice.ai/api/v1`
6. Save the credential.
7. Go to **Settings → Models** (or model picker when creating a notebook).
8. Add or select a **chat** model:
   - Provider: your new OpenAI Compatible / Venice credential
   - **Model ID** — `llama-3.3-70b` (matches NURA Connect + Arden consumer config)
9. Open a notebook, upload a source (PDF, URL, etc.), and run **Chat** to confirm replies stream.

### Embeddings — keep local (free)

Venice does **not** supply embeddings for Open Notebook. Use **Ollama** on your M40 stack:

1. Ensure Ollama is running with `nomic-embed-text` pulled:
   ```powershell
   ollama pull nomic-embed-text
   ```
2. In Open Notebook **Settings → API Keys**, add **Ollama** if not auto-detected:
   - Base URL: `http://host.docker.internal:11434` (Docker on Windows → host Ollama)
   - Or `http://localhost:11434` if using a native/dev install instead of Docker
3. In **Settings → Models**, set the **embedding** model to `nomic-embed-text` via Ollama.

If ingest/search fails, check that Ollama is reachable from the container (`host.docker.internal` is the usual Windows fix).

### Optional: Groq fallback

Arden consumer config falls back to Groq. Only add Groq in Open Notebook if you want a backup when Venice is down — not required for demos.

### NextDNS

If Venice requests fail from the desktop or container, whitelist **api.venice.ai** in NextDNS.

### What stays on other providers

| Use case | Provider |
|----------|----------|
| NURA + Arden chat + Open Notebook doc Q&A | **Venice** (this guide) |
| Open Notebook embeddings | **Ollama** local |
| Heavy Claude-specific work | **Anthropic** (Arden brain swap) |
| Home $0 chat | **Kobold / Gemma** on M40 |

Podcast / TTS warnings in Docker logs are normal until you add ElevenLabs or OpenAI TTS — skip for v1.

---

## Neo4j (Arden engine memory — optional)

PersonaLock/Arden engine compose lives in `D:\dev\Arden\engine\docker-compose.yml`.

Dave already runs `neo4j` on :7474 / :7687 — separate from Open Notebook.
