"""Embedding helper using sentence-transformers with lazy model loading.

Provides `embed_text(text: str) -> list[float]` without loading the model
until the first call, so importing the module is lightweight.
"""
from typing import List

_MODEL = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Lazily import SentenceTransformer and load the model on first use.

    This tries to import `sentence_transformers` at call time so the module can be
    imported before the package is installed; it will raise ImportError if the
    package is not available when called.
    """
    global _MODEL
    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
        except Exception:
            raise ImportError("sentence-transformers is not installed")

        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def embed_text(text: str) -> List[float]:
    """Encode `text` to an embedding vector (list of floats).

    Loads the model on first call.
    """
    model = _get_model()
    vec = model.encode(text)
    # Convert to plain Python list for serialization friendliness
    try:
        return vec.tolist()
    except Exception:
        return list(map(float, vec))


__all__ = ["embed_text"]
