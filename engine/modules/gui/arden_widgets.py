"""Reusable forest-sanctuary widgets — splash #4 cohesive chrome."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from modules.gui.arden_decor import draw_sidebar_tree
from modules.gui.arden_theme import (
    CREAM,
    CREAM_MUTED,
    CREAM_SOFT,
    FONT_SERIF,
    FONT_TAGLINE,
    FONT_TITLE,
    FONT_UI,
    FOREST_DEEP,
    FOREST_ELEVATED,
    FOREST_LINE,
    FOREST_PANEL,
    FOREST_SIDEBAR,
    GILT,
    GILT_DEEP,
    INK1,
    INK2,
    VELLUM1,
    VELLUM2,
)


def forest_card(
    parent: tk.Widget,
    *,
    padx: int = 28,
    pady: int = 24,
    border: str = GILT_DEEP,
) -> tuple[tk.Frame, tk.Frame]:
    """Gold-bordered sanctuary card. Returns (outer, inner)."""
    outer = tk.Frame(parent, bg=FOREST_PANEL, highlightbackground=border, highlightthickness=1)
    inner = tk.Frame(outer, bg=FOREST_PANEL, padx=padx, pady=pady)
    inner.pack(fill=tk.BOTH, expand=True)
    return outer, inner


def card_heading(parent: tk.Widget, text: str) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        bg=FOREST_PANEL,
        fg=GILT,
        font=FONT_TITLE,
    )


def card_body(parent: tk.Widget, text: str, **kwargs) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        bg=FOREST_PANEL,
        fg=CREAM_SOFT,
        font=("Segoe UI", 11),
        justify=tk.LEFT,
        **kwargs,
    )


def card_muted(parent: tk.Widget, text: str) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        bg=FOREST_PANEL,
        fg=VELLUM2,
        font=FONT_TAGLINE,
    )


def status_dot_label(parent: tk.Widget, textvariable: tk.StringVar) -> tk.Label:
    return tk.Label(
        parent,
        textvariable=textvariable,
        bg=FOREST_PANEL,
        fg=CREAM_SOFT,
        font=FONT_UI,
    )


def mini_tree_banner(parent: tk.Widget, width: int = 120, height: int = 72) -> tk.Canvas:
    """Small neural-tree mark for panel headers."""
    canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=FOREST_PANEL,
        highlightthickness=0,
    )
    draw_sidebar_tree(canvas)
    return canvas


def sanctuary_input_frame(parent: tk.Widget) -> tuple[tk.Frame, tk.Frame]:
    """Soft elevated strip behind the chat input row. Returns (outer, inner)."""
    outer = tk.Frame(parent, bg=FOREST_DEEP, highlightbackground=FOREST_LINE, highlightthickness=1)
    inner = tk.Frame(outer, bg=INK2, padx=4, pady=4)
    inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
    return outer, inner


def apply_paned_style(paned: ttk.Panedwindow) -> None:
    try:
        paned.configure(style="Forest.TPanedwindow")
    except tk.TclError:
        pass


def register_extra_styles(style: ttk.Style) -> None:
    """Styles that depend on the shared Style instance."""
    style.configure("Forest.TPanedwindow", background=FOREST_SIDEBAR)
    style.configure(
        "TCheckbutton",
        background=FOREST_PANEL,
        foreground=CREAM_SOFT,
        font=FONT_UI,
    )
    style.map("TCheckbutton", foreground=[("active", GILT)])
