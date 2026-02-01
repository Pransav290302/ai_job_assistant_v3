"""
Data Science API Routes
FastAPI routes for resume analysis, answer generation, and job scraping.
"""

import logging
import os
from typing import Dict, Optional
from pydantic import BaseModel, HttpUrl

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from model.api_integration import (
    analyze_resume_endpoint,
    generate_answer_endpoint,
    scrape_job_description_endpoint
)
from model.utils.config import get_config

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["model"])


# Request/Response Models
class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_url: str


class GenerateAnswerRequest(BaseModel):
    question: str
    user_profile: Dict
    job_url: str


class ScrapeJobRequest(BaseModel):
    job_url: str


class StatusResponse(BaseModel):
    status: str
    openai_configured: bool
    selenium_enabled: bool
    playwright_enabled: bool
    model: str


@router.post("/resume/analyze")
async def analyze_resume(request: ResumeAnalysisRequest) -> Dict:
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
        logger.info(f"Resume analysis request for job: {request.job_url}")
        result = analyze_resume_endpoint(
            resume_text=request.resume_text,
            job_url=request.job_url
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
async def generate_answer(request: GenerateAnswerRequest) -> Dict:
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
        logger.info(f"Answer generation request for job: {request.job_url}")
        result = generate_answer_endpoint(
            question=request.question,
            user_profile=request.user_profile,
            job_url=request.job_url
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Answer generation failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_answer endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.post("/job/scrape")
async def scrape_job(request: ScrapeJobRequest) -> Dict:
    """
    POST /api/job/scrape
    Scrapes a job description from a URL.
    
    Request body:
    {
        "job_url": "https://linkedin.com/jobs/..."
    }
    """
    try:
        logger.info(f"Job scraping request for: {request.job_url}")
        result = scrape_job_description_endpoint(request.job_url)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Scraping failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scrape_job endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.get("/status", response_model=StatusResponse)
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
