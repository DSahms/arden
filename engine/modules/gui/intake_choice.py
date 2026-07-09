"""Install-time intake path: A skip · B quick · C in-depth."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from modules.gui.first_run import _ForestDialog
from modules.gui.arden_theme import CREAM_SOFT, FOREST_PANEL, FONT_TAGLINE
from modules.intake.progress import load_intake_choice, save_intake_choice


class IntakeChoiceDialog(_ForestDialog):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(
            parent,
            title="Help me know you",
            subtitle="Optional — you can always come back later.",
            height=520,
        )
        self._choice: str | None = None
        self._build()

    def _build(self) -> None:
        tk.Label(
            self.body,
            text="How much time do you have right now?",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=FONT_TAGLINE,
            wraplength=420,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 12))

        options = [
            (
                "a",
                "Get started",
                "Open chat now. Add knowledge whenever you like.",
            ),
            (
                "b",
                "Quick get-to-know-you",
                "A few minutes — key people, dates, how you want to be spoken to.",
            ),
            (
                "c",
                "Help me know you",
                "Save & continue anytime. Includes the quick layer, then goes deeper.",
            ),
        ]
        for code, title, blurb in options:
            row = tk.Frame(self.body, bg=FOREST_PANEL)
            row.pack(fill=tk.X, pady=6)
            ttk.Button(
                row,
                text=title,
                style="Accent.TButton" if code == "a" else "TButton",
                command=lambda c=code: self._pick(c),
            ).pack(side=tk.LEFT)
            tk.Label(
                row,
                text=blurb,
                bg=FOREST_PANEL,
                fg=CREAM_SOFT,
                font=("Segoe UI", 9),
                wraplength=300,
                justify=tk.LEFT,
            ).pack(side=tk.LEFT, padx=(10, 0))

    def _pick(self, choice: str) -> None:
        self._choice = choice
        self._result = {"choice": choice}
        self.destroy()


def run_intake_choice_if_needed(parent: tk.Tk) -> str | None:
    """Show A/B/C once after first-run. Returns choice letter or None if already set."""
    existing = load_intake_choice()
    if existing:
        return existing.get("choice")

    dialog = IntakeChoiceDialog(parent)
    data = dialog.wait_result()
    if not data:
        save_intake_choice("a", completed=True)
        return "a"
    choice = data.get("choice", "a")
    save_intake_choice(choice, completed=(choice == "a"))
    return choice
