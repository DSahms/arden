"""MemoryVault - Neo4j CRUD operations for conversation memory."""
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


class MemoryVault:
    """Stores and retrieves conversation memories from Neo4j."""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        if GraphDatabase is None:
            raise ImportError("neo4j package not installed. Run: pip install neo4j")
        
        self.uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "password")
        
        self._driver = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j."""
        self._driver = GraphDatabase.driver(
            self.uri, 
            auth=(self.user, self.password)
        )
    
    def close(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
    
    def is_connected(self) -> bool:
        """Check if Neo4j is reachable."""
        try:
            with self._driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    def store_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a conversation exchange in Neo4j.
        
        Returns the conversation node's uid.
        """
        import uuid
        uid = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        metadata = metadata or {}
        metadata_json = json.dumps(metadata)
        
        cypher = """
        MERGE (u:User {user_id: $user_id})
        CREATE (c:Conversation {
            uid: $uid,
            user_message: $user_message,
            assistant_response: $assistant_response,
            timestamp: $timestamp,
            metadata: $metadata
        })
        CREATE (u)-[:HAD_CONVERSATION]->(c)
        RETURN c.uid as uid
        """
        
        with self._driver.session() as session:
            result = session.run(cypher, {
                "user_id": user_id,
                "uid": uid,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "timestamp": timestamp,
                "metadata": metadata_json
            })
            record = result.single()
            return record["uid"] if record else uid
    
    def get_recent_conversations(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve recent conversations, optionally filtered by user."""
        if user_id:
            cypher = """
            MATCH (u:User {user_id: $user_id})-[:HAD_CONVERSATION]->(c:Conversation)
            RETURN c.uid as uid, c.user_message as user_message, 
                   c.assistant_response as assistant_response,
                   c.timestamp as timestamp, c.metadata as metadata
            ORDER BY c.timestamp DESC
            LIMIT $limit
            """
            params = {"user_id": user_id, "limit": limit}
        else:
            cypher = """
            MATCH (c:Conversation)
            RETURN c.uid as uid, c.user_message as user_message,
                   c.assistant_response as assistant_response,
                   c.timestamp as timestamp, c.metadata as metadata
            ORDER BY c.timestamp DESC
            LIMIT $limit
            """
            params = {"limit": limit}
        
        with self._driver.session() as session:
            result = session.run(cypher, params)
            conversations = []
            for record in result:
                conv = {
                    "uid": record["uid"],
                    "user_message": record["user_message"],
                    "assistant_response": record["assistant_response"],
                    "timestamp": record["timestamp"],
                    "metadata": json.loads(record["metadata"]) if record["metadata"] else {}
                }
                conversations.append(conv)
            return conversations
    
    def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM context.
        
        Returns list of {"role": "user"|"assistant", "content": str}
        """
        conversations = self.get_recent_conversations(user_id=user_id, limit=limit)
        # Reverse to get chronological order (oldest first)
        conversations.reverse()
        
        history = []
        for conv in conversations:
            history.append({"role": "user", "content": conv["user_message"]})
            history.append({"role": "assistant", "content": conv["assistant_response"]})
        
        return history
    
    def search_conversations(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Simple text search in conversations (basic CONTAINS)."""
        if user_id:
            cypher = """
            MATCH (u:User {user_id: $user_id})-[:HAD_CONVERSATION]->(c:Conversation)
            WHERE c.user_message CONTAINS $query OR c.assistant_response CONTAINS $query
            RETURN c.uid as uid, c.user_message as user_message,
                   c.assistant_response as assistant_response,
                   c.timestamp as timestamp
            ORDER BY c.timestamp DESC
            LIMIT $limit
            """
            params = {"user_id": user_id, "query": query, "limit": limit}
        else:
            cypher = """
            MATCH (c:Conversation)
            WHERE c.user_message CONTAINS $query OR c.assistant_response CONTAINS $query
            RETURN c.uid as uid, c.user_message as user_message,
                   c.assistant_response as assistant_response,
                   c.timestamp as timestamp
            ORDER BY c.timestamp DESC
            LIMIT $limit
            """
            params = {"query": query, "limit": limit}
        
        with self._driver.session() as session:
            result = session.run(cypher, params)
            return [dict(record) for record in result]
