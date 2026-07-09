"""Personality Engine for managing AI assistant personality."""

import json
import os
from typing import Dict, List

from .profile import PersonalityProfile

# Path to the desktop persona contract (root-level assets/persona.json)
_PERSONA_JSON_PATH = os.path.join(
    os.path.dirname(__file__),  # modules/personality_engine/
    "..", "..",                 # → project root
    "assets", "persona.json"
)


def _load_persona_json() -> dict:
    """Load and return the persona.json data, or an empty dict on failure."""
    try:
        abs_path = os.path.abspath(_PERSONA_JSON_PATH)
        with open(abs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class PersonalityEngine:
    """Manages the active personality profile and generates prompts."""

    def __init__(self, profile: PersonalityProfile):
        """Initialize with a personality profile.

        Args:
            profile: The PersonalityProfile to use
        """
        self.profile = profile

        # Edition-specific state (populated by load_edition_overrides)
        self.edition: str = ""
        self.voice_config: Dict[str, str] = {}
        self.additional_rules: List[str] = []

        # Load the persona contract once at init
        self.persona_data: dict = _load_persona_json()

    # ------------------------------------------------------------------
    # Edition overrides
    # ------------------------------------------------------------------

    def load_edition_overrides(self, edition: str) -> None:
        """Apply edition-specific trait overrides from persona.json.

        Args:
            edition: Edition name, e.g. "business", "wellness", or "consigliere"
        """
        overrides = (
            self.persona_data
            .get("persona", {})
            .get("edition_overrides", {})
            .get(edition, {})
        )
        if not overrides and edition == "consigliere":
            overrides = (
                self.persona_data
                .get("persona", {})
                .get("edition_overrides", {})
                .get("business", {})
            )

        if "traits" in overrides:
            for trait, value in overrides["traits"].items():
                # Update individual attribute (used by engine internals)
                if hasattr(self.profile, trait):
                    setattr(self.profile, trait, float(value))
                # Keep the traits dict in sync
                if trait in self.profile.traits:
                    self.profile.traits[trait] = float(value)

        if "voice" in overrides:
            self.voice_config = dict(overrides["voice"])

        if "additional_rules" in overrides:
            self.additional_rules = list(overrides["additional_rules"])

        self.edition = edition

    # ------------------------------------------------------------------
    # Prompt generation
    # ------------------------------------------------------------------

    def get_system_prompt(self, memory_context: str = "") -> str:
        """Get the system prompt with personality and optional memory context.

        Args:
            memory_context: Optional memory context to append

        Returns:
            Complete system prompt string
        """
        parts = [self.profile.system_prompt_prefix]

        # Inject edition identity so LLM can answer "what edition are you"
        if self.edition:
            label = "Consigliere Edition" if self.edition == "consigliere" else f"{self.edition.title()} Edition"
            parts.append(
                f"You are running as Arden Desktop {label}. "
                f"If asked what edition you are, say '{label}' clearly."
            )

        # Inject edition rules into system prompt when present
        if self.additional_rules:
            rules_block = "Additional operating rules:\n" + "\n".join(
                f"- {rule}" for rule in self.additional_rules
            )
            parts.append(rules_block)

        if memory_context:
            parts.append(memory_context)

        return "\n\n".join(parts)

    def get_greeting(self) -> str:
        """Get the greeting for the current edition/voice config.

        Returns voice_config greeting if set (edition override), otherwise
        falls back to the profile's static greeting.
        """
        return self.voice_config.get("greeting", self.profile.greeting)
