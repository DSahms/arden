"""Neo4j client for Memory Vault graph database operations.

This module provides a client for interacting with Neo4j to store and retrieve
memory-related graph data including memories, conversations, entities, preferences, and goals.

Note: requires `neo4j` python package to be installed when used at runtime.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


class Neo4jClient:
    """Neo4j database client for Memory Vault operations."""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j client.
        
        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            user: Database username
            password: Database password
        """
        if GraphDatabase is None:
            raise ImportError("neo4j package not installed. Run: pip install neo4j")
        
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None
    
    def connect(self) -> bool:
        """Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._driver = GraphDatabase.driver(
                self._uri, 
                auth=(self._user, self._password)
            )
            # Verify connection
            self._driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self._driver:
            try:
                self._driver.close()
            except Exception:
                pass
            finally:
                self._driver = None
    
    def is_connected(self) -> bool:
        """Check if client is connected to Neo4j.
        
        Returns:
            True if connected, False otherwise
        """
        if self._driver is None:
            return False
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False
    
    def run(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Run a Cypher query and return results as list of dicts.
        
        Args:
            cypher: Cypher query string
            parameters: Optional query parameters
            
        Returns:
            List of result records as dictionaries
        """
        if not self._driver:
            # Auto-connect if not connected
            if not self.connect():
                raise ConnectionError("Not connected to Neo4j")
        
        with self._driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [dict(record) for record in result]
    
    def __enter__(self):
        """Context manager entry - connect to database."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
        return False

    # =========================================================================
    # SCHEMA INITIALIZATION
    # =========================================================================
    
    def initialize_schema(self) -> bool:
        """Initialize Neo4j schema with constraints and indexes for all node types.
        
        Creates:
        - Uniqueness constraints on id fields for all node types
        - Indexes for frequently queried properties
        
        Returns:
            True if schema initialization successful, False otherwise
        """
        try:
            # Memory node constraints and indexes
            self.run("""
                CREATE CONSTRAINT memory_id IF NOT EXISTS
                FOR (m:Memory) REQUIRE m.id IS UNIQUE
            """)
            self.run("""
                CREATE INDEX memory_type IF NOT EXISTS
                FOR (m:Memory) ON (m.memory_type)
            """)
            self.run("""
                CREATE INDEX memory_importance IF NOT EXISTS
                FOR (m:Memory) ON (m.importance)
            """)
            self.run("""
                CREATE INDEX memory_created IF NOT EXISTS
                FOR (m:Memory) ON (m.created_at)
            """)
            
            # Conversation node constraints and indexes
            self.run("""
                CREATE CONSTRAINT conversation_id IF NOT EXISTS
                FOR (c:Conversation) REQUIRE c.id IS UNIQUE
            """)
            self.run("""
                CREATE INDEX conversation_mood IF NOT EXISTS
                FOR (c:Conversation) ON (c.mood)
            """)
            self.run("""
                CREATE INDEX conversation_started IF NOT EXISTS
                FOR (c:Conversation) ON (c.started_at)
            """)
            
            # Entity node constraints and indexes
            self.run("""
                CREATE CONSTRAINT entity_id IF NOT EXISTS
                FOR (e:Entity) REQUIRE e.id IS UNIQUE
            """)
            self.run("""
                CREATE INDEX entity_name IF NOT EXISTS
                FOR (e:Entity) ON (e.name)
            """)
            self.run("""
                CREATE INDEX entity_type IF NOT EXISTS
                FOR (e:Entity) ON (e.entity_type)
            """)
            
            # Preference node constraints and indexes
            self.run("""
                CREATE CONSTRAINT preference_id IF NOT EXISTS
                FOR (p:Preference) REQUIRE p.id IS UNIQUE
            """)
            self.run("""
                CREATE INDEX preference_category IF NOT EXISTS
                FOR (p:Preference) ON (p.category)
            """)
            self.run("""
                CREATE INDEX preference_key IF NOT EXISTS
                FOR (p:Preference) ON (p.key)
            """)
            
            # Goal node constraints and indexes
            self.run("""
                CREATE CONSTRAINT goal_id IF NOT EXISTS
                FOR (g:Goal) REQUIRE g.id IS UNIQUE
            """)
            self.run("""
                CREATE INDEX goal_status IF NOT EXISTS
                FOR (g:Goal) ON (g.status)
            """)
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize schema: {e}")
            return False
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about current schema constraints and indexes.
        
        Returns:
            Dictionary with constraints and indexes information
        """
        constraints = self.run("SHOW CONSTRAINTS")
        indexes = self.run("SHOW INDEXES")
        return {
            "constraints": constraints,
            "indexes": indexes
        }

    # =========================================================================
    # MEMORY NODE CRUD
    # =========================================================================
    
    def create_memory(
        self,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Memory node.
        
        Args:
            content: The actual memory text
            memory_type: One of: fact, event, insight, reflection
            importance: Importance score 0.0-1.0
            id: Optional UUID, auto-generated if not provided
            
        Returns:
            Created Memory node as dictionary
        """
        if id is None:
            id = str(uuid.uuid4())
        
        now = datetime.utcnow().isoformat()
        
        result = self.run("""
            CREATE (m:Memory {
                id: $id,
                content: $content,
                memory_type: $memory_type,
                importance: $importance,
                created_at: datetime($created_at),
                last_accessed: datetime($last_accessed)
            })
            RETURN m
        """, {
            "id": id,
            "content": content,
            "memory_type": memory_type,
            "importance": importance,
            "created_at": now,
            "last_accessed": now
        })
        
        return result[0]["m"] if result else {}
    
    def get_memory(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a Memory node by ID and update last_accessed.
        
        Args:
            id: Memory UUID
            
        Returns:
            Memory node as dictionary, or None if not found
        """
        now = datetime.utcnow().isoformat()
        
        result = self.run("""
            MATCH (m:Memory {id: $id})
            SET m.last_accessed = datetime($now)
            RETURN m
        """, {"id": id, "now": now})
        
        return result[0]["m"] if result else None
    
    def update_memory(
        self,
        id: str,
        content: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a Memory node.
        
        Args:
            id: Memory UUID
            content: New content (optional)
            memory_type: New type (optional)
            importance: New importance (optional)
            
        Returns:
            Updated Memory node, or None if not found
        """
        updates = []
        params = {"id": id}
        
        if content is not None:
            updates.append("m.content = $content")
            params["content"] = content
        if memory_type is not None:
            updates.append("m.memory_type = $memory_type")
            params["memory_type"] = memory_type
        if importance is not None:
            updates.append("m.importance = $importance")
            params["importance"] = importance
        
        if not updates:
            return self.get_memory(id)
        
        updates.append("m.last_accessed = datetime($now)")
        params["now"] = datetime.utcnow().isoformat()
        
        result = self.run(f"""
            MATCH (m:Memory {{id: $id}})
            SET {', '.join(updates)}
            RETURN m
        """, params)
        
        return result[0]["m"] if result else None
    
    def delete_memory(self, id: str) -> bool:
        """Delete a Memory node and its relationships.
        
        Args:
            id: Memory UUID
            
        Returns:
            True if deleted, False if not found
        """
        result = self.run("""
            MATCH (m:Memory {id: $id})
            DETACH DELETE m
            RETURN count(m) as deleted
        """, {"id": id})
        
        return result[0]["deleted"] > 0 if result else False
    
    def list_memories(
        self,
        memory_type: Optional[str] = None,
        min_importance: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List Memory nodes with optional filters.
        
        Args:
            memory_type: Filter by type (optional)
            min_importance: Filter by minimum importance (optional)
            limit: Maximum results to return
            
        Returns:
            List of Memory nodes
        """
        conditions = []
        params = {"limit": limit}
        
        if memory_type:
            conditions.append("m.memory_type = $memory_type")
            params["memory_type"] = memory_type
        if min_importance is not None:
            conditions.append("m.importance >= $min_importance")
            params["min_importance"] = min_importance
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        result = self.run(f"""
            MATCH (m:Memory)
            {where_clause}
            RETURN m
            ORDER BY m.created_at DESC
            LIMIT $limit
        """, params)
        
        return [r["m"] for r in result]

    # =========================================================================
    # CONVERSATION NODE CRUD
    # =========================================================================
    
    def create_conversation(
        self,
        summary: str = "",
        mood: str = "neutral",
        id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Conversation node.
        
        Args:
            summary: Conversation summary text
            mood: One of: neutral, positive, negative, focused, scattered
            id: Optional UUID, auto-generated if not provided
            
        Returns:
            Created Conversation node as dictionary
        """
        if id is None:
            id = str(uuid.uuid4())
        
        now = datetime.utcnow().isoformat()
        
        result = self.run("""
            CREATE (c:Conversation {
                id: $id,
                summary: $summary,
                mood: $mood,
                started_at: datetime($started_at),
                ended_at: null
            })
            RETURN c
        """, {
            "id": id,
            "summary": summary,
            "mood": mood,
            "started_at": now
        })
        
        return result[0]["c"] if result else {}
    
    def get_conversation(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a Conversation node by ID.
        
        Args:
            id: Conversation UUID
            
        Returns:
            Conversation node as dictionary, or None if not found
        """
        result = self.run("""
            MATCH (c:Conversation {id: $id})
            RETURN c
        """, {"id": id})
        
        return result[0]["c"] if result else None
    
    def update_conversation(
        self,
        id: str,
        summary: Optional[str] = None,
        mood: Optional[str] = None,
        ended: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update a Conversation node.
        
        Args:
            id: Conversation UUID
            summary: New summary (optional)
            mood: New mood (optional)
            ended: Set ended_at to now if True
            
        Returns:
            Updated Conversation node, or None if not found
        """
        updates = []
        params = {"id": id}
        
        if summary is not None:
            updates.append("c.summary = $summary")
            params["summary"] = summary
        if mood is not None:
            updates.append("c.mood = $mood")
            params["mood"] = mood
        if ended:
            updates.append("c.ended_at = datetime($ended_at)")
            params["ended_at"] = datetime.utcnow().isoformat()
        
        if not updates:
            return self.get_conversation(id)
        
        result = self.run(f"""
            MATCH (c:Conversation {{id: $id}})
            SET {', '.join(updates)}
            RETURN c
        """, params)
        
        return result[0]["c"] if result else None
    
    def end_conversation(self, id: str) -> Optional[Dict[str, Any]]:
        """Mark a conversation as ended.
        
        Args:
            id: Conversation UUID
            
        Returns:
            Updated Conversation node, or None if not found
        """
        return self.update_conversation(id, ended=True)
    
    def delete_conversation(self, id: str) -> bool:
        """Delete a Conversation node and its relationships.
        
        Args:
            id: Conversation UUID
            
        Returns:
            True if deleted, False if not found
        """
        result = self.run("""
            MATCH (c:Conversation {id: $id})
            DETACH DELETE c
            RETURN count(c) as deleted
        """, {"id": id})
        
        return result[0]["deleted"] > 0 if result else False
    
    def list_conversations(
        self,
        mood: Optional[str] = None,
        active_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List Conversation nodes with optional filters.
        
        Args:
            mood: Filter by mood (optional)
            active_only: Only return conversations without ended_at
            limit: Maximum results to return
            
        Returns:
            List of Conversation nodes
        """
        conditions = []
        params = {"limit": limit}
        
        if mood:
            conditions.append("c.mood = $mood")
            params["mood"] = mood
        if active_only:
            conditions.append("c.ended_at IS NULL")
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        result = self.run(f"""
            MATCH (c:Conversation)
            {where_clause}
            RETURN c
            ORDER BY c.started_at DESC
            LIMIT $limit
        """, params)
        
        return [r["c"] for r in result]

    # =========================================================================
    # ENTITY NODE CRUD
    # =========================================================================
    
    def create_entity(
        self,
        name: str,
        entity_type: str = "concept",
        description: str = "",
        id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Entity node.
        
        Args:
            name: Entity name
            entity_type: One of: person, project, place, concept, tool
            description: Entity description
            id: Optional UUID, auto-generated if not provided
            
        Returns:
            Created Entity node as dictionary
        """
        if id is None:
            id = str(uuid.uuid4())
        
        result = self.run("""
            CREATE (e:Entity {
                id: $id,
                name: $name,
                entity_type: $entity_type,
                description: $description
            })
            RETURN e
        """, {
            "id": id,
            "name": name,
            "entity_type": entity_type,
            "description": description
        })
        
        return result[0]["e"] if result else {}
    
    def get_entity(self, id: str) -> Optional[Dict[str, Any]]:
        """Get an Entity node by ID.
        
        Args:
            id: Entity UUID
            
        Returns:
            Entity node as dictionary, or None if not found
        """
        result = self.run("""
            MATCH (e:Entity {id: $id})
            RETURN e
        """, {"id": id})
        
        return result[0]["e"] if result else None
    
    def get_entity_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an Entity node by name.
        
        Args:
            name: Entity name
            
        Returns:
            Entity node as dictionary, or None if not found
        """
        result = self.run("""
            MATCH (e:Entity {name: $name})
            RETURN e
        """, {"name": name})
        
        return result[0]["e"] if result else None

    def get_entity_names_for_memory(self, memory_id: str) -> List[str]:
        """Return entity names linked to a memory via ABOUT relationships."""
        result = self.run("""
            MATCH (m:Memory {id: $memory_id})-[:ABOUT]->(e:Entity)
            RETURN e.name AS name
        """, {"memory_id": memory_id})
        return [r["name"] for r in result if r.get("name")]
    
    def update_entity(
        self,
        id: str,
        name: Optional[str] = None,
        entity_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an Entity node.
        
        Args:
            id: Entity UUID
            name: New name (optional)
            entity_type: New type (optional)
            description: New description (optional)
            
        Returns:
            Updated Entity node, or None if not found
        """
        updates = []
        params = {"id": id}
        
        if name is not None:
            updates.append("e.name = $name")
            params["name"] = name
        if entity_type is not None:
            updates.append("e.entity_type = $entity_type")
            params["entity_type"] = entity_type
        if description is not None:
            updates.append("e.description = $description")
            params["description"] = description
        
        if not updates:
            return self.get_entity(id)
        
        result = self.run(f"""
            MATCH (e:Entity {{id: $id}})
            SET {', '.join(updates)}
            RETURN e
        """, params)
        
        return result[0]["e"] if result else None
    
    def delete_entity(self, id: str) -> bool:
        """Delete an Entity node and its relationships.
        
        Args:
            id: Entity UUID
            
        Returns:
            True if deleted, False if not found
        """
        result = self.run("""
            MATCH (e:Entity {id: $id})
            DETACH DELETE e
            RETURN count(e) as deleted
        """, {"id": id})
        
        return result[0]["deleted"] > 0 if result else False
    
    def list_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List Entity nodes with optional filters.
        
        Args:
            entity_type: Filter by type (optional)
            limit: Maximum results to return
            
        Returns:
            List of Entity nodes
        """
        params = {"limit": limit}
        
        if entity_type:
            result = self.run("""
                MATCH (e:Entity {entity_type: $entity_type})
                RETURN e
                ORDER BY e.name
                LIMIT $limit
            """, {"entity_type": entity_type, "limit": limit})
        else:
            result = self.run("""
                MATCH (e:Entity)
                RETURN e
                ORDER BY e.name
                LIMIT $limit
            """, params)
        
        return [r["e"] for r in result]

    # =========================================================================
    # PREFERENCE NODE CRUD
    # =========================================================================
    
    def create_preference(
        self,
        category: str,
        key: str,
        value: str,
        confidence: float = 0.5,
        id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Preference node.
        
        Args:
            category: One of: coding, communication, workflow, ui
            key: Preference key name
            value: Preference value
            confidence: Confidence score 0.0-1.0
            id: Optional UUID, auto-generated if not provided
            
        Returns:
            Created Preference node as dictionary
        """
        if id is None:
            id = str(uuid.uuid4())
        
        result = self.run("""
            CREATE (p:Preference {
                id: $id,
                category: $category,
                key: $key,
                value: $value,
                confidence: $confidence
            })
            RETURN p
        """, {
            "id": id,
            "category": category,
            "key": key,
            "value": value,
            "confidence": confidence
        })
        
        return result[0]["p"] if result else {}
    
    def get_preference(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a Preference node by ID.
        
        Args:
            id: Preference UUID
            
        Returns:
            Preference node as dictionary, or None if not found
        """
        result = self.run("""
            MATCH (p:Preference {id: $id})
            RETURN p
        """, {"id": id})
        
        return result[0]["p"] if result else None
    
    def get_preference_by_key(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """Get a Preference node by category and key.
        
        Args:
            category: Preference category
            key: Preference key
            
        Returns:
            Preference node as dictionary, or None if not found
        """
        result = self.run("""
            MATCH (p:Preference {category: $category, key: $key})
            RETURN p
        """, {"category": category, "key": key})
        
        return result[0]["p"] if result else None
    
    def update_preference(
        self,
        id: str,
        value: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a Preference node.
        
        Args:
            id: Preference UUID
            value: New value (optional)
            confidence: New confidence (optional)
            
        Returns:
            Updated Preference node, or None if not found
        """
        updates = []
        params = {"id": id}
        
        if value is not None:
            updates.append("p.value = $value")
            params["value"] = value
        if confidence is not None:
            updates.append("p.confidence = $confidence")
            params["confidence"] = confidence
        
        if not updates:
            return self.get_preference(id)
        
        result = self.run(f"""
            MATCH (p:Preference {{id: $id}})
            SET {', '.join(updates)}
            RETURN p
        """, params)
        
        return result[0]["p"] if result else None
    
    def delete_preference(self, id: str) -> bool:
        """Delete a Preference node and its relationships.
        
        Args:
            id: Preference UUID
            
        Returns:
            True if deleted, False if not found
        """
        result = self.run("""
            MATCH (p:Preference {id: $id})
            DETACH DELETE p
            RETURN count(p) as deleted
        """, {"id": id})
        
        return result[0]["deleted"] > 0 if result else False
    
    def list_preferences(
        self,
        category: Optional[str] = None,
        min_confidence: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List Preference nodes with optional filters.
        
        Args:
            category: Filter by category (optional)
            min_confidence: Filter by minimum confidence (optional)
            limit: Maximum results to return
            
        Returns:
            List of Preference nodes
        """
        conditions = []
        params = {"limit": limit}
        
        if category:
            conditions.append("p.category = $category")
            params["category"] = category
        if min_confidence is not None:
            conditions.append("p.confidence >= $min_confidence")
            params["min_confidence"] = min_confidence
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        result = self.run(f"""
            MATCH (p:Preference)
            {where_clause}
            RETURN p
            ORDER BY p.category, p.key
            LIMIT $limit
        """, params)
        
        return [r["p"] for r in result]

    # =========================================================================
    # TEST / DEMO FUNCTIONS
    # =========================================================================
    
    def test_schema_and_crud(self) -> Dict[str, Any]:
        """Test function that creates sample data and queries it.
        
        Creates:
        - Sample entities (person, project, tool)
        - Sample conversation
        - Sample memories linked to entities and conversation
        - Sample preference and goal linked to entities
        
        Returns:
            Dictionary with test results
        """
        results = {"success": True, "errors": [], "created": {}}
        
        try:
            # Initialize schema first
            self.initialize_schema()
            results["schema_initialized"] = True
            
            # Create sample entities
            python_entity = self.create_entity(
                name="Python",
                entity_type="tool",
                description="Python programming language"
            )
            results["created"]["entity_python"] = python_entity.get("id") if hasattr(python_entity, 'get') else str(python_entity)
            
            personalock_entity = self.create_entity(
                name="PersonaLock",
                entity_type="project",
                description="AI assistant with persistent memory"
            )
            results["created"]["entity_personalock"] = personalock_entity.get("id") if hasattr(personalock_entity, 'get') else str(personalock_entity)
            
            user_entity = self.create_entity(
                name="User",
                entity_type="person",
                description="The human user of the assistant"
            )
            results["created"]["entity_user"] = user_entity.get("id") if hasattr(user_entity, 'get') else str(user_entity)
            
            # Create sample conversation
            conversation = self.create_conversation(
                summary="Discussion about PersonaLock development",
                mood="focused"
            )
            conv_id = conversation.get("id") if hasattr(conversation, 'get') else str(conversation)
            results["created"]["conversation"] = conv_id
            
            # Create sample memories
            memory1 = self.create_memory(
                content="User prefers Python for backend development",
                memory_type="fact",
                importance=0.8
            )
            mem1_id = memory1.get("id") if hasattr(memory1, 'get') else str(memory1)
            results["created"]["memory1"] = mem1_id
            
            memory2 = self.create_memory(
                content="Started implementing Neo4j schema for PersonaLock",
                memory_type="event",
                importance=0.7
            )
            mem2_id = memory2.get("id") if hasattr(memory2, 'get') else str(memory2)
            results["created"]["memory2"] = mem2_id
            
            memory3 = self.create_memory(
                content="Graph databases are excellent for relationship-heavy data",
                memory_type="insight",
                importance=0.6
            )
            mem3_id = memory3.get("id") if hasattr(memory3, 'get') else str(memory3)
            results["created"]["memory3"] = mem3_id
            
            # Create sample preference
            preference = self.create_preference(
                category="coding",
                key="language",
                value="Python",
                confidence=0.9
            )
            pref_id = preference.get("id") if hasattr(preference, 'get') else str(preference)
            results["created"]["preference"] = pref_id
            
            # Create sample goal
            goal = self.create_goal(
                title="Complete Memory Vault Implementation",
                description="Finish Neo4j and ChromaDB integration",
                status="active"
            )
            goal_id = goal.get("id") if hasattr(goal, 'get') else str(goal)
            results["created"]["goal"] = goal_id
            
            # Create relationships
            python_id = python_entity.get("id") if hasattr(python_entity, 'get') else None
            personalock_id = personalock_entity.get("id") if hasattr(personalock_entity, 'get') else None
            user_id = user_entity.get("id") if hasattr(user_entity, 'get') else None
            
            if python_id and mem1_id:
                self.link_memory_to_entity(mem1_id, python_id)
            if personalock_id and mem2_id:
                self.link_memory_to_entity(mem2_id, personalock_id)
            if conv_id and mem1_id:
                self.link_memory_to_conversation(mem1_id, conv_id)
            if conv_id and mem2_id:
                self.link_memory_to_conversation(mem2_id, conv_id)
            if conv_id and personalock_id:
                self.link_conversation_to_entity(conv_id, personalock_id)
            if goal_id and personalock_id:
                self.link_goal_to_entity(goal_id, personalock_id)
            if pref_id and user_id:
                self.link_preference_to_entity(pref_id, user_id)
            
            results["relationships_created"] = True
            
            # Query test
            if personalock_id:
                memories_about_personalock = self.get_memories_about_entity(personalock_id)
                results["query_memories_about_personalock"] = len(memories_about_personalock)
            
            if conv_id:
                memories_from_conv = self.get_memories_from_conversation(conv_id)
                results["query_memories_from_conversation"] = len(memories_from_conv)
            
            all_memories = self.list_memories(limit=10)
            results["query_all_memories"] = len(all_memories)
            
            all_entities = self.list_entities(limit=10)
            results["query_all_entities"] = len(all_entities)
            
        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
        
        return results
    
    def clear_all_data(self) -> bool:
        """Delete all nodes and relationships. USE WITH CAUTION!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.run("MATCH (n) DETACH DELETE n")
            return True
        except Exception as e:
            print(f"Failed to clear data: {e}")
            return False

    # =========================================================================
    # GOAL NODE CRUD
    # =========================================================================
    
    def create_goal(
        self,
        title: str,
        description: str = "",
        status: str = "active",
        target_date: Optional[str] = None,
        id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Goal node.
        
        Args:
            title: Goal title
            description: Goal description
            status: One of: active, completed, paused, abandoned
            target_date: Optional target date (ISO format string)
            id: Optional UUID, auto-generated if not provided
            
        Returns:
            Created Goal node as dictionary
        """
        if id is None:
            id = str(uuid.uuid4())
        
        params = {
            "id": id,
            "title": title,
            "description": description,
            "status": status
        }
        
        if target_date:
            result = self.run("""
                CREATE (g:Goal {
                    id: $id,
                    title: $title,
                    description: $description,
                    status: $status,
                    target_date: datetime($target_date)
                })
                RETURN g
            """, {**params, "target_date": target_date})
        else:
            result = self.run("""
                CREATE (g:Goal {
                    id: $id,
                    title: $title,
                    description: $description,
                    status: $status,
                    target_date: null
                })
                RETURN g
            """, params)
        
        return result[0]["g"] if result else {}
    
    def get_goal(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a Goal node by ID.
        
        Args:
            id: Goal UUID
            
        Returns:
            Goal node as dictionary, or None if not found
        """
        result = self.run("""
            MATCH (g:Goal {id: $id})
            RETURN g
        """, {"id": id})
        
        return result[0]["g"] if result else None
    
    def update_goal(
        self,
        id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        target_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a Goal node.
        
        Args:
            id: Goal UUID
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            target_date: New target date ISO string (optional)
            
        Returns:
            Updated Goal node, or None if not found
        """
        updates = []
        params = {"id": id}
        
        if title is not None:
            updates.append("g.title = $title")
            params["title"] = title
        if description is not None:
            updates.append("g.description = $description")
            params["description"] = description
        if status is not None:
            updates.append("g.status = $status")
            params["status"] = status
        if target_date is not None:
            updates.append("g.target_date = datetime($target_date)")
            params["target_date"] = target_date
        
        if not updates:
            return self.get_goal(id)
        
        result = self.run(f"""
            MATCH (g:Goal {{id: $id}})
            SET {', '.join(updates)}
            RETURN g
        """, params)
        
        return result[0]["g"] if result else None
    
    def complete_goal(self, id: str) -> Optional[Dict[str, Any]]:
        """Mark a goal as completed.
        
        Args:
            id: Goal UUID
            
        Returns:
            Updated Goal node, or None if not found
        """
        return self.update_goal(id, status="completed")
    
    def delete_goal(self, id: str) -> bool:
        """Delete a Goal node and its relationships.
        
        Args:
            id: Goal UUID
            
        Returns:
            True if deleted, False if not found
        """
        result = self.run("""
            MATCH (g:Goal {id: $id})
            DETACH DELETE g
            RETURN count(g) as deleted
        """, {"id": id})
        
        return result[0]["deleted"] > 0 if result else False
    
    def list_goals(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List Goal nodes with optional filters.
        
        Args:
            status: Filter by status (optional)
            limit: Maximum results to return
            
        Returns:
            List of Goal nodes
        """
        params = {"limit": limit}
        
        if status:
            result = self.run("""
                MATCH (g:Goal {status: $status})
                RETURN g
                ORDER BY g.target_date
                LIMIT $limit
            """, {"status": status, "limit": limit})
        else:
            result = self.run("""
                MATCH (g:Goal)
                RETURN g
                ORDER BY g.status, g.target_date
                LIMIT $limit
            """, params)
        
        return [r["g"] for r in result]

    # =========================================================================
    # RELATIONSHIP HELPERS
    # =========================================================================
    
    def link_memory_to_entity(self, memory_id: str, entity_id: str) -> bool:
        """Create ABOUT relationship: (Memory)-[:ABOUT]->(Entity)
        
        Args:
            memory_id: Memory node UUID
            entity_id: Entity node UUID
            
        Returns:
            True if relationship created, False otherwise
        """
        result = self.run("""
            MATCH (m:Memory {id: $memory_id})
            MATCH (e:Entity {id: $entity_id})
            MERGE (m)-[r:ABOUT]->(e)
            RETURN r
        """, {"memory_id": memory_id, "entity_id": entity_id})
        
        return len(result) > 0
    
    def link_memory_to_conversation(self, memory_id: str, conversation_id: str) -> bool:
        """Create FROM_CONVERSATION relationship: (Memory)-[:FROM_CONVERSATION]->(Conversation)
        
        Args:
            memory_id: Memory node UUID
            conversation_id: Conversation node UUID
            
        Returns:
            True if relationship created, False otherwise
        """
        result = self.run("""
            MATCH (m:Memory {id: $memory_id})
            MATCH (c:Conversation {id: $conversation_id})
            MERGE (m)-[r:FROM_CONVERSATION]->(c)
            RETURN r
        """, {"memory_id": memory_id, "conversation_id": conversation_id})
        
        return len(result) > 0
    
    def link_conversation_to_entity(self, conversation_id: str, entity_id: str) -> bool:
        """Create MENTIONS relationship: (Conversation)-[:MENTIONS]->(Entity)
        
        Args:
            conversation_id: Conversation node UUID
            entity_id: Entity node UUID
            
        Returns:
            True if relationship created, False otherwise
        """
        result = self.run("""
            MATCH (c:Conversation {id: $conversation_id})
            MATCH (e:Entity {id: $entity_id})
            MERGE (c)-[r:MENTIONS]->(e)
            RETURN r
        """, {"conversation_id": conversation_id, "entity_id": entity_id})
        
        return len(result) > 0
    
    def link_goal_to_entity(self, goal_id: str, entity_id: str) -> bool:
        """Create RELATED_TO relationship: (Goal)-[:RELATED_TO]->(Entity)
        
        Args:
            goal_id: Goal node UUID
            entity_id: Entity node UUID
            
        Returns:
            True if relationship created, False otherwise
        """
        result = self.run("""
            MATCH (g:Goal {id: $goal_id})
            MATCH (e:Entity {id: $entity_id})
            MERGE (g)-[r:RELATED_TO]->(e)
            RETURN r
        """, {"goal_id": goal_id, "entity_id": entity_id})
        
        return len(result) > 0
    
    def link_preference_to_entity(self, preference_id: str, entity_id: str) -> bool:
        """Create APPLIES_TO relationship: (Preference)-[:APPLIES_TO]->(Entity)
        
        Args:
            preference_id: Preference node UUID
            entity_id: Entity node UUID
            
        Returns:
            True if relationship created, False otherwise
        """
        result = self.run("""
            MATCH (p:Preference {id: $preference_id})
            MATCH (e:Entity {id: $entity_id})
            MERGE (p)-[r:APPLIES_TO]->(e)
            RETURN r
        """, {"preference_id": preference_id, "entity_id": entity_id})
        
        return len(result) > 0
    
    def get_memories_about_entity(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all memories about a specific entity.
        
        Args:
            entity_id: Entity node UUID
            limit: Maximum results to return
            
        Returns:
            List of Memory nodes
        """
        result = self.run("""
            MATCH (m:Memory)-[:ABOUT]->(e:Entity {id: $entity_id})
            RETURN m
            ORDER BY m.created_at DESC
            LIMIT $limit
        """, {"entity_id": entity_id, "limit": limit})
        
        return [r["m"] for r in result]
    
    def get_memories_from_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all memories from a specific conversation.
        
        Args:
            conversation_id: Conversation node UUID
            
        Returns:
            List of Memory nodes
        """
        result = self.run("""
            MATCH (m:Memory)-[:FROM_CONVERSATION]->(c:Conversation {id: $conversation_id})
            RETURN m
            ORDER BY m.created_at
        """, {"conversation_id": conversation_id})
        
        return [r["m"] for r in result]
    
    def get_entities_in_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all entities mentioned in a conversation.
        
        Args:
            conversation_id: Conversation node UUID
            
        Returns:
            List of Entity nodes
        """
        result = self.run("""
            MATCH (c:Conversation {id: $conversation_id})-[:MENTIONS]->(e:Entity)
            RETURN e
            ORDER BY e.name
        """, {"conversation_id": conversation_id})
        
        return [r["e"] for r in result]
    
    def get_goals_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all goals related to an entity.
        
        Args:
            entity_id: Entity node UUID
            
        Returns:
            List of Goal nodes
        """
        result = self.run("""
            MATCH (g:Goal)-[:RELATED_TO]->(e:Entity {id: $entity_id})
            RETURN g
            ORDER BY g.status, g.target_date
        """, {"entity_id": entity_id})
        
        return [r["g"] for r in result]
    
    def get_preferences_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all preferences that apply to an entity.
        
        Args:
            entity_id: Entity node UUID
            
        Returns:
            List of Preference nodes
        """
        result = self.run("""
            MATCH (p:Preference)-[:APPLIES_TO]->(e:Entity {id: $entity_id})
            RETURN p
            ORDER BY p.category, p.key
        """, {"entity_id": entity_id})
        
        return [r["p"] for r in result]
