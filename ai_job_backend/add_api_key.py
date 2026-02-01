"""
Quick script to add API key to .env file
Usage: python add_api_key.py YOUR_API_KEY_HERE
"""

import sys
from pathlib import Path

def add_api_key(api_key):
    """Add API key to .env file"""
    if not api_key:
        print("Error: No API key provided")
        print("Usage: python add_api_key.py YOUR_API_KEY_HERE")
        return False
    
    # Validate key format (OpenAI keys start with sk-)
    if not api_key.startswith('sk-'):
        print("Warning: OpenAI API keys usually start with 'sk-'. Please verify your key.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return False
    
    # Create .env file content (OpenAI API)
    env_content = f"""# OpenAI API Configuration
OPENAI_API_KEY={api_key}
OPENAI_MODEL=gpt-3.5-turbo
# Optional: Use a different base URL if using OpenAI-compatible API
# OPENAI_BASE_URL=https://api.openai.com/v1

# Scraper Configuration
USE_SELENIUM=false
SELENIUM_HEADLESS=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/job_assistant.log

# API Configuration
API_TIMEOUT=30

# Server Configuration
PORT=8000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000

# Database Configuration (PostgreSQL)
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
PG_DATABASE=ai_job_assistant

# Auth Configuration
AUTH_SECRET_KEY=change-me-in-prod-secret-key-here
AUTH_ALGORITHM=HS256
"""
    
    # Write to .env file
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("=" * 60)
    print("SUCCESS! API key has been saved to .env file")
    print("=" * 60)
    print(f"\nKey saved: {api_key[:10]}...{api_key[-4:]}")
    print("\nYou can now use the AI features:")
    print("- Resume Analysis")
    print("- Tailored Answer Generation")
    print("- Job Description Analysis")
    print("\nRestart the server if it's already running to load the new key.")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        api_key = sys.argv[1].strip()
        add_api_key(api_key)
    else:
        print("=" * 60)
        print("OpenAI API Key Setup")
        print("=" * 60)
        print()
        print("To get your OpenAI API key:")
        print("1. Go to: https://platform.openai.com")
        print("2. Sign up or log in")
        print("3. Navigate to: https://platform.openai.com/api-keys")
        print("4. Click 'Create new secret key'")
        print("5. Copy the key (you'll only see it once!)")
        print()
        print("=" * 60)
        print()
        print("Usage:")
        print("  python add_api_key.py YOUR_API_KEY_HERE")
        print()
        print("Or create a .env file manually with:")
        print("  OPENAI_API_KEY=your_key_here")
        print("  OPENAI_MODEL=gpt-3.5-turbo")
        print()
