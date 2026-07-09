"""Headless Consigliere edition checks."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def run_consigliere_acceptance() -> int:
    """Verify Consigliere config, domain pack, and accountability wiring."""
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["LOCALAPPDATA"] = tmp
        os.environ["ARDEN_EDITION"] = "consigliere"
        os.environ.pop("ARDEN_CONFIG", None)

        from modules.consumer_bootstrap import bootstrap_consumer
        from modules.assistant_config import get_config
        from modules.intake.domain_packs import CONSIGLIERE_DOMAINS, get_domains_for_mode, is_consigliere_pack
        from modules.proactive.accountability import pre_send_accountability_alerts
        from modules.intake.facts_store import TacticalFactsStore
        from modules.tactical_context import get_facts_store

        bootstrap_consumer()

        assert get_config("edition") == "consigliere", "edition not consigliere"
        assert get_config("morning_briefing_enabled") is True, "briefing should be on"
        assert is_consigliere_pack(), "domain pack not consigliere"

        domains_c = get_domains_for_mode("c")
        assert len(domains_c) >= 6 + len(CONSIGLIERE_DOMAINS), "consigliere C domains too short"
        ids = {d.id for d in domains_c}
        assert "business_risks" in ids
        assert "accountability" in ids

        store = get_facts_store()
        store.add_fact(
            "business_risks",
            "gambling history — flag casinos and Hard Rock meetings",
            label="risk",
        )

        alerts = pre_send_accountability_alerts(
            "I have a client dinner at the Hard Rock tomorrow"
        )
        assert alerts, "expected accountability alert for Hard Rock + risk fact"

        runtime = Path(tmp) / "Arden" / "assistant_config.runtime.yml"
        assert runtime.exists(), "runtime config not written"

        store.close()
        get_facts_store.cache_clear()

    print("CONSIGLIERE ACCEPTANCE: ALL PASSED")
    return 0
