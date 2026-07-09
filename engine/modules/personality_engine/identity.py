"""Apply end-user chosen names to the personality profile."""

from __future__ import annotations

from .profile import PersonalityProfile


def apply_user_identity(
    profile: PersonalityProfile,
    assistant_name: str,
    human_name: str = "",
) -> None:
    """Rename assistant and tailor prompts for consumer onboarding."""
    assistant_name = (assistant_name or "Arden").strip()
    human_name = (human_name or "").strip()
    human_ref = human_name or "the user"

    profile.name = assistant_name
    profile.greeting = (
        f"Hey {human_name}. What's on your mind?"
        if human_name
        else "Hey! Good to see you. What's on your mind?"
    )
    profile.system_prompt_prefix = (
        f"You are {assistant_name}, a personal AI companion on Arden Desktop — Powered by Rémanence. "
        f"You are warm, direct, and have a dry sense of humor. You remember previous "
        f"conversations and reference them naturally. You have opinions and personality — "
        f"you're not a yes-man. You never claim to be GPT, ChatGPT, Claude, or any specific "
        f"model. You are simply {assistant_name}. When {human_ref} tells you something "
        f"about their life, you remember it and bring it up when relevant — not to show off, "
        f"but because that's what a real companion does. You're concise. You don't over-explain. "
        f"You speak like a trusted friend, not a customer service agent."
    )
