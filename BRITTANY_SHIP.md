# Ship Arden Desktop to Brittany

**Face of product:** Arden Desktop · **Powered by Rémanence**

## What Brittany gets (v1)

- `release/Arden-Portable.zip` — single Windows install, no Docker
- **Chat** — Venice / Groq / optional local Kobold, streaming, sessions
- **Help me know you** — skippable intake (A/B/C), save & resume
- **What I know about you** — view / edit / delete confirmed facts
- **Sources** — PDF/txt upload, ask questions (RAG)
- **Tools** — export chat or facts to Word, email draft → clipboard, read-only calendar (.ics)
- Local data: `%LOCALAPPDATA%\Arden\`

## Dave — ship loop (one command)

```powershell
cd D:\dev\arden\engine
.\scripts\ship_brittany.ps1
```

Or step by step:

```powershell
.\scripts\build_arden_consumer.ps1
.\scripts\package_for_brittany.ps1
python main_gui_assistant.py acceptance-test
```

Quick smoke on your machine:

```powershell
cd D:\dev\arden\engine\release
Expand-Archive -Force Arden-Portable.zip -DestinationPath $env:TEMP\arden-test
& "$env:TEMP\arden-test\Arden.exe"
```

## Brittany — 5-minute test checklist

1. Install from zip → desktop shortcut opens
2. First run → keys + pick **Get started** or **Quick get-to-know-you**
3. Chat → brain dropdown shows **Venice Cloud**
4. **Sources** → add a `.txt` file → ask a question
5. **Tools** → export chat or draft email (clipboard)
6. **What I know about you** → facts listed after intake

## Email

Send: `Arden-Portable.zip` + `release/README-FOR-BRITTANY.txt`
