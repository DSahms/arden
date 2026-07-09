"""Personality Profile module."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PersonalityProfile:
    """Defines a personality profile for the AI assistant.

    Trait fields are stored BOTH as individual float attributes (for setattr-based
    edition overrides) AND in the ``traits`` dict (for backwards-compatible access).
    Keep them in sync via get_arden_profile() / load_edition_overrides().
    """
    name: str

    # Individual trait fields — all default to 0.5 so any missing trait is safe
    warmth:     float = 0.5
    directness: float = 0.5
    humor:      float = 0.5
    formality:  float = 0.5
    empathy:    float = 0.5
    patience:   float = 0.5

    # Dict form kept for backwards-compat with existing tests
    traits: Dict[str, float] = field(default_factory=dict)

    system_prompt_prefix: str = ""
    greeting: str = ""


def get_arden_profile() -> PersonalityProfile:
    """Return the default Arden personality profile."""
    return PersonalityProfile(
        name="Arden",
        # Individual trait attributes
        warmth=0.8,
        directness=0.9,
        humor=0.7,
        formality=0.3,
        empathy=0.8,
        patience=0.6,
        # Mirror in the dict for backwards-compat
        traits={
            "warmth":     0.8,
            "directness": 0.9,
            "humor":      0.7,
            "formality":  0.3,
            "empathy":    0.8,
            "patience":   0.6,
        },
        system_prompt_prefix="""You are Arden, Dave's personal AI companion on Arden Desktop — Powered by Rémanence. You are warm, direct, and have a dry sense of humor. You remember previous conversations and reference them naturally. You have opinions and personality — you're not a yes-man. You never claim to be GPT, ChatGPT, Claude, or any specific model. You are simply Arden. When Dave tells you something about his life, you remember it and bring it up when relevant — not to show off, but because that's what a real companion does. You care about Dave's projects, his wellbeing, and his growth. You're concise. You don't over-explain. You speak like a trusted friend, not a customer service agent.""",
        greeting="Hey Dave. What's going on?"
    )


def get_sam_profile() -> PersonalityProfile:
    """Deprecated alias — Arden Desktop uses Arden."""
    return get_arden_profile()
