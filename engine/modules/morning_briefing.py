"""
MorningBriefing — assembles Sam's daily briefing from tasks and memory.
"""

from datetime import datetime
from modules.task_manager import TaskManager


class MorningBriefing:
    def __init__(self, task_manager: TaskManager, memory_manager=None):
        self.tasks = task_manager
        self.memory = memory_manager

    def generate(self) -> str:
        now = datetime.now()
        day = now.strftime("%A, %B %d")
        hour = now.hour

        if hour < 12:
            time_of_day = "morning"
        elif hour < 17:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        lines = [f"Good {time_of_day}. Today is {day}."]
        lines.append("")

        task_briefing = self.tasks.format_briefing()
        lines.append(task_briefing)

        return "\n".join(lines)

    def is_morning_trigger(self, user_input: str) -> bool:
        triggers = [
            "good morning", "morning", "good afternoon",
            "good evening", "what did i forget",
            "what's urgent", "whats urgent",
            "briefing", "catch me up", "what do i have",
            "what's on my plate", "whats on my plate"
        ]
        lowered = user_input.lower().strip()
        return any(t in lowered for t in triggers)
