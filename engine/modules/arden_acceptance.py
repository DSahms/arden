"""Full Arden Desktop acceptance suite — run before shipping."""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import tkinter as tk
from pathlib import Path

from modules.arden_env import get as arden_get
from modules.arden_env import setdefault as arden_setdefault

arden_setdefault("EDITION", "consumer")
FAILURES: list[str] = []
WARNINGS: list[str] = []


def _ok(name: str) -> None:
    print(f"  [PASS] {name}")


def _warn(name: str, detail: str) -> None:
    WARNINGS.append(f"{name}: {detail}")
    print(f"  [WARN] {name}: {detail}")


def _fail(name: str, detail: str) -> None:
    FAILURES.append(f"{name}: {detail}")
    print(f"  [FAIL] {name}: {detail}")


def test_bootstrap_and_config() -> None:
    from modules.consumer_bootstrap import bootstrap_consumer, load_user_secrets
    from modules.assistant_config import get_config

    bootstrap_consumer()
    assert get_config("edition") == "consumer"
    assert get_config("memory.backend") == "sqlite"
    secrets = load_user_secrets()
    if not secrets.get("venice_key") and not secrets.get("groq_key"):
        _fail("api_keys", "No Venice or Groq key in %LOCALAPPDATA%\\Arden\\.env")
        return
    if secrets.get("venice_key"):
        _ok("venice_key_present")
    if secrets.get("groq_key"):
        _ok("groq_key_present")
    _ok("bootstrap_and_config")


def test_session_store() -> None:
    from modules.gui.session_store import SessionStore, _sessions_path

    marker = f"__acceptance_{int(time.time())}"
    store = SessionStore()
    store.create(marker)
    store.append_message("You", "harness ping")
    store.append_message("Arden", "harness pong")
    raw = json.loads(_sessions_path().read_text(encoding="utf-8"))
    active = store.active()
    bodies = [m.body for m in active.messages]
    assert "harness ping" in bodies and "harness pong" in bodies
    assert raw.get("active_id") == store.active_id
    _ok("session_store")

def test_sqlite_memory_background() -> None:
    from modules.consumer_bootstrap import bootstrap_consumer
    from modules.memory_vault.memory_factory import create_graph_store
    from modules.memory_vault.memory_manager import MemoryManager
    from utils.embedding_utils import HashEmbedder

    bootstrap_consumer()
    graph = create_graph_store()
    mm = MemoryManager(
        neo4j_client=graph,
        chroma_store=None,
        embedding_function=HashEmbedder().embed,
    )
    result: list[str] = []
    err: list[Exception] = []

    def worker() -> None:
        try:
            mid = mm.remember(
                "User: acceptance\nAssistant: background write ok",
                memory_type="event",
                importance=0.5,
            )
            result.append(mid or "")
        except Exception as exc:
            err.append(exc)

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout=10)
    if err:
        raise err[0]
    assert result and result[0], "background remember failed"
    _ok("sqlite_memory_background")


def test_stream_mark_tk() -> None:
    from tkinter import scrolledtext

    root = tk.Tk()
    root.withdraw()
    chat = scrolledtext.ScrolledText(root)
    chat.insert(tk.END, "Arden\n", "arden_name")
    chat.insert(tk.END, "", "stream")
    chat.mark_set("stream_mark", "insert")
    chat.insert("stream_mark", "Hello ", "stream")
    chat.mark_set("stream_mark", "insert")
    chat.insert("stream_mark", "Dave!", "stream")
    chat.insert("stream_mark", "\n\n", "stream")
    body = chat.get("1.0", tk.END).strip()
    root.destroy()
    assert "Hello Dave!" in body, f"unexpected stream body: {body!r}"
    _ok("stream_mark_tk")


