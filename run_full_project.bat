@echo off
echo ========================================
echo Starting Full AI Job Assistant Project
echo ========================================
echo.
echo This will start both backend and frontend
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Starting backend in new window...
start "AI Job Assistant - Backend" cmd /k "cd /d %~dp0 && run_backend.bat"

timeout /t 3 /nobreak >nul

echo.
echo Starting frontend in new window...
start "AI Job Assistant - Frontend" cmd /k "cd /d %~dp0 && run_frontend.bat"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the windows to stop the servers.
echo.
pause
