# Voice In / Voice Out — Roadmap

**Consumer edition (what ships now):**

| Layer | v0 (now) | Next |
|-------|----------|------|
| **Voice out** | Windows local TTS (`pyttsx3` / SAPI). "Speak replies" checkbox in GUI. | ElevenLabs optional tier; voice picker |
| **Voice in** | **Mic** button → `speech_recognition` + Google Web Speech (needs internet). | CPU Whisper in-process; wake word |
| **Workaround** | Windows Win+H dictation into chat box (Dave-verified) | Native mic UI with live partial text |

**Dave edition (dev stack):**

- RealtimeSTT + faster-whisper on CPU (`small.en`, int8)
- RealtimeTTS / ElevenLabs optional
- VRAM reserved for Kobold on M40

**Not in consumer PyInstaller bundle (too heavy):**

- `torch`, RealtimeSTT, RealtimeTTS (excluded intentionally)

**To test voice locally (dev):**

```powershell
cd D:\dev\PersonaLock
$env:PERSONALOCK_CONFIG="assistant_config.consumer.yml"
python main_gui_assistant.py chat
```

Enable Mic, check "Speak replies", allow microphone permission when Windows prompts.

**Rebuild portable zip after voice changes:**

```powershell
.\scripts\build_consumer.ps1
.\scripts\package_for_janice.ps1
```
