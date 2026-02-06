"""
Database connection check script.

Run from ai_job_backend directory:
    python scripts/check_db.py

Uses the same configuration as the API (api/database): DATABASE_URL,
USE_SQLITE, or PG_* environment variables. See env_template.txt.
"""

import sys
from pathlib import Path

# Ensure backend root is on path when running as script
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

def main():
    from dotenv import load_dotenv
    load_dotenv(_backend_root / ".env")

    try:
        from sqlalchemy import text
        from api.database import engine
    except ImportError as e:
        print("Database connection failed: missing dependencies.")
        print("  ", e)
        print("Install them from ai_job_backend: pip install -r requirements.txt")
        print("If you use a virtual environment, activate it first (e.g. .venv\\Scripts\\activate on Windows).")
        sys.exit(1)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection OK (PostgreSQL/SQLite).")
    except Exception as e:
        print("Database connection failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
