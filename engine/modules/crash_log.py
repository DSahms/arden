"""Capture uncaught exceptions to %LOCALAPPDATA%\\Arden\\crash-last.txt."""

from __future__ import annotations

import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path


def _crash_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Arden"
    base.mkdir(parents=True, exist_ok=True)
    return base / "crash-last.txt"


def _write_crash(label: str, exc: BaseException) -> None:
    try:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        body = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        _crash_path().write_text(f"[{stamp}] {label}\n{body}\n", encoding="utf-8")
    except Exception:
        pass


def install_crash_logging() -> None:
    """Register global exception hooks (safe to call more than once)."""
    if getattr(install_crash_logging, "_installed", False):
        return
    install_crash_logging._installed = True  # type: ignore[attr-defined]

    def _sys_hook(exc_type, exc, tb):
        if exc is not None:
            _write_crash("sys.excepthook", exc)
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _sys_hook

    if hasattr(threading, "excepthook"):
        def _thread_hook(args):  # type: ignore[no-untyped-def]
            if args.exc_value is not None:
                _write_crash(f"thread:{args.thread.name}", args.exc_value)

        threading.excepthook = _thread_hook  # type: ignore[attr-defined]
