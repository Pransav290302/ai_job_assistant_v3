@echo off
echo ========================================
echo PostgreSQL Database Setup
echo ========================================
echo.

cd ai_job_backend

echo [1/4] Checking PostgreSQL installation...
psql --version >nul 2>&1
if errorlevel 1 (
    echo [X] PostgreSQL not found in PATH
    echo.
    echo Please install PostgreSQL from: https://www.postgresql.org/download/
    echo Or make sure PostgreSQL bin directory is in your PATH
    echo.
    pause
    exit /b 1
) else (
    psql --version
    echo [OK] PostgreSQL is installed
)

echo.
echo [2/4] Checking for .env file...
if not exist .env (
    echo Creating .env from template...
    copy env_template.txt .env
    echo .env file created!
) else (
    echo .env file already exists.
)

echo.
echo [3/4] Configuring PostgreSQL in .env...
findstr /C:"USE_SQLITE=false" .env >nul 2>&1
if errorlevel 1 (
    echo Setting USE_SQLITE=false in .env...
    (
        echo.
        echo # Database Configuration - PostgreSQL
        echo USE_SQLITE=false
    ) >> .env
    echo PostgreSQL enabled in .env file!
) else (
    echo PostgreSQL is already configured in .env file.
)

echo.
echo [4/4] Database Configuration
echo.
echo Please update your .env file with PostgreSQL credentials:
echo.
echo USE_SQLITE=false
echo PG_HOST=localhost
echo PG_PORT=5432
echo PG_USER=postgres
echo PG_PASSWORD=your_postgres_password
echo PG_DATABASE=ai_job_assistant
echo.
echo IMPORTANT: Make sure you have created the database:
echo   CREATE DATABASE ai_job_assistant;
echo.
echo You can do this by running:
echo   psql -U postgres
echo   CREATE DATABASE ai_job_assistant;
echo   \q
echo.
pause
