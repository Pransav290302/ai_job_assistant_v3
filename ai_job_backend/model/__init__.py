"""
Data Science Service Layer

Core agent components for backend integration:
- scrape_job_description: Scraper tool (URL -> job description text)
- analyze_resume_and_jd: Resume analyzer (resume + jd -> score, suggestions)
- analyze_resume_and_jd_full: Full workflow (resume + job_url or jd -> scrape if needed -> analyze)
- generate_tailored_answer: Tailored answer generator
"""

from model.answer_generator import AnswerGenerator, generate_tailored_answer
from model.mock_ai import get_mock_resume_analysis, get_mock_tailored_answer
from model.job_scraper import (
    JobScraper,
    scrape_job_description,
    scrape_job_description_async,
)
from model.resume_analyzer import analyze_resume_and_jd
from model.agents import analyze_resume_and_jd as analyze_resume_and_jd_full
from model.job_assistant_service import JobAssistantService
from model.api_integration import (
    get_service,
    analyze_resume_endpoint,
    generate_answer_endpoint,
    scrape_job_description_endpoint,
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
    "analyze_resume_and_jd_full",
    "JobAssistantService",
    "get_service",
    "analyze_resume_endpoint",
    "generate_answer_endpoint",
    "scrape_job_description_endpoint",
]
