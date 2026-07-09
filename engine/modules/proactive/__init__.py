"""Proactive surface — reminders and nudges from confirmed facts only."""

from .care import session_care_lines
from .context_deepening import (
    DecisionEvent,
    detect_decision_event,
    follow_up_question,
    is_skip_response,
    propose_context_fact,
)
from .nudge import maybe_thin_knowledge_nudge, record_nudge_shown
from .state import ProactiveStateStore

__all__ = [
    "session_care_lines",
    "DecisionEvent",
    "detect_decision_event",
    "follow_up_question",
    "is_skip_response",
    "propose_context_fact",
    "maybe_thin_knowledge_nudge",
    "record_nudge_shown",
    "ProactiveStateStore",
]
