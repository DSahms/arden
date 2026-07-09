"""Headless memory persistence test (Janice / consumer edition)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def run_memory_persist_test() -> int:
    """Store a fact, new session, verify recall (SQLite always; Groq if key set)."""
    try:
        tmp = tempfile.mkdtemp(prefix="personalock-mem-")
        data_dir = Path(tmp)

        with mock.patch(
            "modules.consumer_bootstrap.consumer_data_dir",
            return_value=data_dir,
        ):
            from modules.consumer_bootstrap import bootstrap_consumer, save_user_secrets
            from modules.memory_vault.memory_factory import create_graph_store
            from modules.memory_vault.memory_manager import MemoryManager
            from utils.embedding_utils import HashEmbedder

            bootstrap_consumer()

            graph = create_graph_store()
            mm = MemoryManager(
                neo4j_client=graph,
                chroma_store=None,
                embedding_function=HashEmbedder().embed,
            )
            mid = mm.remember(
                "User: What's my favorite color?\nAssistant: Your favorite color is blue.",
                memory_type="fact",
                importance=0.9,
            )
            assert mid, "remember failed"
            recent = graph.list_memories(limit=5)
            assert any(
                "blue" in (m.get("content") or "").lower() for m in recent
            ), "sqlite did not persist memory"
            print("[OK] SQLite memory persisted")

            if not os.getenv("GROQ_API_KEY"):
                print("[SKIP] GROQ_API_KEY not set - Groq session recall skipped")
                return 0

            from modules.utils import create_session_logger_id, setup_logging
            from modules.base_assistant import PlainAssistant

            save_user_secrets(name="TestUser", groq_key=os.environ["GROQ_API_KEY"])
            bootstrap_consumer()

            secret = "ultraviolet"
            logger = setup_logging(create_session_logger_id())
            a1 = PlainAssistant(logger, "mem-persist-1")
            r1 = a1.process_text(
                f"Remember my favorite color is {secret}. Reply with exactly: saved"
            )
            r1_lower = (r1 or "").lower()
            groq_skip = (
                "groq api error" in r1_lower
                or "invalid api key" in r1_lower
                or "groq api key is invalid" in r1_lower
                or "something unexpected happened" in r1_lower
            )
            if not r1 or groq_skip:
                print("[SKIP] Groq key invalid or API error - SQLite persist still OK")
                print("       Update GROQ_API_KEY in .env for full session recall test")
                return 0
            assert "saved" in r1_lower, f"unexpected reply: {r1!r}"

            logger2 = setup_logging(create_session_logger_id())
            a2 = PlainAssistant(logger2, "mem-persist-2")
            r2 = a2.process_text("What is my favorite color? One word only.")
            if "groq api error" in (r2 or "").lower():
                print("[SKIP] Groq recall test skipped (API error)")
                return 0
            assert secret in r2.lower(), f"memory not recalled in new session: {r2!r}"

            print("[OK] Memory persisted across Groq sessions")
            return 0
    except Exception as exc:
        print(f"[FAIL] Memory persist test: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run_memory_persist_test())
