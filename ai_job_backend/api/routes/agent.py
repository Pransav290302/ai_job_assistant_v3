"""
Agent API Routes
Agentic flow: perceive goal → reason → take actions (scraper, LLM) to achieve it.
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from api.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["agent"])

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="agent")
MAX_TASK_LEN = 4_000
MAX_RESUME_LEN = 50_000


class AgentRunRequest(BaseModel):
    """Natural-language task for the agent to accomplish."""
    task: str = Field(..., max_length=MAX_TASK_LEN, description="Goal, e.g. 'Scrape this job URL and analyze my resume against it'")
    resume_text: str | None = Field(None, max_length=MAX_RESUME_LEN, description="Optional resume text for analyze/extract tasks")
    user_id: str | None = Field(None, max_length=64, description="Optional user ID for get_user_profile tool (Supabase auth UUID)")


@router.post("/agent/run")
@limiter.limit("5/minute")
async def run_agent(req: Request, request: AgentRunRequest) -> dict:
    """
    POST /api/agent/run
    Run the AI agent on a natural-language task. The agent perceives the goal,
    reasons about which tools to use (scraper, resume analyzer, answer generator),
    and takes actions to achieve it.
    
    Example tasks:
    - "Scrape https://linkedin.com/jobs/123 and analyze my resume against it"
    - "Extract my profile from my resume"
    - "Generate an answer to 'Why are you a good fit?' for job at [URL]"
    """
    try:
        from model.agents import run_job_assistant_agent, is_smolagents_available
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Agent not available. Install: pip install \"smolagents[openai]\"",
        )
    
    if not is_smolagents_available():
        raise HTTPException(
            status_code=503,
            detail="Agent framework not installed. Run: pip install \"smolagents[openai]\"",
        )
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY not set. Agent requires LLM.",
        )
    
    # Build task with optional resume and user context (for get_user_profile tool)
    task_text = request.task.strip()
    if request.resume_text and request.resume_text.strip():
        resume_preview = request.resume_text.strip()[:6000]
        task_text = f"My resume text:\n{resume_preview}\n\nTask: {task_text}"
    if request.user_id and request.user_id.strip():
        task_text = f"User ID (use get_user_profile to fetch my profile): {request.user_id.strip()}\n\n{task_text}"
    
    task_lower = request.task.strip().lower()
    if "linkedin.com" in task_lower:
        raise HTTPException(
            status_code=400,
            detail="LinkedIn is not supported. Use Indeed or Glassdoor job URLs, or paste the job description.",
        )
    has_browserless = bool(os.getenv("BROWSERLESS_URL"))
    has_scraper_api = bool(os.getenv("SCRAPER_API_KEY"))
    if "glassdoor.com" in task_lower and not has_browserless and not has_scraper_api:
        raise HTTPException(
            status_code=400,
            detail=(
                "Glassdoor needs JS rendering. Set SCRAPER_API_KEY or BROWSERLESS_URL in backend .env, "
                "or use Indeed URLs / paste the job description."
            ),
        )
    logger.info("Agent task: %s", request.task[:100])

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        _executor,
        lambda: run_job_assistant_agent(task=task_text),
    )

    if not result.get("success"):
        err = (result.get("error") or "").strip()
        if not err:
            err = "Agent failed (no error message from agent). Check OPENAI_API_KEY and scraper config."
        raise HTTPException(status_code=500, detail=err)

    return {
        "success": True,
        "output": result.get("output", ""),
    }
