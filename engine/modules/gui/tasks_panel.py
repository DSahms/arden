"""Tasks panel — open tasks and mark done (Consigliere edition)."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from modules.gui.arden_theme import CREAM, FOREST_PANEL, GILT
from modules.gui.first_run import _ForestDialog
from modules.task_manager import TaskManager


class TasksDialog(_ForestDialog):
    def __init__(self, parent: tk.Tk, task_manager: TaskManager) -> None:
        super().__init__(
            parent,
            title="Tasks",
            subtitle="Open items — chief-of-staff view. Facts only; you mark done.",
            width=520,
            height=480,
        )
        self.tasks = task_manager
        self._build()
        self._refresh()

    def _build(self) -> None:
        toolbar = ttk.Frame(self.body, style="Header.TFrame")
        toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        self.listbox = tk.Listbox(
            self.body,
            bg=FOREST_PANEL,
            fg=CREAM,
            selectbackground=GILT,
            selectforeground=FOREST_PANEL,
            font=("Segoe UI", 10),
            height=16,
            activestyle="none",
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        btn_row = ttk.Frame(self.body, style="Header.TFrame")
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Mark selected done", command=self._mark_done).pack(side=tk.LEFT)

        self.hint = tk.Label(
            self.body,
            text="Tip: say “remind me to …” in chat to add tasks.",
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.hint.pack(fill=tk.X, pady=(8, 0))

        self._open_tasks: list = []

    def _refresh(self) -> None:
        self.listbox.delete(0, tk.END)
        self._open_tasks = self.tasks.get_open_tasks()
        if not self._open_tasks:
            self.listbox.insert(tk.END, "No open tasks — you're clear.")
            return
        for task in self._open_tasks:
            pri = task.priority.value.upper()
            due = f" · due {task.due_date}" if task.due_date else ""
            self.listbox.insert(tk.END, f"#{task.id} [{pri}]{due} — {task.content}")

    def _mark_done(self) -> None:
        sel = self.listbox.curselection()
        if not sel or not self._open_tasks:
            return
        idx = sel[0]
        if idx >= len(self._open_tasks):
            return
        task = self._open_tasks[idx]
        if messagebox.askyesno("Mark done", f"Mark this done?\n\n{task.content}", parent=self):
            self.tasks.mark_done(task.id)
            self._refresh()


def open_tasks_dialog(parent: tk.Tk, task_manager: TaskManager) -> None:
    TasksDialog(parent, task_manager)
