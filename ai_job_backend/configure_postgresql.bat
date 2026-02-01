@echo off
echo ========================================
echo PostgreSQL Configuration Helper
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo This script will help you configure PostgreSQL in your .env file.
echo.

if not exist .env (
    echo Creating .env from template...
    if exist env_template.txt (
        copy env_template.txt .env
    ) else (
        echo ERROR: env_template.txt not found!
        pause
        exit /b 1
    )
    echo.
)

echo Please provide your PostgreSQL configuration:
echo.
set /p PG_PASSWORD="Enter PostgreSQL password for 'postgres' user: "
set /p PG_HOST="Enter PostgreSQL host [localhost]: "
if "%PG_HOST%"=="" set PG_HOST=localhost
set /p PG_PORT="Enter PostgreSQL port [5432]: "
if "%PG_PORT%"=="" set PG_PORT=5432
set /p PG_USER="Enter PostgreSQL user [postgres]: "
if "%PG_USER%"=="" set PG_USER=postgres
set /p PG_DATABASE="Enter database name [ai_job_assistant]: "
if "%PG_DATABASE%"=="" set PG_DATABASE=ai_job_assistant

echo.
echo Updating .env file...

REM Remove existing database configuration lines
findstr /V "USE_SQLITE" .env > .env.tmp
findstr /V "PG_HOST" .env.tmp > .env.tmp2
findstr /V "PG_PORT" .env.tmp2 > .env.tmp3
findstr /V "PG_USER" .env.tmp3 > .env.tmp4
findstr /V "PG_PASSWORD" .env.tmp4 > .env.tmp5
findstr /V "PG_DATABASE" .env.tmp5 > .env
del .env.tmp .env.tmp2 .env.tmp3 .env.tmp4 .env.tmp5 2>nul

REM Add PostgreSQL configuration
(
echo.
echo # Database Configuration - PostgreSQL
echo USE_SQLITE=false
echo PG_HOST=%PG_HOST%
echo PG_PORT=%PG_PORT%
echo PG_USER=%PG_USER%
echo PG_PASSWORD=%PG_PASSWORD%
echo PG_DATABASE=%PG_DATABASE%
) >> .env

echo.
echo ========================================
echo PostgreSQL Configuration Complete!
echo ========================================
echo.
echo Configuration added to .env file:
echo   USE_SQLITE=false
echo   PG_HOST=%PG_HOST%
echo   PG_PORT=%PG_PORT%
echo   PG_USER=%PG_USER%
echo   PG_PASSWORD=***hidden***
echo   PG_DATABASE=%PG_DATABASE%
echo.
echo IMPORTANT: Make sure you have created the database:
echo   psql -U postgres
echo   CREATE DATABASE %PG_DATABASE%;
echo   \q
echo.
pause
