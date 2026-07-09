"""Arden companion intake domains — not memoir chapters."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IntakeDomain:
    id: str
    title: str
    subtitle: str
    seed_questions: list[str] = field(default_factory=list)
    opt_in: bool = False
    depth_questions: list[str] = field(default_factory=list)


# Quick layer (B) — woven into C automatically
_QUICK: list[tuple[str, str]] = [
    (
        "people",
        "Who are the people who matter most right now? Names and how they fit in your life.",
    ),
    (
        "dates",
        "Any birthdays, anniversaries, or hard dates I should keep in mind?",
    ),
    (
        "preferences",
        "How do you want me to talk to you — direct, gentle, casual, something else?",
    ),
]

ARDEN_DOMAINS: list[IntakeDomain] = [
    IntakeDomain(
        id="people",
        title="People",
        subtitle="Who matters, relationships, loyalty",
        seed_questions=[q for did, q in _QUICK if did == "people"],
        depth_questions=[
            "Anyone I should never speak ill of — or always treat with extra care?",
            "Who usually shows up for you when things get hard?",
        ],
    ),
    IntakeDomain(
        id="health",
        title="Health & routines",
        subtitle="Opt-in — meds, appointments, daily rhythms",
        opt_in=True,
        depth_questions=[
            "Anything you want me to remember about daily routines — meds, check-ins, rest?",
            "Any appointments or recurring health things I should know about?",
        ],
    ),
    IntakeDomain(
        id="dates",
        title="Dates & milestones",
        subtitle="Grief, anniversaries, hard days",
        seed_questions=[q for did, q in _QUICK if did == "dates"],
        depth_questions=[
            "Are there days of the year that hit harder than others?",
        ],
    ),
    IntakeDomain(
        id="triggers",
        title="Triggers & recovery",
        subtitle="Opt-in — places, patterns, boundaries",
        opt_in=True,
        depth_questions=[
            "Any places, situations, or patterns you prefer to avoid?",
            "Anything from your past you want me to tread lightly around?",
        ],
    ),
    IntakeDomain(
        id="work",
        title="Work & obligations",
        subtitle="Schedule reality, not spreadsheets",
        depth_questions=[
            "What does a typical work week look like for you?",
            "Any standing obligations I should factor in when we talk?",
        ],
    ),
    IntakeDomain(
        id="preferences",
        title="Preferences",
        subtitle="Tone, annoyances, how you want to be spoken to",
        seed_questions=[q for did, q in _QUICK if did == "preferences"],
        depth_questions=[
            "What annoys you in how AI or people talk to you?",
        ],
    ),
]


def get_domain(domain_id: str) -> IntakeDomain:
    for d in ARDEN_DOMAINS:
        if d.id == domain_id:
            return d
    raise ValueError(f"Unknown intake domain: {domain_id}")


def get_domains_for_mode(mode: str) -> list[IntakeDomain]:
    """Return ordered domains for quick (b) or in-depth (c). Delegates to domain pack."""
    from modules.intake.domain_packs import get_domains_for_mode as _pack_domains

    return _pack_domains(mode)


def questions_for_domain(domain: IntakeDomain, mode: str) -> list[str]:
    """All questions for one domain in order."""
    out: list[str] = list(domain.seed_questions)
    if mode == "c":
        out.extend(domain.depth_questions)
    return out
