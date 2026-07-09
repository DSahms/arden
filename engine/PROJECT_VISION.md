# PersonaLock — Project Vision

> **"Keep the soul. Change the brain."**

---

## What Is PersonaLock?

PersonaLock is a **stateful wrapper** that sits between the user and any LLM. It decouples identity (personality, memory, preferences) from inference (the LLM itself).

The LLM is just a brain — interchangeable, upgradeable, disposable.  
PersonaLock holds everything else.

---

## The Problem We're Solving

**AI's Amnesia Crisis**

Mainstream assistants like ChatGPT and Claude are amnesiac gods — incredible capabilities, zero continuity. Every model update resets personality. Every vendor switch starts from zero. Users are forced to re-explain context endlessly.

PersonaLock breaks that dependency. **You own the continuity.**

---

## The Architecture

```
User Input
    ↓
┌─────────────────────────────┐
│     PersonaLock Wrapper     │
│  - Inject Persona & Memory  │
│  - Manage State             │
└─────────────────────────────┘
    ↓ (Context Injection)
┌─────────────────────────────┐
│   Swappable LLM Backends    │
│  Ollama | OpenAI | Claude   │
└─────────────────────────────┘
    ↓
Response (with personality + memory context)
```

---

## The Four Components

| Component | Purpose | Location | Swappable Options |
|-----------|---------|----------|-------------------|
| **Ears** (STT) | Capture voice | User's choice | RealtimeSTT, Whisper, cloud APIs |
| **Memory** (State) | Store facts, history, preferences | Always local | Neo4j, ChromaDB, SQLite |
| **Brain** (LLM) | Reasoning and response generation | Local OR cloud | Ollama, LM Studio, GPT, Claude, DeepSeek |
| **Voice** (TTS) | Speak responses | User's choice | Piper, pyttsx3, ElevenLabs |

---

## Key Principles

### 1. Decouple State from Brain
Personality and memory live **outside** the LLM. When you swap models, your assistant's identity persists.

### 2. Soul is Local, Brain is Flexible
- **Always local**: Memory Vault, Personality Engine, user data
- **User's choice**: LLM can be local (privacy, cost) or cloud (power, capability)

### 3. Modularity Over Monoliths
Every component is swappable. Balance privacy, cost, and performance per use case.

---

## What PersonaLock Is NOT

- ❌ A chatbot that resets every session
- ❌ A cloud-dependent service
- ❌ A generic assistant with no personality
- ❌ Tied to any single LLM vendor

---

## Success Criteria

> You say "Ada, I hate mornings" today.  
> Next week you say "Ada, when should we schedule this?"  
> Ada says "Afternoon — you mentioned you hate mornings."

**The assistant remembers. The assistant knows you. The brain doesn't matter.**

---

## Use Cases

1. **Engineer's Co-Pilot** — Always-on assistant with scratchpad for multi-step tasks
2. **Brand Voice** — White-labeled assistant that maintains persona across LLM upgrades
3. **Private Wellness Journal** — Fully offline, voice-first reflection space

---

## The Tagline

**Portable AI identity — persistent memory and personality that survives any brain swap.**

---

*Last updated: January 27, 2026*
