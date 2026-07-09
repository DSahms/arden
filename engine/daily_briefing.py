# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sqlite3
from datetime import date, timedelta
from modules.task_manager import TaskManager

def run_daily_briefing():
    tm = TaskManager("data/tasks.db")
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    week_out = (date.today() + timedelta(days=7)).isoformat()

    print("=" * 50)
    print(f"  ADA DAILY BRIEFING — {today}")
    print("=" * 50)

    # Overdue
    overdue = tm.get_overdue_tasks("Spring Garden 2026")
    if overdue:
        print(f"\n⚠️  OVERDUE ({len(overdue)} tasks):")
        for t in overdue:
            print(f"  • [{t.get('due_date','')}] {t.get('content', t.get('name',''))[:70]}")
    else:
        print("\n✅ Nothing overdue.")

    # Due today
    cursor = sqlite3.connect("data/tasks.db").cursor()
    cursor.execute("""
        SELECT content, due_date, category FROM tasks
        WHERE project = 'Spring Garden 2026'
          AND status != 'complete'
          AND due_date = ?
        ORDER BY category
    """, (today,))
    due_today = cursor.fetchall()

    if due_today:
        print(f"\n📌 DUE TODAY ({len(due_today)} tasks):")
        for row in due_today:
            print(f"  • [{row[2]}] {row[0][:70]}")
    else:
        print("\n📌 Nothing due today.")

    # Due this week
    cursor.execute("""
        SELECT content, due_date, category FROM tasks
        WHERE project = 'Spring Garden 2026'
          AND status != 'complete'
          AND due_date > ?
          AND due_date <= ?
        ORDER BY due_date, category
    """, (today, week_out))
    upcoming = cursor.fetchall()

    if upcoming:
        print(f"\n📅 COMING UP THIS WEEK ({len(upcoming)} tasks):")
        for row in upcoming:
            print(f"  • [{row[1]}] [{row[2]}] {row[0][:70]}")
    else:
        print("\n📅 Nothing else due this week.")

    # Progress summary
    progress = tm.get_project_progress("Spring Garden 2026")
    print(f"\n📊 SPRING GARDEN PROGRESS:")
    print(f"  {progress['complete']} of {progress['total']} tasks complete ({progress['percent_done']}%)")
    print(f"  {progress['remaining']} remaining | {progress['overdue']} overdue")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    run_daily_briefing()
