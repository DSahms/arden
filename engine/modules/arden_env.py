"""Arden Desktop environment variables.

Canonical names use the ``ARDEN_*`` prefix. Legacy ``PERSONALOCK_*`` names
from the deprecated PersonaLock Desktop brand are still read as fallbacks so
existing installs and scripts keep working.
"""

from __future__ import annotations

import os
from typing import Optional

_CANONICAL = {
    "EDITION": "ARDEN_EDITION",
    "CONFIG": "ARDEN_CONFIG",
    "DATA_DIR": "ARDEN_DATA_DIR",
    "OUTPUT_DIR": "ARDEN_OUTPUT_DIR",
    "USER_NAME": "ARDEN_USER_NAME",
    "ASSISTANT_NAME": "ARDEN_ASSISTANT_NAME",
    "SMOKE_BRAIN": "ARDEN_SMOKE_BRAIN",
}

_LEGACY: dict[str, str] = {
    "ARDEN_EDITION": "PERSONALOCK_EDITION",
    "ARDEN_CONFIG": "PERSONALOCK_CONFIG",
    "ARDEN_DATA_DIR": "PERSONALOCK_DATA_DIR",
    "ARDEN_OUTPUT_DIR": "PERSONALOCK_OUTPUT_DIR",
    "ARDEN_USER_NAME": "PERSONALOCK_USER_NAME",
    "ARDEN_ASSISTANT_NAME": "PERSONALOCK_ASSISTANT_NAME",
    "ARDEN_SMOKE_BRAIN": "PERSONALOCK_SMOKE_BRAIN",
}


def _canonical(key: str) -> str:
    if key.startswith("ARDEN_"):
        return key
    return _CANONICAL.get(key, f"ARDEN_{key}")


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read ``ARDEN_*`` with legacy ``PERSONALOCK_*`` fallback."""
    canon = _canonical(key)
    if canon in os.environ:
        return os.environ[canon]
    legacy = _LEGACY.get(canon)
    if legacy and legacy in os.environ:
        return os.environ[legacy]
    return default


def setdefault(key: str, value: str) -> None:
    """Set ``ARDEN_*`` and mirror to legacy name when unset."""
    canon = _canonical(key)
    legacy = _LEGACY.get(canon)
    if canon not in os.environ and (not legacy or legacy not in os.environ):
        os.environ[canon] = value
        if legacy:
            os.environ[legacy] = value
    elif canon in os.environ and legacy:
        os.environ.setdefault(legacy, os.environ[canon])
    elif legacy and legacy in os.environ:
        os.environ.setdefault(canon, os.environ[legacy])


def set_(key: str, value: str) -> None:
    """Set ``ARDEN_*`` and mirror to legacy name."""
    canon = _canonical(key)
    os.environ[canon] = value
    legacy = _LEGACY.get(canon)
    if legacy:
        os.environ[legacy] = value


def is_consumer() -> bool:
    return get("EDITION") == "consumer"


def is_consigliere() -> bool:
    return get("EDITION") == "consigliere"


def get_edition() -> str:
    return get("EDITION", "consumer") or "consumer"


def is_business_edition() -> bool:
    """Business chief-of-staff features (briefing, tasks, accountability)."""
    return get("EDITION") in ("consigliere", "business")
