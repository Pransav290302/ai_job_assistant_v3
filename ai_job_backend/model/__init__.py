"""
Data Science Service Layer

This module contains all data science and AI-related services.
"""

from datascientist.answer_generator import AnswerGenerator, generate_tailored_answer
from datascientist.mock_ai import get_mock_resume_analysis, get_mock_tailored_answer
from datascientist.job_scraper import (
    JobScraper,
    scrape_job_description,
    scrape_job_description_async
)
from datascientist.resume_analyzer import analyze_resume_and_jd
from datascientist.job_assistant_service import JobAssistantService
from datascientist.api_integration import (
    get_service,
    analyze_resume_endpoint,
    generate_answer_endpoint,
    scrape_job_description_endpoint
)

__all__ = [
    "AnswerGenerator", 
    "generate_tailored_answer",
    "get_mock_resume_analysis",
    "get_mock_tailored_answer",
    "JobScraper",
    "scrape_job_description",
    "scrape_job_description_async",
    "analyze_resume_and_jd",
    "JobAssistantService",
    "get_service",
    "analyze_resume_endpoint",
    "generate_answer_endpoint",
    "scrape_job_description_endpoint"
]
