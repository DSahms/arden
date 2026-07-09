"""
TaskManager — persistent task and priority storage for Business Sam.
Stores tasks in a local SQLite database (separate from Neo4j).
"""

import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    OPEN = "open"
    DONE = "done"
    SNOOZED = "snoozed"


@dataclass
class Task:
    id: Optional[int] = None
    content: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.OPEN
    due_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "voice"


class TaskManager:
    def __init__(self, db_path=None):
        if db_path is None:
            try:
                from modules.assistant_config import get_config
                db_path = get_config("data.tasks_db_path", default="data/tasks.db")
            except Exception:
                db_path = "data/tasks.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        self._migrate_schema()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    due_date TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    source TEXT DEFAULT 'voice'
                )
            """)
            conn.commit()

    def _migrate_schema(self):
        """Add new columns and tables if they don't already exist. Safe to run multiple times."""
        with sqlite3.connect(self.db_path) as conn:
            # Get existing columns on the tasks table
            cursor = conn.execute("PRAGMA table_info(tasks)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            # New columns to add if missing
            new_columns = {
                "project":      "TEXT DEFAULT NULL",
                "week_group":   "TEXT DEFAULT NULL",
                "category":     "TEXT DEFAULT NULL",
                "depends_on":   "TEXT DEFAULT NULL",
                "notes":        "TEXT DEFAULT NULL",
                "completed_at": "TEXT DEFAULT NULL",
            }
            for col_name, col_def in new_columns.items():
                if col_name not in existing_columns:
                    conn.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_def}")

            # Create projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    target_end_date TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    # =========================================================================
    # EXISTING METHODS (unchanged except get_overdue_tasks extended below)
    # =========================================================================

    def add_task(self, content: str, priority: Priority = Priority.MEDIUM,
                 due_date: Optional[str] = None, source: str = "voice") -> int:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (content, priority, status, due_date, created_at, updated_at, source) VALUES (?,?,?,?,?,?,?)",
                (content, priority.value, TaskStatus.OPEN.value, due_date, now, now, source)
            )
            conn.commit()
            return cursor.lastrowid

    def get_open_tasks(self) -> List[Task]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content, priority, status, due_date, created_at, updated_at, source FROM tasks WHERE status = 'open' ORDER BY CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END"
            ).fetchall()
        return [Task(id=r[0], content=r[1], priority=Priority(r[2]),
                     status=TaskStatus(r[3]), due_date=r[4],
                     created_at=r[5], updated_at=r[6], source=r[7]) for r in rows]

    def get_overdue_tasks(self, project_name: Optional[str] = None) -> List[Task]:
        """Get all tasks past their due_date that are not 'done'.
        If project_name given, filter to that project."""
        today = datetime.now().date().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            if project_name:
                rows = conn.execute(
                    "SELECT id, content, priority, status, due_date, created_at, updated_at, source"
                    " FROM tasks WHERE status = 'open' AND due_date IS NOT NULL AND due_date < ?"
                    " AND project = ?",
                    (today, project_name)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, content, priority, status, due_date, created_at, updated_at, source"
                    " FROM tasks WHERE status = 'open' AND due_date IS NOT NULL AND due_date < ?",
                    (today,)
                ).fetchall()
        return [Task(id=r[0], content=r[1], priority=Priority(r[2]),
                     status=TaskStatus(r[3]), due_date=r[4],
                     created_at=r[5], updated_at=r[6], source=r[7]) for r in rows]

    def get_due_this_week(self) -> List[Task]:
        today = datetime.now().date()
        week_end = (today + timedelta(days=7)).isoformat()
        today_str = today.isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content, priority, status, due_date, created_at, updated_at, source FROM tasks WHERE status = 'open' AND due_date IS NOT NULL AND due_date >= ? AND due_date <= ?",
                (today_str, week_end)
            ).fetchall()
        return [Task(id=r[0], content=r[1], priority=Priority(r[2]),
                     status=TaskStatus(r[3]), due_date=r[4],
                     created_at=r[5], updated_at=r[6], source=r[7]) for r in rows]

    def mark_done(self, task_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = 'done', updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), task_id)
            )
            conn.commit()
        return True

    def get_forgotten_tasks(self, days_old: int = 3) -> List[Task]:
        cutoff = (datetime.now() - timedelta(days=days_old)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content, priority, status, due_date, created_at, updated_at, source FROM tasks WHERE status = 'open' AND updated_at < ? ORDER BY priority",
                (cutoff,)
            ).fetchall()
        return [Task(id=r[0], content=r[1], priority=Priority(r[2]),
                     status=TaskStatus(r[3]), due_date=r[4],
                     created_at=r[5], updated_at=r[6], source=r[7]) for r in rows]

    def format_briefing(self) -> str:
        overdue = self.get_overdue_tasks()
        forgotten = self.get_forgotten_tasks()
        this_week = self.get_due_this_week()
        all_open = self.get_open_tasks()

        lines = []

        if overdue:
            lines.append(f"OVERDUE — {len(overdue)} item(s) past due:")
            for t in overdue:
                lines.append(f"  • {t.content} (was due {t.due_date})")

        if forgotten:
            lines.append(f"FORGOTTEN — {len(forgotten)} item(s) you haven't touched in 3+ days:")
            for t in forgotten:
                lines.append(f"  • {t.content}")

        if this_week:
            lines.append(f"THIS WEEK — {len(this_week)} item(s) due in the next 7 days:")
            for t in this_week:
                lines.append(f"  • {t.content} (due {t.due_date})")

        urgent = [t for t in all_open if t.priority == Priority.URGENT and t not in overdue]
        if urgent:
            lines.append(f"URGENT — {len(urgent)} item(s) marked urgent:")
            for t in urgent:
                lines.append(f"  • {t.content}")

        if not lines:
            lines.append("No outstanding tasks. You're clear.")

        return "\n".join(lines)

    # =========================================================================
    # PROJECT METHODS
    # =========================================================================

    def create_project(self, name: str, description: str = "",
                       start_date: Optional[str] = None,
                       target_end_date: Optional[str] = None) -> str:
        """Create a new project. Returns the project ID (uuid4 hex)."""
        project_id = uuid.uuid4().hex
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO projects (id, name, description, start_date, target_end_date, status, created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (project_id, name, description, start_date, target_end_date, "active", now)
            )
            conn.commit()
        return project_id

    def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project by name. Returns dict or None."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM projects WHERE name = ?", (project_name,)
            ).fetchone()
        return dict(row) if row else None

    def list_projects(self, status: str = "active") -> List[Dict[str, Any]]:
        """List all projects with given status. Returns list of dicts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM projects WHERE status = ? ORDER BY created_at",
                (status,)
            ).fetchall()
        return [dict(row) for row in rows]

    def add_project_task(self, project_name: str, content: str,
                         week_group: Optional[str] = None,
                         category: Optional[str] = None,
                         priority: str = "medium",
                         due_date: Optional[str] = None,
                         depends_on: Optional[str] = None,
                         notes: Optional[str] = None) -> int:
        """Add a task to a specific project. Returns task ID."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO tasks"
                " (content, priority, status, due_date, created_at, updated_at, source,"
                "  project, week_group, category, depends_on, notes)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (content, priority, TaskStatus.OPEN.value, due_date, now, now, "project",
                 project_name, week_group, category, depends_on, notes)
            )
            conn.commit()
            return cursor.lastrowid

    def get_project_tasks(self, project_name: str,
                          status: Optional[str] = None,
                          week_group: Optional[str] = None,
                          category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks for a project, optionally filtered by status, week, or category.
        Returns list of dicts ordered by due_date then priority."""
        query = "SELECT * FROM tasks WHERE project = ?"
        params: List[Any] = [project_name]

        if status:
            query += " AND status = ?"
            params.append(status)
        if week_group:
            query += " AND week_group = ?"
            params.append(week_group)
        if category:
            query += " AND category = ?"
            params.append(category)

        query += (
            " ORDER BY due_date ASC,"
            " CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2"
            " WHEN 'medium' THEN 3 ELSE 4 END"
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_project_progress(self, project_name: str) -> dict:
        """Returns progress summary for a named project."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM tasks WHERE project = ?
        """, (project_name,))
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM tasks WHERE project = ? AND status = 'complete'
        """, (project_name,))
        complete = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM tasks WHERE project = ? AND status != 'complete'
              AND due_date < date('now')
        """, (project_name,))
        overdue = cursor.fetchone()[0]

        conn.close()

        return {
            "project": project_name,
            "total": total,
            "complete": complete,
            "remaining": total - complete,
            "overdue": overdue,
            "percent_done": round((complete / total * 100), 1) if total > 0 else 0
        }

    def get_upcoming_tasks(self, project_name: Optional[str] = None,
                           days: int = 7) -> List[Dict[str, Any]]:
        """Get tasks due within the next N days that are not 'done'.
        If project_name given, filter to that project. Returns list of dicts."""
        today = datetime.now().date()
        end_date = (today + timedelta(days=days)).isoformat()
        today_str = today.isoformat()

        query = (
            "SELECT * FROM tasks"
            " WHERE status != 'done'"
            "   AND due_date IS NOT NULL"
            "   AND due_date >= ?"
            "   AND due_date <= ?"
        )
        params: List[Any] = [today_str, end_date]

        if project_name:
            query += " AND project = ?"
            params.append(project_name)

        query += (
            " ORDER BY due_date ASC,"
            " CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2"
            " WHEN 'medium' THEN 3 ELSE 4 END"
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
