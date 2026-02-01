"""
Tailored Answer Generator Agent
Generates personalized answers to application questions based on user profile and job description.
"""

import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    AI agent that generates tailored answers to job application questions.
    Acts as a career coach to help users write compelling responses.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7, 
                 api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the answer generator.
        
        Args:
            model_name: Model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (higher = more creative)
            api_key: API key (if None, reads from environment)
            base_url: Base URL for API (if None, uses OpenAI default)
        """
        # Use OpenAI client (defaults to https://api.openai.com/v1 if base_url not provided)
        final_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not final_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file: "
                "OPENAI_API_KEY=your_api_key_here"
            )
        
        self.client = OpenAI(
            api_key=final_api_key,
            base_url=base_url or os.getenv("OPENAI_BASE_URL"),  # None = use OpenAI default
        )
        self.model_name = model_name
        self.temperature = temperature
        
        self.system_prompt = """You are an expert career coach helping job applicants write compelling, 
personalized answers to application questions. Your goal is to help the applicant stand out by 
connecting their unique background, skills, and experiences to the specific job requirements.

Guidelines:
1. Be authentic and specific - reference actual experiences from their profile
2. Connect their background directly to the job requirements
3. Use concrete examples and achievements
4. Show enthusiasm and genuine interest
5. Keep the tone professional but personable
6. Aim for 2-4 paragraphs (approximately 150-300 words)

Write a compelling answer that would make a hiring manager want to interview this candidate."""
    
    def generate(self, question: str, user_profile: Dict, job_description: str) -> str:
        """
        Generate a tailored answer to an application question.
        
        Args:
            question: The application question (e.g., "Why are you a good fit?")
            user_profile: Dictionary with user profile data (work_history, skills, education, etc.)
            job_description: The job description text
            
        Returns:
            Generated answer text
        """
        logger.info(f"Generating tailored answer for question: {question[:50]}...")
        
        try:
            # Extract profile information
            work_history = user_profile.get('work_history', 'Not provided')
            skills = user_profile.get('skills', [])
            if isinstance(skills, list):
                skills = ', '.join(skills)
            education = user_profile.get('education', 'Not provided')
            additional_info = user_profile.get('additional_info', '')
            
            # Format the user prompt
            user_prompt = f"""Generate a tailored answer to this application question:

QUESTION: {question}

USER PROFILE:
- Work History: {work_history}
- Skills: {skills}
- Education: {education}
- Additional Info: {additional_info if additional_info else 'None'}

JOB DESCRIPTION:
{job_description}

Write a compelling, personalized answer that connects the user's background to this specific role."""
            
            # Call OpenAI API using the same pattern as the backend
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
            )
            
            answer = completion.choices[0].message.content.strip()
            
            logger.info(f"Generated answer ({len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise ValueError(f"Failed to generate answer: {str(e)}")


def generate_tailored_answer(question: str, user_profile: Dict, job_description: str,
                            model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None,
                            base_url: Optional[str] = None) -> str:
    """
    Convenience function for generating tailored answers.
    
    Args:
        question: The application question
        user_profile: Dictionary with user profile data
        job_description: The job description text
        model_name: Model to use (default: gpt-3.5-turbo)
        api_key: API key (optional, reads from environment if not provided)
        base_url: Base URL for API (optional, uses OpenAI default if not provided)
        
    Returns:
        Generated answer text
    """
    generator = AnswerGenerator(model_name=model_name, api_key=api_key, base_url=base_url)
    return generator.generate(question, user_profile, job_description)
