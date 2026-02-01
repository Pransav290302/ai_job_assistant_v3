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
            llm_model=config.OPENAI_MODEL,
            llm_api_key=config.OPENAI_API_KEY,
            llm_base_url=config.OPENAI_BASE_URL
        )
    
    return _service_instance


def analyze_resume_endpoint(resume_text: str, job_url: str) -> Dict:
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
        result = service.analyze_resume(resume_text, job_url)
        return result
    except Exception as e:
        logger.error(f"Error in analyze_resume_endpoint: {str(e)}")
        return {
            'success': False,
            'error': f"Internal server error: {str(e)}"
        }


def generate_answer_endpoint(question: str, user_profile: Dict, job_url: str) -> Dict:
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
        result = service.generate_answer(question, user_profile, job_url)
        return result
    except Exception as e:
        logger.error(f"Error in generate_answer_endpoint: {str(e)}")
        return {
            'success': False,
            'error': f"Internal server error: {str(e)}"
        }


def scrape_job_description_endpoint(job_url: str) -> Dict:
    """
    API endpoint function for scraping job descriptions.
    This function can be called directly from FastAPI routes.
    
    Args:
        job_url: URL of the job posting
        
    Returns:
        Dictionary with scraped job description or error information
        
    Example FastAPI route:
        @router.post("/scrape/job")
        async def scrape_job(data: ScrapeRequest):
            result = scrape_job_description_endpoint(data.job_url)
            return result
    """
    logger.info(f"Scrape job description endpoint called for: {job_url}")
    
    try:
        config = get_config()
        text = scrape_job_description(job_url, use_selenium=config.USE_SELENIUM)
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
