"""
Environment Validation Script
Validates that all required environment variables are set in .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def validate_env():
    """
    Validate that required environment variables are set.
    
    Returns:
        tuple: (is_valid: bool, missing_vars: list, warnings: list)
    """
    # Load .env file
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        return False, [], [f".env file not found at {env_path}. Please create it from env_template.txt"]
    
    load_dotenv(env_path)
    
    missing_vars = []
    warnings = []
    
    # Required variables
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for AI features"
    }
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.strip() == "" or "your_" in value.lower():
            missing_vars.append(f"{var} - {description}")
    
    # Optional but recommended variables
    optional_vars = {
        "OPENAI_MODEL": "AI model to use (default: gpt-3.5-turbo)",
        "USE_SQLITE": "Database type (true for SQLite, false for PostgreSQL)",
    }
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value:
            warnings.append(f"{var} not set - {description} (will use default)")
    
    is_valid = len(missing_vars) == 0
    
    return is_valid, missing_vars, warnings


def print_validation_report():
    """Print a formatted validation report."""
    print("=" * 60)
    print("Environment Variables Validation")
    print("=" * 60)
    print()
    
    is_valid, missing, warnings = validate_env()
    
    if is_valid:
        print("✅ All required environment variables are set!")
    else:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print()
        print("Please update your .env file with the missing variables.")
        print("You can copy env_template.txt to .env and fill in the values.")
    
    if warnings:
        print()
        print("⚠️  Warnings (optional variables):")
        for warning in warnings:
            print(f"   - {warning}")
    
    print()
    print("=" * 60)
    
    return is_valid


if __name__ == "__main__":
    import sys
    is_valid = print_validation_report()
    sys.exit(0 if is_valid else 1)
