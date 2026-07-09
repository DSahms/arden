"""Arden Desktop splash — forest splash #4 + gilt tagline."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

from modules.gui.arden_decor import draw_sidebar_tree
from modules.gui.arden_theme import (
    CREAM_SOFT,
    FOREST_DEEP,
    FOREST_PANEL,
    GILT,
    QUOTE,
    TAGLINE,
    VELLUM0,
    VELLUM1,
)


def _splash_path() -> Path | None:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path.cwd()))
        candidates.append(bundle / "assets" / "splash.png")
    repo = Path(__file__).resolve().parent.parent.parent
    candidates.append(repo / "assets" / "splash.png")
    for path in candidates:
        if path.exists():
            return path
    return None


def _canvas_splash(root: tk.Tk, duration_ms: int) -> None:
    """Fallback branded splash when image missing."""
    w, h = 820, 480
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    root.configure(bg=FOREST_DEEP)
    c = tk.Canvas(root, width=w, height=h, bg=FOREST_DEEP, highlightthickness=0)
    c.pack(fill=tk.BOTH, expand=True)

    # soft forest bands
    for i, color in enumerate(["#0d1410", "#122018", "#1a2e22", "#1f3a28", "#234a32"]):
        c.create_rectangle(0, h - 160 + i * 30, w, h - 130 + i * 30, fill=color, outline="")

    # firefly dots
    for fx, fy in [(120, 180), (680, 200), (200, 120), (600, 140), (400, 90)]:
        c.create_oval(fx - 3, fy - 3, fx + 3, fy + 3, fill=GILT, outline="")

    tree = tk.Canvas(c, width=160, height=110, bg=FOREST_DEEP, highlightthickness=0)
    c.create_window(w // 2, 130, window=tree)
    draw_sidebar_tree(tree)

    c.create_text(w // 2, 210, text="ARDEN DESKTOP", fill=GILT, font=("Segoe UI", 28, "bold"))
    c.create_text(w // 2, 242, text=TAGLINE, fill=VELLUM1, font=("Segoe UI", 10))
    c.create_text(w // 2, h // 2 + 20, text=f'"{QUOTE}"', fill=CREAM_SOFT, font=("Georgia", 13, "italic"), width=w - 120)

    c.create_rectangle(80, h - 36, w - 80, h - 28, fill=FOREST_PANEL, outline="")
    bar = c.create_rectangle(80, h - 36, 82, h - 28, fill=GILT, outline="")
    c.create_text(w // 2, h - 18, text="LOADING . . .", fill=VELLUM1, font=("Segoe UI", 8))

    def grow(step: int = 0) -> None:
        if step > 40:
            root.destroy()
            return
        x = 80 + int((w - 160) * step / 40)
        c.coords(bar, 80, h - 36, x, h - 28)
        root.after(duration_ms // 40, lambda: grow(step + 1))

    grow()


def apply_window_icon(root: tk.Tk) -> None:
    """Taskbar / title bar icon from splash tree art."""
    path = _splash_path()
    if not path:
        return
    try:
        from PIL import Image, ImageTk

        img = Image.open(path)
        img.thumbnail((64, 64), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(True, photo)
        root._arden_icon = photo  # prevent GC
    except Exception:
        pass


def show_splash(duration_ms: int = 3400) -> None:
    """Show branded splash; canvas fallback if image missing."""
    path = _splash_path()
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    if not path:
        _canvas_splash(root, duration_ms)
        root.mainloop()
        return

    try:
        from PIL import Image, ImageTk
    except ImportError:
        root.destroy()
        _canvas_splash(tk.Tk(), duration_ms)
        return

    img = Image.open(path)
    max_w, max_h = 960, 540
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    w, h = photo.width(), photo.height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.configure(bg=FOREST_DEEP)

    frame = tk.Frame(root, bg=FOREST_DEEP)
    frame.pack(fill=tk.BOTH, expand=True)
    label = tk.Label(frame, image=photo, borderwidth=0, bg=FOREST_DEEP)
    label.image = photo
    label.pack()

    tag = tk.Label(
        frame,
        text="Powered by Rémanence",
        bg=FOREST_DEEP,
        fg=VELLUM0,
        font=("Segoe UI", 9),
    )
    tag.place(relx=0.5, rely=0.92, anchor=tk.CENTER)

    bar_frame = tk.Frame(frame, bg=FOREST_PANEL, height=4)
    bar_frame.place(relx=0.1, rely=0.96, relwidth=0.8, anchor=tk.W)
    bar_fill = tk.Frame(bar_frame, bg=GILT, height=4, width=0)
    bar_fill.place(x=0, y=0, relheight=1)

    def grow(step: int = 0) -> None:
        if step > 36:
            root.destroy()
            return
        bar_fill.place(relwidth=step / 36, relheight=1)
        root.after(max(40, duration_ms // 36), lambda: grow(step + 1))

    root.after(200, grow)
    root.mainloop()
