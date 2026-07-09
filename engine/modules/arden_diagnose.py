"""Headless Arden diagnostics — no human in the loop."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _report_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Arden"
    base.mkdir(parents=True, exist_ok=True)
    return base / "diagnose-last.txt"


def _log(lines: list[str], msg: str) -> None:
    print(msg)
    lines.append(msg)


def _exe_info(path: Path, lines: list[str]) -> None:
    if path.exists():
        item = path.stat()
        _log(
            lines,
            f"  OK  {path}  ({item.st_size} bytes, {datetime.fromtimestamp(item.st_mtime)})",
        )
    else:
        _log(lines, f"  --  missing: {path}")


def run_diagnose() -> int:
    from modules.arden_env import setdefault as arden_setdefault
    from modules.consumer_bootstrap import bootstrap_consumer, consumer_data_dir

    arden_setdefault("EDITION", "consumer")
    lines: list[str] = []
    _log(lines, "Arden Desktop diagnose")
    _log(lines, "=" * 40)

    _log(lines, "\nInstall copies (newest should be what you run):")
    for path in (
        Path(r"D:\Test two\Arden.exe"),
        Path(__file__).resolve().parents[1] / "dist" / "Arden" / "Arden.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Arden" / "App" / "Arden.exe",
    ):
        _exe_info(path, lines)

    data = consumer_data_dir()
    _log(lines, f"\nData dir: {data}")
    env_path = data / ".env"
    venice = os.getenv("VENICE_API_KEY", "")
    groq = os.getenv("GROQ_API_KEY", "")
    bootstrap_consumer()
    from dotenv import load_dotenv

    load_dotenv(env_path, override=True)
    venice = os.getenv("VENICE_API_KEY", "") or venice
    groq = os.getenv("GROQ_API_KEY", "") or groq
    _log(lines, f"VENICE_API_KEY: {'present' if venice else 'MISSING'} ({len(venice)} chars)")
    _log(lines, f"GROQ_API_KEY: {'present' if groq else 'MISSING'} ({len(groq)} chars)")

    _log(lines, "\nVenice API probe:")
    if not venice:
        _log(lines, "  FAIL  no key")
    else:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=venice, base_url="https://api.venice.ai/api/v1", timeout=30.0
            )
            reply = client.chat.completions.create(
                model="llama-3.3-70b",
                messages=[{"role": "user", "content": "Reply exactly: venice ok"}],
                max_tokens=16,
            )
            text = (reply.choices[0].message.content or "").strip()
            _log(lines, f"  OK  {text[:60]}")
        except Exception as exc:
            _log(lines, f"  FAIL  {exc}")

    _log(lines, "\nBrain switch + inference (Kobold -> Venice):")
    try:
        from modules.base_assistant import PlainAssistant
        from modules.utils import create_session_logger_id, setup_logging

        logger = setup_logging(create_session_logger_id())
        assistant = PlainAssistant(logger, "diagnose")
        for brain in ("kobold", "venice"):
            ok = assistant.switch_brain(brain)
            _log(lines, f"  switch {brain}: {'OK' if ok else 'FAIL'}")
        chunks: list[str] = []

        def on_chunk(c: str) -> None:
            if c:
                chunks.append(c)

        reply = assistant.process_text("Say: diagnose ok", chunk_callback=on_chunk)
        _log(lines, f"  venice reply: {(reply or '')[:80]}")
        _log(lines, f"  stream chunks: {len(chunks)}")
    except Exception as exc:
        _log(lines, f"  FAIL  {exc}")

    crash = data / "crash-last.txt"
    if crash.exists():
        _log(lines, f"\nCrash log present: {crash}")
        tail = crash.read_text(encoding="utf-8", errors="replace").splitlines()[-8:]
        for row in tail:
            _log(lines, f"  {row}")

    _log(lines, "\nRecommendation:")
    test_two = Path(r"D:\Test two\Arden.exe")
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Arden" / "App" / "Arden.exe"
    if test_two.exists() and local.exists():
        if test_two.stat().st_mtime > local.stat().st_mtime:
            _log(
                lines,
                "  Run D:\\Test two\\Arden.exe — your desktop shortcut may be the OLD Jun 13 build.",
            )
    _log(lines, "  Or: python main_gui_assistant.py acceptance-test")

    body = "\n".join(lines) + "\n"
    _report_path().write_text(body, encoding="utf-8")
    _log(lines, f"\nSaved: {_report_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_diagnose())
