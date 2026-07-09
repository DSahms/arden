# Arden Consigliere — Phase 6 Ship Guide

**Edition:** Consigliere (business chief-of-staff on the same Arden rail as Brittany)  
**Powered by Rémanence**

---

## What Consigliere adds (v1)

| Feature | Consumer (Brittany) | Consigliere (Dave) |
|---------|---------------------|---------------------|
| Intake domains | 6 companion domains | **+3 business domains** (stakes, risks, accountability) |
| Morning briefing | Off | **On** — tasks, overdue, this week |
| Task capture | Off | **On** — “remind me…”, Tasks panel |
| Accountability alerts | Personal care only | **Risk flags** before meetings/travel (facts only) |
| Brains | Venice, Groq, Kobold | **+ Claude, Ollama, LM Studio** when configured |
| Persona | Plain friend | **Chief of staff** — direct, efficient |

Same data folder: `%LOCALAPPDATA%\Arden\` — same soul, richer domains.

---

## Launch (Dave)

```powershell
D:\dev\arden\engine\Arden-Consigliere.bat
```

Or:

```powershell
cd D:\dev\arden\engine
$env:ARDEN_EDITION = "consigliere"
python main_gui_assistant.py chat
```

---

## Acceptance

```powershell
cd D:\dev\arden\engine
$env:ARDEN_EDITION = "consigliere"
python -c "from modules.consigliere_acceptance import run_consigliere_acceptance; raise SystemExit(run_consigliere_acceptance())"
```

---

## Business domain pack (intake C)

1. **Business stakes** — clients, deals, key relationships  
2. **Risk flags** (opt-in) — casinos, bars, high-stress venues — *speak up before*  
3. **Accountability** (opt-in) — recovery + business boundaries  

North Star example: Hard Rock meeting + stored gambling fact → heads-up in chat.

---

## Hardware bundle (SKU — not built yet)

Future **Consigliere desk bundle** (documentation only for v1):

| Component | Role |
|-----------|------|
| Mini PC or NUC | Runs Arden Consigliere locally |
| Optional Kobold box | Local brain when cloud off |
| Encrypted USB backup | Corpus export (Phase 6.2+) |

No separate installer — same `Arden.exe` with `ARDEN_EDITION=consigliere`.

---

## Not in v1

- Separate git fork  
- Facility / NURA guardrails  
- Email OAuth or agent loops  
- Play Store / multi-tenant business deploy  

---

*Phase 6 v1 shipped in codebase — hardware bundle and field deploy remain future.*
