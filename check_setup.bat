@echo off
echo ========================================
echo AI Job Assistant - Setup Checker
echo ========================================
echo.

set ERRORS=0

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed or not in PATH
    set /a ERRORS+=1
) else (
    python --version
    echo [OK] Python is installed
)

echo.
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js is not installed or not in PATH
    set /a ERRORS+=1
) else (
    node --version
    echo [OK] Node.js is installed
)

echo.
echo [3/6] Checking backend setup...
cd ai_job_backend
if not exist venv (
    echo [X] Backend virtual environment not found
    echo     Run: setup_backend.bat
    set /a ERRORS+=1
) else (
    echo [OK] Backend virtual environment exists
)

if not exist .env (
    echo [X] Backend .env file not found
    echo     Create .env file or run: python add_api_key.py YOUR_KEY
    set /a ERRORS+=1
) else (
    echo [OK] Backend .env file exists
)
cd ..

echo.
echo [4/6] Checking frontend setup...
cd ai_job_frontend
if not exist node_modules (
    echo [X] Frontend dependencies not installed
    echo     Run: setup_frontend.bat
    set /a ERRORS+=1
) else (
    echo [OK] Frontend dependencies installed
)

if not exist .env.local (
    echo [!] Frontend .env.local not found (optional but recommended)
    echo     Create .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
) else (
    echo [OK] Frontend .env.local exists
)
cd ..

echo.
echo [5/6] Checking database...
cd ai_job_backend
if exist .env (
    findstr /C:"PG_HOST" .env >nul 2>&1
    if errorlevel 1 (
        echo [!] Database configuration not found in .env
        echo     Add PostgreSQL config or use SQLite
    ) else (
        echo [OK] Database configuration found
    )
)
cd ..

echo.
echo [6/6] Summary
echo ========================================
if %ERRORS% EQU 0 (
    echo [SUCCESS] All checks passed!
    echo.
    echo You can now run:
    echo   - run_backend.bat (to start backend)
    echo   - run_frontend.bat (to start frontend)
    echo   - run_full_project.bat (to start both)
) else (
    echo [WARNING] Found %ERRORS% issue(s)
    echo.
    echo Please fix the issues above before running the project.
)
echo.
pause