def test_venice_inference() -> None:
    from modules.consumer_bootstrap import bootstrap_consumer, load_user_secrets
    from modules.brain_backends.venice_backend import VeniceBackend
    from modules.assistant_config import get_config

    bootstrap_consumer()
    secrets = load_user_secrets()
    key = secrets.get("venice_key") or os.getenv("VENICE_API_KEY")
    if not key:
        _warn("venice_inference", "skipped — no key")
        return

    cfg = get_config("brain.venice", default={}) or {}
    backend = VeniceBackend({**cfg, "api_key": key})
    chunks: list[str] = []

    def on_chunk(c: str) -> None:
        chunks.append(c)

    reply = backend.generate_response_stream(
        system_prompt="You are Arden. Reply in one short sentence.",
        user_message='Reply with exactly: acceptance ok',
        on_chunk=on_chunk,
    )
    reply = (reply or "").strip()
    if not reply or "error" in reply.lower():
        _fail("venice_inference", reply or "empty reply")
        return
    if not chunks:
        _fail("venice_streaming", "no stream chunks received")
        return
    _ok("venice_inference")
    _ok("venice_streaming")


def test_groq_key_status() -> None:
    from modules.consumer_bootstrap import bootstrap_consumer, load_user_secrets

    bootstrap_consumer()
    key = load_user_secrets().get("groq_key") or os.getenv("GROQ_API_KEY")
    if not key:
        _warn("groq_key", "not configured (Venice-only is fine)")
        return
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1", timeout=20.0)
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "say: ok"}],
            max_tokens=8,
        )
        text = (r.choices[0].message.content or "").strip()
        if text:
            _ok("groq_inference")
        else:
            _fail("groq_inference", "empty reply")
    except Exception as exc:
        msg = str(exc).lower()
        if "401" in msg or "invalid" in msg:
            _warn("groq_inference", "key invalid — use Venice in Brain dropdown")
        else:
            _fail("groq_inference", str(exc))


def test_echo_filter_allows_repeat_user_message() -> None:
    """Typed 'hello' twice must not be swallowed as 'own speech'."""
    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant

    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-echo")
    assistant.conversation_history = [{"role": "user", "content": "hello"}]
    # Would have returned "" before fix when last message is also user hello
    out = assistant.process_text("hello", chunk_callback=None)
    if not (out or "").strip():
        _fail("echo_filter", "repeated user hello was blocked")
        return
    _ok("echo_filter_repeat_user")


def test_process_text_full_flow() -> None:
    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant
    from modules.consumer_bootstrap import bootstrap_consumer, load_user_secrets

    bootstrap_consumer()
    if not (load_user_secrets().get("venice_key") or os.getenv("VENICE_API_KEY")):
        _warn("process_text_flow", "skipped — no Venice key")
        return

    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-flow")
    assistant.switch_brain("venice")
    chunks: list[str] = []

    def on_chunk(c: str) -> None:
        if c:
            chunks.append(c)

    reply = assistant.process_text(
        "Say exactly: Arden acceptance test passed.",
        chunk_callback=on_chunk,
    )
    reply = (reply or "").strip()
    if not reply:
        _fail("process_text_flow", "empty reply")
        return
    if not chunks:
        _fail("process_text_stream", "no chunks from process_text")
        return
    _ok("process_text_flow")
    _ok("process_text_stream")


def test_chat_queue_busy_clears() -> None:
    """Simulate GUI queue: chunks + done must leave busy=False."""
    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant
    from modules.gui.chat_app import ChatApp

    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-gui")
    root = tk.Tk()
    root.withdraw()
    app = ChatApp(root, assistant, logger)
    app._request_id = 1
    app._set_busy(True)
    app._queue.put(("chunk", ("Hi ", 1)))
    app._queue.put(("chunk", ("Dave", 1)))
    app._queue.put(("done", ("Hi Dave", False, 1)))
    app._poll_queue()
    root.update_idletasks()
    if app._busy:
        _fail("chat_queue_busy", "still busy after done")
        root.destroy()
        return
    text = app.chat.get("1.0", tk.END)
    if "Hi Dave" not in text:
        _fail("chat_queue_text", f"missing streamed text in {text!r}")
        root.destroy()
        return
    root.destroy()
    _ok("chat_queue_busy_clears")
    _ok("chat_queue_stream_text")


