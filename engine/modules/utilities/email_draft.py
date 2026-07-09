"""Email draft helper — generates text and copies to clipboard. Never sends."""

from __future__ import annotations

from typing import Callable


def draft_email_to_clipboard(
    *,
    topic: str,
    brain_generate: Callable[[str, str], str],
    clipboard_set: Callable[[str], None],
    user_name: str = "",
    assistant_name: str = "Arden",
) -> str:
    """Return draft body and copy to clipboard."""
    topic = topic.strip()
    if not topic:
        raise ValueError("Describe what the email should be about.")

    system = (
        f"You are {assistant_name}, helping draft an email for the user. "
        "Write ONLY the email body — no subject line unless they asked. "
        "Plain, human tone. Do not send anything; this is a draft for them to paste. "
        "Do not invent facts about their life."
    )
    user = f"Draft an email about: {topic}"
    if user_name:
        user += f"\nSign naturally as {user_name} if appropriate."

    body = brain_generate(system, user).strip()
    if not body:
        raise RuntimeError("Brain returned an empty draft.")

    clipboard_set(body)
    return body
