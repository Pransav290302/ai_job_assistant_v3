"""
Data Science API Routes
FastAPI routes for resume analysis, answer generation, and job scraping.
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional  # noqa: F401 - Optional used in BaseModel

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl

from api.limiter import limiter
from model.api_integration import (
    analyze_resume_endpoint,
    extract_resume_profile_endpoint,
    generate_answer_endpoint,
    scrape_job_description_endpoint,
)
from model.utils.config import get_config

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["model"])


# 1 worker for free tier (demo) to save RAM; 2 for paid
_free_tier = os.getenv("FREE_TIER", "false").lower() == "true"
_executor = ThreadPoolExecutor(
    max_workers=1 if _free_tier else 2,
    thread_name_prefix="api",
)

# Request/Response Models - field constraints for production (prevent abuse)
MAX_RESUME_LEN = 50_000
MAX_JOB_DESC_LEN = 100_000
MAX_QUESTION_LEN = 2_000
MAX_URL_LEN = 2_048


class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(..., max_length=MAX_RESUME_LEN)
    job_url: Optional[str] = Field(None, max_length=MAX_URL_LEN)
    job_description: Optional[str] = Field(None, max_length=MAX_JOB_DESC_LEN)


class GenerateAnswerRequest(BaseModel):
    question: str = Field(..., max_length=MAX_QUESTION_LEN)
    user_profile: Dict
    job_url: Optional[str] = Field(None, max_length=MAX_URL_LEN)
    job_description: Optional[str] = Field(None, max_length=MAX_JOB_DESC_LEN)


class ScrapeJobRequest(BaseModel):
    job_url: Optional[str] = Field(None, max_length=MAX_URL_LEN)
    job_description: Optional[str] = Field(None, max_length=MAX_JOB_DESC_LEN)


class ExtractResumeRequest(BaseModel):
    resume_text: str = Field(..., max_length=MAX_RESUME_LEN)


class StatusResponse(BaseModel):
    status: str
    openai_configured: bool
    selenium_enabled: bool
    playwright_enabled: bool
    model: str


@router.post("/resume/analyze")
@limiter.limit("15/minute")
async def analyze_resume(req: Request, request: ResumeAnalysisRequest) -> Dict:
    """
    POST /api/resume/analyze
    Analyzes a resume against a job description.
    
    Request body:
    {
        "resume_text": "User's resume text...",
        "job_url": "https://linkedin.com/jobs/..."
    }
    """
    try:
        if not request.job_description and not request.job_url:
            raise HTTPException(status_code=400, detail="Provide job_url or job_description")
        logger.info(f"Resume analysis request for job: {request.job_url or 'pasted'}")
        loop = asyncio.get_event_loop()
        r = request
        result = await loop.run_in_executor(
            _executor,
            lambda: analyze_resume_endpoint(
                resume_text=r.resume_text,
                job_url=r.job_url,
                job_description=r.job_description,
            ),
        )
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Analysis failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_resume endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.post("/generate/answer")
@limiter.limit("15/minute")
async def generate_answer(req: Request, request: GenerateAnswerRequest) -> Dict:
    """
    POST /api/generate/answer
    Generates a tailored answer to an application question.
    
    Request body:
    {
        "question": "Why are you a good fit?",
        "user_profile": {
            "work_history": "...",
            "skills": ["...", "..."],
            "education": "...",
            "additional_info": "..."
        },
        "job_url": "https://linkedin.com/jobs/..."
    }
    """
    try:
        if not request.job_description and not request.job_url:
            raise HTTPException(status_code=400, detail="Provide job_url or job_description")
        logger.info(f"Answer generation request for job: {request.job_url or 'pasted'}")
        loop = asyncio.get_event_loop()
        r = request
        result = await loop.run_in_executor(
            _executor,
            lambda: generate_answer_endpoint(
                question=r.question,
                user_profile=r.user_profile,
                job_url=r.job_url,
                job_description=r.job_description,
            ),
        )
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Answer generation failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_answer endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.post("/resume/extract")
@limiter.limit("20/minute")
async def extract_resume_profile(req: Request, request: ExtractResumeRequest) -> Dict:
    """
    POST /api/resume/extract
    Extracts work_history, skills, education from resume text using AI.
    """
    try:
        result = extract_resume_profile_endpoint(request.resume_text)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Extraction failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in extract_resume_profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job/scrape")
@limiter.limit("15/minute")
async def scrape_job(req: Request, request: ScrapeJobRequest) -> Dict:
    """
    POST /api/job/scrape
    Scrapes a job description from a URL.
    
    Request body:
    {
        "job_url": "https://linkedin.com/jobs/..."
    }
    """
    try:
        if not request.job_url and not (request.job_description and len((request.job_description or "").strip()) >= 80):
            raise HTTPException(status_code=400, detail="Provide job_url or job_description (80+ chars)")
        logger.info(f"Job scraping request for: {request.job_url or 'pasted'}")
        job_url = request.job_url or "https://pasted-job-description"
        job_desc = request.job_description
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: scrape_job_description_endpoint(
                job_url=job_url,
                job_description=job_desc,
            ),
        )
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Scraping failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scrape_job endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.get("/status", response_model=StatusResponse)
@limiter.exempt
async def get_status() -> StatusResponse:
    """
    GET /api/status
    Get service status and configuration.
    """
    config = get_config()
    return StatusResponse(
        status='running',
        openai_configured=bool(config.OPENAI_API_KEY),
        selenium_enabled=config.USE_SELENIUM,
        playwright_enabled=config.USE_PLAYWRIGHT,
        model=config.OPENAI_MODEL
    )
