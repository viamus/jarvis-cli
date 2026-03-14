@echo off
echo === Jarvis-CLI Install ===

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating venv...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -e .

echo Installing pytest...
pip install pytest -q

echo.
echo === Done! Run "run.bat" to start Jarvis ===
