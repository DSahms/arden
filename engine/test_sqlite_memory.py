"""Tests for SQLite graph store (Consumer edition memory backend)."""

import os
import tempfile

from modules.memory_vault.sqlite_graph_store import SQLiteGraphStore
from modules.memory_vault.memory_manager import MemoryManager
from modules.memory_vault.chroma_store import ChromaStore


def test_sqlite_remember_and_forget():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        store = SQLiteGraphStore(db)
        assert store.connect()
        store.initialize_schema()

        # Graph-only path (Chroma optional for consumer SQLite mode)
        mm = MemoryManager(neo4j_client=store, chroma_store=None, embedding_function=None)

        mid = mm.remember("User: hi\nAssistant: hey", memory_type="event", importance=0.7)
        assert mid is not None

        recent = store.list_memories(limit=1)
        assert len(recent) == 1
        assert recent[0]["content"].startswith("User:")

        forgot = mm.forget_most_recent()
        assert forgot == mid
        assert store.list_memories(limit=1) == []
        store.close()


def test_sqlite_entity_link():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        store = SQLiteGraphStore(db)
        store.connect()
        store.initialize_schema()

        mid = store.create_memory("Sherri is Dave's friend", memory_type="fact")["id"]
        ent = store.create_entity("Sherri", entity_type="person")
        store.link_memory_to_entity(mid, ent["id"])
        store.add_entity_alias(ent["id"], "SHERRI")

        names = store.get_entity_names_for_memory(mid)
        assert "Sherri" in names
        store.close()


if __name__ == "__main__":
    test_sqlite_remember_and_forget()
    test_sqlite_entity_link()
    print("[SUCCESS] SQLite memory tests passed")
