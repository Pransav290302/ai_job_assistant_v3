"""
Backend API Integration
Helper functions for integrating with FastAPI backend.
These functions can be directly imported and called by the backend server.
"""

import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from model.job_assistant_service import JobAssistantService
from model.job_scraper import scrape_job_description
from model.resume_analyzer import analyze_resume_and_jd
from model.resume_extractor import extract_profile_from_resume
from model.answer_generator import generate_tailored_answer
from model.utils.config import Config, get_config
from model.utils.logging_config import setup_logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = setup_logging()

# Initialize service (can be reused across requests)
_service_instance: Optional[JobAssistantService] = None


def get_service() -> JobAssistantService:
    """
    Get or create the service instance (singleton pattern for efficiency).
    
    Returns:
        JobAssistantService instance
    """
    global _service_instance
    
    if _service_instance is None:
        config = get_config()
        _service_instance = JobAssistantService(
            use_selenium=config.USE_SELENIUM,
            use_playwright=config.USE_PLAYWRIGHT,
            llm_api_key=config.OPENAI_API_KEY,
            llm_base_url=config.get_base_url()
        )
    
    return _service_instance


def analyze_resume_endpoint(
    resume_text: str,
    job_url: Optional[str] = None,
    job_description: Optional[str] = None,
) -> Dict:
    """
    API endpoint function for resume analysis.
    This function can be called directly from FastAPI routes.
    
    Args:
        resume_text: User's resume text
        job_url: URL of the job posting
        
    Returns:
        Dictionary with analysis results or error information
        
    Example FastAPI route:
        @router.post("/resume/analyze")
        async def analyze_resume(data: ResumeAnalysisRequest):
            result = analyze_resume_endpoint(
                resume_text=data.resume_text,
                job_url=data.job_url
            )
            return result
    """
    logger.info("Resume analysis endpoint called")
    
    try:
        service = get_service()
        result = service.analyze_resume(
            resume_text=resume_text,
            job_url=job_url,
            job_description=job_description,
        )
        return result
    except Exception as e:
        logger.error(f"Error in analyze_resume_endpoint: {str(e)}")
        return {
            'success': False,
            'error': f"Internal server error: {str(e)}"
        }


def generate_answer_endpoint(
    question: str,
    user_profile: Dict,
    job_url: Optional[str] = None,
    job_description: Optional[str] = None,
) -> Dict:
    """
    API endpoint function for generating tailored answers.
    This function can be called directly from FastAPI routes.
    
    Args:
        question: Application question
        user_profile: Dictionary with user profile data
        job_url: URL of the job posting
        
    Returns:
        Dictionary with generated answer or error information
        
    Example FastAPI route:
        @router.post("/generate/answer")
        async def generate_answer(data: AnswerRequest):
            result = generate_answer_endpoint(
                question=data.question,
                user_profile=data.user_profile,
                job_url=data.job_url
            )
            return result
    """
    logger.info("Generate answer endpoint called")
    
    try:
        service = get_service()
        result = service.generate_answer(
            question=question,
            user_profile=user_profile,
            job_url=job_url,
            job_description=job_description,
        )
        return result
    except Exception as e:
        logger.error(f"Error in generate_answer_endpoint: {str(e)}")
        return {
            'success': False,
            'error': f"Internal server error: {str(e)}"
        }


def extract_resume_profile_endpoint(resume_text: str) -> Dict:
    """Extract work_history, skills, education from resume text using AI."""
    logger.info("Extract resume profile endpoint called")
    try:
        profile = extract_profile_from_resume(resume_text)
        return {"success": True, **profile}
    except Exception as e:
        logger.error(f"Error in extract_resume_profile_endpoint: {str(e)}")
        return {"success": False, "error": str(e)}


def scrape_job_description_endpoint(job_url: str) -> Dict:
    """
    Scrape job description from Indeed or Glassdoor URL (LinkedIn not supported).
    """
    logger.info(f"Scrape job description endpoint called for: {job_url}")
    
    try:
        config = get_config()
        url_lower = job_url.lower()
        if "linkedin.com" in url_lower:
            return {
                "success": False,
                "error": "LinkedIn is not supported. Use Indeed or Glassdoor job URLs.",
                "url": job_url,
            }
        needs_js = "glassdoor.com" in url_lower
        scraper_key = os.getenv("SCRAPER_API_KEY") or getattr(config, "SCRAPER_API_KEY", None)
        has_js_option = config.BROWSERLESS_URL or scraper_key
        if needs_js and not has_js_option:
            return {
                "success": False,
                "error": (
                    "Glassdoor needs JS rendering. Set SCRAPER_API_KEY (scraperapi.com) or "
                    "BROWSERLESS_URL (wss://chrome.browserless.io?token=YOUR_TOKEN). Or use Indeed URLs."
                ),
                "url": job_url,
            }
        text = scrape_job_description(
            job_url,
            use_selenium=False,
            use_playwright=bool(config.BROWSERLESS_URL),
            scraper_api_key=scraper_key,
        )
        return {
            'success': True,
            'text': text,
            'url': job_url
        }
    except Exception as e:
        logger.error(f"Error in scrape_job_description_endpoint: {str(e)}")
        return {
            'success': False,
            'error': f"Failed to scrape job description: {str(e)}",
            'url': job_url
        }
