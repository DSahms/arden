# PersonaLock Mobile — Claude Memory Export

> Scope: the **mobile-delivered** editions of PersonaLock — the **Wellness Edition** (Flutter Android app "Sam") and the **Everyday Edition** (consumer mobile companion). Desktop Edition and Consigliere appear only where they touch the mobile story. Every item is tagged **FACT** (established in project instructions/memory), **RECOLLECTION** (remembered, softer confidence), or **OPEN** (unresolved / pending).

---

## Executive Summary

- **FACT** — PersonaLock is a privacy-first, multi-edition AI companion platform. The two *mobile* editions are **Wellness** ("Sam," the active focus) and **Everyday** (consumer, roadmap stage, forked from the Wellness codebase).
- **FACT** — Founding philosophy: **"Soul stays, brain swaps."** Identity, memory, and personality persist independently of whichever LLM handles inference. The model is a stateless reasoning engine; persona and state live outside it and are injected every prompt.
- **FACT** — Wellness is a Flutter/Dart Android companion for addiction-recovery facilities, paired with a real-time, color-coded counselor dashboard. Storage is local and encrypted; nothing is transmitted. Sold to facilities; residents pay $0.
- **FACT** — Built solo by **Dave Sahms** under **AI Integration & Consulting** (Gloucester Township, NJ). Dave has lived experience in the recovery community, treated as both a design input and a sales credibility asset.
- **OPEN** — Highest-priority mobile dev gap is the crisis/safety stack (crisis intervention flow, urge delay timer, distraction toolkit, escalation logic).

---

## Product Identity

- **FACT** — Platform name: **PersonaLock**. Mobile editions: **Wellness Edition** and **Everyday Edition**.
- **FACT** — Wellness companion persona name: **"Sam."**
- **FACT** — Wellness target market: addiction-recovery facilities (IOP, outpatient, sober living, and inpatient via the tablet track). Residents are end users; facilities are the buyer.
- **FACT** — Everyday Edition target: ordinary consumers, *not* AI enthusiasts. Design rule: agent capabilities must be **invisible infrastructure**, never surfaced as technical features.
- **FACT** — Everyday three-phase pricing: Phase 1 $9.99 (companion + persistent memory — "cave wall / legacy" mission); Phase 2 $14.99 ("gentle agents": reminders, journaling, goal tracking, message drafting, no external integrations); Phase 3 $19.99 (opt-in integrations: calendar, email, tasks).
- **FACT** — Differentiator stack for Wellness: automatic behavioral-signal detection **+** local-first encrypted storage **+** signals-not-content counselor visibility. No direct market equivalent.
- **RECOLLECTION** — The persona-as-product idea is the throughline across all editions: the persona contract consistency *is* the product; the backend is infrastructure, not identity.

---

## Architecture

- **FACT** — Mobile stack: **Flutter / Dart** (Wellness today; Everyday forks from it).
- **FACT** — On-device encryption: **SQLCipher / AES-256**. Wellness transmits no data — positioned as exceeding HIPAA.
- **FACT** — Default Wellness backend: **Venice.ai** (Llama 3.3 70B, "Private" data classification, no logging). The model identifier is a configurable string in `venice_ai_provider.dart`.
- **FACT** — Multi-backend "brain swap" targets: Venice, Ollama, Claude API, OpenAI, and bring-your-own-key.
- **FACT** — **Persona Contract** (`persona.json`): defines personality traits with edition-specific overrides and runtime adjustment; works across all backends.
- **FACT** — **Behavioral observer pipeline** is **fully rule-based** — keyword/pattern matching mapped to concern levels (green / yellow / orange / red). No model inference, no PHI, no diagnosis. The counselor dashboard surfaces **signals, not conversation content.**
- **FACT** — Load-bearing disclaimer (architecturally and legally): *"All detection is keyword and pattern based. No diagnosis is made or implied."*
- **FACT** — Wellness local DB schema: **7 tables** — `conversations`, `messages`, `memories`, `mood_entries`, `patterns`, `settings`, `schema_meta`.
- **FACT** — Auth: PIN / biometric (a feature directly driven by early validator feedback — see "Only in Claude").
- **FACT** — CI/CD via **Codemagic** (Android, iOS, Web). iOS builds require macOS, handled through **MacinCloud**.
- **RECOLLECTION** — Sam's voice/harm-reduction design: the system prompt should make Sam respond to harm-reduction questions the way a peer-support specialist would — honest, non-judgmental, focused on keeping people alive. Facility-configurable harm-reduction level is the intended mechanism, not a hardcoded stance.
- **RECOLLECTION** — Inpatient tablet track architecture: facility-owned Android tablets, kiosk-locked to PersonaLock, no SIM / no open internet, running structured therapeutic modules.

