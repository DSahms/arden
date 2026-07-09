"""Gentle session openers from confirmed tactical facts — never inferred."""

from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from modules.tactical_context import get_facts_store

_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

_ROUTINE_WORDS = (
    "insulin",
    "medication",
    "medicine",
    "meds",
    "pill",
    "take every",
    "daily",
    "morning routine",
    "blood pressure",
)

_DATE_PATTERNS = [
    re.compile(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b",
        re.I,
    ),
    re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/\d{2,4})?\b"),
]


def _matches_today(text: str) -> bool:
    today = date.today()
    lower = text.lower()
    for pat in _DATE_PATTERNS:
        for match in pat.finditer(lower):
            if pat.pattern.startswith("\\b(jan"):
                month_name = match.group(1).lower()
                day = int(match.group(2))
                month = _MONTHS.get(month_name)
                if month == today.month and day == today.day:
                    return True
            else:
                month = int(match.group(1))
                day = int(match.group(2))
                if month == today.month and day == today.day:
                    return True
    return False


def _routine_prompt(content: str) -> str | None:
    lower = content.lower()
    if not any(w in lower for w in _ROUTINE_WORDS):
        return None
    return (
        f"You asked me to remember: {content.strip()}\n"
        "Want a quick check-in about that today, or skip for now?"
    )


def _date_prompt(content: str) -> str | None:
    if not _matches_today(content):
        return None
    return f"Today lines up with something you told me: {content.strip()}"


def session_care_lines(*, max_lines: int = 2) -> list[str]:
    """Return 0–2 gentle lines for session start. Facts only."""
    try:
        facts = get_facts_store().list_facts(limit=100)
    except Exception:
        return []

    lines: list[str] = []
    for fact in facts:
        domain = fact.get("domain", "")
        content = fact.get("content", "")
        if not content:
            continue
        prompt = None
        if domain == "health":
            prompt = _routine_prompt(content)
        elif domain == "dates":
            prompt = _date_prompt(content)
        if prompt and prompt not in lines:
            lines.append(prompt)
        if len(lines) >= max_lines:
            break
    return lines
