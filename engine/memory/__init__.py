"""Memory module - wraps memory_vault and embeddings."""
from .memory_vault import MemoryVault
from .embeddings import EmbeddingManager

__all__ = ["MemoryVault", "EmbeddingManager"]