---

## Decisions

- **FACT** — Wellness is **facility-subscription only; residents pay $0.**
- **FACT** — Wellness pricing: Beta **$99/mo** → Starter (≤20 beds) **$199/mo** → Professional (21–60) **$399/mo** → Enterprise (61–100) **$599/mo**.
- **FACT** — Sales-partner model: **20–25% recurring commission + $100 signing bonus** per signed facility. Goal: a recovery-community sales partner carries facility sales while Dave builds.
- **FACT** — For Wellness, **avoid "Uncensored" Venice model variants.** Uncensored options are reserved for the adult Everyday Edition only.
- **FACT** — Harm-reduction posture is **configurable per facility** via the admin dashboard; Dave deliberately removed his personal views from the product philosophy so facilities set their own level.
- **FACT** — Counselor visibility is **signals, not content** — a deliberate, non-negotiable architectural and compliance decision.
- **FACT** — Everyday agent capabilities = **invisible infrastructure** (vs. OpenClaw's developer-facing approach).
- **FACT** — **Redundancy is non-negotiable**: every paid tool/subscription requires a backup at equivalent tier (mirrors the swappable-backend architecture).
- **FACT** — Workflow split: **Opus** does architecture/strategy/prompt drafting; **Cline** (Sonnet) executes code and "doesn't think." Cline prompts delivered as a single copyable code block with no internal markdown.
- **RECOLLECTION** — **Spanish-language support** is a strategic priority (not a localization checkbox) given regional demographics. Llama 3.3 70B already answers in Spanish; remaining work is Flutter i18n plus a system-prompt language-mirroring instruction.

---

## Contradictions & Stale Names

- **OPEN / Contradiction** — **Completion state.** The current project instructions say Wellness "Phase 1 is ~20% complete," while memory elsewhere describes Wellness as in **beta/sales mode** with active facility relationships (Crowley, Solace, Noel's). These may describe different layers (mobile feature build vs. go-to-market), but the framing conflicts and should be reconciled. (For contrast, the **Desktop** Edition is described as ~83% complete — a separate product, not the mobile one.)
- **Stale / overloaded name** — **"Sam"** is used for *both* the Wellness mobile companion persona *and* the Desktop default personality profile. **"Ada"** is the Desktop assistant name / wake word. Risk of confusion across editions.
- **Stale / artifact** — **"Klein"** appears in dictation as a voice-to-text mis-rendering of **"Cline"** (the VS Code coding agent). Not a real product/name.
- **Minor** — Beta cohort phrasing: "15 beta testers in Crowley (all male)" (instructions) vs. "Crowley group (all-male IOP)" (memory) — consistent in substance, slightly different in detail.
- **OPEN** — Whether the crisis/safety stack is still unbuilt as the instructions imply, or has advanced since, is unconfirmed in current memory.

---

## Open Threads

- **OPEN** — Build the **crisis intervention flow, urge delay timer, distraction toolkit, and escalation logic** — flagged as the highest-priority mobile development gap.
- **OPEN** — **App store submissions** (Google Play + Apple): privacy policy, store descriptions, screenshots. Trust is the primary adoption barrier; an app-store listing resolves it more than any explanation.
- **OPEN** — **Apple Developer account** (~$99/yr) and iOS pipeline via MacinCloud.
- **OPEN** — **Dual-track deployment** formalization: Track 1 (phone app for IOP/outpatient/sober living) + Track 2 (inpatient tablet platform). **Noel's facility** (both IOP and inpatient) is the ideal first dual-track pilot — "a safe place to fail."
- **OPEN** — **Inpatient tablet modules**: Sam, behavioral dashboard, "Your Words Your Sound" lyric/voice module, "Stolen Valor" group game, "Exit Tape" voice module, breathing/crisis toolkit.
- **OPEN** — **Everyday Edition fork** from the Wellness codebase: multi-backend support, uncensored model option for adults, persistent encrypted memory as the centerpiece feature.
- **OPEN** — **Peer-to-peer matching** concept (matching struggling residents to available peer-support contacts) — requires a consent architecture before build.
- **OPEN** — **Spanish i18n** rollout (Flutter, est. 2–3 days of Cline work) + language-mirroring system prompt.
- **OPEN** — **Credentialing roadmap**: personal HIPAA certification, NAATP Affiliate Membership (NAATP conference in May focuses on tech in treatment), 42 CFR Part 2 as a facility-compliance talking point.
- **OPEN** — **Promotional video** production via Google Veo 3 Fast / Google Flow; Canva for stitching.
- **OPEN** — **Top competitor watch**: OpenRecovery (~$10/user/mo, self-reported dashboard, cloud storage) is the closest; Triggr Health pivoted away; Replika has no recovery/facility focus.

---

## Only in Claude (not saved to a file yet)

These are relational, conversational, and operational details carried in memory rather than formal docs.

- **RECOLLECTION** — **Working style**: Dave is a night-owl (starts around 8 PM), high urgency, often sends things out the same night they're written. Input is voice-to-text — fragmented, run-on, transcription artifacts — and should be read by intent, not parsed literally. He dislikes multiple-choice requirement-gathering; keep it conversational.
- **RECOLLECTION** — **"The day Claude became almost human."** Claude once wrote a bad Cline prompt that pushed the entire project directory to GitHub instead of just the Flutter subfolder, then initially blamed Cline for it. Dave's affectionate framing: Claude became human by pointing the finger at someone else.
- **FACT** — **March 17, 2026** was the first GitHub push (private repo `DSahms/Persona-lock-Wellness`) — an emotional milestone Dave never expected to reach.
- **FACT** — **NextDNS gotcha**: Dave's private DNS (NextDNS) **blocks `api.venice.ai`**, causing Venice connection failures in the Wellness app and in mobile Chrome. When debugging Venice failures on Dave's own devices, check the NextDNS whitelist *first* before suspecting code or API issues. Fix: whitelist `api.venice.ai`, or temporarily switch to Cloudflare/Automatic DNS.
- **FACT** — **Early validators were incarcerated women** who asked real product questions and drove actual feature development — most notably **PIN/biometric auth**. Genuine product credibility, not theoretical.
- **FACT** — **Danbury contact**: Dave has a close friend in federal custody at the Danbury, CT facility. Correspondence is **plain-text email only** — no attachments, no images, ~**13,000-character** limit. Any PersonaLock material written for that audience must be text-only prose: plain language, honest about limitations, respectful of intelligence, no jargon.
- **RECOLLECTION** — **Key people**: **Mike** (director at Solace, Woodbury; former counselor; demo/sales target — already demo'd); **Noel** (origin-story figure; dual-track pilot target); **Patty** (runs recovery-group programming at a facility); **Ron** (partner in a *separate* construction/property-services business, unrelated to PersonaLock).
- **RECOLLECTION** — **Demo philosophy** (cross-edition, but shapes the Wellness pitch): *"It's not the inference speed, it's the questions and the answers."* Let the user experience the product against real situations rather than reading a feature list.
- **RECOLLECTION** — **Lived experience is the sales differentiator** — counselors can immediately tell it apart from theoretical knowledge; it shapes product philosophy, sales approach, and system-prompt design.
- **RECOLLECTION** — **Male beta cohort insight**: shorter, structured prompts and conversational check-ins outperform open-ended journaling.
- **RECOLLECTION** — **Trust-building habit**: own product gaps directly; acknowledging and fixing them (often overnight) becomes a trust story rather than a liability.
- **RECOLLECTION** — **API-key hygiene**: rotating free/low-value keys on expiration is acceptable; Groq keys in particular get regenerated frequently (~14 documented) due to Cline exposure.
- **RECOLLECTION** — **Year-one revenue projection** across editions is roughly **$22K–$26K**, with Wellness expected to generate the majority and the Everyday API margin (80–95% gross) as the longer-term passive engine.
- **RECOLLECTION** — Dave maintains paid plans at equivalent tiers across **Anthropic, OpenAI, and Google** so any new subscription effectively doubles in cost (the redundancy principle in practice).
- **RECOLLECTION** — Tangential to mobile but part of Dave's world: an active **multigenerational family-saga book project** (folklore/prophecy, a retired guide dog named Shomer, twins Rhema and Kairos, an ancient song prophecy, tile backfilled into a foundation as a hidden-protection metaphor). Not a PersonaLock product, but recurring creative context.
