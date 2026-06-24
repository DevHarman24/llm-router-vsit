@echo off
title LLM Router
echo ===================================================
echo Starting LLM Router (Backend + Frontend)
echo ===================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    pause
    exit /b
)

:: Check if uvicorn is installed (simple check)
python -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requirements...
    pip install -r requirements.txt
)

echo.
echo The app will open in your browser automatically...
timeout /t 2 /nobreak >nul

:: Open browser
start http://localhost:8000

:: Run the server
echo.
echo Server running on http://localhost:8000 (Press CTRL+C to quit)
python -m uvicorn backend.server:app --port 8000 --reload

pause
