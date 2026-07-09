"""Read-only calendar glance — ICS file + known dates from facts."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from modules.consumer_bootstrap import consumer_data_dir
from modules.tactical_context import get_facts_store

_LINK_NAME = "calendar_link.json"


def _link_path() -> Path:
    return consumer_data_dir() / _LINK_NAME


def link_calendar_file(path: Path) -> None:
    payload = {"path": str(Path(path)), "linked_at": datetime.now(timezone.utc).isoformat()}
    _link_path().write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _linked_ics_path() -> Path | None:
    p = _link_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        path = Path(data.get("path", ""))
        return path if path.exists() else None
    except Exception:
        return None


def _parse_ics_date(raw: str) -> date | None:
    raw = raw.strip()
    if not raw:
        return None
    if "T" in raw:
        raw = raw.split("T", 1)[0]
    raw = raw.replace("Z", "")[:8]
    try:
        return datetime.strptime(raw, "%Y%m%d").date()
    except ValueError:
        return None


def parse_ics_file(path: Path) -> list[dict[str, Any]]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    events: list[dict[str, Any]] = []
    blocks = re.split(r"BEGIN:VEVENT", text, flags=re.I)
    for block in blocks[1:]:
        summary = ""
        start: date | None = None
        for line in block.splitlines():
            line = line.strip()
            if line.upper().startswith("SUMMARY"):
                summary = line.split(":", 1)[-1].strip()
            elif line.upper().startswith("DTSTART"):
                start = _parse_ics_date(line.split(":", 1)[-1])
        if summary and start:
            events.append({"date": start.isoformat(), "title": summary})
    events.sort(key=lambda e: e["date"])
    return events


def list_upcoming_events(*, days: int = 60) -> list[str]:
    """Human-readable lines: ICS events + date facts."""
    lines: list[str] = []
    today = date.today()
    end = today + timedelta(days=days)

    ics_path = _linked_ics_path()
    if ics_path:
        for ev in parse_ics_file(ics_path):
            d = date.fromisoformat(ev["date"])
            if today <= d <= end:
                lines.append(f"{d.strftime('%b %d')} — {ev['title']} (calendar file)")

    for fact in get_facts_store().list_facts(domain="dates", limit=50):
        content = fact.get("content", "")
        if content:
            lines.append(f"Remembered — {content}")

    if not lines:
        lines.append("No upcoming items yet. Link an .ics file or add dates in Help me know you.")
    return lines
