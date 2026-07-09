"""Headless consumer edition checks (post-build / CI)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

from modules.arden_env import get as arden_get


def _write_smoke_result(message: str) -> None:
    try:
        from modules.consumer_bootstrap import consumer_data_dir

        path = consumer_data_dir() / "smoke-last.txt"
        path.write_text(message + "\n", encoding="utf-8")
    except Exception:
        pass


def run_consumer_smoke(*, use_isolated_data: bool = False) -> int:
    """Verify consumer bootstrap, SQLite memory, and optional Groq brain.

    Returns 0 on success, 1 on failure.
    """
    patches: list = []
    data_dir: Path | None = None

    if use_isolated_data:
        tmp = tempfile.mkdtemp(prefix="arden-smoke-")
        data_dir = Path(tmp)
        patches.append(
            mock.patch(
                "modules.consumer_bootstrap.consumer_data_dir",
                return_value=data_dir,
            )
        )

    for patch in patches:
        patch.start()

    try:
        from modules.consumer_bootstrap import bootstrap_consumer
        from modules.memory_vault.memory_factory import create_graph_store
        from modules.memory_vault.chroma_store import ChromaStore
        from modules.memory_vault.memory_manager import MemoryManager
        from modules.assistant_config import get_config
        from utils.embedding_utils import HashEmbedder

        bootstrap_consumer()

        assert get_config("edition") == "consumer", "edition not consumer"
        assert get_config("memory.backend") == "sqlite", "memory backend not sqlite"
        assert get_config("memory.embedding.backend") == "hash", "embedding not hash"

        graph = create_graph_store()
        chroma = None
        try:
            chroma = ChromaStore(
                persist_directory=get_config("memory.chroma.persist_directory")
            )
        except Exception as chroma_err:
            print(f"[WARN] Chroma unavailable in smoke test: {chroma_err}")

        mm = MemoryManager(
            neo4j_client=graph,
            chroma_store=chroma,
            embedding_function=HashEmbedder().embed,
        )
        mid = mm.remember(
            "User: smoke test\nAssistant: Janice edition memory ok",
            memory_type="event",
            importance=0.5,
        )
        assert mid, "remember returned empty id"

        if chroma:
            results = mm.recall("smoke test", limit=3)
            assert results, "recall returned nothing"
        elif graph and hasattr(graph, "list_memories"):
            recent = graph.list_memories(limit=1)
            assert recent, "sqlite list_memories returned nothing"

        if arden_get("SMOKE_BRAIN") == "1" and os.getenv("GROQ_API_KEY"):
            from modules.utils import create_session_logger_id, setup_logging
            from modules.base_assistant import PlainAssistant

            logger = setup_logging(create_session_logger_id())
            assistant = PlainAssistant(logger, "smoke")
            reply = assistant.process_text("Reply with exactly: smoke ok")
            reply_lower = (reply or "").lower()
            if any(
                s in reply_lower
                for s in (
                    "invalid api key",
                    "groq api key is invalid",
                    "groq api error",
                    "something unexpected happened",
                )
            ):
                print("[SKIP] Groq key invalid - update GROQ_API_KEY in .env")
            else:
                assert reply and len(reply.strip()) > 0, "empty Groq reply"
                print("[OK] Groq brain responded")
        else:
            print(
                "[SKIP] Brain test (set ARDEN_SMOKE_BRAIN=1 and GROQ_API_KEY)"
            )

        msg = "[OK] Consumer smoke test passed"
        print(msg)
        _write_smoke_result(msg)
        return 0
    except Exception as exc:
        msg = f"[FAIL] Consumer smoke test: {exc}"
        print(msg, file=sys.stderr)
        _write_smoke_result(msg)
        return 1
    finally:
        for patch in reversed(patches):
            patch.stop()
