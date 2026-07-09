"""What I know about you — view, edit, delete confirmed facts."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from modules.gui.first_run import _ForestDialog
from modules.gui.arden_theme import CREAM, CREAM_SOFT, FOREST_PANEL, FOREST_SIDEBAR, GILT
from modules.tactical_context import get_facts_store


class KnowledgeDialog(_ForestDialog):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(
            parent,
            title="What I know about you",
            subtitle="Confirmed facts only — edit or delete anything that's wrong.",
            width=620,
            height=640,
        )
        self.store = get_facts_store()
        self._build()
        self._reload()

    def _build(self) -> None:
        tk.Label(
            self.body,
            text="These are stored on your PC. Arden won't invent details beyond what's here.",
            bg=FOREST_PANEL,
            fg=CREAM_SOFT,
            font=("Segoe UI", 9),
            wraplength=520,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 8))

        list_frame = tk.Frame(self.body, bg=FOREST_PANEL)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            height=14,
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            selectbackground=GILT,
            selectforeground=FOREST_PANEL,
            relief=tk.FLAT,
            highlightthickness=0,
            yscrollcommand=scroll.set,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        tk.Label(
            self.body,
            text="Edit selected",
            bg=FOREST_PANEL,
            fg=GILT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(10, 4))
        self.edit = tk.Text(
            self.body,
            height=3,
            font=("Segoe UI", 11),
            bg=FOREST_SIDEBAR,
            fg=CREAM,
            insertbackground=CREAM,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=GILT,
            wrap=tk.WORD,
        )
        self.edit.pack(fill=tk.X)

        btn_row = tk.Frame(self.body, bg=FOREST_PANEL)
        btn_row.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(btn_row, text="Delete", command=self._delete).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Save edit", command=self._save_edit).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(btn_row, text="Export…", command=self._export).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(btn_row, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        self._facts: list[dict] = []

    def _reload(self) -> None:
        self._facts = self.store.list_facts()
        self.listbox.delete(0, tk.END)
        for f in self._facts:
            domain = f.get("domain", "?").replace("_", " ").title()
            self.listbox.insert(tk.END, f"[{domain}] {f.get('content', '')}")
        self.edit.delete("1.0", tk.END)

    def _selected_index(self) -> int | None:
        sel = self.listbox.curselection()
        return int(sel[0]) if sel else None

    def _on_select(self, _event=None) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        self.edit.delete("1.0", tk.END)
        self.edit.insert("1.0", self._facts[idx].get("content", ""))

    def _save_edit(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        fact = self._facts[idx]
        new_text = self.edit.get("1.0", tk.END).strip()
        if not new_text:
            return
        self.store.update_fact(fact["id"], content=new_text)
        self._reload()

    def _delete(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        fact = self._facts[idx]
        if not messagebox.askyesno("Delete fact", f"Remove this?\n\n{fact.get('content', '')}"):
            return
        self.store.delete_fact(fact["id"])
        self._reload()

    def _export(self) -> None:
        from tkinter import filedialog

        from modules.utilities.export_docx import export_facts_docx

        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export what I know",
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


def open_knowledge_dialog(parent: tk.Tk) -> None:
    KnowledgeDialog(parent)