def test_venice_gui_send_survives() -> None:
    """Send via GUI worker on Venice — window must stay alive."""
    import time

    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant
    from modules.gui.chat_app import ChatApp

    if not os.getenv("VENICE_API_KEY"):
        _warn("venice_gui_send", "skipped — no Venice key")
        return

    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-venice-gui")
    root = tk.Tk()
    root.withdraw()
    app = ChatApp(root, assistant, logger)
    app.brain_var.set("venice")
    app._append("You", "hello", persist=False)
    rid = app._bump_request_id()
    app._set_busy(True)
    app._worker("hello", "venice", rid, False)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        app._poll_queue()
        root.update()
        if not app._busy:
            break
        time.sleep(0.05)
    if not root.winfo_exists():
        _fail("venice_gui_send", "root window destroyed")
        return
    if app._busy:
        _warn("venice_gui_send", "still busy after 45s — UI should remain usable")
    text = app.chat.get("1.0", tk.END)
    if "hello" not in text.lower():
        _fail("venice_gui_send", "user message missing from chat")
        root.destroy()
        return
    root.destroy()
    _ok("venice_gui_send_survives")


def test_kobold_local() -> None:
    try:
        import requests
        from modules.assistant_config import get_config

        url = get_config("kobold.base_url", default="http://127.0.0.1:5001/v1")
        r = requests.get(f"{url.rstrip('/')}/models", timeout=3)
        if r.status_code == 200:
            _ok("kobold_local_online")
        else:
            _warn("kobold_local", f"port 5001 returned {r.status_code}")
    except Exception as exc:
        _warn("kobold_local", f"not reachable ({exc}) — still in Brain dropdown when you start it")


def test_tactical_facts_and_intake() -> None:
    import tempfile
    from pathlib import Path

    from modules.intake.domains import get_domains_for_mode
    from modules.intake.engine import IntakeEngine
    from modules.intake.facts_store import TacticalFactsStore
    from modules.proactive.context_deepening import detect_decision_event

    db = Path(tempfile.mkdtemp()) / "facts.db"
    store = TacticalFactsStore(db)
    store.connect()
    store.add_fact("people", "Mom — birthday March 12", label="Mom")
    assert len(store.list_facts()) == 1
    assert get_domains_for_mode("b")
    engine = IntakeEngine("b", store)
    assert engine.current_question() is not None
    assert detect_decision_event("I'm declining a birthday party invitation")
    _ok("tactical_facts_and_intake")


def test_sources_local_index() -> None:
    import tempfile
    from pathlib import Path

    from modules.sources.document_store import DocumentStore
    from modules.sources.rag import ingest_file
    from utils.embedding_utils import HashEmbedder

    td = Path(tempfile.mkdtemp())
    store = DocumentStore(sources_dir=td / "sources", chroma_dir=td / "chroma", embed=HashEmbedder().embed)
    f = td / "note.txt"
    f.write_text("Payment due April 1 amount 99.00", encoding="utf-8")
    ingest_file(store, f)
    hits = store.query("when is payment due", n_results=1)
    assert hits, "sources query returned nothing"
    _ok("sources_local_index")


def test_utilities_export() -> None:
    import tempfile
    from pathlib import Path

    from modules.gui.session_store import ChatMessage, ChatSession
    from modules.utilities.export_docx import export_session_docx

    session = ChatSession.new("Export test")
    session.messages = [ChatMessage("You", "hello")]
    out = export_session_docx(session, Path(tempfile.mktemp(suffix=".docx")))
    assert Path(out).exists() and Path(out).stat().st_size > 0
    _ok("utilities_export_docx")


def test_consumer_brain_dropdown() -> None:
    from modules.gui.chat_app import CONSUMER_BRAINS, ChatApp, _brain_id, _brain_label
    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant

    assert "kobold" in CONSUMER_BRAINS
    assert "venice" in CONSUMER_BRAINS
    assert "groq" in CONSUMER_BRAINS
    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-brains")
    root = tk.Tk()
    root.withdraw()
    app = ChatApp(root, assistant, logger)
    values = list(app.brain_combo.cget("values"))
    for brain in CONSUMER_BRAINS:
        label = _brain_label(brain)
        if label not in values and brain not in values:
            _fail("brain_dropdown", f"{brain} missing from combobox {values}")
            root.destroy()
            return
    assert _brain_id(_brain_label("venice")) == "venice"
    assert hasattr(app, "entry"), "input bar missing"
    assert app.entry.winfo_exists()
    _ok("brain_dropdown_all_three")
    _ok("input_bar_present")
    root.destroy()


