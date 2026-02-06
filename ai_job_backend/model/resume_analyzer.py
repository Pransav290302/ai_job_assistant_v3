"""
Resume Analyzer Agent
Analyzes resume against job description to provide match score and suggestions.
"""

import json
import logging
import os
import re
from typing import Dict, Optional

from dotenv import load_dotenv

from model.utils.config import get_config

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def analyze_resume_and_jd(
    resume_text: str,
    job_description: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> Dict:
    """
    Analyze resume against job description. Uses Azure ML DeepSeek-R1.
    
    Args:
        resume_text: User's resume text
        job_description: Job description text
        api_key: API key (optional, reads from environment if not provided)
        base_url: Base URL for API (optional)
        
    Returns:
        Dictionary with analysis results including:
        - score: Match score (0-100)
        - suggestions: List of improvement suggestions
        - strengths: List of strengths
        - missing_skills: List of missing skills
        - match_percentage: Match percentage as float
    """
    logger.info("Analyzing resume against job description...")
    
    try:
        # Initialize OpenAI client (defaults to https://api.openai.com/v1 if base_url not provided)
        final_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not final_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file: "
                "OPENAI_API_KEY=your_api_key_here"
            )
        
        config = get_config()
        client = config.create_openai_client(
            api_key=final_api_key,
            base_url=base_url or config.get_base_url(),
        )
        system_prompt = """You are an expert resume reviewer and career advisor. Analyze a resume against a job description and provide:
1. A match score from 0-100
2. Specific strengths that align with the job
3. Missing skills or experiences
4. Actionable suggestions for improvement

Be specific and constructive in your feedback."""
        
        user_prompt = f"""Analyze this resume against the job description:

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{job_description[:4000]}

Provide a JSON response with:
- "score": integer 0-100
- "suggestions": array of strings (3-5 items)
- "strengths": array of strings (3-5 items)
- "missing_skills": array of strings (up to 5 items)
- "match_percentage": float (same as score)

Format your response as valid JSON only."""
        
        completion = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Extract JSON from response (in case there's extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        analysis = json.loads(response_text)
        
        # Ensure all required fields exist
        result = {
            "score": analysis.get("score", 0),
            "suggestions": analysis.get("suggestions", []),
            "strengths": analysis.get("strengths", []),
            "missing_skills": analysis.get("missing_skills", []),
            "match_percentage": float(analysis.get("match_percentage", analysis.get("score", 0)))
        }
        
        logger.info(f"Resume analysis complete. Score: {result['score']}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        # Fallback: return basic structure
        return {
            "score": 70,
            "suggestions": ["Review the analysis response format"],
            "strengths": ["Analysis completed"],
            "missing_skills": [],
            "match_percentage": 70.0
        }
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise ValueError(f"Failed to analyze resume: {str(e)}")
