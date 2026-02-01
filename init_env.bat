@echo off
echo ========================================
echo Initializing Environment Files
echo ========================================
echo.

cd ai_job_backend
if not exist .env (
    if exist env_template.txt (
        copy env_template.txt .env >nul
        echo [OK] Created .env file from template
        echo.
        echo IMPORTANT: Please edit .env and add your API keys:
        echo   - AZURE_DEEPSEEK_API_KEY
        echo   - AZURE_DEEPSEEK_ENDPOINT
        echo.
        echo You can also run: python add_api_key.py YOUR_KEY
    ) else (
        echo [X] env_template.txt not found
    )
) else (
    echo [OK] .env file already exists
)
cd ..

cd ai_job_frontend
if not exist .env.local (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
    echo [OK] Created .env.local file
    echo.
    echo IMPORTANT: Add Supabase configuration to .env.local:
    echo   - NEXT_PUBLIC_SUPABASE_URL
    echo   - NEXT_PUBLIC_SUPABASE_ANON_KEY
) else (
    echo [OK] .env.local file already exists
)
cd ..

echo.
echo ========================================
echo Environment files initialized!
echo ========================================
pause
