@echo off
echo ========================================
echo Starting AI Job Assistant Backend
echo ========================================
echo.

cd ai_job_backend

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup_backend.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking for .env file...
if not exist .env (
    echo WARNING: .env file not found!
    echo Creating from template...
    copy env_template.txt .env
    echo.
    echo Please edit .env file and add your API key:
    echo - OPENAI_API_KEY
    echo.
    echo You can use: python add_api_key.py YOUR_API_KEY
    echo.
    pause
)

echo.
echo Validating environment variables...
python validate_env.py
if errorlevel 1 (
    echo.
    echo WARNING: Some required environment variables are missing!
    echo Please update your .env file before starting the server.
    echo.
    pause
)

echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

pause
