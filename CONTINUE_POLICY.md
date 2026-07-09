# Arden — Autonomous work policy

**Standing permission (Dave, 2026-06-09):** Keep marching on Arden without waiting for "continue" after each step.

## When the agent keeps going

- Next item in `ARDEN_DESKTOP.md` phases
- Rename/migrate engine copy under `D:\dev\Arden\` only
- Docker compose, shell scaffolding, docs in `D:\dev\Arden\`
- Fix obvious breakages from the migration

## When the agent stops and asks

| Blocker | What Dave provides |
|---------|-------------------|
| Missing API key | Anthropic / Venice / Groq in `.env` or confirm reuse from PersonaLock |
| Docker not running | Start Docker Desktop for Open Notebook smoke test |
| Destructive choice | e.g. delete PersonaLock repo, migrate `%LOCALAPPDATA%\PersonaLock` data |
| Product ambiguity | NURA Connect stays untouched unless Dave says otherwise |

## What Dave does *not* need to do

- Say "continue" after every completed subtask
- Queue "continue" in chat — optional nudge only, not required
- Micromanage phase order — plan in `ARDEN_DESKTOP.md` is the queue

## Off limits

- `D:\dev\PersonaLock\personalock_wellness\` (NURA Connect)
- Force-push, git commits (unless Dave asks)
