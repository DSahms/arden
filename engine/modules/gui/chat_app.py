"""Arden Desktop shell — ink/vellum/gilt theme, tabs, streaming chat."""

from __future__ import annotations

import logging
import os
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

from modules.arden_env import is_business_edition, is_consumer, is_consigliere
from modules.assistant_config import get_config
from modules.base_assistant import AVAILABLE_BACKENDS, PlainAssistant
from modules.gui.arden_decor import StatusPulse, draw_sidebar_tree, forest_canvas_bg, gold_rule, style_listbox
from modules.gui.arden_theme import GILT, TAGLINE, apply as apply_arden_theme
from modules.gui.arden_theme import configure_chat_text
from modules.gui.arden_widgets import apply_paned_style, sanctuary_input_frame
from modules.gui.sources_panel import SourcesPanel
from modules.gui.session_store import SessionStore
from modules.utils import create_session_logger_id, setup_logging
from modules.gui.first_run import run_first_run_wizard
from modules.gui.first_run import open_settings_dialog
from modules.gui.startup_check import require_groq_key_or_exit
from modules.gui.voice_io import listen_once, speak_text

CONSUMER_BRAINS = ("kobold", "venice", "groq")
DAVE_BRAINS = ("kobold", "venice", "groq", "claude", "ollama", "lm_studio")

BRAIN_LABELS: dict[str, str] = {
    "kobold": "Local (Kobold)",
    "venice": "Venice Cloud",
    "groq": "Groq Cloud",
    "claude": "Claude",
    "ollama": "Ollama Local",
    "lm_studio": "LM Studio",
}


def _brain_label(brain_id: str) -> str:
    return BRAIN_LABELS.get(brain_id, brain_id)


def _brain_id(label_or_id: str) -> str:
    t = (label_or_id or "").strip()
    if not t:
        return ""
    lower = t.lower()
    for bid, lbl in BRAIN_LABELS.items():
        if lower == bid or lower == lbl.lower():
            return bid
    return lower


