"""Save & resume intake sessions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from modules.consumer_bootstrap import consumer_data_dir


@dataclass
class IntakeTurn:
    domain_id: str
    question: str
    answer: str
    skipped: bool = False


@dataclass
class IntakeProgress:
    mode: str  # b | c
    domain_index: int = 0
    question_index: int = 0
    skipped_opt_in: list[str] = field(default_factory=list)
    turns: list[IntakeTurn] = field(default_factory=list)
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "domain_index": self.domain_index,
            "question_index": self.question_index,
            "skipped_opt_in": list(self.skipped_opt_in),
            "turns": [asdict(t) for t in self.turns],
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IntakeProgress:
        turns = [IntakeTurn(**t) for t in data.get("turns", [])]
        return cls(
            mode=data.get("mode", "b"),
            domain_index=int(data.get("domain_index", 0)),
            question_index=int(data.get("question_index", 0)),
            skipped_opt_in=list(data.get("skipped_opt_in", [])),
            turns=turns,
            completed=bool(data.get("completed", False)),
        )


class IntakeProgressStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (consumer_data_dir() / "intake_progress.json")

    def load(self) -> IntakeProgress | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return IntakeProgress.from_dict(data)
        except Exception:
            return None

    def save(self, progress: IntakeProgress) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(progress.to_dict(), indent=2), encoding="utf-8")

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()


def intake_choice_path() -> Path:
    return consumer_data_dir() / "intake.json"


def load_intake_choice() -> dict[str, Any] | None:
    path = intake_choice_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_intake_choice(choice: str, *, completed: bool = False) -> None:
    path = intake_choice_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    payload = {
        "choice": choice,
        "completed": completed,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
