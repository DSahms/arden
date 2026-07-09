# Personality Engine

Scaffold for a personality engine which holds an active `PersonalityProfile` and renders it into prompt fragments that can be injected into system prompts.

- `profile.py`: `PersonalityProfile` dataclass
- `renderer.py`: convert profile to prompt fragment
- `api.py`: simple engine for load/save/get/set active profile
