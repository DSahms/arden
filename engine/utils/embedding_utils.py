"""
PersonaLock — Embedding Utilities
==================================
Local-first text embeddings using Ollama.

Usage:
    from utils.embedding_utils import embed_text, OllamaEmbedder

    # Simple function
    vector = embed_text("Some text to embed")

    # Or use the class for more control
    embedder = OllamaEmbedder(model="nomic-embed-text")
    vector = embedder.embed("Some text to embed")
    vectors = embedder.embed_batch(["text1", "text2", "text3"])
"""

import hashlib
import math
import requests
from typing import List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/embeddings"
DEFAULT_MODEL = "nomic-embed-text"
DEFAULT_TIMEOUT = 30


# ============================================================
# SIMPLE FUNCTION API
# ============================================================
def embed_text(
    text: str,
    model: str = DEFAULT_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
    timeout: int = DEFAULT_TIMEOUT
) -> Optional[List[float]]:
    """
    Convert text to vector embedding using Ollama.
    
    Args:
        text: The text to embed
        model: Ollama model name (default: nomic-embed-text)
        url: Ollama API endpoint
        timeout: Request timeout in seconds
        
    Returns:
        List of floats representing the embedding vector,
        or None if embedding fails.
    """
    try:
        response = requests.post(
            url,
            json={"model": model, "prompt": text},
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Ollama at {url}. Is it running?")
        return None
    except requests.exceptions.Timeout:
        logger.error(f"Ollama request timed out after {timeout}s")
        return None
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None


# ============================================================
# CLASS-BASED API (for dependency injection)
# ============================================================
class OllamaEmbedder:
    """
    Ollama-based text embedder with connection pooling and batch support.
    
    Use this when you need:
    - Dependency injection into MemoryManager
    - Batch embedding for efficiency
    - Custom configuration
    """
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        url: str = DEFAULT_OLLAMA_URL,
        timeout: int = DEFAULT_TIMEOUT
    ):
        self.model = model
        self.url = url
        self.timeout = timeout
        self._session = requests.Session()
        self._dimension = None
        
    @property
    def dimension(self) -> Optional[int]:
        """Get embedding dimension (cached after first embed)."""
        if self._dimension is None:
            # Do a test embed to get dimension
            test_vec = self.embed("test")
            if test_vec:
                self._dimension = len(test_vec)
        return self._dimension
    
    def embed(self, text: str) -> Optional[List[float]]:
        """Embed a single text string."""
        try:
            response = self._session.post(
                self.url,
                json={"model": self.model, "prompt": text},
                timeout=self.timeout
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
            
            # Cache dimension on first successful embed
            if self._dimension is None:
                self._dimension = len(embedding)
                
            return embedding
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Embed multiple texts.
        
        Note: Ollama doesn't have native batch support,
        so this processes sequentially. Still useful for
        consistent error handling.
        """
        return [self.embed(text) for text in texts]
    
    def __call__(self, text: str) -> Optional[List[float]]:
        """Allow using instance as a function."""
        return self.embed(text)
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            test_embedding = self.embed("connection test")
            return test_embedding is not None
        except:
            return False
    
    def close(self):
        """Close the session."""
        self._session.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================
# FACTORY FUNCTION
# ============================================================
class HashEmbedder:
    """Lightweight local embedder — no Ollama, no GPU. For Consumer edition."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dimensions
        for word in text.lower().split():
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            for i, byte in enumerate(digest):
                vec[i % self.dimensions] += byte / 255.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def is_available(self) -> bool:
        return True

    def __call__(self, text: str) -> List[float]:
        return self.embed(text)


def get_embedding_function(
    backend: str = "ollama",
    **kwargs
) -> Callable[[str], Optional[List[float]]]:
    """
    Factory to get an embedding function.
    
    Currently supports:
    - "ollama" (default, local)
    
    Future options:
    - "openai" (API-based)
    - "sentence-transformers" (local, if torch works)
    
    Returns a callable that takes text and returns embedding vector.
    """
    if backend == "ollama":
        embedder = OllamaEmbedder(**kwargs)
        return embedder.embed
    if backend == "hash":
        return HashEmbedder(**kwargs).embed
    raise ValueError(f"Unknown embedding backend: {backend}")


# ============================================================
# QUICK TEST
# ============================================================
if __name__ == "__main__":
    print("Testing Ollama Embedder...")
    
    embedder = OllamaEmbedder()
    
    if embedder.is_available():
        print(f"✅ Ollama is available")
        print(f"✅ Model: {embedder.model}")
        
        test_vec = embedder.embed("Hello, PersonaLock!")
        if test_vec:
            print(f"✅ Embedding dimension: {len(test_vec)}")
            print(f"✅ First 5 values: {test_vec[:5]}")
        else:
            print("❌ Embedding failed")
    else:
        print("❌ Ollama not available")
        print("   Run: ollama serve")
