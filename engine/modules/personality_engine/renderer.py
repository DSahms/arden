from .profile import PersonalityProfile


def render_personality_to_prompt(profile: PersonalityProfile) -> str:
    """Render a PersonalityProfile into a prompt fragment for system/context injection."""
    return profile.to_prompt_fragment()
