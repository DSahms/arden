"""Sources panel — upload docs, multi-select, RAG with active brain."""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import TYPE_CHECKING

from modules.assistant_config import get_config
from modules.gui.arden_theme import CREAM, FOREST_PANEL, FOREST_SIDEBAR, GILT
from modules.gui.arden_widgets import mini_tree_banner
from modules.sources.document_store import DocumentStore
from modules.sources.ingest import supported_extensions
from modules.sources.rag import answer_from_sources, ingest_file
from utils.embedding_utils import HashEmbedder

if TYPE_CHECKING:
    from modules.base_assistant import PlainAssistant


class SourcesPanel(ttk.Frame):
    """User files + doc Q&A — same brain as Chat."""

    def __init__(
        self,
        master: tk.Widget,
        assistant: PlainAssistant,
        logger: logging.Logger,
        **kwargs,
    ) -> None:
        super().__init__(master, style="Header.TFrame", **kwargs)
        self.assistant = assistant
        self.logger = logger
        self._busy = False
        self._store = DocumentStore(embed=HashEmbedder().embed)
        self._assistant_name = get_config("base_assistant.assistant_name", default="Arden")
        self._check_vars: dict[str, tk.BooleanVar] = {}
        self._checks_inner: tk.Frame | None = None
        self._build()
        self._reload_docs()

    def _build(self) -> None:
        toolbar = ttk.Frame(self, style="Header.TFrame", padding=(16, 10, 16, 6))
        toolbar.pack(fill=tk.X)

        head = ttk.Frame(toolbar, style="Header.TFrame")
        head.pack(fill=tk.X)
        ttk.Label(head, text="Sources", style="PanelTitle.TLabel").pack(side=tk.LEFT)
        mini_tree_banner(head, width=96, height=56).pack(side=tk.RIGHT)

        meta = ttk.Frame(toolbar, style="Header.TFrame")
        meta.pack(fill=tk.X, pady=(4, 6))
        ttk.Label(
            meta,
            text="Select files on the left · ask about one, some, or all",
            style="HeaderMuted.TLabel",
        ).pack(side=tk.LEFT)

        body = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        left = ttk.Frame(body, style="Header.TFrame", width=240)
        body.add(left, weight=0)

        ttk.Label(left, text="YOUR FILES", style="Eyebrow.TLabel").pack(anchor="w", pady=(0, 4))

        sel_row = ttk.Frame(left, style="Header.TFrame")
        sel_row.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(sel_row, text="Select all", command=self._select_all).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(sel_row, text="Select none", command=self._select_none).pack(side=tk.LEFT)

        list_wrap = ttk.Frame(left, style="Header.TFrame")
        list_wrap.pack(fill=tk.BOTH, expand=True)
        list_wrap.grid_rowconfigure(0, weight=1)
        list_wrap.grid_columnconfigure(0, weight=1)

        self._checks_canvas = tk.Canvas(
            list_wrap,
            bg=FOREST_SIDEBAR,
            highlightthickness=0,
            borderwidth=0,
        )
        scroll = ttk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=self._checks_canvas.yview)
        self._checks_canvas.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self._checks_canvas.configure(yscrollcommand=scroll.set)

        self._checks_inner = tk.Frame(self._checks_canvas, bg=FOREST_SIDEBAR)
        self._checks_window = self._checks_canvas.create_window(
            (0, 0), window=self._checks_inner, anchor="nw"
        )
        self._checks_inner.bind(
            "<Configure>",
            lambda _e: self._checks_canvas.configure(
                scrollregion=self._checks_canvas.bbox("all")
            ),
        )
        self._checks_canvas.bind(
            "<Configure>",
            lambda e: self._checks_canvas.itemconfig(self._checks_window, width=e.width),
        )

        btn_row = ttk.Frame(left, style="Header.TFrame")
        btn_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btn_row, text="Add file…", command=self._add_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Remove", command=self._remove_file).pack(side=tk.LEFT)

        self._scope_label = ttk.Label(
            left,
            text="0 sources selected",
            style="HeaderMuted.TLabel",
            wraplength=220,
        )
        self._scope_label.pack(anchor="w", pady=(8, 0))

        right = ttk.Frame(body, style="Header.TFrame")
        body.add(right, weight=1)
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        input_row = ttk.Frame(right, style="Header.TFrame")
        input_row.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ask_head = ttk.Frame(input_row, style="Header.TFrame")
        ask_head.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(ask_head, text="Ask about selected sources", style="Eyebrow.TLabel").pack(
            side=tk.LEFT
        )
        self._ask_scope = ttk.Label(ask_head, text="", style="HeaderMuted.TLabel")
        self._ask_scope.pack(side=tk.RIGHT)

        entry_row = ttk.Frame(input_row, style="Header.TFrame")
        entry_row.pack(fill=tk.X)
        self.question = tk.Entry(entry_row, font=("Segoe UI", 11))
        self.question.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.question.bind("<Return>", lambda _e: self._ask())
        ttk.Button(entry_row, text="Ask", style="Accent.TButton", command=self._ask).pack(
            side=tk.RIGHT
        )

        self.chat = scrolledtext.ScrolledText(
            right,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=FOREST_PANEL,
            fg="#d4d0bc",
            insertbackground="#d4d0bc",
            relief=tk.FLAT,
            font=("Segoe UI", 11),
            height=8,
        )
        self.chat.grid(row=0, column=0, sticky="nsew")

    def _append(self, speaker: str, text: str) -> None:
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{speaker}\n{text}\n\n")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)

    def _update_scope_labels(self) -> None:
        docs = self._store.list_documents()
        selected = self._selected_doc_ids()
        n_sel = len(selected)
        n_all = len(docs)
        if n_all == 0:
            self._scope_label.configure(text="Add files to get started")
            self._ask_scope.configure(text="")
            return
        if n_sel == 0:
            self._scope_label.configure(text="No files selected — check at least one")
            self._ask_scope.configure(text="")
        elif n_sel == n_all:
            self._scope_label.configure(text=f"All {n_all} sources selected")
            self._ask_scope.configure(text=f"{n_all} sources")
        elif n_sel == 1:
            doc = self._store.get_document(selected[0])
            name = (doc or {}).get("filename", "1 file")
            self._scope_label.configure(text=f"1 source: {name}")
            self._ask_scope.configure(text="1 source")
        else:
            self._scope_label.configure(text=f"{n_sel} of {n_all} sources selected")
            self._ask_scope.configure(text=f"{n_sel} sources")

    def _reload_docs(self) -> None:
        prev = {did: var.get() for did, var in self._check_vars.items()}
        self._check_vars.clear()
        if self._checks_inner is not None:
            for child in self._checks_inner.winfo_children():
                child.destroy()

        docs = self._store.list_documents()
        for doc in docs:
            did = doc.get("id", "")
            if not did:
                continue
            var = tk.BooleanVar(value=prev.get(did, True))
            self._check_vars[did] = var
            label = doc.get("filename", "file")
            if len(label) > 36:
                label = label[:33] + "…"
            tk.Checkbutton(
                self._checks_inner,
                text=label,
                variable=var,
                anchor="w",
                bg=FOREST_SIDEBAR,
                fg=CREAM,
                selectcolor=FOREST_PANEL,
                activebackground=FOREST_SIDEBAR,
                activeforeground=CREAM,
                highlightthickness=0,
                command=self._update_scope_labels,
            ).pack(fill=tk.X, padx=4, pady=1)

        self._update_scope_labels()

    def _selected_doc_ids(self) -> list[str]:
        return [did for did, var in self._check_vars.items() if var.get()]

    def _select_all(self) -> None:
        for var in self._check_vars.values():
            var.set(True)
        self._update_scope_labels()

    def _select_none(self) -> None:
        for var in self._check_vars.values():
            var.set(False)
        self._update_scope_labels()

    def _add_file(self) -> None:
        exts = " ".join(f"*{e}" for e in supported_extensions())
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title="Add source file",
            filetypes=[("Documents", exts), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            ingest_file(self._store, Path(path))
            self._reload_docs()
            self._append("Sources", f"Added {Path(path).name}. Check files on the left, then ask below.")
        except Exception as exc:
            messagebox.showerror("Add file", str(exc), parent=self.winfo_toplevel())

    def _remove_file(self) -> None:
        selected = self._selected_doc_ids()
        if not selected:
            messagebox.showinfo("Remove", "Check at least one file to remove.")
            return
        if len(selected) == 1:
            doc = self._store.get_document(selected[0])
            name = (doc or {}).get("filename", "this file")
            msg = f"Remove {name} from sources?"
        else:
            msg = f"Remove {len(selected)} selected files from sources?"
        if not messagebox.askyesno("Remove", msg):
            return
        for doc_id in selected:
            self._store.delete_document(doc_id)
        self._reload_docs()

    def _brain_generate(self, system: str, user: str) -> str:
        if not self.assistant.brain_backend:
            return "No brain selected — pick Venice or Groq in the Chat tab first."
        return self.assistant.brain_backend.generate_response(system, user)

    def _ask(self) -> None:
        if self._busy:
            return
        q = self.question.get().strip()
        if not q:
            return
        if not self._store.list_documents():
            messagebox.showinfo("Sources", "Add a file first.")
            return
        selected = self._selected_doc_ids()
        if not selected:
            messagebox.showinfo("Sources", "Check at least one file on the left.")
            return

        self.question.delete(0, tk.END)
        scope_note = f" ({len(selected)} source{'s' if len(selected) != 1 else ''})"
        self._append("You", q + scope_note)
        self._busy = True
        doc_ids = selected
        all_docs = self._store.list_documents()
        if len(selected) == len(all_docs):
            doc_ids = None

        def worker() -> None:
            try:
                answer, snippets = answer_from_sources(
                    self._store,
                    question=q,
                    doc_ids=doc_ids,
                    brain_generate=self._brain_generate,
                )
                if snippets:
                    cite = "\n".join(f"  · {s}" for s in snippets[:3])
                    answer = f"{answer}\n\n(from your files)\n{cite}"
                self.after(0, lambda: self._append(self._assistant_name, answer))
            except Exception as exc:
                self.logger.exception("[Sources] ask failed")
                self.after(0, lambda: self._append("Sources", f"Error: {exc}"))
            finally:
                self.after(0, lambda: setattr(self, "_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    def on_show(self) -> None:
        self._reload_docs()

    def on_hide(self) -> None:
        pass
