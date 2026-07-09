"""EmbeddingManager - ChromaDB semantic search for conversation memory."""
import os
from typing import Any, Dict, List, Optional
import hashlib

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None


class EmbeddingManager:
    """Manages embeddings and semantic search via ChromaDB."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        if chromadb is None:
            raise ImportError("chromadb package not installed. Run: pip install chromadb")
        
        self.persist_directory = persist_directory or os.environ.get(
            "CHROMA_PERSIST_DIR", "./data/chroma"
        )
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="conversation_memory",
            metadata={"hnsw:space": "cosine"}
        )
    
    def is_connected(self) -> bool:
        """Check if ChromaDB is operational."""
        try:
            # Try to count - if it works, we're connected
            self.collection.count()
            return True
        except Exception:
            return False
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate a simple hash-based embedding for text.
        
        This is a fallback when no external embedding model is available.
        For production, replace with sentence-transformers or OpenAI embeddings.
        """
        # Simple approach: use character/word frequencies + hash
        # This is NOT semantically meaningful but allows basic operation
        import struct
        
        # Create a deterministic 384-dimensional embedding from text
        embedding = []
        text_lower = text.lower()
        
        # Use multiple hash seeds to create dimensions
        for i in range(384):
            h = hashlib.md5(f"{i}:{text_lower}".encode()).digest()
            # Convert first 4 bytes to float between -1 and 1
            val = struct.unpack('f', h[:4])[0]
            # Normalize to [-1, 1] range
            normalized = (val % 2) - 1
            embedding.append(normalized)
        
        # Normalize the vector
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def store(
        self,
        text: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> str:
        """Store text with embedding in ChromaDB.
        
        If no embedding provided, generates a simple one.
        Returns the document ID.
        """
        import uuid
        
        doc_id = doc_id or str(uuid.uuid4())
        
        if embedding is None:
            embedding = self._generate_simple_embedding(text)
        
        # ChromaDB metadata must be flat (no nested dicts)
        flat_metadata = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                flat_metadata[k] = v
            else:
                flat_metadata[k] = str(v)
        
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[flat_metadata]
        )
        
        return doc_id
    
    def store_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Store a conversation exchange for semantic retrieval.
        
        Combines user message and response into a single searchable document.
        """
        import uuid
        
        doc_id = conversation_id or str(uuid.uuid4())
        
        # Create combined text for embedding
        combined_text = f"User: {user_message}\nAssistant: {assistant_response}"
        
        metadata = {
            "user_id": user_id,
            "user_message": user_message,
            "assistant_response": assistant_response,
            "type": "conversation"
        }
        
        return self.store(combined_text, metadata, doc_id)
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        user_id: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """Query for similar documents.
        
        Returns list of matching documents with metadata.
        """
        if embedding is None:
            embedding = self._generate_simple_embedding(query_text)
        
        where_filter = None
        if user_id:
            where_filter = {"user_id": user_id}
        
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            # If query fails (e.g., empty collection), return empty
            return []
        
        # Format results
        documents = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            for i, doc_id in enumerate(ids):
                doc = {
                    "id": doc_id,
                    "text": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": distances[i] if i < len(distances) else 0.0
                }
                documents.append(doc)
        
        return documents
    
    def get_relevant_context(
        self,
        query: str,
        user_id: Optional[str] = None,
        max_results: int = 3
    ) -> str:
        """Get relevant past conversations as context string.
        
        Returns formatted string suitable for including in LLM prompt.
        """
        results = self.query(query, n_results=max_results, user_id=user_id)
        
        if not results:
            return ""
        
        context_parts = ["Relevant memories from past conversations:"]
        for i, doc in enumerate(results, 1):
            meta = doc.get("metadata", {})
            user_msg = meta.get("user_message", "")
            assistant_msg = meta.get("assistant_response", "")
            if user_msg and assistant_msg:
                context_parts.append(f"\n[Memory {i}]")
                context_parts.append(f"User said: {user_msg}")
                context_parts.append(f"You responded: {assistant_msg}")
        
        return "\n".join(context_parts)
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False
    
    def count(self) -> int:
        """Return total number of stored documents."""
        return self.collection.count()
