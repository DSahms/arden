"""Test morning briefing and task manager."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.task_manager import TaskManager, Priority
from modules.morning_briefing import MorningBriefing


def test_task_manager():
    # Use temp db for testing
    tm = TaskManager(db_path="data/test_tasks.db")

    # Add tasks
    id1 = tm.add_task("Call the recovery center", Priority.HIGH)
    id2 = tm.add_task("Review PersonaLock roadmap", Priority.MEDIUM)
    id3 = tm.add_task("Follow up with Jennifer's counselor", Priority.URGENT)

    assert id1 > 0
    assert id2 > 0
    assert id3 > 0
    print("[PASS] Task creation")

    # Get open tasks
    tasks = tm.get_open_tasks()
    assert len(tasks) >= 3
    # Urgent should be first
    assert tasks[0].priority == Priority.URGENT
    print("[PASS] Task retrieval and priority ordering")

    # Mark done
    tm.mark_done(id1)
    tasks_after = tm.get_open_tasks()
    ids = [t.id for t in tasks_after]
    assert id1 not in ids
    print("[PASS] Mark done")

    # Briefing format
    briefing = tm.format_briefing()
    assert len(briefing) > 0
    print("[PASS] Briefing generation")

    # Morning trigger detection
    mb = MorningBriefing(tm)
    assert mb.is_morning_trigger("good morning")
    assert mb.is_morning_trigger("what did i forget")
    assert mb.is_morning_trigger("catch me up")
    assert not mb.is_morning_trigger("what is the weather")
    print("[PASS] Morning trigger detection")

    # Full briefing generate
    full_briefing = mb.generate()
    assert len(full_briefing) > 0
    assert "Today is" in full_briefing
    print("[PASS] Full briefing generation")

    # Cleanup — force GC so SQLite releases Windows file lock before deletion
    import gc
    gc.collect()
    try:
        os.remove("data/test_tasks.db")
    except PermissionError:
        import time
        time.sleep(0.2)
        os.remove("data/test_tasks.db")
    print("[SUCCESS] ALL MORNING BRIEFING TESTS PASSED")


if __name__ == "__main__":
    test_task_manager()
