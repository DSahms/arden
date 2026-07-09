"""Arden Desktop visual theme — forest sanctuary / gilt (splash #4 sampled)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# Sampled from assets/splash.png — forest greens, gilt gold, cream text
FOREST_DEEP = "#182d25"
FOREST_SIDEBAR = "#1a3228"
FOREST_PANEL = "#243d32"
FOREST_ELEVATED = "#2d4a3a"
FOREST_LINE = "#325242"
FOREST_MIST = "#4a6b58"

CREAM = "#d4d0bc"
CREAM_SOFT = "#b8c4bc"
CREAM_MUTED = "#8a9a92"

GILT = "#dbb874"
GILT_DEEP = "#bfa46f"
GILT_GLOW = "#e8cc90"

# Legacy aliases
INK0 = FOREST_DEEP
INK1 = FOREST_SIDEBAR
INK2 = FOREST_PANEL
INK3 = FOREST_ELEVATED
LINE = FOREST_LINE
VELLUM0 = CREAM
VELLUM1 = CREAM_SOFT
VELLUM2 = CREAM_MUTED

FONT_UI = ("Segoe UI", 10)
FONT_CHAT = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 15, "bold")
FONT_DISPLAY = ("Segoe UI", 20, "bold")
FONT_TAGLINE = ("Segoe UI", 9)
FONT_EYEBROW = ("Segoe UI", 8)
FONT_SERIF = ("Georgia", 11, "italic")

TAGLINE = "All remembered. Deeply encrypted. Never-leaving."
QUOTE = "Where nothing is forgotten, and nothing leaves the forest."


def apply(root: tk.Tk) -> ttk.Style:
    """Apply forest sanctuary theme to root and return configured style."""
    root.configure(bg=FOREST_DEEP)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=FOREST_DEEP, foreground=CREAM, font=FONT_UI)
    style.configure("TFrame", background=FOREST_DEEP)
    style.configure("Sidebar.TFrame", background=FOREST_SIDEBAR)
    style.configure("Header.TFrame", background=FOREST_PANEL)
    style.configure("TLabel", background=FOREST_DEEP, foreground=CREAM)
    style.configure("Sidebar.TLabel", background=FOREST_SIDEBAR, foreground=CREAM_SOFT)
    style.configure("Muted.TLabel", background=FOREST_DEEP, foreground=CREAM_MUTED, font=FONT_TAGLINE)
    style.configure("HeaderMuted.TLabel", background=FOREST_PANEL, foreground=CREAM_MUTED, font=FONT_TAGLINE)
    style.configure("Title.TLabel", background=FOREST_SIDEBAR, foreground=GILT, font=FONT_TITLE)
    style.configure("PanelTitle.TLabel", background=FOREST_PANEL, foreground=GILT, font=FONT_TITLE)
    style.configure("HeaderTitle.TLabel", background=FOREST_PANEL, foreground=GILT, font=FONT_DISPLAY)
    style.configure("Eyebrow.TLabel", background=FOREST_PANEL, foreground=CREAM_MUTED, font=FONT_EYEBROW)
    style.configure("SidebarEyebrow.TLabel", background=FOREST_SIDEBAR, foreground=FOREST_MIST, font=FONT_EYEBROW)
    style.configure("Quote.TLabel", background=FOREST_PANEL, foreground=CREAM_SOFT, font=FONT_SERIF)

    style.configure(
        "TButton",
        background=FOREST_ELEVATED,
        foreground=CREAM,
        bordercolor=FOREST_LINE,
        focusthickness=1,
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[("active", FOREST_PANEL), ("pressed", FOREST_DEEP)],
        foreground=[("active", GILT_GLOW)],
    )
    style.configure(
        "Accent.TButton",
        background=GILT_DEEP,
        foreground=FOREST_DEEP,
        font=("Segoe UI", 10, "bold"),
    )
    style.map("Accent.TButton", background=[("active", GILT)])

    style.configure(
        "TEntry",
        fieldbackground=FOREST_ELEVATED,
        foreground=CREAM,
        insertcolor=CREAM,
        bordercolor=FOREST_LINE,
    )
    style.configure(
        "TCombobox",
        fieldbackground=FOREST_ELEVATED,
        background=FOREST_ELEVATED,
        foreground=CREAM,
        arrowcolor=GILT,
    )
    style.configure(
        "Sidebar.TButton",
        background=FOREST_PANEL,
        foreground=CREAM_SOFT,
        anchor="w",
        padding=(8, 6),
    )
    style.map(
        "Sidebar.TButton",
        background=[("active", FOREST_ELEVATED)],
        foreground=[("active", GILT)],
    )

    style.configure(
        "Tab.TButton",
        background=FOREST_SIDEBAR,
        foreground=CREAM_MUTED,
        padding=(14, 8),
        font=("Segoe UI", 10),
    )
    style.map("Tab.TButton", foreground=[("active", CREAM)])
    style.configure(
        "TabActive.TButton",
        background=FOREST_ELEVATED,
        foreground=GILT,
        padding=(14, 8),
        font=("Segoe UI", 10, "bold"),
    )
    style.map("TabActive.TButton", background=[("active", FOREST_PANEL)])

    style.configure("Gold.TFrame", background=GILT)

    from modules.gui.arden_widgets import register_extra_styles

    register_extra_styles(style)
    return style


def configure_chat_text(widget: tk.Text) -> None:
    """Tag styles for chat transcript."""
    widget.configure(
        bg=FOREST_DEEP,
        fg=CREAM,
        insertbackground=CREAM,
        selectbackground=FOREST_ELEVATED,
        selectforeground=CREAM,
        relief=tk.FLAT,
        padx=14,
        pady=10,
        spacing1=4,
        spacing3=8,
        font=FONT_CHAT,
        wrap=tk.WORD,
        highlightthickness=1,
        highlightbackground=FOREST_LINE,
        highlightcolor=GILT_DEEP,
    )
    widget.tag_configure("user_name", foreground=CREAM_SOFT, font=("Segoe UI", 10, "bold"))
    widget.tag_configure("user_body", foreground=CREAM)
    widget.tag_configure("arden_name", foreground=GILT, font=("Segoe UI", 10, "bold"))
    widget.tag_configure("arden_body", foreground=CREAM)
    widget.tag_configure("system", foreground=CREAM_MUTED, font=("Segoe UI", 9, "italic"))
    widget.tag_configure("stream", foreground=CREAM)
    widget.tag_configure("quote", foreground=CREAM_MUTED, font=FONT_SERIF)
