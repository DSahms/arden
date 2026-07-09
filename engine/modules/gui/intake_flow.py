"""Get-to-know-you flow — one question, confirm before store, finish later."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from modules.gui.first_run import _ForestDialog
from modules.gui.arden_theme import CREAM, CREAM_SOFT, FOREST_PANEL, FOREST_SIDEBAR, GILT
from modules.intake.engine import IntakeEngine
from modules.intake.facts_store import TacticalFactsStore
from modules.intake.progress import save_intake_choice
from modules.tactical_context import facts_db_path, get_facts_store


class IntakeFlowDialog(_ForestDialog):
    def __init__(
        self,
        parent: tk.Tk,
        *,
        mode: str,
        brain_generate: Callable[[str], str] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Help me know you",
            subtitle="One question at a time — skip anything you'd rather not say.",
            width=560,
            height=620,
        )
        self.mode = mode
        self.on_complete = on_complete
        store = TacticalFactsStore(facts_db_path())
        store.connect()
        self.engine = IntakeEngine(mode, store, brain_generate=brain_generate)
        self._pending: dict[str, str] | None = None
        self._current: tuple[str, str] | None = None
        self._build()
        self._show_current()

    def _build(self) -> None:
        self.progress_var = tk.StringVar(value="")
        ttk.Label(self.body, textvariable=self.progress_var, style="HeaderMuted.TLabel").pack(
            anchor="w", pady=(0, 8)
        )

        self.domain_var = tk.StringVar(value="")
        tk.Label(
            self.body,
            textvariable=self.domain_var,
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.question_var = tk.StringVar(value="")
        tk.Label(
            self.body,
            textvariable=self.question_var,
            bg=FOREST_PANEL,
            fg=CREAM,
            font=("Segoe UI", 12),
            wraplength=460,
            justify=tk.LEFT,
        ).pack(fill=tk.X, pady=(8, 12))

        tk.Label(
            self.body,
            text="Your answer",
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X)
        self.answer = tk.Text(
            self.body,
            height=5,
            font=("Segoe UI", 11),
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            insertbackground=CREAM,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=GILT,
            wrap=tk.WORD,
        )
        self.answer.pack(fill=tk.X, pady=(4, 12))

        btn_row = tk.Frame(self.body, bg=FOREST_PANEL)
        btn_row.pack(fill=tk.X)

        ttk.Button(btn_row, text="Finish later", command=self._finish_later).pack(side=tk.LEFT)
        domain = self.engine.current_domain()
        if domain and domain.opt_in:
            ttk.Button(btn_row, text="Rather not say", command=self._skip_domain).pack(
                side=tk.LEFT, padx=(8, 0)
            )
        ttk.Button(btn_row, text="Skip", command=self._skip_question).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            btn_row,
            text="Next",
            style="Accent.TButton",
            command=self._next,
        ).pack(side=tk.RIGHT)

    def _show_current(self) -> None:
        self.progress_var.set(self.engine.progress_summary())
        pair = self.engine.current_question()
        self._current = pair
        if not pair:
            self._complete()
            return
        domain_id, question = pair
        domain = self.engine.current_domain()
        title = domain.title if domain else domain_id
        self.domain_var.set(title)
        self.question_var.set(question)
        self.answer.delete("1.0", tk.END)

    def _finish_later(self) -> None:
        self.engine.finish_later()
        save_intake_choice(self.mode, completed=False)
        self.destroy()

    def _skip_domain(self) -> None:
        if self.engine.skip_opt_in_domain():
            self._show_current()

    def _skip_question(self) -> None:
        if not self._current:
            return
        domain_id, question = self._current
        self.engine.skip_question(domain_id, question)
        self._show_current()

    def _next(self) -> None:
        if not self._current:
            return
        domain_id, question = self._current
        answer = self.answer.get("1.0", tk.END).strip()
        if not answer:
            messagebox.showinfo("Help me know you", "Type an answer, or use Skip / Rather not say.")
            return

        proposal = self.engine.propose_fact(domain_id, question, answer)
        # In intake, Next means "yes, remember this" — edit/delete anytime under What I know about you.
        self.engine.record_answer(
            domain_id,
            question,
            answer,
            store_fact=True,
            proposal=proposal,
        )
        if self.engine.mode == "c":
            follow = self.engine.generate_follow_up(domain_id, question, answer)
            if follow:
                self.engine.inject_follow_up(domain_id, follow)
        self._show_current()

    def _complete(self) -> None:
        self.engine.mark_complete()
        save_intake_choice(self.mode, completed=True)
        get_facts_store().format_for_prompt()
        if self.on_complete:
            self.on_complete()
        messagebox.showinfo(
            "Help me know you",
            "Thank you — I'll show up better with what you shared.\n"
            "You can edit anytime under What I know about you.",
        )
        self.destroy()


def open_intake_flow(
    parent: tk.Tk,
    *,
    mode: str | None = None,
    brain_generate: Callable[[str], str] | None = None,
) -> None:
    from modules.intake.progress import IntakeProgressStore, load_intake_choice

    progress = IntakeProgressStore().load()
    if progress and not progress.completed:
        mode = progress.mode
    elif mode is None:
        choice = load_intake_choice()
        mode = (choice or {}).get("choice", "c")
        if mode == "a":
            mode = "c"
    IntakeFlowDialog(parent, mode=mode, brain_generate=brain_generate)
