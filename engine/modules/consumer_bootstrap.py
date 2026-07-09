"""Bootstrap paths and secrets for Arden Desktop consumer edition."""

from __future__ import annotations

import json
import os
import shutil
import sys
import threading
from pathlib import Path

import yaml
from dotenv import load_dotenv

from modules.arden_env import get as arden_get
from modules.arden_env import set_ as arden_set
from modules.arden_env import setdefault as arden_setdefault

_BOOTSTRAP_LOCK = threading.Lock()


def consumer_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Arden"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _template_path() -> Path:
    edition = arden_get("EDITION", "consumer")
    name = (
        "assistant_config.consigliere.yml"
        if edition == "consigliere"
        else "assistant_config.consumer.yml"
    )
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path.cwd()))
        candidate = bundle / name
        if candidate.exists():
            return candidate
        # Consigliere builds before bundle included this file — try data dir copy
        data_copy = consumer_data_dir() / name
        if data_copy.exists():
            return data_copy
    repo_root = Path(__file__).resolve().parent.parent
    path = repo_root / name
    if path.exists():
        return path
    if edition == "consigliere":
        fallback = repo_root / "assistant_config.consumer.yml"
        if fallback.exists():
            return fallback
    return path


def reload_consumer_secrets() -> None:
    """Reload API keys from the consumer .env without rewriting runtime config."""
    load_dotenv(consumer_data_dir() / ".env", override=True)


def bootstrap_consumer() -> Path:
    """Prepare edition bootstrap: consumer or consigliere."""
    with _BOOTSTRAP_LOCK:
        edition = arden_get("EDITION", "consumer") or "consumer"
        arden_setdefault("EDITION", edition)
        return _bootstrap_consumer_unlocked()


def _bootstrap_consumer_unlocked() -> Path:
    data_dir = consumer_data_dir()
    edition = arden_get("EDITION", "consumer") or "consumer"
    arden_set("EDITION", edition)
    arden_setdefault("DATA_DIR", str(data_dir))

    logs_dir = data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    arden_setdefault("OUTPUT_DIR", str(logs_dir))

    load_dotenv(data_dir / ".env")

    runtime_config = data_dir / "assistant_config.runtime.yml"
    _write_runtime_config(data_dir, runtime_config)
    arden_set("CONFIG", str(runtime_config))

    _apply_user_profile(data_dir)
    return data_dir


def _write_runtime_config(data_dir: Path, dest: Path) -> None:
    """Generate runtime config with absolute data paths under LOCALAPPDATA."""
    template = _template_path()
    if not template.exists():
        raise FileNotFoundError(f"Consumer config template not found: {template}")

    cfg = yaml.safe_load(template.read_text(encoding="utf-8")) or {}

    edition = arden_get("EDITION", "consumer") or "consumer"
    cfg["edition"] = edition
    if edition == "consigliere":
        cfg.setdefault("intake", {})
        cfg["intake"]["domain_pack"] = "consigliere"
        cfg["morning_briefing_enabled"] = True

    chroma = data_dir / "chroma"
    chroma.mkdir(parents=True, exist_ok=True)

    cfg.setdefault("memory", {})
    cfg["memory"]["backend"] = "sqlite"
    cfg["memory"].setdefault("embedding", {})
    cfg["memory"]["embedding"]["backend"] = "hash"
    cfg["memory"]["sqlite_path"] = str(data_dir / "consumer_memory.db")
    cfg["memory"].setdefault("chroma", {})
    cfg["memory"]["chroma"]["persist_directory"] = str(chroma)

    cfg.setdefault("data", {})
    cfg["data"]["tasks_db_path"] = str(data_dir / "tasks.db")
    cfg["data"]["tactical_facts_db"] = str(data_dir / "tactical_facts.db")
    cfg["data"]["sources_dir"] = str(data_dir / "sources")

    for cloud in ("venice", "groq", "claude", "openai", "gemini"):
        section = cfg.get(cloud)
        if isinstance(section, dict):
            section.pop("api_key", None)

    name = arden_get("USER_NAME")
    assistant = arden_get("ASSISTANT_NAME")
    cfg.setdefault("base_assistant", {})
    if name:
        cfg["base_assistant"]["human_companion_name"] = name
    if assistant:
        cfg["assistant_name"] = assistant
        cfg["base_assistant"]["assistant_name"] = assistant

    dest.write_text(yaml.dump(cfg, default_flow_style=False, sort_keys=False), encoding="utf-8")


def load_user_secrets() -> dict[str, str]:
    """Read saved API keys from consumer data dir."""
    data_dir = consumer_data_dir()
    load_dotenv(data_dir / ".env", override=True)
    return {
        "venice_key": os.getenv("VENICE_API_KEY", "") or "",
        "groq_key": os.getenv("GROQ_API_KEY", "") or "",
    }


def save_user_secrets(
    name: str | None = None,
    groq_key: str | None = None,
    venice_key: str | None = None,
    assistant_name: str | None = None,
) -> None:
    """Persist first-run wizard answers."""
    data_dir = consumer_data_dir()

    if venice_key:
        env_path = data_dir / ".env"
        lines: list[str] = []
        if env_path.exists():
            lines = [
                ln
                for ln in env_path.read_text(encoding="utf-8").splitlines()
                if not ln.startswith("VENICE_API_KEY=")
            ]
        lines.append(f"VENICE_API_KEY={venice_key}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.environ["VENICE_API_KEY"] = venice_key
        load_dotenv(env_path, override=True)

    if groq_key:
        env_path = data_dir / ".env"
        lines: list[str] = []
        if env_path.exists():
            lines = [
                ln for ln in env_path.read_text(encoding="utf-8").splitlines()
                if not ln.startswith("GROQ_API_KEY=")
            ]
        lines.append(f"GROQ_API_KEY={groq_key}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.environ["GROQ_API_KEY"] = groq_key
        load_dotenv(env_path, override=True)

    profile: dict = {}
    if (data_dir / "user.json").exists():
        try:
            profile = json.loads((data_dir / "user.json").read_text(encoding="utf-8"))
        except Exception:
            profile = {}

    if name:
        profile["name"] = name
        arden_set("USER_NAME", name)
    if assistant_name:
        profile["assistant_name"] = assistant_name
        arden_set("ASSISTANT_NAME", assistant_name)

    if profile:
        (data_dir / "user.json").write_text(
            json.dumps(profile), encoding="utf-8"
        )

    _write_runtime_config(data_dir, data_dir / "assistant_config.runtime.yml")
    arden_set("CONFIG", str(data_dir / "assistant_config.runtime.yml"))


def _apply_user_profile(data_dir: Path) -> None:
    profile_path = data_dir / "user.json"
    if not profile_path.exists():
        return
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        if profile.get("name"):
            arden_set("USER_NAME", profile["name"])
        if profile.get("assistant_name"):
            arden_set("ASSISTANT_NAME", profile["assistant_name"])
    except Exception:
        pass


def ensure_consumer_template_in_data_dir() -> None:
    """Copy bundled consumer template into data dir for reference."""
    if not getattr(sys, "frozen", False):
        return
    template = _template_path()
    target = consumer_data_dir() / "assistant_config.consumer.yml"
    if template.exists() and not target.exists():
        shutil.copy(template, target)