class ChatApp:
    """Unified Arden Desktop chrome — chat + sources in one window."""

    def __init__(self, root: tk.Tk, assistant: PlainAssistant, logger: logging.Logger):
        self.root = root
        self.assistant = assistant
        self.logger = logger
        self._queue: queue.Queue = queue.Queue()
        self._busy = False
        self._assistant_name = get_config("base_assistant.assistant_name", default="Arden")
        self._voice_out = get_config("base_assistant.voice", default="none") != "none"
        self._listening = False
        self._sessions = SessionStore()
        self._brain_options = self._brains_for_edition()
        self._active_tab = "chat"
        self._stream_job: str | None = None
        self._live_stream = False
        self._worker_timeout_s = 120
        self._busy_watchdog: str | None = None
        self._request_id = 0
        self._shutting_down = False
        self._poll_job: str | None = None
        self._startup_jobs: list[str] = []
        self._user_messages_session = 0
        self._deepening_pending = None
        self._deepening_used_session = False
        self._last_user_text = ""

        self.root.title(
            "Arden Consigliere Desktop"
            if is_consigliere()
            else "Arden Desktop"
        )
        self.root.geometry("1120x780")
        self.root.minsize(860, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._shutdown)

        self._build_ui()
        self._reload_session_list()
        self._load_session(self._sessions.active())
        if not self._sessions.active().messages:
            self._show_greeting()
        self._poll_queue()

    def _kobold_reachable(self) -> bool:
        try:
            import requests

            url = get_config("kobold.base_url", default="http://127.0.0.1:5001/v1")
            r = requests.get(f"{url.rstrip('/')}/models", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def _brains_for_edition(self) -> tuple[str, ...]:
        if is_consumer():
            brains = list(CONSUMER_BRAINS)
            if self._kobold_reachable() and "kobold" in brains:
                brains.remove("kobold")
                brains.insert(0, "kobold")
            return tuple(brains)
        current = get_config("brain.default", default="kobold")
        opts = [b for b in DAVE_BRAINS if b in AVAILABLE_BACKENDS]
        if current in opts:
            opts.remove(current)
            opts.insert(0, current)
        return tuple(opts)

    def _build_ui(self) -> None:
        outer = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        outer.pack(fill=tk.BOTH, expand=True)
        apply_paned_style(outer)

        # --- Sidebar ---
        sidebar = ttk.Frame(outer, style="Sidebar.TFrame", width=220)
        outer.add(sidebar, weight=0)

        tree_canvas = tk.Canvas(
            sidebar,
            width=200,
            height=100,
            bg=forest_canvas_bg(),
            highlightthickness=0,
        )
        tree_canvas.pack(padx=8, pady=(14, 0))
        draw_sidebar_tree(tree_canvas)

        ttk.Label(sidebar, text="ARDEN", style="Title.TLabel").pack(anchor="w", padx=14, pady=(6, 0))
        ttk.Label(
            sidebar,
            text=TAGLINE,
            style="Sidebar.TLabel",
            wraplength=190,
        ).pack(anchor="w", padx=14, pady=(4, 6))
        gold_rule(sidebar)

        ttk.Button(
            sidebar,
            text="+ New chat",
            style="Sidebar.TButton",
            command=self._new_chat,
        ).pack(fill=tk.X, padx=10, pady=(8, 4))

        ttk.Button(
            sidebar,
            text="Sources",
            style="Sidebar.TButton",
            command=lambda: self._switch_tab("sources"),
        ).pack(fill=tk.X, padx=10, pady=(0, 4))

        ttk.Button(
            sidebar,
            text="Help me know you",
            style="Sidebar.TButton",
            command=self._open_intake,
        ).pack(fill=tk.X, padx=10, pady=(0, 4))

        ttk.Button(
            sidebar,
            text="What I know about you",
            style="Sidebar.TButton",
            command=self._open_knowledge,
        ).pack(fill=tk.X, padx=10, pady=(0, 4))

        ttk.Button(
            sidebar,
            text="Tools",
            style="Sidebar.TButton",
            command=self._open_tools,
        ).pack(fill=tk.X, padx=10, pady=(0, 4))

        if is_business_edition():
            ttk.Button(
                sidebar,
                text="Today's briefing",
                style="Sidebar.TButton",
                command=self._show_briefing,
            ).pack(fill=tk.X, padx=10, pady=(0, 4))
            ttk.Button(
                sidebar,
                text="Tasks",
                style="Sidebar.TButton",
                command=self._open_tasks,
            ).pack(fill=tk.X, padx=10, pady=(0, 4))

        ttk.Button(
            sidebar,
            text="Settings",
            style="Sidebar.TButton",
            command=self._open_settings,
        ).pack(fill=tk.X, padx=10, pady=(0, 4))

        ttk.Label(sidebar, text="SESSIONS", style="SidebarEyebrow.TLabel").pack(anchor="w", padx=14, pady=(8, 2))
        self.session_list = tk.Listbox(sidebar, height=12)
        style_listbox(self.session_list)
        self.session_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))
        self.session_list.bind("<<ListboxSelect>>", self._on_session_select)
        self.session_list.bind("<Double-Button-1>", self._rename_session)

        ttk.Label(
            sidebar,
            text="Keep the soul.\nChange the brain.",
            style="Sidebar.TLabel",
        ).pack(anchor="w", padx=14, pady=(0, 4))
        ttk.Label(sidebar, text="Powered by Rémanence", style="SidebarEyebrow.TLabel").pack(
            anchor="w", padx=14, pady=(0, 14)
        )

        # --- Main ---
        main = ttk.Frame(outer, style="Header.TFrame")
        outer.add(main, weight=1)

        header = ttk.Frame(main, style="Header.TFrame", padding=(20, 14, 20, 0))
        header.pack(fill=tk.X)

        title_row = ttk.Frame(header, style="Header.TFrame")
        title_row.pack(fill=tk.X)
        header_name = self._assistant_name
        if is_consigliere():
            header_name = f"{self._assistant_name} · Consigliere"
        self.header_title = ttk.Label(
            title_row,
            text=header_name,
            style="HeaderTitle.TLabel",
        )
        self.header_title.pack(side=tk.LEFT)
        self.status = ttk.Label(title_row, text=self._status_text(), style="HeaderMuted.TLabel")
        self.status.pack(side=tk.RIGHT)
        self._pulse = StatusPulse(self.status, self._status_text())

        tab_row = ttk.Frame(header, style="Header.TFrame")
        tab_row.pack(fill=tk.X, pady=(8, 6))
        self.tab_chat_btn = ttk.Button(
            tab_row,
            text="  Chat  ",
            style="TabActive.TButton",
            command=lambda: self._switch_tab("chat"),
        )
        self.tab_chat_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.tab_sources_btn = ttk.Button(
            tab_row,
            text="  Sources  ",
            style="Tab.TButton",
            command=lambda: self._switch_tab("sources"),
        )
        self.tab_sources_btn.pack(side=tk.LEFT)

        gilt = tk.Frame(main, bg=GILT, height=2)
        gilt.pack(fill=tk.X, padx=16)

        self.content = ttk.Frame(main, style="Header.TFrame")
        self.content.pack(fill=tk.BOTH, expand=True)

        self.chat_panel = ttk.Frame(self.content, style="Header.TFrame")
        self.chat_panel.pack(fill=tk.BOTH, expand=True)
        self.chat_panel.grid_rowconfigure(0, weight=1)
        self.chat_panel.grid_columnconfigure(0, weight=1)

        chat_frame = ttk.Frame(self.chat_panel, padding=(16, 12, 16, 4))
        chat_frame.grid(row=0, column=0, sticky="nsew")

        self.chat = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED)
        configure_chat_text(self.chat)
        self.chat.pack(fill=tk.BOTH, expand=True)
        self.chat.bind("<Key>", self._block_chat_edit)
        self.chat.bind("<Button-1>", self._on_chat_click)

        controls = ttk.Frame(self.chat_panel, padding=(16, 2, 16, 2))
        controls.grid(row=1, column=0, sticky="ew")

        self.speak_var = tk.BooleanVar(value=False if is_consumer() else self._voice_out)
        ttk.Checkbutton(controls, text="Speak replies", variable=self.speak_var).pack(side=tk.LEFT)

        ttk.Label(controls, text="Brain:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(20, 4))
        self._brain_options_list = list(self._brains_for_edition()) or ["venice", "groq"]
        default_brain = get_config("base_assistant.brain", default=self._brain_options_list[0])
        if default_brain not in self._brain_options_list:
            default_brain = self._brain_options_list[0]
        self.brain_var = tk.StringVar(value=_brain_label(default_brain))
        self.brain_combo = ttk.Combobox(
            controls,
            textvariable=self.brain_var,
            values=[_brain_label(b) for b in self._brain_options_list],
            state="readonly",
            width=18,
        )
        self.brain_combo.pack(side=tk.LEFT)
        self.brain_combo.bind("<<ComboboxSelected>>", self._on_brain_change)
        self._startup_jobs.append(self.root.after(100, self._ensure_brain_ready))
        self._startup_jobs.append(self.root.after(3000, self._refresh_brain_list))

        input_outer, input_inner = sanctuary_input_frame(self.chat_panel)
        input_outer.grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 14))

        input_row = ttk.Frame(input_inner, padding=(4, 2, 4, 2))
        input_row.pack(fill=tk.X)

        self.mic_btn = ttk.Button(input_row, text="Mic", width=4, command=self._on_mic)
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.entry = ttk.Entry(input_row, font=("Segoe UI", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda _e: self._on_send())
        self.entry.focus_set()

        self.send_btn = ttk.Button(
            input_row, text="Send", style="Accent.TButton", command=self._on_send
        )
        self.send_btn.pack(side=tk.RIGHT)

        self.root.bind("<Escape>", lambda _e: self._cancel_thinking())

        self.sources_panel = SourcesPanel(self.content, self.assistant, self.logger)
        # hidden until tab switch

    def _refresh_brain_list(self) -> None:
        """Re-probe local Kobold so the dropdown order stays accurate."""
        opts = list(self._brains_for_edition())
        if opts == self._brain_options_list:
            return
        current = _brain_id(self.brain_var.get() or "")
        self._brain_options_list = opts
        self.brain_combo.configure(values=[_brain_label(b) for b in opts])
        if current in opts:
            self.brain_var.set(_brain_label(current))
        elif not self._busy:
            self.brain_var.set(_brain_label(opts[0]))

    def _block_chat_edit(self, _event=None) -> str:
        """Chat transcript is read-only — type in the input bar only."""
        return "break"

    def _on_chat_click(self, _event=None) -> None:
        if not self._busy:
            self.entry.focus_set()

    def _bump_request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _is_stale(self, rid: int | None) -> bool:
        return rid is not None and rid != self._request_id

    def _worker_timeout_for(self, choice: str) -> int:
        return 120 if choice == "kobold" else 60

    def _cancel_thinking(self) -> None:
        if not self._busy:
            return
        self._bump_request_id()
        if self._live_stream:
            self._end_stream()
            self._live_stream = False
        self._append(
            self._assistant_name,
            "Stopped waiting. Switch Brain or press Send to try again.",
            persist=False,
        )
        self._set_busy(False)
        self.status.configure(text=self._status_text())

    def _brain_switch_hint(self, choice: str) -> str:
        if choice == "kobold":
            return "Start KoboldCpp on port 5001 (local, no API key), or pick Venice/Groq."
        return (
            "Check names and API keys in Settings, or pick another brain. "
            "Venice: venice.ai · Groq: console.groq.com"
        )

    def _switch_brain_backend(self, choice: str) -> bool:
        """Reload secrets and switch brain without rewriting runtime config."""
        from modules.consumer_bootstrap import reload_consumer_secrets

        reload_consumer_secrets()
        if not choice:
            choice = self._brain_options_list[0]
        return self.assistant.switch_brain(choice)

    def _activate_brain(self, choice: str, *, update_ui: bool = True) -> bool:
        """Switch brain backend; optional status-line refresh (main thread only)."""
        if self._switch_brain_backend(choice):
            if update_ui:
                self._pulse._on_rest = self._status_text()
                self.status.configure(text=self._status_text())
            return True
        return False

    def _prepare_brain_for_send(self) -> bool:
        """Sync brain dropdown + API keys before each message."""
        choice = _brain_id(self.brain_var.get() or "")
        if not choice:
            choice = self._brain_options_list[0]
            self.brain_var.set(_brain_label(choice))
        if self._activate_brain(choice):
            return True

        hint = f"Could not connect to {_brain_label(choice)}. {self._brain_switch_hint(choice)}"
        self._append(self._assistant_name, hint.replace("**", ""))
        return False

    def _ensure_brain_ready(self) -> None:
        """Activate the selected brain with fresh API keys from Settings."""
        choice = _brain_id(self.brain_var.get() or "")
        if not choice:
            choice = self._brain_options_list[0]
            self.brain_var.set(_brain_label(choice))
        if not self._activate_brain(choice):
            self.status.configure(text=f"Brain: {_brain_label(choice)} — not ready (check Settings keys)")

    def _reload_companion_identity(self) -> None:
        """Apply assistant + user names from saved profile after Settings."""
        from modules.assistant_config import get_config
        from modules.consumer_bootstrap import bootstrap_consumer
        from modules.personality_engine.identity import apply_user_identity

        bootstrap_consumer()
        name = get_config("base_assistant.assistant_name", default="Arden")
        human = get_config("base_assistant.human_companion_name", default="")
        engine = self.assistant.personality_engine
        if engine:
            apply_user_identity(engine.profile, name, human)
            if human and engine.voice_config is not None:
                engine.voice_config["greeting"] = f"Hey {human}. What's on your mind?"
        self._assistant_name = name
        self.header_title.configure(text=name)
        self._pulse._on_rest = self._status_text()

    def _open_settings(self) -> None:
        open_settings_dialog(self.root)
        self._reload_companion_identity()
        self._ensure_brain_ready()

    def _open_intake(self) -> None:
        from modules.gui.intake_flow import open_intake_flow

        def _brain_generate(prompt: str) -> str:
            if not self.assistant.brain_backend:
                return ""
            return self.assistant.brain_backend.generate_response(
                "You are a warm companion helping someone share facts about their life. "
                "Ask exactly one question. Never invent details they did not state.",
                prompt,
            )

        open_intake_flow(self.root, brain_generate=_brain_generate)

    def _open_knowledge(self) -> None:
        from modules.gui.knowledge_panel import open_knowledge_dialog

        open_knowledge_dialog(self.root)

    def _open_tools(self) -> None:
        from modules.gui.utilities_dialog import open_utilities_dialog

        def _brain_generate(system: str, user: str) -> str:
            if not self.assistant.brain_backend:
                return ""
            return self.assistant.brain_backend.generate_response(system, user)

        human = ""
        try:
            from modules.assistant_config import get_config

            human = get_config("base_assistant.human_companion_name", default="") or ""
        except Exception:
            pass

        open_utilities_dialog(
            self.root,
            session=self._sessions.active(),
            brain_generate=_brain_generate,
            user_name=human,
            assistant_name=self._assistant_name,
        )

    def _open_tasks(self) -> None:
        from modules.gui.tasks_panel import open_tasks_dialog

        open_tasks_dialog(self.root, self.assistant.task_manager)

    def _show_briefing(self) -> None:
        self._switch_tab("chat")
        briefing = self.assistant.morning_briefing.generate()
        self._append(self._assistant_name, briefing)
        self._sessions.append_message(self._assistant_name, briefing)

    def _reload_session_list(self, *, select_id: str | None = None) -> None:
        self.session_list.delete(0, tk.END)
        active_idx = 0
        for i, (sid, title) in enumerate(self._sessions.titles()):
            self.session_list.insert(tk.END, title)
            if sid == (select_id or self._sessions.active_id):
                active_idx = i
        self.session_list.selection_clear(0, tk.END)
        self.session_list.selection_set(active_idx)
        self.session_list.see(active_idx)

    def _on_session_select(self, _event=None) -> None:
        if self._busy:
            return
        sel = self.session_list.curselection()
        if not sel:
            return
        sid, _title = self._sessions.titles()[sel[0]]
        if sid == self._sessions.active_id:
            return
        session = self._sessions.set_active(sid)
        if session:
            self._load_session(session)

    def _rename_session(self, _event=None) -> None:
        from tkinter import simpledialog

        sel = self.session_list.curselection()
        if not sel:
            return
        sid, title = self._sessions.titles()[sel[0]]
        session = self._sessions.get(sid)
        if not session:
            return
        new_title = simpledialog.askstring(
            "Rename chat",
            "Session name:",
            parent=self.root,
            initialvalue=title,
        )
        if not new_title or not new_title.strip():
            return
        session.title = new_title.strip()
        session.touch()
        self._sessions.save()
        self._reload_session_list(select_id=sid)

    def _load_session(self, session) -> None:
        if self._stream_job:
            self.root.after_cancel(self._stream_job)
            self._stream_job = None
        self._switch_tab("chat")
        self.assistant.conversation_history.clear()
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state=tk.DISABLED)
        for msg in session.messages:
            if msg.speaker.lower() in ("you", "user"):
                self._append(msg.speaker, msg.body, persist=False)
            else:
                self._append(msg.speaker, msg.body, persist=False)
        self._sync_history_from_session(session)

    def _sync_history_from_session(self, session) -> None:
        for msg in session.messages:
            if msg.speaker.lower() in ("you", "user"):
                self.assistant.conversation_history.append({"role": "user", "content": msg.body})
            elif msg.speaker == self._assistant_name:
                self.assistant.conversation_history.append({"role": "assistant", "content": msg.body})

    def _switch_tab(self, tab: str) -> None:
        if tab == self._active_tab:
            return
        self._active_tab = tab
        if tab == "chat":
            self.sources_panel.on_hide()
            self.sources_panel.pack_forget()
            self.chat_panel.pack(fill=tk.BOTH, expand=True)
            self.tab_chat_btn.configure(style="TabActive.TButton")
            self.tab_sources_btn.configure(style="Tab.TButton")
            self.entry.focus_set()
        else:
            self.chat_panel.pack_forget()
            self.sources_panel.pack(fill=tk.BOTH, expand=True)
            self.tab_sources_btn.configure(style="TabActive.TButton")
            self.tab_chat_btn.configure(style="Tab.TButton")
            self.sources_panel.on_show()

    def _status_text(self) -> str:
        backend = get_config("memory.backend", default="sqlite")
        brain = "unknown"
        if self.assistant.brain_backend:
            brain = self.assistant.brain_backend.name
        return f"Brain: {brain}  ·  Memory: {backend}"

    def _add_session_item(self, label: str) -> None:
        """Legacy helper — session list now comes from SessionStore."""
        self._reload_session_list()

    def _append(
        self,
        speaker: str,
        message: str,
        *,
        tags: tuple[str, ...] | None = None,
        persist: bool = True,
    ) -> None:
        is_user = speaker.lower() in ("you", "user")
        is_arden = speaker == self._assistant_name or not is_user

        self.chat.configure(state=tk.NORMAL)
        if is_user:
            self.chat.insert(tk.END, f"{speaker}\n", "user_name")
            self.chat.insert(tk.END, f"{message}\n\n", tags or ("user_body",))
        elif is_arden:
            self.chat.insert(tk.END, f"{speaker}\n", "arden_name")
            self.chat.insert(tk.END, f"{message}\n\n", tags or ("arden_body",))
        else:
            self.chat.insert(tk.END, f"{message}\n\n", tags or ("system",))
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)
        if persist:
            self._sessions.append_message(speaker, message)

    def _begin_stream(self, speaker: str) -> None:
        try:
            self.chat.configure(state=tk.NORMAL)
            self.chat.insert(tk.END, f"{speaker}\n", "arden_name")
            self.chat.insert(tk.END, "", "stream")
            self.chat.mark_set("stream_mark", "insert")
            self.chat.mark_gravity("stream_mark", tk.LEFT)
            self.chat.configure(state=tk.DISABLED)
        except tk.TclError as exc:
            self.logger.warning("[GUI] begin_stream failed: %s", exc)

    def _stream_chunk(self, text: str) -> None:
        try:
            if "stream_mark" not in self.chat.mark_names():
                self._begin_stream(self._assistant_name)
            self.chat.configure(state=tk.NORMAL)
            self.chat.insert("stream_mark", text, "stream")
            self.chat.mark_set("stream_mark", "insert")
            self.chat.configure(state=tk.DISABLED)
            self.chat.see(tk.END)
        except tk.TclError as exc:
            self.logger.warning("[GUI] stream_chunk failed: %s", exc)

    def _end_stream(self) -> None:
        try:
            if "stream_mark" not in self.chat.mark_names():
                return
            self.chat.configure(state=tk.NORMAL)
            self.chat.insert("stream_mark", "\n\n", "stream")
            self.chat.configure(state=tk.DISABLED)
        except tk.TclError as exc:
            self.logger.warning("[GUI] end_stream failed: %s", exc)

    def _animate_response(self, message: str, *, speak: bool) -> None:
        tokens = message.split(" ")
        self._begin_stream(self._assistant_name)
        # Unlock the input bar while tokens animate — don't trap the user.
        self._set_busy(False)

        def step(i: int = 0) -> None:
            if i >= len(tokens):
                self._end_stream()
                self._sessions.append_message(self._assistant_name, message)
                if speak:
                    self._queue_speak(message)
                self._maybe_thin_nudge()
                self._maybe_offer_deepening(self._last_user_text)
                return
            chunk = tokens[i] + (" " if i < len(tokens) - 1 else "")
            self._stream_chunk(chunk)
            delay = 18 if len(tokens) > 80 else 28
            self._stream_job = self.root.after(delay, lambda: step(i + 1))

        step()

    def _show_greeting(self) -> None:
        greeting = (
            "Welcome back. I'm here — same soul, your machine, your forest. "
            "Speak or type whenever you're ready."
        )
        if self.assistant.personality_engine:
            greeting = self.assistant.personality_engine.get_greeting()
        self._append(self._assistant_name, greeting)

        try:
            from modules.proactive.care import session_care_lines
            from modules.proactive.state import ProactiveStateStore

            state = ProactiveStateStore()
            if not state.care_shown_today():
                lines = session_care_lines(max_lines=2)
                for line in lines:
                    self._append(self._assistant_name, line)
                if lines:
                    state.mark_care_shown()
        except Exception:
            pass

        if is_business_edition():
            try:
                open_tasks = self.assistant.task_manager.get_open_tasks()
                if open_tasks:
                    n = len(open_tasks)
                    self._append(
                        self._assistant_name,
                        f"You have {n} open task{'s' if n != 1 else ''}. "
                        "Say “briefing” or open Tasks in the sidebar.",
                    )
            except Exception:
                pass

    def _maybe_thin_nudge(self) -> None:
        try:
            from modules.proactive.nudge import maybe_thin_knowledge_nudge, record_nudge_shown

            text = maybe_thin_knowledge_nudge(
                user_messages_this_session=self._user_messages_session
            )
            if text:
                self._append(self._assistant_name, text)
                record_nudge_shown()
        except Exception:
            pass

    def _handle_deepening_answer(self, text: str) -> bool:
        """If awaiting a why-answer, store or skip. Returns True if consumed."""
        if not self._deepening_pending:
            return False
        from modules.proactive.context_deepening import is_skip_response, propose_context_fact
        from tkinter import messagebox

        from modules.tactical_context import get_facts_store

        event = self._deepening_pending
        self._deepening_pending = None
        if is_skip_response(text):
            self._append(self._assistant_name, "Okay — we can leave it there.")
            return True
        proposal = propose_context_fact(event, text)
        if messagebox.askyesno(
            "Remember this?",
            f"Should I remember:\n\n{proposal['content']}",
            parent=self.root,
        ):
            get_facts_store().add_fact(
                proposal["domain"],
                proposal["content"],
                label=proposal.get("label", ""),
                source="context",
            )
            self._append(self._assistant_name, "Got it — I'll keep that in mind.")
        else:
            self._append(self._assistant_name, "No problem — I won't store that.")
        return True

    def _maybe_offer_deepening(self, user_text: str) -> None:
        if self._deepening_pending or self._deepening_used_session:
            return
        try:
            from modules.proactive.context_deepening import detect_decision_event, follow_up_question

            event = detect_decision_event(user_text)
            if not event:
                return
            self._deepening_pending = event
            self._deepening_used_session = True
            self._append(self._assistant_name, follow_up_question(event))
        except Exception:
            pass

    def _new_chat(self) -> None:
        if self._stream_job:
            self.root.after_cancel(self._stream_job)
            self._stream_job = None
        self._switch_tab("chat")
        title = f"Chat {len(self._sessions.sessions) + 1}"
        session = self._sessions.create(title)
        self.assistant.conversation_history.clear()
        self._user_messages_session = 0
        self._deepening_pending = None
        self._deepening_used_session = False
        self._last_user_text = ""
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state=tk.DISABLED)
        self._reload_session_list(select_id=session.id)
        self._show_greeting()

    def _on_brain_change(self, _event=None) -> None:
        if self._busy:
            self._cancel_thinking()
        choice = _brain_id(self.brain_var.get() or "")
        if not choice:
            return
        if self._activate_brain(choice):
            self._append(
                self._assistant_name,
                f"Switched to {_brain_label(choice)}. Same soul — different brain.",
            )
        else:
            hint = (
                f"Could not switch to {_brain_label(choice)}. {self._brain_switch_hint(choice)}"
            )
            self._append(self._assistant_name, hint)
        self._pulse._on_rest = self._status_text()
        self.status.configure(text=self._status_text())

    def _queue_speak(self, text: str) -> None:
        """Run TTS on the Tk main thread — pyttsx3 deadlocks if called from workers."""
        if text and self.speak_var.get():
            self._queue.put(("speak", text))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self.entry.configure(state=state)
        self.send_btn.configure(state=state)
        self.mic_btn.configure(state=state)
        # Brain stays switchable so you can bail out of a stuck local model.
        self.brain_combo.configure(state="readonly")
        self.tab_sources_btn.configure(state=tk.NORMAL)
        if self._busy_watchdog:
            self.root.after_cancel(self._busy_watchdog)
            self._busy_watchdog = None
        if busy:
            self._pulse.start(f"{self._assistant_name} is thinking")
            grace_ms = (self._worker_timeout_for(
                _brain_id(self.brain_var.get() or "")
            ) + 10) * 1000
            self._busy_watchdog = self.root.after(grace_ms, self._busy_watchdog_fire)
        else:
            self._pulse.stop()

    def _busy_watchdog_fire(self) -> None:
        self._busy_watchdog = None
        if not self._busy:
            return
        self.logger.warning("[GUI] Busy watchdog fired — unlocking UI")
        if self._live_stream:
            self._end_stream()
        self._live_stream = False
        self._set_busy(False)
        self.status.configure(text=self._status_text())

    def _on_mic(self) -> None:
        if self._busy or self._listening:
            return
        self._listening = True
        self.mic_btn.configure(text="…")
        self.status.configure(text="Listening…")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self) -> None:
        text = listen_once()
        self._queue.put(("heard", text or ""))

    def _on_send(self, text: str | None = None) -> None:
        try:
            if self._busy:
                return
            if text is None:
                text = self.entry.get().strip()
            if not text:
                return
            self.entry.delete(0, tk.END)
            self._switch_tab("chat")
            self._append("You", text)
            self._user_messages_session += 1

            if self._handle_deepening_answer(text):
                return

            if is_consigliere():
                try:
                    from modules.proactive.accountability import pre_send_accountability_alerts

                    for alert in pre_send_accountability_alerts(text):
                        self._append(self._assistant_name, alert)
                except Exception:
                    pass

            if text.lower() in ("exit", "quit", "bye"):
                farewell = "Talk soon!"
                if self.assistant.personality_engine:
                    farewell = self.assistant.personality_engine.voice_config.get(
                        "farewell", farewell
                    )
                self._append(self._assistant_name, farewell)
                self.root.after(300, self._shutdown)
                return

            choice = _brain_id(self.brain_var.get() or "")
            if not choice:
                choice = self._brain_options_list[0]
                self.brain_var.set(_brain_label(choice))
            self._last_user_text = text
            rid = self._bump_request_id()
            speak = bool(self.speak_var.get())
            self._set_busy(True)
            threading.Thread(
                target=self._worker, args=(text, choice, rid, speak), daemon=True
            ).start()
        except Exception:
            self.logger.exception("[GUI] _on_send failed")
            self._set_busy(False)

    def _friendly_error(self, exc: Exception) -> str:
        msg = str(exc).lower()
        if "venice" in msg and ("api key" in msg or "401" in msg or "403" in msg):
            return "Venice API key missing or invalid. Check venice.ai or first-run setup."
        if "groq" in msg and ("api key" in msg or "401" in msg or "403" in msg):
            return "Groq API key missing or invalid. Get a free key at console.groq.com."
        if "timeout" in msg or "timed out" in msg:
            return "That took too long. Check your internet and try again."
        if "connection" in msg or "network" in msg:
            return "I could not reach the internet. Try again in a moment."
        if "5001" in msg or "kobold" in msg:
            return "Kobold is not reachable on port 5001. Start KoboldCpp or switch brain to Venice."
        return f"Something went wrong: {exc}"

    def _worker(self, text: str, choice: str, rid: int, speak: bool) -> None:
        if self._is_stale(rid):
            return
        try:
            if not self._switch_brain_backend(choice):
                self._queue.put(
                    (
                        "err",
                        (
                            f"Could not connect to {choice}. {self._brain_switch_hint(choice)}",
                            rid,
                        ),
                    )
                )
                return

            streamed = False

            def on_chunk(chunk: str) -> None:
                nonlocal streamed
                if self._is_stale(rid):
                    return
                if chunk:
                    streamed = True
                    self._queue.put(("chunk", (chunk, rid)))

            response = self.assistant.process_text(text, chunk_callback=on_chunk)
            if self._is_stale(rid):
                return
            response = (response or "").strip()
            if streamed:
                self._queue.put(("done", (response, speak, rid)))
            elif response:
                self._queue.put(("ok", (response, rid)))
            else:
                self._queue.put(
                    (
                        "err",
                        (
                            "No reply came back. Pick Venice in the Brain dropdown, check Settings keys, "
                            "or press Escape if a previous attempt got stuck.",
                            rid,
                        ),
                    )
                )
        except Exception as exc:
            if self._is_stale(rid):
                return
            self.logger.exception("[GUI] process_text failed")
            self._queue.put(("err", (self._friendly_error(exc), rid)))

    def _payload_rid(self, payload):
        if isinstance(payload, tuple) and payload and isinstance(payload[-1], int):
            return payload[:-1], payload[-1]
        return payload, None

    def _handle_queue_item(self, kind: str, payload) -> None:
        if kind == "heard":
            self._listening = False
            self.mic_btn.configure(text="Mic")
            if payload:
                self.entry.insert(0, payload)
                self._on_send(payload)
            else:
                self.status.configure(text="Didn't catch that — type instead.")
                self.root.after(
                    2000,
                    lambda: self.status.configure(text=self._status_text()),
                )
            return

        if kind == "chunk" and payload:
            body, rid = self._payload_rid(payload)
            if self._is_stale(rid):
                return
            chunk = body[0] if isinstance(body, tuple) else body
            if not chunk:
                return
            if not self._live_stream:
                self._live_stream = True
                self._begin_stream(self._assistant_name)
            self._stream_chunk(chunk)
            return

        if kind == "done":
            body, rid = self._payload_rid(payload)
            if self._is_stale(rid):
                return
            if isinstance(body, tuple):
                full_text = body[0] if body else ""
                speak = body[1] if len(body) > 1 else False
            else:
                full_text = body
                speak = False
            try:
                if self._live_stream:
                    self._end_stream()
                elif full_text:
                    self._append(self._assistant_name, full_text, persist=False)
                if full_text:
                    self._sessions.append_message(self._assistant_name, full_text)
                if speak and full_text:
                    self._queue_speak(full_text)
            finally:
                self._live_stream = False
                self._set_busy(False)
                self.status.configure(text=self._status_text())
                self._maybe_thin_nudge()
                self._maybe_offer_deepening(self._last_user_text)
            return

        if kind == "ok":
            body, rid = self._payload_rid(payload)
            if self._is_stale(rid):
                return
            message = body[0] if isinstance(body, tuple) else body
            if message:
                self._animate_response(message, speak=self.speak_var.get())
            else:
                self._set_busy(False)
            return

        if kind == "speak":
            speak_text(self.assistant, payload or "")
            return

        if kind == "err":
            body, rid = self._payload_rid(payload)
            if self._is_stale(rid):
                return
            message = body[0] if isinstance(body, tuple) else body
            try:
                if self._live_stream:
                    self._end_stream()
                self._append(self._assistant_name, message)
            finally:
                self._live_stream = False
                self._set_busy(False)
                self.status.configure(text=self._status_text())

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self._queue.get_nowait()
                kind = item[0]
                payload = item[1] if len(item) == 2 else tuple(item[1:])
                try:
                    self._handle_queue_item(kind, payload)
                except Exception:
                    self.logger.exception("[GUI] Queue handler failed for %s", kind)
                    self._live_stream = False
                    self._set_busy(False)
        except queue.Empty:
            pass
        if not self._shutting_down:
            self._poll_job = self.root.after(80, self._poll_queue)

    def _cancel_timers(self) -> None:
        self._shutting_down = True
        if self._poll_job:
            try:
                self.root.after_cancel(self._poll_job)
            except tk.TclError:
                pass
            self._poll_job = None
        if self._busy_watchdog:
            try:
                self.root.after_cancel(self._busy_watchdog)
            except tk.TclError:
                pass
            self._busy_watchdog = None
        if self._stream_job:
            try:
                self.root.after_cancel(self._stream_job)
            except tk.TclError:
                pass
            self._stream_job = None
        for job in self._startup_jobs:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self._startup_jobs.clear()

    def _shutdown(self) -> None:
        self._cancel_timers()
        self._pulse.stop()
        try:
            if hasattr(self.assistant, "cleanup"):
                self.assistant.cleanup()
        except Exception:
            pass
        self.root.destroy()


