@echo off
echo ========================================
echo SQLite Database Setup
echo ========================================
echo.

cd ai_job_backend

echo [1/3] Checking for .env file...
if not exist .env (
    echo Creating .env from template...
    copy env_template.txt .env
    echo .env file created!
) else (
    echo .env file already exists.
)

echo.
echo [2/3] Configuring SQLite...
findstr /C:"USE_SQLITE=true" .env >nul 2>&1
if errorlevel 1 (
    echo Setting USE_SQLITE=true in .env...
    (
        echo.
        echo # Database Configuration - SQLite enabled
        echo USE_SQLITE=true
    ) >> .env
    echo SQLite enabled in .env file!
) else (
    echo SQLite is already enabled in .env file.
)

echo.
echo [3/3] Verifying configuration...
findstr /C:"USE_SQLITE=true" .env >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to set USE_SQLITE=true
    echo Please manually edit .env and add: USE_SQLITE=true
    pause
    exit /b 1
) else (
    echo [OK] SQLite is configured!
)

echo.
echo ========================================
echo SQLite Setup Complete!
echo ========================================
echo.
echo SQLite is now enabled. When you start the backend:
echo - Database file will be created automatically at: job_assistant.db
echo - No database server installation needed
echo - No additional configuration required
echo.
echo Next steps:
echo 1. Add your OPENAI_API_KEY to .env file
echo 2. Run: run_backend.bat
echo.
pause
