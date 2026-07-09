"""Persist proactive UI state (nudge cadence, dismissed care items)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from modules.consumer_bootstrap import consumer_data_dir


class ProactiveStateStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (consumer_data_dir() / "proactive_state.json")

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def care_shown_today(self) -> bool:
        return self.load().get("care_shown_date") == date.today().isoformat()

    def mark_care_shown(self) -> None:
        data = self.load()
        data["care_shown_date"] = date.today().isoformat()
        self.save(data)

    def nudge_shown_today(self) -> bool:
        return self.load().get("nudge_shown_date") == date.today().isoformat()

    def mark_nudge_shown(self) -> None:
        data = self.load()
        data["nudge_shown_date"] = date.today().isoformat()
        self.save(data)
