@echo off
echo ========================================
echo Setting up AI Job Assistant Frontend
echo ========================================
echo.

cd ai_job_frontend

echo [1/2] Checking Node.js installation...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

npm --version
if errorlevel 1 (
    echo ERROR: npm is not installed
    pause
    exit /b 1
)

echo.
echo [2/2] Installing dependencies...
npm install

echo.
echo ========================================
echo Frontend setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure backend is running
echo 2. Run: run_frontend.bat
echo.
pause
