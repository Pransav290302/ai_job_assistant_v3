"""
Database configuration and session management.

- Keeps engine/session creation isolated from business logic.
- Uses env-driven PostgreSQL URL so it works locally and in production.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Database configuration - supports SQLite, PostgreSQL, and DATABASE_URL (Render/Heroku)
use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true"
database_url = os.getenv("DATABASE_URL")

if use_sqlite and not database_url:
    # Use SQLite for easier development setup
    SQLALCHEMY_DATABASE_URL = "sqlite:///./job_assistant.db"
elif database_url:
    # Production: use DATABASE_URL (e.g. from Render PostgreSQL add-on)
    # Render may pass postgres:// - SQLAlchemy expects postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = database_url
else:
    # PostgreSQL via individual env vars
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    database = os.getenv("PG_DATABASE", "ai_job_assistant")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Engine and session factory
# For SQLite, add connect_args to handle foreign keys
connect_args = {}
if use_sqlite:
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
