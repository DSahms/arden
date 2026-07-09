"""Tactical facts DB path and prompt formatting."""

from __future__ import annotations

from functools import lru_cache

from modules.consumer_bootstrap import consumer_data_dir
from modules.intake.facts_store import TacticalFactsStore


def facts_db_path() -> str:
    return str(consumer_data_dir() / "tactical_facts.db")


@lru_cache(maxsize=1)
def get_facts_store() -> TacticalFactsStore:
    store = TacticalFactsStore(facts_db_path())
    store.connect()
    return store


def tactical_context_for_prompt() -> str:
    try:
        return get_facts_store().format_for_prompt()
    except Exception:
        return ""
