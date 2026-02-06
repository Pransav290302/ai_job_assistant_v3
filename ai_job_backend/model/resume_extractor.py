"""
Extract structured profile (work_history, skills, education) from raw resume text using AI.
"""

import json
import logging
import os
import re
from typing import Dict, Optional

from dotenv import load_dotenv
from model.utils.config import get_config

load_dotenv()
logger = logging.getLogger(__name__)


def extract_profile_from_resume(
    resume_text: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict:
    """
    Use AI to extract work_history, skills, education, additional_info from resume text.
    """
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not final_api_key:
        raise ValueError("OPENAI_API_KEY not found")

    config = get_config()
    client = config.create_openai_client(
        api_key=final_api_key,
        base_url=base_url or config.get_base_url(),
    )

    prompt = f"""Extract structured information from this resume. Return valid JSON only.

RESUME:
{resume_text[:6000]}

Return a JSON object with exactly these keys:
- "work_history": string - summary of work experience, roles, companies, dates
- "skills": string - comma-separated list of skills (e.g. "Python, SQL, Tableau")
- "education": string - degrees, institutions, GPA if mentioned
- "additional_info": string - certifications, projects, other relevant info (or empty string)

No markdown, no extra text. JSON only."""

    completion = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    response_text = completion.choices[0].message.content.strip()
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse extract response: {e}")
        raise ValueError("Could not parse resume structure from AI response") from e
    return {
        "work_history": str(data.get("work_history", "")),
        "skills": str(data.get("skills", "")),
        "education": str(data.get("education", "")),
        "additional_info": str(data.get("additional_info", "")),
    }
