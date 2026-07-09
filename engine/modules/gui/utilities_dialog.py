"""Tools dialog — export, email draft, calendar glance."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Callable

from modules.gui.first_run import _ForestDialog
from modules.gui.arden_theme import CREAM, CREAM_SOFT, FOREST_PANEL, FOREST_SIDEBAR, GILT, FONT_TAGLINE
from modules.gui.session_store import ChatSession
from modules.utilities.calendar_view import link_calendar_file, list_upcoming_events
from modules.utilities.email_draft import draft_email_to_clipboard
from modules.utilities.export_docx import export_facts_docx, export_session_docx


class UtilitiesDialog(_ForestDialog):
    def __init__(
        self,
        parent: tk.Tk,
        *,
        session: ChatSession,
        brain_generate: Callable[[str, str], str] | None,
        user_name: str = "",
        assistant_name: str = "Arden",
    ) -> None:
        super().__init__(
            parent,
            title="Tools",
            subtitle="Export · draft email · calendar glance",
            width=580,
            height=640,
        )
        self.session = session
        self.brain_generate = brain_generate
        self.user_name = user_name
        self.assistant_name = assistant_name
        self._build()

    def _build(self) -> None:
        tk.Label(
            self.body,
            text="Nothing sends automatically. Drafts go to your clipboard; you paste and send.",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=FONT_TAGLINE,
            wraplength=500,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 12))

        export_row = tk.Frame(self.body, bg=FOREST_PANEL)
        export_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(export_row, text="Export this chat…", command=self._export_chat).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(export_row, text="Export what I know…", command=self._export_facts).pack(
            side=tk.LEFT
        )

        tk.Label(
            self.body,
            text="Email draft",
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(12, 4))
        self.email_topic = tk.Entry(
            self.body,
            font=("Segoe UI", 11),
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            insertbackground=CREAM,
            relief=tk.FLAT,
        )
        self.email_topic.pack(fill=tk.X, ipady=6, pady=(0, 6))
        self.email_topic.insert(0, "Follow up on yesterday's meeting")
        ttk.Button(
            self.body,
            text="Draft & copy to clipboard",
            style="Accent.TButton",
            command=self._draft_email,
        ).pack(anchor="w", pady=(0, 8))

        self.draft_preview = scrolledtext.ScrolledText(
            self.body,
            height=5,
            wrap=tk.WORD,
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            relief=tk.FLAT,
            font=("Segoe UI", 10),
        )
        self.draft_preview.pack(fill=tk.X, pady=(0, 8))

        cal_row = tk.Frame(self.body, bg=FOREST_PANEL)
        cal_row.pack(fill=tk.X, pady=(8, 4))
        ttk.Button(cal_row, text="Link .ics calendar…", command=self._link_ics).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(cal_row, text="Refresh", command=self._refresh_calendar).pack(side=tk.LEFT)

        tk.Label(
            self.body,
            text="Upcoming (read-only)",
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(8, 4))
        self.cal_list = scrolledtext.ScrolledText(
            self.body,
            height=8,
            wrap=tk.WORD,
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            state=tk.DISABLED,
        )
        self.cal_list.pack(fill=tk.BOTH, expand=True)
        self._refresh_calendar()

        ttk.Button(self.body, text="Close", command=self.destroy).pack(anchor="e", pady=(12, 0))

    def _export_chat(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export chat",
            defaultextension=".docx",
            filetypes=[("Word document", "*.docx"), ("Text", "*.txt")],
            initialfile=f"{self.session.title}.docx",
        )
        if not path:
            return
        try:
            out = export_session_docx(self.session, Path(path))
            messagebox.showinfo("Export", f"Saved:\n{out}", parent=self)
        except Exception as exc:
            messagebox.showerror("Export", str(exc), parent=self)

    def _export_facts(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export facts",
            defaultextension=".docx",
            filetypes=[("Word document", "*.docx"), ("Text", "*.txt")],
            initialfile="what-i-know.docx",
        )
        if not path:
            return
        try:
            out = export_facts_docx(Path(path))
            messagebox.showinfo("Export", f"Saved:\n{out}", parent=self)
        except Exception as exc:
            messagebox.showerror("Export", str(exc), parent=self)

    def _clipboard(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def _draft_email(self) -> None:
        if not self.brain_generate:
            messagebox.showwarning("Draft email", "Pick a brain in Chat first.", parent=self)
            return
        topic = self.email_topic.get().strip()
        try:
            body = draft_email_to_clipboard(
                topic=topic,
                brain_generate=self.brain_generate,
                clipboard_set=self._clipboard,
                user_name=self.user_name,
                assistant_name=self.assistant_name,
            )
            self.draft_preview.delete("1.0", tk.END)
            self.draft_preview.insert("1.0", body)
            messagebox.showinfo("Draft email", "Copied to clipboard — paste into your mail app.", parent=self)
        except Exception as exc:
            messagebox.showerror("Draft email", str(exc), parent=self)

    def _link_ics(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Link calendar file",
            filetypes=[("iCalendar", "*.ics"), ("All", "*.*")],
        )
        if not path:
            return
        try:
            link_calendar_file(Path(path))
            self._refresh_calendar()
            messagebox.showinfo("Calendar", "Linked. Read-only — Arden never sends or edits events.", parent=self)
        except Exception as exc:
            messagebox.showerror("Calendar", str(exc), parent=self)

    def _refresh_calendar(self) -> None:
        lines = list_upcoming_events()
        self.cal_list.configure(state=tk.NORMAL)
        self.cal_list.delete("1.0", tk.END)
        self.cal_list.insert("1.0", "\n".join(lines))
        self.cal_list.configure(state=tk.DISABLED)


def open_utilities_dialog(
    parent: tk.Tk,
    *,
    session: ChatSession,
    brain_generate: Callable[[str, str], str] | None = None,
    user_name: str = "",
    assistant_name: str = "Arden",
) -> None:
    UtilitiesDialog(
        parent,
        session=session,
        brain_generate=brain_generate,
        user_name=user_name,
        assistant_name=assistant_name,
    )
