"""Structured tactical facts — separate from episodic chat memory."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TacticalFactsStore:
    def __init__(self, db_path: str | Path):
        self.db_path = str(Path(db_path))
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _initialize_schema(self) -> None:
        assert self._conn is not None
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tactical_facts (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                label TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL,
                confirmed INTEGER NOT NULL DEFAULT 1,
                source TEXT NOT NULL DEFAULT 'intake',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_facts_domain ON tactical_facts(domain);
            CREATE INDEX IF NOT EXISTS idx_facts_confirmed ON tactical_facts(confirmed);
            """
        )
        self._conn.commit()

    def add_fact(
        self,
        domain: str,
        content: str,
        *,
        label: str = "",
        source: str = "intake",
        confirmed: bool = True,
    ) -> dict[str, Any]:
        assert self._conn is not None
        fact_id = str(uuid.uuid4())
        now = _utc_now()
        self._conn.execute(
            """
            INSERT INTO tactical_facts (id, domain, label, content, confirmed, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (fact_id, domain, label, content, 1 if confirmed else 0, source, now, now),
        )
        self._conn.commit()
        return self.get_fact(fact_id) or {}

    def update_fact(self, fact_id: str, *, content: str | None = None, label: str | None = None) -> bool:
        assert self._conn is not None
        row = self.get_fact(fact_id)
        if not row:
            return False
        new_content = content if content is not None else row["content"]
        new_label = label if label is not None else row["label"]
        now = _utc_now()
        self._conn.execute(
            """
            UPDATE tactical_facts SET content = ?, label = ?, updated_at = ? WHERE id = ?
            """,
            (new_content, new_label, now, fact_id),
        )
        self._conn.commit()
        return True

    def delete_fact(self, fact_id: str) -> bool:
        assert self._conn is not None
        cur = self._conn.execute("DELETE FROM tactical_facts WHERE id = ?", (fact_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def get_fact(self, fact_id: str) -> dict[str, Any] | None:
        assert self._conn is not None
        row = self._conn.execute("SELECT * FROM tactical_facts WHERE id = ?", (fact_id,)).fetchone()
        return dict(row) if row else None

    def list_facts(
        self,
        *,
        domain: str | None = None,
        confirmed_only: bool = True,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        assert self._conn is not None
        sql = "SELECT * FROM tactical_facts WHERE 1=1"
        params: list[Any] = []
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        if confirmed_only:
            sql += " AND confirmed = 1"
        sql += " ORDER BY domain, created_at DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def format_for_prompt(self, limit: int = 40) -> str:
        facts = self.list_facts(limit=limit)
        if not facts:
            return ""
        lines = ["[What I know about you — confirmed facts only. Do not invent beyond this.]"]
        by_domain: dict[str, list[str]] = {}
        for f in facts:
            by_domain.setdefault(f["domain"], [])
            prefix = f"{f['label']}: " if f.get("label") else ""
            by_domain[f["domain"]].append(f"{prefix}{f['content']}")
        for domain, items in sorted(by_domain.items()):
            lines.append(f"{domain.replace('_', ' ').title()}:")
            for item in items:
                lines.append(f"  - {item}")
        lines.append(
            "If a detail is not listed above, say you do not know yet — do not guess life details."
        )
        return "\n".join(lines)
