@echo off
REM PersonaLock Consumer — launch Sam chat window
cd /d "%~dp0"
set ARDEN_EDITION=consumer
python main_gui_assistant.py chat
