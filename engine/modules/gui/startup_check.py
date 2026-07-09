"""Startup validation for consumer edition."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, simpledialog

from modules.arden_env import is_consumer


def _preferred_brain() -> str:
    try:
        from modules.assistant_config import get_config

        return get_config("brain.default", default="venice")
    except Exception:
        return "venice"


def check_brain_key_available() -> bool:
    """True if Venice or Groq key present (consumer edition)."""
    if not is_consumer():
        return True
    if os.getenv("VENICE_API_KEY"):
        return True
    if os.getenv("GROQ_API_KEY"):
        return True
    return False


def require_brain_key_or_exit(root: tk.Tk) -> bool:
    """Block until a cloud brain API key is saved, or exit if user cancels."""
    if check_brain_key_available():
        return True

    preferred = _preferred_brain()
    if preferred == "venice":
        help_text = (
            "Your assistant needs a Venice API key (recommended).\n\n"
            "Privacy-focused cloud · Llama 3.3 70B · venice.ai\n\n"
            "Or use a free Groq key at console.groq.com as backup."
        )
        prompt_label = "Venice API key (recommended)"
        env_name = "VENICE_API_KEY"
    else:
        help_text = (
            "Your assistant needs a Groq API key.\n\n"
            "Get one at console.groq.com"
        )
        prompt_label = "Groq API key"
        env_name = "GROQ_API_KEY"

    while not check_brain_key_available():
        messagebox.showinfo("Cloud brain API key required", help_text, parent=root)
        api_key = simpledialog.askstring(
            prompt_label,
            f"Paste your {env_name}:",
            parent=root,
            show="*",
        )
        if not api_key or not api_key.strip():
            alt = simpledialog.askstring(
                "Alternate key (optional)",
                "Paste GROQ_API_KEY or VENICE_API_KEY, or Cancel to quit:",
                parent=root,
                show="*",
            )
            if not alt or not alt.strip():
                messagebox.showerror(
                    "Cannot start without a key",
                    "Add a Venice or Groq API key, or close this window.",
                    parent=root,
                )
                root.destroy()
                return False
            api_key = alt

        from modules.consumer_bootstrap import bootstrap_consumer, save_user_secrets

        if preferred == "venice":
            save_user_secrets(venice_key=api_key.strip())
        else:
            save_user_secrets(groq_key=api_key.strip())
        bootstrap_consumer()

    return True


# Back-compat alias
check_groq_key_available = check_brain_key_available
require_groq_key_or_exit = require_brain_key_or_exit
