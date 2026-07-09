"""ChromaDB vector store for Memory Vault semantic search.

This module provides a vector database for storing and querying memory embeddings,
enabling semantic similarity search across memories.

Note: requires `chromadb` python package to be installed when used at runtime.
"""
from typing import Any, Dict, List, Optional, Callable
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    Settings = None
    CHROMADB_AVAILABLE = False


class ChromaStore:
    """ChromaDB vector store for memory embeddings and semantic search."""
    
    # Collection name for memories
    MEMORIES_COLLECTION = "memories"
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Callable[[str], List[float]]] = None
    ):
        """Initialize ChromaDB client and memories collection.
        
        Args:
            persist_directory: Directory for persistent storage (None for in-memory)
            embedding_function: Optional function to generate embeddings from text.
                               If not provided, embeddings must be passed explicitly.
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb package not installed. Run: pip install chromadb")
        
        self._persist_directory = persist_directory
        self._embedding_function = embedding_function
        
        # Initialize client
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        
        # Get or create the memories collection
        self.memories_collection = self.client.get_or_create_collection(
            name=self.MEMORIES_COLLECTION,
            metadata={"description": "Memory embeddings for semantic search"}
        )
    
    def set_embedding_function(self, func: Callable[[str], List[float]]):
        """Set the embedding function for automatic text embedding.
        
        Args:
            func: Function that takes text and returns embedding vector
        """
        self._embedding_function = func
    
    # =========================================================================
    # MEMORY STORAGE
    # =========================================================================
    
    def store_memory(
        self,
        neo4j_id: str,
        text: str,
        memory_type: str,
        importance: float,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a memory with its embedding, linked to Neo4j Memory node ID.
        
        Args:
            neo4j_id: The UUID of the Memory node in Neo4j (used as document ID)
            text: The memory content text
            memory_type: Memory type (fact, event, insight, reflection)
            importance: Importance score 0.0-1.0
            embedding: Pre-computed embedding vector. If None, uses embedding_function.
            metadata: Additional metadata to store
            
        Returns:
            The document ID (same as neo4j_id)
            
        Raises:
            ValueError: If no embedding provided and no embedding_function set
        """
        # Generate embedding if not provided
        if embedding is None:
            if self._embedding_function is None:
                raise ValueError("No embedding provided and no embedding_function set")
            embedding = self._embedding_function(text)
        
        # Build metadata
        doc_metadata = {
            "neo4j_id": neo4j_id,
            "memory_type": memory_type,
            "importance": importance,
        }
        if metadata:
            doc_metadata.update(metadata)
        
        # Upsert into collection (using neo4j_id as document id for linking)
        self.memories_collection.upsert(
            ids=[neo4j_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[doc_metadata]
        )
        
        return neo4j_id
    
    def get_memory(self, neo4j_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by its Neo4j ID.
        
        Args:
            neo4j_id: The UUID of the Memory node in Neo4j
            
        Returns:
            Dictionary with id, document, metadata, embedding or None if not found
        """
        result = self.memories_collection.get(
            ids=[neo4j_id],
            include=["documents", "metadatas", "embeddings"]
        )
        
        if not result["ids"]:
            return None
        
        return {
            "id": result["ids"][0],
            "document": result["documents"][0] if result["documents"] else None,
            "metadata": result["metadatas"][0] if result["metadatas"] else None,
            "embedding": result["embeddings"][0] if result["embeddings"] else None
        }
    
    def delete_memory(self, neo4j_id: str) -> bool:
        """Delete a memory from the vector store.
        
        Args:
            neo4j_id: The UUID of the Memory node in Neo4j
            
        Returns:
            True if deleted (always returns True as ChromaDB doesn't error on missing)
        """
        try:
            self.memories_collection.delete(ids=[neo4j_id])
            return True
        except Exception:
            return False
    
    def update_memory(
        self,
        neo4j_id: str,
        text: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """Update an existing memory's content or metadata.
        
        Args:
            neo4j_id: The UUID of the Memory node in Neo4j
            text: New text content (optional)
            memory_type: New memory type (optional)
            importance: New importance score (optional)
            embedding: New embedding vector (optional, regenerated if text changes)
            
        Returns:
            True if updated successfully
        """
        # Get existing memory
        existing = self.get_memory(neo4j_id)
        if not existing:
            return False
        
        # Determine new values
        new_text = text if text is not None else existing["document"]
        new_metadata = existing["metadata"] or {}
        
        if memory_type is not None:
            new_metadata["memory_type"] = memory_type
        if importance is not None:
            new_metadata["importance"] = importance
        
        # Regenerate embedding if text changed
        if text is not None and embedding is None:
            if self._embedding_function:
                embedding = self._embedding_function(text)
            else:
                embedding = existing["embedding"]
        elif embedding is None:
            embedding = existing["embedding"]
        
        # Update
        self.memories_collection.update(
            ids=[neo4j_id],
            embeddings=[embedding] if embedding else None,
            documents=[new_text],
            metadatas=[new_metadata]
        )
        
        return True
    
    # =========================================================================
    # SEMANTIC SEARCH
    # =========================================================================
    
    def query_similar_memories(
        self,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 5,
        memory_type: Optional[str] = None,
        min_importance: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Query for memories similar to the given text or embedding.
        
        Args:
            query_text: Text to find similar memories for (requires embedding_function)
            query_embedding: Pre-computed query embedding vector
            n_results: Maximum number of results to return
            memory_type: Filter by memory type (optional)
            min_importance: Filter by minimum importance (optional)
            
        Returns:
            List of similar memories with id, document, metadata, distance
            
        Raises:
            ValueError: If neither query_text nor query_embedding provided
        """
        # Get embedding
        if query_embedding is None:
            if query_text is None:
                raise ValueError("Must provide either query_text or query_embedding")
            if self._embedding_function is None:
                raise ValueError("No embedding_function set for text queries")
            query_embedding = self._embedding_function(query_text)
        
        # Build where clause for filtering
        where_clause = None
        where_conditions = []
        
        if memory_type:
            where_conditions.append({"memory_type": {"$eq": memory_type}})
        if min_importance is not None:
            where_conditions.append({"importance": {"$gte": min_importance}})
        
        if len(where_conditions) == 1:
            where_clause = where_conditions[0]
        elif len(where_conditions) > 1:
            where_clause = {"$and": where_conditions}
        
        # Query
        results = self.memories_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        memories = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                memories.append({
                    "id": doc_id,
                    "neo4j_id": doc_id,  # Same as id since we use neo4j_id as doc id
                    "document": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else None,
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "similarity": 1.0 - results["distances"][0][i] if results["distances"] else None
                })
        
        return memories
    
    def query_by_embedding(
        self,
        embedding: List[float],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Query memories by embedding vector (legacy compatibility).
        
        Args:
            embedding: Query embedding vector
            n_results: Maximum number of results
            
        Returns:
            Raw query results from ChromaDB
        """
        return self.memories_collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def count_memories(self) -> int:
        """Get the total count of memories in the store.
        
        Returns:
            Number of memories stored
        """
        return self.memories_collection.count()
    
    def list_all_memory_ids(self) -> List[str]:
        """Get all memory IDs (Neo4j IDs) in the store.
        
        Returns:
            List of all memory IDs
        """
        result = self.memories_collection.get(include=[])
        return result["ids"] if result["ids"] else []
    
    def clear_all_memories(self) -> bool:
        """Delete all memories from the collection. USE WITH CAUTION!
        
        Returns:
            True if successful
        """
        try:
            # Get all IDs and delete them
            all_ids = self.list_all_memory_ids()
            if all_ids:
                self.memories_collection.delete(ids=all_ids)
            return True
        except Exception as e:
            print(f"Failed to clear memories: {e}")
            return False
    
    # =========================================================================
    # LEGACY COMPATIBILITY
    # =========================================================================
    
    def upsert(
        self,
        uid: str,
        text: str,
        metadata: Dict[str, Any],
        embedding: List[float]
    ):
        """Legacy upsert method for backward compatibility.
        
        Args:
            uid: Document/memory ID
            text: Document text
            metadata: Document metadata
            embedding: Embedding vector
        """
        self.memories_collection.upsert(
            ids=[uid],
            metadatas=[metadata],
            documents=[text],
            embeddings=[embedding]
        )
    
    def query(
        self,
        embedding: List[float],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Legacy query method for backward compatibility.
        
        Args:
            embedding: Query embedding vector
            n_results: Number of results
            
        Returns:
            ChromaDB query results
        """
        return self.memories_collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
