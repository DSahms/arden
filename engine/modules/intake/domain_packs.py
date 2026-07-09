"""Domain packs — consumer (Brittany) vs Consigliere business depth."""

from __future__ import annotations

from modules.assistant_config import get_config
from modules.intake.domains import ARDEN_DOMAINS, IntakeDomain, get_domain

CONSIGLIERE_DOMAINS: list[IntakeDomain] = [
    IntakeDomain(
        id="business_stakes",
        title="Business stakes",
        subtitle="Clients, deals, relationships that matter",
        depth_questions=[
            "Who are the people or deals that would hurt most if you dropped the ball?",
            "Any standing client or partner commitments I should keep on radar?",
        ],
    ),
    IntakeDomain(
        id="business_risks",
        title="Risk flags",
        subtitle="Venues and situations — speak up before, not after",
        opt_in=True,
        depth_questions=[
            "Any places or situations you want me to flag before you walk in — "
            "casinos, bars, high-stress meetings?",
            "Past patterns you want a direct heads-up about in business context?",
        ],
    ),
    IntakeDomain(
        id="accountability",
        title="Accountability",
        subtitle="Opt-in — recovery + business boundaries",
        opt_in=True,
        depth_questions=[
            "Anything from recovery you want respected in work travel or entertaining?",
            "When should I push back hard versus stay quiet?",
        ],
    ),
]


def domain_pack_id() -> str:
    return get_config("intake.domain_pack", default="consumer")


def is_consigliere_pack() -> bool:
    return domain_pack_id() == "consigliere"


def get_domains_for_mode(mode: str) -> list[IntakeDomain]:
    """Return ordered domains for quick (b) or in-depth (c)."""
    if mode == "b":
        ids = ["people", "dates", "preferences"]
        return [get_domain(i) for i in ids]
    if mode == "c":
        domains = list(ARDEN_DOMAINS)
        if is_consigliere_pack():
            domains.extend(CONSIGLIERE_DOMAINS)
        return domains
    raise ValueError(f"Unknown intake mode: {mode}")
