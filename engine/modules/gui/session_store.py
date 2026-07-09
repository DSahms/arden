"""Persist Arden Desktop chat sessions locally."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Arden"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _sessions_path() -> Path:
    return _data_dir() / "sessions.json"


@dataclass
class ChatMessage:
    speaker: str
    body: str


@dataclass
class ChatSession:
    id: str
    title: str
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    @staticmethod
    def new(title: str) -> ChatSession:
        now = datetime.now(timezone.utc).isoformat()
        sid = now.replace(":", "").replace("-", "").replace("+00:00", "")[:17]
        return ChatSession(id=sid, title=title, created_at=now, updated_at=now)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["messages"] = [asdict(m) for m in self.messages]
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatSession:
        msgs = [ChatMessage(**m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            messages=msgs,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


class SessionStore:
    """JSON-backed session list for sidebar persistence."""

    def __init__(self) -> None:
        self.sessions: list[ChatSession] = []
        self.active_id: str | None = None
        self.load()

    def load(self) -> None:
        path = _sessions_path()
        if not path.exists():
            default = ChatSession.new("This conversation")
            self.sessions = [default]
            self.active_id = default.id
            self.save()
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.sessions = [ChatSession.from_dict(s) for s in raw.get("sessions", [])]
            self.active_id = raw.get("active_id")
        except (json.JSONDecodeError, OSError, TypeError, KeyError):
            default = ChatSession.new("This conversation")
            self.sessions = [default]
            self.active_id = default.id
        if not self.sessions:
            default = ChatSession.new("This conversation")
            self.sessions = [default]
            self.active_id = default.id
        if not self.active_id or not self.get(self.active_id):
            self.active_id = self.sessions[0].id

    def save(self) -> None:
        payload = {
            "active_id": self.active_id,
            "sessions": [s.to_dict() for s in self.sessions],
        }
        _sessions_path().write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self, session_id: str) -> ChatSession | None:
        for s in self.sessions:
            if s.id == session_id:
                return s
        return None

    def active(self) -> ChatSession:
        session = self.get(self.active_id or "")
        if session:
            return session
        return self.sessions[0]

    def set_active(self, session_id: str) -> ChatSession | None:
        if not self.get(session_id):
            return None
        self.active_id = session_id
        self.save()
        return self.get(session_id)

    def create(self, title: str) -> ChatSession:
        session = ChatSession.new(title)
        self.sessions.insert(0, session)
        self.active_id = session.id
        self.save()
        return session

    def append_message(self, speaker: str, body: str) -> None:
        session = self.active()
        session.messages.append(ChatMessage(speaker=speaker, body=body))
        session.touch()
        self.save()

    def replace_messages(self, session_id: str, messages: list[ChatMessage]) -> None:
        session = self.get(session_id)
        if not session:
            return
        session.messages = messages
        session.touch()
        self.save()

    def titles(self) -> list[tuple[str, str]]:
        return [(s.id, s.title) for s in self.sessions]
