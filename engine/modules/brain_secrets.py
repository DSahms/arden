"""Resolve brain backend config with user secrets from .env."""

from __future__ import annotations

import os

from modules.consumer_bootstrap import reload_consumer_secrets

_CLOUD_ENV_KEYS: dict[str, str] = {
    "venice": "VENICE_API_KEY",
    "groq": "GROQ_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def load_brain_config(backend_type: str) -> dict:
    """Load YAML brain config and overlay cloud API keys from the consumer .env."""
    from modules.assistant_config import get_config

    reload_consumer_secrets()

    backend_config: dict = {}
    for key in ("base_url", "model", "timeout", "api_key"):
        value = get_config(f"{backend_type}.{key}", default=None)
        if value is not None:
            backend_config[key] = value

    env_var = _CLOUD_ENV_KEYS.get(backend_type)
    if env_var:
        env_key = (os.getenv(env_var) or "").strip()
        if env_key:
            backend_config["api_key"] = env_key
        else:
            backend_config.pop("api_key", None)

    return backend_config
