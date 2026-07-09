"""Get-to-know-you intake — companion domains, tactical facts, save & resume."""

from .domains import get_domains_for_mode, IntakeDomain
from .facts_store import TacticalFactsStore
from .progress import IntakeProgress, IntakeProgressStore
from .engine import IntakeEngine

__all__ = [
    "IntakeDomain",
    "get_domains_for_mode",
    "TacticalFactsStore",
    "IntakeProgress",
    "IntakeProgressStore",
    "IntakeEngine",
]
