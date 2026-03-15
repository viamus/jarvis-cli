@echo off
echo === Jarvis-CLI ===

if not exist .venv (
    echo Venv not found. Run install.bat first.
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Running tests...
python -m pytest tests/test_storage.py -v
if errorlevel 1 (
    echo Tests failed! Fix before running daemon.
	pause
    exit /b 1
)

echo.
echo Installing skill...
jarvis install-skill

echo.
echo Starting Jarvis (system tray)...
start "" .venv\Scripts\pythonw.exe -m jarvis daemon
echo Jarvis is running in the system tray!
echo You can close this window.
timeout /t 3
