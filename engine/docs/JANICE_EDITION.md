# Janice Edition — Finish Line

**TLDR:** `PersonaLock_Setup.exe` → install → desktop icon → talk to Sam. No Docker. No terminal.

---

## Finish line test

1. Email Janice `PersonaLock_Setup.exe`
2. She installs alone
3. She talks to Sam
4. Tomorrow — Sam still remembers her
5. She never hears the word Docker

**Pass = shipped.**

---

## Dave edition vs Janice edition

| | Dave | Janice |
|---|------|--------|
| Brain | Kobold + Gemma (M40) | Groq/Venice (cloud) |
| Memory | Neo4j + Chroma | SQLite + Chroma (portable) |
| Install | Dev stack | One `.exe` installer |
| Config | `assistant_config.yml` | `assistant_config.consumer.yml` |

Same Sam soul. Different plumbing.

---

## Build gates

### Gate 1 — Sam works without Dave
- [x] SQLite memory backend (replace Neo4j for consumer)
- [x] Chroma embedded (already works)
- [x] Cloud brain default (Groq)
- [x] Consumer bootstrap — `%LOCALAPPDATA%\PersonaLock\`
- [x] Simple chat window — `python main_gui_assistant.py chat`

### Gate 2 — Installer
- [x] PyInstaller → `dist/PersonaLock/PersonaLock.exe` (run `.\scripts\build_consumer.ps1`)
- [x] Portable ship package → `release/PersonaLock-Portable.zip` + `Install-Sam.ps1`
- [ ] NSIS → `PersonaLock_Setup.exe` (optional; `makensis` not installed on Dave's PC)
- [x] First-run wizard (name, optional API key)
- [x] Desktop shortcut (defined in `installer.nsi`)

### Gate 3 — Ship
- [x] Preflight script — `.\scripts\preflight_ship.ps1` (zip extract + exe smoke)
- [ ] Dave double-click test (Install-Sam.ps1 → Sam icon → chat)
- [ ] Janice test on clean Windows laptop

---

## Run consumer edition (dev test)

```powershell
Sam.bat
# or: python main_gui_assistant.py chat  (with PERSONALOCK_EDITION=consumer)

# Data + memories: %LOCALAPPDATA%\PersonaLock\
```

## Build + ship to Janice

```powershell
.\scripts\build_consumer.ps1
.\scripts\package_for_janice.ps1
.\scripts\preflight_ship.ps1        # full gate before email
```

Send her `release/PersonaLock-Portable.zip`. She unzips, runs `Install-Sam.ps1`, clicks **Sam** on desktop.

Draft email: `release/EMAIL-TO-JANICE.txt`

Optional one-click installer:
```powershell
winget install NSIS.NSIS
.\scripts\build_setup.ps1           # -> release/PersonaLock_Setup.exe
```

**Logs (if she needs help):** `%LOCALAPPDATA%\PersonaLock\logs\`

Optional NSIS: `makensis packaging/installer.nsi` → `PersonaLock_Setup.exe`

---

## Phase 7 (after Janice ships)

ESP32 room nodes → mic/speaker → central Sam server on Dave's PC. See `DESKTOP_MASTER_PLAN.md`.
