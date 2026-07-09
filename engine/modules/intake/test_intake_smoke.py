"""Smoke test for intake engine — run: python -m modules.intake.test_intake_smoke"""

from __future__ import annotations

import tempfile
from pathlib import Path

from modules.intake.domains import get_domains_for_mode
from modules.intake.engine import IntakeEngine
from modules.intake.facts_store import TacticalFactsStore


def main() -> None:
    db = Path(tempfile.mkdtemp()) / "facts.db"
    store = TacticalFactsStore(db)
    store.connect()
    engine = IntakeEngine("b", store)
    q = engine.current_question()
    assert q is not None
    domain_id, question = q
    proposal = engine.propose_fact(domain_id, question, "Mom — birthday March 12")
    engine.confirm_fact(proposal)
    assert store.list_facts()
    assert len(get_domains_for_mode("c")) == 6
    print("intake smoke OK")


if __name__ == "__main__":
    main()
