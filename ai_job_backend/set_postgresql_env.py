"""
PostgreSQL Environment Configuration Script
Non-interactive script to set PostgreSQL configuration in .env file.
"""

import os
import sys
from pathlib import Path

def configure_postgresql(
    password: str,
    host: str = "localhost",
    port: str = "5432",
    user: str = "postgres",
    database: str = "ai_job_assistant"
):
    """
    Configure PostgreSQL settings in .env file.
    
    Args:
        password: PostgreSQL password (required)
        host: PostgreSQL host (default: localhost)
        port: PostgreSQL port (default: 5432)
        user: PostgreSQL user (default: postgres)
        database: Database name (default: ai_job_assistant)
    """
    env_path = Path(__file__).parent / ".env"
    template_path = Path(__file__).parent / "env_template.txt"
    
    # Create .env from template if it doesn't exist
    if not env_path.exists():
        if template_path.exists():
            env_path.write_text(template_path.read_text())
            print(f"Created .env file from template")
        else:
            print("ERROR: env_template.txt not found!")
            return False
    
    # Read current .env
    lines = env_path.read_text().splitlines()
    
    # Remove existing database configuration
    new_lines = []
    skip_next = False
    for line in lines:
        line_stripped = line.strip()
        # Skip lines with database config
        if any(keyword in line_stripped for keyword in [
            "USE_SQLITE", "PG_HOST", "PG_PORT", 
            "PG_USER", "PG_PASSWORD", "PG_DATABASE"
        ]):
            continue
        # Skip empty lines before adding new config
        if line_stripped == "" and new_lines and new_lines[-1].strip() == "":
            continue
        new_lines.append(line)
    
    # Add PostgreSQL configuration
    new_lines.append("")
    new_lines.append("# Database Configuration - PostgreSQL")
    new_lines.append("USE_SQLITE=false")
    new_lines.append(f"PG_HOST={host}")
    new_lines.append(f"PG_PORT={port}")
    new_lines.append(f"PG_USER={user}")
    new_lines.append(f"PG_PASSWORD={password}")
    new_lines.append(f"PG_DATABASE={database}")
    
    # Write updated .env
    env_path.write_text("\n".join(new_lines) + "\n")
    
    print("=" * 60)
    print("PostgreSQL Configuration Complete!")
    print("=" * 60)
    print()
    print("Configuration added to .env file:")
    print(f"  USE_SQLITE=false")
    print(f"  PG_HOST={host}")
    print(f"  PG_PORT={port}")
    print(f"  PG_USER={user}")
    print(f"  PG_PASSWORD=***hidden***")
    print(f"  PG_DATABASE={database}")
    print()
    print("IMPORTANT: Make sure you have created the database:")
    print(f"  psql -U {user}")
    print(f"  CREATE DATABASE {database};")
    print("  \\q")
    print()
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("=" * 60)
        print("PostgreSQL Configuration Script")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python set_postgresql_env.py YOUR_POSTGRES_PASSWORD")
        print()
        print("Or with all options:")
        print("  python set_postgresql_env.py PASSWORD [HOST] [PORT] [USER] [DATABASE]")
        print()
        print("Example:")
        print("  python set_postgresql_env.py mypassword123")
        print("  python set_postgresql_env.py mypassword123 localhost 5432 postgres ai_job_assistant")
        print()
        sys.exit(1)
    
    password = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
    port = sys.argv[3] if len(sys.argv) > 3 else "5432"
    user = sys.argv[4] if len(sys.argv) > 4 else "postgres"
    database = sys.argv[5] if len(sys.argv) > 5 else "ai_job_assistant"
    
    success = configure_postgresql(password, host, port, user, database)
    sys.exit(0 if success else 1)
