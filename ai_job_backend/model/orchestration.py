"""
Agent orchestration for the AI Job Assistant (Senior Data Scientist todo).
Complete workflows: scrape -> prompt -> LLM -> parse -> validate.
"""

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

from dotenv import load_dotenv

from model.prompts import format_tailored_answer_prompt

if TYPE_CHECKING:
    from openai import OpenAI
from model.resume_analyzer import analyze_resume_and_jd as _analyze_resume_and_jd
from model.utils.config import get_config

load_dotenv()
logger = logging.getLogger(__name__)


def _get_llm_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> tuple["OpenAI", str]:
    """Return (OpenAI client, model). Uses Azure ML DeepSeek-R1."""
    config = get_config()
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not found. Set it in .env or pass api_key.")
    client = config.create_openai_client(
        api_key=key,
        base_url=base_url or config.get_base_url(),
    )
    return client, config.OPENAI_MODEL


def analyze_resume_and_jd(
    resume_text: str,
    job_url: Optional[str] = None,
    job_description: Optional[str] = None,
    llm_client: Any = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Complete workflow for resume vs job analysis.

    Steps:
    1. Scrape job description (if job_url provided and no job_description).
    2. Call resume_analyzer.analyze_resume_and_jd (prompt -> LLM -> parse -> validate).
    3. Return ResumeScoreOutput.

    Args:
        resume_text: User's resume text.
        job_url: URL of job posting (used if job_description not provided).
        job_description: Optional. If provided (e.g. pasted), skip scrape.
        llm_client: Unused; resume_analyzer uses config. Kept for API compatibility.
        api_key, base_url: Passed to resume_analyzer when llm_client is None.

    Returns:
        Validated ResumeScoreOutput dict (score, match_percentage, suggestions, etc.).
    """
    logger.info("Starting resume analysis workflow")
    # Step 1: Get job description
    if job_description and len(job_description.strip()) >= 80:
        jd_text = job_description.strip()
        logger.info(f"Using provided job description ({len(jd_text)} chars)")
    elif job_url:
        from model.job_scraper import scrape_job_description
        from model.utils.config import get_config
        config = get_config()
        jd_text = scrape_job_description(
            job_url,
            use_selenium=False,
            use_playwright=bool(config.BROWSERLESS_URL),
            scraper_api_key=None,
        )
        logger.info(f"Scraped job description ({len(jd_text)} chars)")
    else:
        raise ValueError("Provide job_url or job_description")
    # Step 2 & 3: Analyze (prompt -> LLM -> parse -> validate in resume_analyzer)
    return _analyze_resume_and_jd(
        resume_text=resume_text,
        job_description=jd_text,
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        base_url=base_url or get_config().get_base_url(),
    )


def generate_tailored_answer(
    user_profile: Dict[str, Any],
    job_description: str,
    question: str,
    llm_client: Any = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
) -> str:
    """
    Complete workflow for generating a tailored application answer.

    Steps:
    1. Format user_profile as string for prompt.
    2. Format prompt from prompts.TAILORED_ANSWER_PROMPT.
    3. Call LLM.
    4. Return answer text.

    Args:
        user_profile: Dict with work_history, skills, education, etc. (can be loose format).
        job_description: Job description text.
        question: Application question (e.g. "Why are you a good fit?").
        llm_client: Optional OpenAI-compatible client.
        api_key, base_url: Used when llm_client is None.
        temperature: LLM temperature (default 0.7 for creative answers).

    Returns:
        Generated answer string.
    """
    logger.info("Starting tailored answer workflow")
    try:
        # Serialize profile for prompt
        work = user_profile.get("work_history", "")
        if isinstance(work, list):
            work = "\n".join(str(x) for x in work)
        skills = user_profile.get("skills", [])
        if isinstance(skills, list):
            skills = ", ".join(str(s) for s in skills)
        education = user_profile.get("education", "")
        if isinstance(education, list):
            education = "\n".join(str(x) for x in education)
        profile_str = (
            f"Work History: {work}\n"
            f"Skills: {skills}\n"
            f"Education: {education}\n"
            f"Additional: {user_profile.get('additional_info', '')}"
        )

        prompt = format_tailored_answer_prompt(profile_str, job_description, question)

        if llm_client is not None:
            if hasattr(llm_client, "chat") and hasattr(llm_client.chat, "completions"):
                completion = llm_client.chat.completions.create(
                    model=get_config().OPENAI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                )
            else:
                raise ValueError("llm_client must have chat.completions.create")
        else:
            client, model = _get_llm_client(api_key=api_key, base_url=base_url)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )

        answer = completion.choices[0].message.content.strip()
        logger.info(f"Tailored answer generated ({len(answer)} chars)")
        return answer

    except Exception as e:
        logger.error(f"Tailored answer failed: {e}", exc_info=True)
        raise ValueError(f"Failed to generate answer: {e}") from e
