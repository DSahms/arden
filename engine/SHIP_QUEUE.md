# PersonaLock Ship Queue

**Say "continue" to run the next automatable item.**  
**Finish line:** Janice installs Sam, talks, remembers — no Docker.

Last updated: 2026-06-08

---

## Queue (top = next)

| # | Task | Owner | Status | Command / doc |
|---|------|-------|--------|----------------|
| 1 | Full preflight (zip + tests + exe smoke) | Auto | DONE | `.\scripts\preflight_ship.ps1` |
| 2 | Janice install simulation | Auto | DONE | `.\scripts\simulate_janice_install.ps1` |
| 3 | Groq brain smoke | Auto | DONE | `$env:PERSONALOCK_SMOKE_BRAIN="1"; python main_gui_assistant.py smoke-test` |
| 4 | Memory persistence (headless) | Auto | DONE* | `python scripts\test_memory_persist.py` |
| 5 | Dave GUI test | Dave | DONE | Verified live chat + install |
| 6 | Custom assistant name onboarding | Auto | DONE | first-run picks name + your name |
| 7 | Voice in/out v0 (Mic + Speak) | Auto | DONE | `docs/VOICE_ROADMAP.md` — rebuild zip to ship |
| 8 | Email Brittany the zip | Dave | **NEXT** | `release/EMAIL-TO-BRITTANY.txt` |
| 7 | Brittany feedback / investor convo | Brittany | WAITING | — |
| 8 | Janice laptop test | Janice | BACK BURNER | — |
| 8 | NSIS `PersonaLock_Setup.exe` | Optional | SKIPPED | `winget install NSIS.NSIS` then `.\scripts\build_setup.ps1` |

---

## Ship artifact

```
release/PersonaLock-Portable.zip   (~284 MB)
release/Install-Sam.ps1
release/Uninstall-Sam.ps1
release/README-FOR-JANICE.txt
```

---

## After Janice ships (not in this queue)

- Phase 4: encryption at rest
- Entity reconciler (Patty/Sherri)
- Phase 7: ESP32 room nodes

---

\* Step 4 passes SQLite persist always; Groq session recall skips if `.env` key is invalid.

---

## One command (runs all auto gates)

```powershell
cd D:\dev\PersonaLock
.\scripts\ship_queue.ps1
```