def run_chat_app() -> None:
    """Launch the Arden Desktop chat window."""
    from modules.arden_env import get as arden_get, setdefault as arden_setdefault
    from modules.consumer_bootstrap import bootstrap_consumer, ensure_consumer_template_in_data_dir
    from modules.crash_log import install_crash_logging
    from modules.gui.intake_choice import run_intake_choice_if_needed
    from modules.gui.intake_flow import IntakeFlowDialog
    from modules.intake.progress import load_intake_choice
    from modules.gui.splash import apply_window_icon, show_splash

    try:
        _run_chat_app_impl(
            arden_get=arden_get,
            arden_setdefault=arden_setdefault,
            bootstrap_consumer=bootstrap_consumer,
            ensure_consumer_template_in_data_dir=ensure_consumer_template_in_data_dir,
            install_crash_logging=install_crash_logging,
            run_intake_choice_if_needed=run_intake_choice_if_needed,
            IntakeFlowDialog=IntakeFlowDialog,
            load_intake_choice=load_intake_choice,
            show_splash=show_splash,
            apply_window_icon=apply_window_icon,
        )
    except Exception as exc:
        _fatal_startup_error("Arden could not start", exc)


def _run_chat_app_impl(**_imports) -> None:
    arden_get = _imports["arden_get"]
    arden_setdefault = _imports["arden_setdefault"]
    bootstrap_consumer = _imports["bootstrap_consumer"]
    ensure_consumer_template_in_data_dir = _imports["ensure_consumer_template_in_data_dir"]
    install_crash_logging = _imports["install_crash_logging"]
    run_intake_choice_if_needed = _imports["run_intake_choice_if_needed"]
    IntakeFlowDialog = _imports["IntakeFlowDialog"]
    load_intake_choice = _imports["load_intake_choice"]
    show_splash = _imports["show_splash"]
    apply_window_icon = _imports["apply_window_icon"]

    install_crash_logging()
    arden_setdefault("EDITION", arden_get("EDITION", "consumer") or "consumer")

    show_splash()
    ensure_consumer_template_in_data_dir()
    bootstrap_consumer()

    session_id = create_session_logger_id()
    logger = setup_logging(session_id)
    logger.info("[GUI] Starting Arden Desktop shell")

    root = tk.Tk()
    apply_arden_theme(root)
    apply_window_icon(root)
    run_first_run_wizard(root)
    choice = run_intake_choice_if_needed(root)
    bootstrap_consumer()

    assistant = PlainAssistant(logger, session_id)
    if not require_groq_key_or_exit(root):
        return

    ic = load_intake_choice()
    if choice in ("b", "c") and ic and not ic.get("completed"):

        def _brain_generate(prompt: str) -> str:
            if not assistant.brain_backend:
                return ""
            return assistant.brain_backend.generate_response(
                "You are a warm companion helping someone share facts about their life. "
                "Ask exactly one question. Never invent details they did not state.",
                prompt,
            )

        IntakeFlowDialog(root, mode=choice, brain_generate=_brain_generate).wait_window()

    ChatApp(root, assistant, logger)
    try:
        root.mainloop()
    except Exception:
        logger.exception("[GUI] mainloop crashed")
        raise


def _fatal_startup_error(title: str, exc: BaseException) -> None:
    from tkinter import messagebox

    from modules.crash_log import _write_crash

    _write_crash("startup", exc)
    try:
        err = tk.Tk()
        err.withdraw()
        messagebox.showerror(
            title,
            f"{exc}\n\nDetails: %LOCALAPPDATA%\\Arden\\crash-last.txt",
            parent=err,
        )
        err.destroy()
    except Exception:
        pass
