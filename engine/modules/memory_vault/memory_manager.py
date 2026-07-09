"""Unified memory manager combining graph metadata (Neo4j) and vector store (Chroma).

This module provides high-level memory operations that coordinate between
Neo4j (graph relationships) and ChromaDB (semantic search).
"""
from typing import Any, Callable, Dict, List, Optional
import uuid

from .neo4j_client import Neo4jClient
from .chroma_store import ChromaStore


class MemoryManager:
    """High-level memory management combining Neo4j graph and ChromaDB vectors."""
    
    def __init__(
        self,
        neo4j_client: Optional[Neo4jClient] = None,
        chroma_store: Optional[ChromaStore] = None,
        embedding_function: Optional[Callable[[str], List[float]]] = None
    ):
        """Initialize MemoryManager.
        
        Args:
            neo4j_client: Neo4j client for graph operations
            chroma_store: ChromaDB store for vector operations
            embedding_function: Function to convert text to embeddings
        """
        self.neo4j = neo4j_client
        self.chroma = chroma_store
        self._embedding_function = embedding_function
        
        # Pass embedding function to chroma if both exist
        if self.chroma and self._embedding_function:
            self.chroma.set_embedding_function(self._embedding_function)
    
    def set_embedding_function(self, func: Callable[[str], List[float]]):
        """Set the embedding function for text-to-vector conversion.
        
        Args:
            func: Function that takes text and returns embedding vector
        """
        self._embedding_function = func
        if self.chroma:
            self.chroma.set_embedding_function(func)
    
    # =========================================================================
    # HIGH-LEVEL MEMORY OPERATIONS
    # =========================================================================
    
    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall memories semantically similar to the query.
        
        Uses ChromaDB to find similar memories, then enriches with Neo4j data
        including related entity names.
        
        Args:
            query: Text query to find similar memories
            limit: Maximum number of memories to return
            
        Returns:
            List of memory dicts with:
            - id: Memory UUID
            - content: Memory text
            - memory_type: Type of memory
            - importance: Importance score
            - entity_names: List of related entity names
            - similarity: Similarity score (if available)
        """
        if not self.chroma:
            return []
        
        # Get embedding for query
        if self._embedding_function is None:
            return []
        
        query_embedding = self._embedding_function(query)
        
        # Query ChromaDB for similar memories
        similar_memories = self.chroma.query_similar_memories(
            query_embedding=query_embedding,
            n_results=limit
        )
        
        # Enrich with Neo4j data
        results = []
        for mem in similar_memories:
            memory_id = mem.get("neo4j_id") or mem.get("id")
            
            result = {
                "id": memory_id,
                "content": mem.get("document", ""),
                "memory_type": mem.get("metadata", {}).get("memory_type", "unknown"),
                "importance": mem.get("metadata", {}).get("importance", 0.5),
                "similarity": mem.get("similarity"),
                "entity_names": []
            }
            
            # Get related entities from Neo4j if available
            if self.neo4j and memory_id:
                try:
                    if hasattr(self.neo4j, "get_entity_names_for_memory"):
                        result["entity_names"] = self.neo4j.get_entity_names_for_memory(memory_id)
                    else:
                        entity_result = self.neo4j.run("""
                            MATCH (m:Memory {id: $memory_id})-[:ABOUT]->(e:Entity)
                            RETURN e.name as name
                        """, {"memory_id": memory_id})
                        result["entity_names"] = [r["name"] for r in entity_result if r.get("name")]
                except Exception:
                    pass
            
            results.append(result)
        
        return results
    
    def remember(
        self,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        entity_names: Optional[List[str]] = None
    ) -> Optional[str]:
        """Store a new memory in both Neo4j and ChromaDB.
        
        Creates a Memory node in Neo4j, embeds and stores in ChromaDB,
        and optionally creates ABOUT relationships to entities.
        
        Args:
            content: The memory text content
            memory_type: One of: fact, event, insight, reflection
            importance: Importance score 0.0-1.0
            entity_names: Optional list of entity names to link via ABOUT relationship
            
        Returns:
            The memory UUID if successful, None otherwise
        """
        if not self.neo4j and not self.chroma:
            return None
        
        memory_id = str(uuid.uuid4())
        
        # Create Memory node in Neo4j
        if self.neo4j:
            try:
                self.neo4j.create_memory(
                    content=content,
                    memory_type=memory_type,
                    importance=importance,
                    id=memory_id
                )
            except Exception as e:
                print(f"Failed to create memory in Neo4j: {e}")
                return None
        
        # Embed and store in ChromaDB
        if self.chroma:
            try:
                # Generate embedding
                embedding = None
                if self._embedding_function:
                    embedding = self._embedding_function(content)
                
                self.chroma.store_memory(
                    neo4j_id=memory_id,
                    text=content,
                    memory_type=memory_type,
                    importance=importance,
                    embedding=embedding
                )
            except Exception as e:
                print(f"Failed to store memory in ChromaDB: {e}")
                # Continue - Neo4j storage succeeded
        
        # Create ABOUT relationships to entities if provided
        if entity_names and self.neo4j:
            for entity_name in entity_names:
                try:
                    # Find or create the entity
                    entity = self.neo4j.get_entity_by_name(entity_name)
                    
                    if entity is None:
                        # Create the entity if it doesn't exist
                        entity = self.neo4j.create_entity(
                            name=entity_name,
                            entity_type="concept",  # Default type
                            description=""
                        )
                    
                    # Get entity ID
                    entity_id = None
                    if hasattr(entity, 'get'):
                        entity_id = entity.get("id")
                    elif isinstance(entity, dict):
                        entity_id = entity.get("id")
                    
                    # Create ABOUT relationship
                    if entity_id:
                        self.neo4j.link_memory_to_entity(memory_id, entity_id)
                        
                except Exception as e:
                    print(f"Failed to link memory to entity '{entity_name}': {e}")
                    # Continue with other entities
        
        return memory_id

    def forget(self, memory_id: str) -> bool:
        """Delete a memory from Neo4j and ChromaDB.

        Args:
            memory_id: Memory UUID to delete

        Returns:
            True if deleted from at least one store
        """
        deleted = False

        if self.neo4j:
            try:
                if self.neo4j.delete_memory(memory_id):
                    deleted = True
            except Exception as e:
                print(f"Failed to delete memory from Neo4j: {e}")

        if self.chroma:
            try:
                if self.chroma.delete_memory(memory_id):
                    deleted = True
            except Exception as e:
                print(f"Failed to delete memory from ChromaDB: {e}")

        return deleted

    def forget_most_recent(self) -> Optional[str]:
        """Delete the most recently created memory.

        Returns:
            Deleted memory ID, or None if nothing to delete
        """
        if not self.neo4j:
            return None

        try:
            recent = self.neo4j.list_memories(limit=1)
            if not recent:
                return None

            memory = recent[0]
            memory_id = memory.get("id") if isinstance(memory, dict) else None
            if memory_id and self.forget(memory_id):
                return memory_id
        except Exception as e:
            print(f"Failed to forget most recent memory: {e}")

        return None

    # =========================================================================
    # LEGACY METHODS (backward compatibility)
    # =========================================================================
    
    def store(self, text: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None) -> str:
        """Store a memory item in both Neo4j and Chroma (legacy method).
        
        Args:
            text: Memory content
            metadata: Memory metadata
            embedding: Optional pre-computed embedding
            
        Returns:
            Memory UUID
        """
        uid = str(uuid.uuid4())
        
        if self.neo4j:
            try:
                self.neo4j.create_memory(
                    content=text,
                    memory_type=metadata.get("memory_type", "fact"),
                    importance=metadata.get("importance", 0.5),
                    id=uid
                )
            except Exception:
                pass

        if self.chroma and embedding is not None:
            try:
                self.chroma.upsert(uid=uid, text=text, metadata=metadata, embedding=embedding)
            except Exception:
                pass

        return uid

    def query(self, embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """Query vector store and return matching memories (legacy method).
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results
            
        Returns:
            Query results
        """
        if not self.chroma:
            return {"results": []}

        try:
            res = self.chroma.query(embedding=embedding, n_results=top_k)
            return res
        except Exception:
            return {"results": []}
