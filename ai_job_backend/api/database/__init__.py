"""
Database configuration for AI Job Assistant backend.

Supports:
1. DATABASE_URL - full connection string (Render, Supabase, etc.)
2. PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE, PG_PORT - separate vars (avoids password URL encoding)

On Render: DATABASE_URL or PG_* must be set in Render Dashboard → Environment.
Never defaults to localhost on Render.
"""
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

_RENDER = os.getenv("RENDER", "").lower() in ("true", "1", "yes")
use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true"
database_url = os.getenv("DATABASE_URL", "").strip()

# Build connection URL
if use_sqlite and not database_url:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./job_assistant.db"
elif database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = database_url
else:
    pg_host = os.getenv("PG_HOST", "").strip()
    pg_user = os.getenv("PG_USER", "postgres")
    pg_password = os.getenv("PG_PASSWORD", "")
    pg_database = os.getenv("PG_DATABASE", "postgres")
    pg_port = os.getenv("PG_PORT", "5432")

    # On Render: require explicit DB config; never use localhost
    if _RENDER and (not pg_host or pg_host == "localhost"):
        raise RuntimeError(
            "Database not configured on Render. Set either:\n"
            "  • DATABASE_URL = your Supabase/Postgres connection string\n"
            "  • PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE (e.g. Supabase: "
            "PG_HOST=db.YOUR-PROJECT.supabase.co, PG_USER=postgres)\n"
            "Add in Render Dashboard → Your Service → Environment."
        )
    if _RENDER and pg_host and not pg_password:
        raise RuntimeError(
            "PG_PASSWORD is required when using PG_* on Render. "
            "Set PG_PASSWORD in Render Dashboard → Environment."
        )

    # Local dev: allow localhost
    if not pg_host:
        pg_host = "localhost"
        pg_database = pg_database or "ai_job_assistant"

    # URL-encode password to handle special chars (@, :, /, etc.)
    safe_password = quote_plus(pg_password) if pg_password else ""
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{pg_user}:{safe_password}@{pg_host}:{pg_port}/{pg_database}"
    )

# Engine config
connect_args = {}
engine_kwargs = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    free_tier = os.getenv("FREE_TIER", "false").lower() == "true"
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 2 if free_tier else 5,
        "max_overflow": 3 if free_tier else 10,
        "pool_recycle": 300,
        "pool_timeout": 30,
    }

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
