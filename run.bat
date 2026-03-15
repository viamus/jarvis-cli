@echo off
echo === Jarvis-CLI ===

if not exist .venv (
    echo Venv not found. Run install.bat first.
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Running tests...
python -m pytest tests/test_storage.py tests/test_hook.py -v
if errorlevel 1 (
    echo Tests failed! Fix before running daemon.
	pause
    exit /b 1
)

echo.
echo Installing hook...
jarvis install-hook

echo.
echo Installing skill...
jarvis install-skill

echo.
echo Starting daemon...
jarvis daemon

