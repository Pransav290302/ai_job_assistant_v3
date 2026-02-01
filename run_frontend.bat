@echo off
echo ========================================
echo Starting AI Job Assistant Frontend
echo ========================================
echo.

cd ai_job_frontend

if not exist node_modules (
    echo ERROR: Dependencies not installed!
    echo Please run setup_frontend.bat first
    pause
    exit /b 1
)

echo.
echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Make sure the backend is running on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
