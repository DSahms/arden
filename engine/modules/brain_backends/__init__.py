"""
Brain Backends Module

Provides pluggable LLM backends for PersonaLock.
Personality and memory live outside the LLM - "keep the soul, change the brain."
"""

from .base_backend import BaseBrainBackend
from .brain_factory import BrainFactory

__all__ = ['BaseBrainBackend', 'BrainFactory']
