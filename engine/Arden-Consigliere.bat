@echo off
REM Arden Consigliere — Dave edition (briefing, tasks, business intake)
cd /d "%~dp0"
set ARDEN_EDITION=consigliere
REM Direct launch — no Typer subcommand; use pythonw so no flash console
pythonw main_gui_assistant.py
if errorlevel 1 (
  echo Arden Consigliere failed. Check %%LOCALAPPDATA%%\Arden\crash-last.txt
  pause
)
