@echo off
echo ========================================
echo Setting up AI Job Assistant Backend
echo ========================================
echo.

cd ai_job_backend

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/4] Installing Playwright browsers...
playwright install chromium

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a .env file in ai_job_backend folder
echo 2. Add your API keys (see env_template.txt)
echo 3. Run: run_backend.bat
echo.
pause
