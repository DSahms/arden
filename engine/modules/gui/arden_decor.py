"""Visual accents for Arden Desktop — gilt rules, neural tree, status pulse."""

from __future__ import annotations

import tkinter as tk

from modules.gui.arden_theme import (
    FOREST_ELEVATED,
    FOREST_LINE,
    FOREST_PANEL,
    FOREST_SIDEBAR,
    GILT,
    GILT_DEEP,
    GILT_GLOW,
    LINE,
    VELLUM1,
)


def gold_rule(parent: tk.Widget, *, pady: int = 6) -> tk.Frame:
    """Soft gilt separator."""
    frame = tk.Frame(parent, bg=FOREST_SIDEBAR, height=2)
    inner = tk.Frame(frame, bg=GILT_DEEP, height=1)
    inner.pack(fill=tk.X, padx=12, pady=pady)
    frame.pack(fill=tk.X)
    return frame


def draw_sidebar_tree(canvas: tk.Canvas) -> None:
    """Neural-network tree mark — splash #4: gold nodes, forest trunk, soft glow."""
    w = int(canvas["width"])
    h = int(canvas["height"])
    cx = w // 2
    base = h - 10

    # ambient forest floor
    canvas.create_rectangle(0, h - 28, w, h, fill=FOREST_PANEL, outline="")
    canvas.create_oval(cx - 70, h - 40, cx + 70, h + 8, fill=FOREST_ELEVATED, outline=FOREST_LINE)

    # trunk — warm gold-brown
    canvas.create_line(cx, base, cx, base - 32, fill=GILT_DEEP, width=4, capstyle=tk.ROUND)
    canvas.create_line(cx - 1, base - 8, cx - 1, base - 28, fill=GILT_GLOW, width=1)

    # branch graph: (x, y) node positions
    nodes: list[tuple[int, int]] = [
        (cx, base - 36),
        (cx - 22, base - 48),
        (cx + 22, base - 48),
        (cx - 38, base - 58),
        (cx - 8, base - 62),
        (cx + 8, base - 62),
        (cx + 38, base - 58),
        (cx - 18, base - 72),
        (cx + 18, base - 72),
        (cx, base - 78),
    ]
    edges = [
        (0, 1), (0, 2),
        (1, 3), (1, 4),
        (2, 5), (2, 6),
        (4, 7), (5, 8),
        (7, 9), (8, 9),
        (3, 7), (6, 8),
    ]

    for a, b in edges:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        canvas.create_line(x1, y1, x2, y2, fill=GILT_DEEP, width=2, capstyle=tk.ROUND)

    for i, (nx, ny) in enumerate(nodes):
        r = 5 if i == 9 else 4
        canvas.create_oval(nx - r, ny - r, nx + r, ny + r, fill=GILT, outline=GILT_GLOW, width=1)

    # memory star — top glow
    canvas.create_oval(cx - 2, 6, cx + 2, 10, fill=GILT_GLOW, outline="")


class StatusPulse:
    """Animate status line while Arden is thinking."""

    def __init__(self, label: tk.Widget, on_rest: str) -> None:
        self._label = label
        self._on_rest = on_rest
        self._tick = 0
        self._job: str | None = None
        self._active = False

    def start(self, prefix: str = "Arden is thinking") -> None:
        self.stop()
        self._active = True
        self._prefix = prefix
        self._tick = 0
        self._step()

    def stop(self) -> None:
        self._active = False
        if self._job and self._label.winfo_exists():
            self._label.after_cancel(self._job)
        self._job = None
        if self._label.winfo_exists():
            self._label.configure(text=self._on_rest)

    def _step(self) -> None:
        if not self._active or not self._label.winfo_exists():
            return
        dot = "." * (self._tick % 4)
        self._label.configure(text=f"{self._prefix}{dot}")
        self._tick += 1
        self._job = self._label.after(400, self._step)


def style_listbox(widget: tk.Listbox) -> None:
    widget.configure(
        bg=FOREST_PANEL,
        fg=VELLUM1,
        selectbackground=FOREST_ELEVATED,
        selectforeground=GILT,
        highlightthickness=1,
        highlightbackground=LINE,
        highlightcolor=GILT_DEEP,
        borderwidth=0,
        font=("Segoe UI", 10),
        activestyle="none",
    )


def forest_canvas_bg() -> str:
    return FOREST_SIDEBAR
