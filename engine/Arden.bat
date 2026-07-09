@echo off
REM Arden Desktop — launch Arden chat window
cd /d "%~dp0"
set ARDEN_EDITION=consumer
python main_gui_assistant.py chat
