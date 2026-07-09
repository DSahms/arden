"""Factory for memory vault graph stores (Neo4j vs SQLite)."""

from typing import Any, Optional, Union

from modules.assistant_config import get_config

from .neo4j_client import Neo4jClient
from .sqlite_graph_store import SQLiteGraphStore

GraphStore = Union[Neo4jClient, SQLiteGraphStore]


def create_graph_store(config_path: Optional[str] = None) -> Optional[GraphStore]:
    """Create graph store from config memory.backend setting.

    Args:
        config_path: Optional override for ARDEN_CONFIG

    Returns:
        Neo4jClient or SQLiteGraphStore, or None on failure
    """
    kwargs = {} if config_path is None else {"config_path": config_path}

    backend = get_config("memory.backend", default="neo4j", **kwargs)

    if backend == "sqlite":
        db_path = get_config("memory.sqlite_path", default="data/consumer_memory.db", **kwargs)
        store = SQLiteGraphStore(db_path=db_path)
        if store.connect():
            store.initialize_schema()
            return store
        return None

    # Default: neo4j
    uri = get_config("memory.neo4j.uri", default="bolt://localhost:7687", **kwargs)
    user = get_config("memory.neo4j.user", default="neo4j", **kwargs)
    password = get_config("memory.neo4j.password", default="password", **kwargs)
    client = Neo4jClient(uri=uri, user=user, password=password)
    if client.connect():
        try:
            client.initialize_schema()
        except Exception:
            pass
        return client
    return client
