# Deprecated Code — Do Not Extend

These paths are a **legacy parallel stack** from an earlier architecture. The active PersonaLock Desktop code lives in `modules/`.

## Deprecated directories

| Path | Was | Use instead |
|------|-----|-------------|
| `api/` | FastAPI routes | `modules/base_assistant.py` |
| `memory/` | Old memory layer | `modules/memory_vault/` |
| `core/` | Old personality engine | `modules/personality_engine/` |
| `llm/` | Old inference | `modules/brain_backends/` |

## Deprecated files

| Path | Reason |
|------|--------|
| `modules/personality_engine/api.py` | Broken duplicate engine; removed |
| `main.py` | Empty placeholder |

## Policy

- **Do not** add features to deprecated paths
- **Do not** delete until smoke tests confirm no imports
- **Lift** useful patterns into `modules/` if needed

Active north star: `DESKTOP_MASTER_PLAN.md`
