"""Forest-themed first-run and settings dialogs for Arden Desktop."""

from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from modules.gui.arden_decor import draw_sidebar_tree, gold_rule
from modules.gui.arden_theme import (
    CREAM,
    CREAM_SOFT,
    FONT_DISPLAY,
    FONT_SERIF,
    FONT_TAGLINE,
    FOREST_DEEP,
    FOREST_PANEL,
    FOREST_SIDEBAR,
    GILT,
    QUOTE,
    TAGLINE,
)

DEFAULT_ASSISTANT_NAME = "Arden"


def _data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Arden"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _marker_path() -> Path:
    return _data_dir() / ".first_run_done"


def needs_first_run() -> bool:
    return not _marker_path().exists()


class _ForestDialog(tk.Toplevel):
    """Shared forest sanctuary modal chrome."""

    def __init__(
        self,
        parent: tk.Tk,
        *,
        title: str,
        subtitle: str,
        width: int = 520,
        height: int = 560,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.configure(bg=FOREST_DEEP)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        outer = tk.Frame(self, bg=FOREST_DEEP, padx=24, pady=20)
        outer.pack(fill=tk.BOTH, expand=True)

        tree = tk.Canvas(outer, width=120, height=72, bg=FOREST_DEEP, highlightthickness=0)
        tree.pack()
        draw_sidebar_tree(tree)

        tk.Label(
            outer,
            text="ARDEN DESKTOP",
            bg=FOREST_DEEP,
            fg=GILT,
            font=FONT_DISPLAY,
        ).pack(pady=(8, 2))
        tk.Label(
            outer,
            text=subtitle,
            bg=FOREST_DEEP,
            fg=CREAM_SOFT,
            font=FONT_TAGLINE,
            wraplength=440,
            justify=tk.CENTER,
        ).pack(pady=(0, 4))
        tk.Label(
            outer,
            text=f'"{QUOTE}"',
            bg=FOREST_DEEP,
            fg=CREAM_SOFT,
            font=FONT_SERIF,
            wraplength=440,
            justify=tk.CENTER,
        ).pack(pady=(0, 12))

        gold_rule(outer)

        self.body = tk.Frame(outer, bg=FOREST_PANEL, padx=20, pady=16)
        self.body.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self._result: dict | None = None

    def _field(self, label: str, *, show: str | None = None, default: str = "") -> tk.Entry:
        tk.Label(
            self.body,
            text=label,
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(10, 4))
        entry = tk.Entry(
            self.body,
            show=show,
            font=("Segoe UI", 11),
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            insertbackground=CREAM,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=GILT,
        )
        if default:
            entry.insert(0, default)
        entry.pack(fill=tk.X, ipady=6)
        return entry

    def wait_result(self) -> dict | None:
        self.wait_window()
        return self._result


class FirstRunWizard(_ForestDialog):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(
            parent,
            title="Welcome to Arden",
            subtitle=TAGLINE,
        )

        tk.Label(
            self.body,
            text="Set up your companion — everything stays on your machine.",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=FONT_TAGLINE,
            wraplength=400,
            justify=tk.LEFT,
        ).pack(anchor="w")

        self.assistant_entry = self._field(
            "Assistant name",
            default=DEFAULT_ASSISTANT_NAME,
        )
        self.name_entry = self._field("What should they call you?")
        self.venice_entry = self._field("Venice API key (recommended)", show="*")
        self.groq_entry = self._field("Groq API key (free backup)", show="*")

        tk.Label(
            self.body,
            text="venice.ai · private Llama 3.3 70B  ·  or console.groq.com",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(8, 0))

        btn_row = tk.Frame(self.body, bg=FOREST_PANEL)
        btn_row.pack(fill=tk.X, pady=(16, 0))

        ttk.Button(
            btn_row,
            text="Begin",
            style="Accent.TButton",
            command=self._finish,
        ).pack(side=tk.RIGHT)

    def _finish(self) -> None:
        venice = self.venice_entry.get().strip()
        groq = self.groq_entry.get().strip()
        if not venice and not groq:
            self.venice_entry.configure(highlightbackground="#c97a6a")
            return

        assistant = self.assistant_entry.get().strip() or DEFAULT_ASSISTANT_NAME
        self._result = {
            "assistant_name": assistant,
            "human_name": self.name_entry.get().strip() or None,
            "venice_key": venice or None,
            "groq_key": groq or None,
        }
        self.destroy()


class SettingsDialog(_ForestDialog):
    """Update companion name, your name, and API keys."""

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(
            parent,
            title="Arden Settings",
            subtitle="Keep the soul. Change the brain.",
            height=580,
        )

        from modules.consumer_bootstrap import load_user_secrets

        secrets = load_user_secrets() or {}
        profile: dict = {}
        profile_path = _data_dir() / "user.json"
        if profile_path.exists():
            try:
                import json

                profile = json.loads(profile_path.read_text(encoding="utf-8"))
            except Exception:
                profile = {}

        tk.Label(
            self.body,
            text="Name your companion anything you like — Arden is just the default.",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=FONT_TAGLINE,
            wraplength=400,
            justify=tk.LEFT,
        ).pack(anchor="w")

        self.assistant_entry = self._field(
            "Assistant name",
            default=profile.get("assistant_name", DEFAULT_ASSISTANT_NAME),
        )
        self.name_entry = self._field(
            "What should they call you?",
            default=profile.get("name", ""),
        )

        self.venice_entry = self._field(
            "Venice API key",
            show="*",
            default=secrets.get("venice_key", "") or os.getenv("VENICE_API_KEY", ""),
        )
        self.groq_entry = self._field(
            "Groq API key",
            show="*",
            default=secrets.get("groq_key", "") or os.getenv("GROQ_API_KEY", ""),
        )

        tk.Label(
            self.body,
            text="Brain is chosen in the Chat tab (bottom bar), not here.\n"
            "Local: kobold (KoboldCpp on port 5001, no key). Cloud: Venice or Groq.\n"
            "Keys save to this PC only.",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=("Segoe UI", 9),
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(8, 0))

        btn_row = tk.Frame(self.body, bg=FOREST_PANEL)
        btn_row.pack(fill=tk.X, pady=(16, 0))
        ttk.Button(btn_row, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(
            btn_row,
            text="Save",
            style="Accent.TButton",
            command=self._save,
        ).pack(side=tk.RIGHT)

    def _save(self) -> None:
        venice = self.venice_entry.get().strip()
        groq = self.groq_entry.get().strip()
        assistant = self.assistant_entry.get().strip() or DEFAULT_ASSISTANT_NAME
        self._result = {
            "assistant_name": assistant,
            "human_name": self.name_entry.get().strip() or None,
            "venice_key": venice or None,
            "groq_key": groq or None,
        }
        self.destroy()


def run_first_run_wizard(root: tk.Tk) -> None:
    """Forest-themed setup on first launch."""
    if not needs_first_run():
        return

    wizard = FirstRunWizard(root)
    data = wizard.wait_result()
    if not data:
        root.destroy()
        return

    from modules.consumer_bootstrap import bootstrap_consumer, save_user_secrets

    save_user_secrets(
        name=data.get("human_name"),
        groq_key=data.get("groq_key"),
        venice_key=data.get("venice_key"),
        assistant_name=data.get("assistant_name"),
    )
    bootstrap_consumer()
    _marker_path().touch()


def open_settings_dialog(root: tk.Tk) -> None:
    """Re-open API key settings from the shell."""
    dialog = SettingsDialog(root)
    data = dialog.wait_result()
    if not data:
        return

    from modules.consumer_bootstrap import bootstrap_consumer, save_user_secrets

    save_user_secrets(
        name=data.get("human_name"),
        assistant_name=data.get("assistant_name"),
        venice_key=data.get("venice_key"),
        groq_key=data.get("groq_key"),
    )
    bootstrap_consumer()
