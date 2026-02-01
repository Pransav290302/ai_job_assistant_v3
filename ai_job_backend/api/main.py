import os
import sys
import asyncio
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import models
from api.database import engine
from api.routes import auth, jobs, health, model

# Force Windows-specific event loop policy for Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()
APP_PORT = int(os.getenv("PORT", 8000))

app = FastAPI(title="AI Job Application Assistant")
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(health.router)
app.include_router(model.router)

# Configure CORS – localhost + Vercel production and preview URLs
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
_allowed = os.getenv("ALLOWED_ORIGINS", _frontend_url)
allow_origins = [o.strip() for o in _allowed.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database tables
models.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)