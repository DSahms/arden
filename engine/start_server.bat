@echo off
cd /d c:\Users\david\Projects\PersonaLock
python -m uvicorn api.routes:app --host 127.0.0.1 --port 8000
pause