def test_companion_rename_settings() -> None:
    import json
    import tempfile
    from unittest import mock

    from modules.consumer_bootstrap import save_user_secrets, bootstrap_consumer
    from modules.assistant_config import get_config

    old_config = arden_get("CONFIG")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with mock.patch("modules.consumer_bootstrap.consumer_data_dir", return_value=data):
                save_user_secrets(name="TestUser", assistant_name="Rhema")
                bootstrap_consumer()
                assert get_config("base_assistant.assistant_name") == "Rhema"
                assert get_config("base_assistant.human_companion_name") == "TestUser"
                profile = json.loads((data / "user.json").read_text(encoding="utf-8"))
                assert profile["assistant_name"] == "Rhema"
        _ok("companion_rename_persist")
    finally:
        bootstrap_consumer()


def test_brain_switch_kobold() -> None:
    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant

    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-kobold")
    if assistant.switch_brain("kobold"):
        _ok("brain_switch_kobold")
    else:
        _warn("brain_switch_kobold", "Kobold not running — dropdown still offers it")


def test_brain_switch() -> None:
    from modules.utils import create_session_logger_id, setup_logging
    from modules.base_assistant import PlainAssistant

    logger = setup_logging(create_session_logger_id())
    assistant = PlainAssistant(logger, "acceptance-brain")
    assert assistant.switch_brain("venice"), "venice switch failed"
    _ok("brain_switch_venice")


def run_acceptance() -> int:
    print("Arden Desktop acceptance suite")
    print("=" * 40)
    tests = [
        ("Bootstrap & config", test_bootstrap_and_config),
        ("Tactical facts + intake + deepening", test_tactical_facts_and_intake),
        ("Sources local index", test_sources_local_index),
        ("Utilities export", test_utilities_export),
        ("Session store", test_session_store),
        ("SQLite memory (background thread)", test_sqlite_memory_background),
        ("Tk stream marks", test_stream_mark_tk),
        ("Venice inference + stream", test_venice_inference),
        ("Groq key status", test_groq_key_status),
        ("Echo filter (repeat hello)", test_echo_filter_allows_repeat_user_message),
        ("process_text full flow", test_process_text_full_flow),
        ("Chat queue / busy state", test_chat_queue_busy_clears),
        ("Venice GUI send survives", test_venice_gui_send_survives),
        ("Brain dropdown + input bar", test_consumer_brain_dropdown),
        ("Companion rename (Settings path)", test_companion_rename_settings),
        ("Local Kobold (port 5001)", test_kobold_local),
        ("Brain switch Venice", test_brain_switch),
        ("Brain switch Kobold", test_brain_switch_kobold),
    ]
    for label, fn in tests:
        print(f"\n{label}")
        try:
            fn()
        except Exception as exc:
            _fail(label, str(exc))

    print("\n" + "=" * 40)
    if WARNINGS:
        print(f"Warnings: {len(WARNINGS)}")
        for w in WARNINGS:
            print(f"  - {w}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print(f"  - {f}")
        _write_result("FAIL", FAILURES, WARNINGS)
        return 1
    print("ALL ACCEPTANCE CHECKS PASSED")
    _write_result("PASS", [], WARNINGS)
    return 0


def _write_result(status: str, failures: list[str], warnings: list[str]) -> None:
    try:
        from modules.consumer_bootstrap import consumer_data_dir

        lines = [f"status={status}", f"at={time.strftime('%Y-%m-%d %H:%M:%S')}"]
        for w in warnings:
            lines.append(f"warn={w}")
        for f in failures:
            lines.append(f"fail={f}")
        (consumer_data_dir() / "acceptance-last.txt").write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )
    except Exception:
        pass


if __name__ == "__main__":
    raise SystemExit(run_acceptance())
