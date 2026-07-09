@echo off
:: ─────────────────────────────────────────────
:: Craigslist South Jersey Free Stuff Digest
:: Runs craigslist_digest.py and saves output
:: to logs\craigslist_YYYY-MM-DD.txt
:: ─────────────────────────────────────────────

cd /d "%~dp0"

:: Get today's date for log filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set LOGDATE=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%

:: Create logs directory if needed
if not exist logs mkdir logs

set LOGFILE=logs\craigslist_%LOGDATE%.txt

echo Running Craigslist digest at %TIME% on %DATE% >> "%LOGFILE%"
echo ================================================ >> "%LOGFILE%"

:: Run the digest — try py launcher first, then python
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    py craigslist_digest.py >> "%LOGFILE%" 2>&1
) else (
    python craigslist_digest.py >> "%LOGFILE%" 2>&1
)

echo.
echo ✅ Craigslist digest saved to: %LOGFILE%

:: Optional: Open the log in Notepad automatically
:: notepad "%LOGFILE%"

pause
