"""SQLite graph store — portable memory backend for consumer (Brittany) edition.

Drop-in replacement for Neo4jClient for the subset of operations MemoryManager uses.
No Docker, no JVM — single file on disk.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteGraphStore:
    """SQLite-backed graph store compatible with MemoryManager expectations."""

    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path))
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> bool:
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception:
            return False

    def is_connected(self) -> bool:
        return self._conn is not None

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def initialize_schema(self) -> None:
        if not self._conn:
            self.connect()
        assert self._conn is not None
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL DEFAULT 'fact',
                importance REAL NOT NULL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                entity_type TEXT NOT NULL DEFAULT 'concept',
                description TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS entity_aliases (
                entity_id TEXT NOT NULL,
                alias TEXT NOT NULL UNIQUE,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS memory_entities (
                memory_id TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                PRIMARY KEY (memory_id, entity_id),
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                summary TEXT NOT NULL DEFAULT '',
                mood TEXT NOT NULL DEFAULT 'neutral',
                started_at TEXT NOT NULL,
                ended_at TEXT
            );

            CREATE TABLE IF NOT EXISTS memory_conversations (
                memory_id TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                PRIMARY KEY (memory_id, conversation_id),
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
            """
        )
        self._conn.commit()

    def create_memory(
        self,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        memory_id = id or str(uuid.uuid4())
        now = _utc_now()
        assert self._conn is not None
        self._conn.execute(
            """
            INSERT INTO memories (id, content, memory_type, importance, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (memory_id, content, memory_type, importance, now, now),
        )
        self._conn.commit()
        return {
            "id": memory_id,
            "content": content,
            "memory_type": memory_type,
            "importance": importance,
            "created_at": now,
            "last_accessed": now,
        }

    def delete_memory(self, id: str) -> bool:
        assert self._conn is not None
        cur = self._conn.execute("DELETE FROM memories WHERE id = ?", (id,))
        self._conn.commit()
        return cur.rowcount > 0

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        min_importance: Optional[float] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        assert self._conn is not None
        sql = "SELECT * FROM memories WHERE 1=1"
        params: List[Any] = []
        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)
        if min_importance is not None:
            sql += " AND importance >= ?"
            params.append(min_importance)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_entity_names_for_memory(self, memory_id: str) -> List[str]:
        assert self._conn is not None
        rows = self._conn.execute(
            """
            SELECT e.name AS name
            FROM memory_entities me
            JOIN entities e ON e.id = me.entity_id
            WHERE me.memory_id = ?
            """,
            (memory_id,),
        ).fetchall()
        return [row["name"] for row in rows if row["name"]]

    def create_entity(
        self,
        name: str,
        entity_type: str = "concept",
        description: str = "",
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        entity_id = id or str(uuid.uuid4())
        assert self._conn is not None
        self._conn.execute(
            """
            INSERT OR IGNORE INTO entities (id, name, entity_type, description)
            VALUES (?, ?, ?, ?)
            """,
            (entity_id, name, entity_type, description),
        )
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM entities WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else {"id": entity_id, "name": name}

    def get_entity_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT * FROM entities WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None

    def link_memory_to_entity(self, memory_id: str, entity_id: str) -> bool:
        assert self._conn is not None
        try:
            self._conn.execute(
                """
                INSERT OR IGNORE INTO memory_entities (memory_id, entity_id)
                VALUES (?, ?)
                """,
                (memory_id, entity_id),
            )
            self._conn.commit()
            return True
        except Exception:
            return False

    def create_conversation(
        self,
        summary: str = "",
        mood: str = "neutral",
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        conv_id = id or str(uuid.uuid4())
        now = _utc_now()
        assert self._conn is not None
        self._conn.execute(
            """
            INSERT INTO conversations (id, summary, mood, started_at, ended_at)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (conv_id, summary, mood, now),
        )
        self._conn.commit()
        return {"id": conv_id, "summary": summary, "mood": mood, "started_at": now}

    def link_memory_to_conversation(self, memory_id: str, conversation_id: str) -> bool:
        assert self._conn is not None
        try:
            self._conn.execute(
                """
                INSERT OR IGNORE INTO memory_conversations (memory_id, conversation_id)
                VALUES (?, ?)
                """,
                (memory_id, conversation_id),
            )
            self._conn.commit()
            return True
        except Exception:
            return False

    def add_entity_alias(self, entity_id: str, alias: str) -> bool:
        """Register an alias (e.g. SHERRI -> Sherri) for future EntityReconciler."""
        assert self._conn is not None
        try:
            self._conn.execute(
                "INSERT OR IGNORE INTO entity_aliases (entity_id, alias) VALUES (?, ?)",
                (entity_id, alias),
            )
            self._conn.commit()
            return True
        except Exception:
            return False
