"""Pre-send accountability alerts — confirmed facts only, never inferred."""

from __future__ import annotations

from modules.tactical_context import get_facts_store

_RISK_DOMAINS = ("triggers", "business_risks", "accountability")

_VENUE_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "gambling or casino venue",
        ("casino", "hard rock", "sportsbook", "slots", "atlantic city", "vegas"),
    ),
    (
        "bar or heavy drinking",
        ("open bar", "nightclub", "happy hour", "strip club"),
    ),
    (
        "high-stress meeting",
        ("performance review", "termination", "layoff", "audit"),
    ),
]

_MEETING_WORDS = (
    "meeting",
    "meet with",
    "dinner with",
    "lunch with",
    "going to",
    "heading to",
    "trip to",
    "visit",
    "conference",
    "client dinner",
)


def _mentioned_venues(text: str) -> list[str]:
    lower = text.lower()
    return [label for label, keywords in _VENUE_PATTERNS if any(k in lower for k in keywords)]


def _looks_like_plan(text: str) -> bool:
    lower = text.lower()
    return any(w in lower for w in _MEETING_WORDS)


def _risk_facts() -> list[dict]:
    try:
        store = get_facts_store()
    except Exception:
        return []
    facts: list[dict] = []
    for domain in _RISK_DOMAINS:
        facts.extend(store.list_facts(domain=domain))
    return facts


def pre_send_accountability_alerts(user_text: str) -> list[str]:
    """Return 0–2 direct lines when user plans something that hits stored risk facts."""
    text = (user_text or "").strip()
    if len(text) < 12 or not _looks_like_plan(text):
        return []

    venues = _mentioned_venues(text)
    facts = _risk_facts()
    if not facts:
        return []

    lines: list[str] = []
    if venues:
        venue_str = venues[0]
        for fact in facts[:3]:
            content = fact.get("content", "").strip()
            if not content:
                continue
            lines.append(
                f"Heads-up before you go: you mentioned {venue_str}, and you asked me to remember "
                f"this — {content}. Want to talk it through or skip?"
            )
            break

    if not lines and facts:
        top = facts[0].get("content", "").strip()
        if top and any(k in text.lower() for k in ("travel", "client", "investor", "pitch", "deal")):
            lines.append(
                f"Quick check — you told me: {top}. Does this plan touch that? "
                "Say the word if you want me to flag something."
            )

    return lines[:2]
