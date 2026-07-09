# Cloud Brain Policy — Consumer Edition

**Default (2026-06):** Venice AI → `llama-3.3-70b`  
**Fallback:** Groq → `llama-3.3-70b-versatile`

## Why Venice over Groq

| | Venice | Groq |
|---|--------|------|
| Speed | Fast | Extremely fast (often faster) |
| Model stability | Consistent product | Frequent model ID churn |
| Privacy posture | No logging, proxy architecture | Standard cloud API |
| Dave's experience | Reliable day-to-day | Impressive bursts, less dependable |

Soul + memory stay local either way. Only the inference request hits cloud.

## Scar tissue

Recovery **scar tissue** (harm-reduction prompts, never "I'm an AI", etc.) is a **Wellness edition** layer — not required in general consumer Sam. Import when shipping to facilities or recovery lane.

## Dave dev stack

Kobold + Gemma 4 12B on M40 remains the dogfood brain (`assistant_config.yml`).
