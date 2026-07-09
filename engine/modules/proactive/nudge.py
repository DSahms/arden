"""Thin-knowledge nudge — once per day, after some chat use, never day-one nag."""

from __future__ import annotations

from modules.intake.progress import load_intake_choice
from modules.proactive.state import ProactiveStateStore
from modules.tactical_context import get_facts_store

_NUDGE_TEXT = (
    "I'm still light on a few things about you — "
    "a few minutes on Help me know you so I can show up better?"
)


def maybe_thin_knowledge_nudge(*, user_messages_this_session: int) -> str | None:
    """Return nudge copy if appropriate, else None."""
    if user_messages_this_session < 3:
        return None

    state = ProactiveStateStore()
    if state.nudge_shown_today():
        return None

    try:
        fact_count = len(get_facts_store().list_facts(limit=200))
    except Exception:
        fact_count = 0

    if fact_count >= 5:
        return None

    intake = load_intake_choice() or {}
    if intake.get("choice") == "c" and intake.get("completed"):
        return None

    return _NUDGE_TEXT


def record_nudge_shown() -> None:
    ProactiveStateStore().mark_nudge_shown()
