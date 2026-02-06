import logging
import os
import sys
import asyncio
import time
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api import models
from api.limiter import limiter
from api.database import engine
from api.routes import agent, auth, jobs, health, model, users

# Force Windows-specific event loop policy for Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
APP_PORT = int(os.getenv("PORT", 8000))

_request_log = logging.getLogger("api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each request: method, path, status_code, duration."""

    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        _request_log.info(
            "request %s %s -> %s %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


app = FastAPI(title="AI Job Application Assistant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(health.router)
app.include_router(users.router)
app.include_router(model.router)
app.include_router(agent.router)

# Configure CORS – allow Vercel (*.vercel.app) + explicit origins from env
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
_allowed = os.getenv("ALLOWED_ORIGINS", _frontend_url)
allow_origins = [o.strip() for o in _allowed.split(",") if o.strip()]
# Regex: any *.vercel.app (production + preview deployments)
_vercel_regex = r"^https://[a-zA-Z0-9][a-zA-Z0-9-]*\.vercel\.app$"
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=_vercel_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Database tables
models.Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_checks():
    """Logging setup and production config validation."""
    from model.utils.logging_config import setup_logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    setup_logging(log_level=log_level, log_file=log_file)
    if os.getenv("RENDER"):
        secret = os.getenv("AUTH_SECRET_KEY", "")
        if not secret or secret == "change-me-in-prod":
            logging.getLogger("uvicorn.error").warning(
                "AUTH_SECRET_KEY not set or using default. Set it in Render Dashboard."
            )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)