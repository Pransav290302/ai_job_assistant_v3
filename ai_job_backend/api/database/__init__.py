import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true"
database_url = os.getenv("DATABASE_URL")

if use_sqlite and not database_url:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./job_assistant.db"
elif database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = database_url
else:
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    database = os.getenv("PG_DATABASE", "ai_job_assistant")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

connect_args = {}
engine_kwargs = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Lighter pool for free tier (Vercel/Render/Supabase demo)
    free_tier = os.getenv("FREE_TIER", "false").lower() == "true"
    pool_size = 2 if free_tier else 5
    max_overflow = 3 if free_tier else 10
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": pool_size,
        "max_overflow": max_overflow,
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
