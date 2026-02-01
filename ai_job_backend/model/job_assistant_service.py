"""
Job Assistant Service
High-level service that orchestrates scraping and AI agent workflows.
"""

import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from model.job_scraper import JobScraper, scrape_job_description
from model.resume_analyzer import analyze_resume_and_jd
from model.answer_generator import generate_tailored_answer

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class JobAssistantService:
    """
    Main service class that coordinates job scraping and AI agent operations.
    This is the primary interface for backend integration.
    """
    
    def __init__(self, use_selenium: bool = False, use_playwright: bool = True, llm_model: str = "gpt-3.5-turbo",
                 llm_api_key: Optional[str] = None, llm_base_url: Optional[str] = None):
        """
        Initialize the job assistant service.
        
        Args:
            use_selenium: Whether to use Selenium for scraping
            use_playwright: Whether to use Playwright (works on Render free tier)
            llm_model: Model name (default: gpt-3.5-turbo)
            llm_api_key: API key (optional, reads from env if not provided)
            llm_base_url: Base URL for API (optional, uses OpenAI default if not provided)
        """
        self.scraper = JobScraper(use_selenium=use_selenium, use_playwright=use_playwright)
        self.llm_model = llm_model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        # Use provided API key or get from environment
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.llm_base_url = llm_base_url or os.getenv("OPENAI_BASE_URL")
        
        # Validate API key is available
        if not self.llm_api_key:
            logger.warning(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in your .env file: OPENAI_API_KEY=your_api_key_here"
            )
    
    def analyze_resume(self, resume_text: str, job_url: str) -> Dict:
        """
        Complete workflow: scrape job description and analyze resume.
        
        Args:
            resume_text: User's resume text
            job_url: URL of the job posting
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting resume analysis workflow for job: {job_url}")
        
        # Step 1: Scrape job description
        scrape_result = self.scraper.scrape(job_url)
        
        if not scrape_result['success']:
            logger.error(f"Failed to scrape job description from {job_url}")
            return {
                'success': False,
                'error': f"Failed to scrape job description: {scrape_result.get('error', 'Unknown error')}",
                'job_url': job_url
            }
        
        job_description = scrape_result['text']
        logger.info(f"Successfully scraped job description ({len(job_description)} characters)")
        
        # Step 2: Analyze resume against job description
        try:
            analysis = analyze_resume_and_jd(
                resume_text=resume_text,
                job_description=job_description,
                model_name=self.llm_model,
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            logger.info(f"Resume analysis complete. Score: {analysis.get('score', 'N/A')}")
            
            return {
                'success': True,
                'analysis': analysis,
                'job_description': job_description,
                'job_url': job_url
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"OpenAI API error: {error_msg}. Using mock response for demo.")
            
            # Use mock response if API fails (for demo/presentation)
            if 'quota' in error_msg.lower() or '429' in error_msg or 'insufficient' in error_msg.lower():
                from model.mock_ai import get_mock_resume_analysis
                logger.info("Using mock analysis for demonstration")
                analysis = get_mock_resume_analysis(resume_text, job_description)
                return {
                    'success': True,
                    'analysis': analysis,
                    'job_description': job_description,
                    'job_url': job_url,
                    'demo_mode': True,
                    'note': 'Using mock analysis due to API quota limits'
                }
            
            logger.error(f"Error during resume analysis: {error_msg}")
            return {
                'success': False,
                'error': f"Resume analysis failed: {error_msg}",
                'job_url': job_url
            }
    
    def generate_answer(self, question: str, user_profile: Dict, job_url: str) -> Dict:
        """
        Complete workflow: scrape job description and generate tailored answer.
        
        Args:
            question: Application question
            user_profile: User profile dictionary
            job_url: URL of the job posting
            
        Returns:
            Dictionary with generated answer
        """
        logger.info(f"Starting answer generation workflow for job: {job_url}")
        
        # Step 1: Scrape job description
        scrape_result = self.scraper.scrape(job_url)
        
        if not scrape_result['success']:
            logger.error(f"Failed to scrape job description from {job_url}")
            return {
                'success': False,
                'error': f"Failed to scrape job description: {scrape_result.get('error', 'Unknown error')}",
                'job_url': job_url
            }
        
        job_description = scrape_result['text']
        logger.info(f"Successfully scraped job description ({len(job_description)} characters)")
        
        # Step 2: Generate tailored answer
        try:
            answer = generate_tailored_answer(
                question=question,
                user_profile=user_profile,
                job_description=job_description,
                model_name=self.llm_model,
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            logger.info(f"Answer generation complete ({len(answer)} characters)")
            
            return {
                'success': True,
                'answer': answer,
                'question': question,
                'job_url': job_url
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"OpenAI API error: {error_msg}. Using mock response for demo.")
            
            # Use mock response if API fails (for demo/presentation)
            if 'quota' in error_msg.lower() or '429' in error_msg or 'insufficient' in error_msg.lower():
                from model.mock_ai import get_mock_tailored_answer
                logger.info("Using mock answer for demonstration")
                answer = get_mock_tailored_answer(question, user_profile, job_description)
                return {
                    'success': True,
                    'answer': answer,
                    'question': question,
                    'job_url': job_url,
                    'demo_mode': True,
                    'note': 'Using mock answer due to API quota limits'
                }
            
            logger.error(f"Error during answer generation: {error_msg}")
            return {
                'success': False,
                'error': f"Answer generation failed: {error_msg}",
                'job_url': job_url
            }
    
    def close(self):
        """Clean up resources."""
        self.scraper.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
