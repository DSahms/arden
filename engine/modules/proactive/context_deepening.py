"""Phase 3b — gentle why follow-ups after declines/decisions (facts only, confirm to store)."""

from __future__ import annotations

import re
from dataclasses import dataclass

_DECLINE = (
    "decline",
    "declined",
    "declining",
    "not going",
    "won't go",
    "wont go",
    "can't make",
    "cant make",
    "passing on",
    "pass on",
    "rather not",
    "don't want to",
    "dont want to",
    "no thanks",
    "turn it down",
    "turned it down",
    "skip the",
    "skipping",
    "avoid",
    "staying home",
)

_CONTEXT = (
    "party",
    "invite",
    "invitation",
    "birthday",
    "wedding",
    "dinner",
    "meeting",
    "event",
    "trip",
    "plans",
    "get-together",
    "gathering",
    "bbq",
    "reunion",
)

_SKIP = (
    "skip",
    "rather not say",
    "rather not",
    "no thanks",
    "pass",
    "don't ask",
    "dont ask",
    "leave it",
    "never mind",
    "nevermind",
)


@dataclass
class DecisionEvent:
    summary: str
    domain: str
    user_text: str


def is_skip_response(text: str) -> bool:
    t = text.lower().strip()
    return t in _SKIP or t.startswith("rather not")


def detect_decision_event(text: str) -> DecisionEvent | None:
    """Return a decision/decline worth a single why follow-up, or None."""
    lower = text.lower().strip()
    if len(lower) < 8:
        return None
    has_decline = any(p in lower for p in _DECLINE)
    has_context = any(p in lower for p in _CONTEXT)
    if not has_decline:
        return None
    if not has_context and not re.search(r"\b(no|not)\b", lower):
        return None

    domain = "triggers" if any(w in lower for w in ("avoid", "trigger", "can't", "cant", "stress")) else "preferences"
    short = text.strip()
    if len(short) > 120:
        short = short[:117] + "…"
    return DecisionEvent(summary=short, domain=domain, user_text=text.strip())


def follow_up_question(event: DecisionEvent) -> str:
    return (
        "Quick one — so I can show up better next time: "
        "is there a reason behind that (venue, crowd, timing, someone involved)? "
        "Totally fine to say rather not say."
    )


def propose_context_fact(event: DecisionEvent, reason: str) -> dict[str, str]:
    label = f"Why: {event.summary[:60]}"
    content = reason.strip()
    return {"domain": event.domain, "label": label, "content": content}
