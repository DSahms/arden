"""Test Telegram bridge initialization without a real token."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.task_manager import TaskManager
from modules.morning_briefing import MorningBriefing


def test_task_manager_for_telegram():
    tm = TaskManager(db_path="data/test_telegram.db")
    id1 = tm.add_task("Test task for Telegram", source="telegram")
    tasks = tm.get_open_tasks()
    assert any(t.id == id1 for t in tasks)
    tm.mark_done(id1)
    tasks_after = tm.get_open_tasks()
    assert not any(t.id == id1 for t in tasks_after)
    print("[PASS] Task manager works for Telegram source")

    mb = MorningBriefing(tm)
    briefing = mb.generate()
    assert "Good" in briefing
    print("[PASS] Briefing generates correctly")

    # Verify telegram_bridge module imports cleanly (no token needed for import)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "telegram_bridge",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "modules", "telegram_bridge.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "TelegramBridge"), "TelegramBridge class not found"
        print("[PASS] telegram_bridge.py imports cleanly")
    except ImportError as e:
        print(f"[SKIP] telegram_bridge import skipped (dependency missing): {e}")

    # Cleanup
    import gc
    gc.collect()
    try:
        os.remove("data/test_telegram.db")
    except PermissionError:
        import time
        time.sleep(0.2)
        os.remove("data/test_telegram.db")
    print("[SUCCESS] TELEGRAM BRIDGE TESTS PASSED")


if __name__ == "__main__":
    test_task_manager_for_telegram()
