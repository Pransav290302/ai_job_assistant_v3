"""
Job Assistant Agent – core agentic pattern: agent uses tools to interact with the world.

Key tools:
  1. Web scraper – get job posting data from URL
  2. Database function – retrieve user profile from DB

Install: pip install "smolagents[openai]"
"""

import json
import os
from typing import Any, Dict, Optional

try:
    from smolagents import OpenAIModel, ToolCallingAgent, tool
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    SMOLAGENTS_AVAILABLE = False
    tool = None  # type: ignore


def is_smolagents_available() -> bool:
    return SMOLAGENTS_AVAILABLE


def _get_config() -> Any:
    from model.utils.config import get_config
    return get_config()


# ---- Tools (wrap existing model logic) ----

if SMOLAGENTS_AVAILABLE:

    @tool
    def scrape_job(job_url: str) -> str:
        """
        Web scraper: fetch job description from Indeed or Glassdoor job URL (LinkedIn not supported).
        Use before analyzing resume or generating answers.

        Args:
            job_url: Full URL of the job posting (e.g. https://indeed.com/viewjob?jk=... or https://glassdoor.com/...)
        """
        from model.job_scraper import scrape_job_description
        import os as _os
        config = _get_config()
        scraper_key = _os.getenv("SCRAPER_API_KEY") or getattr(config, "SCRAPER_API_KEY", None)
        try:
            text = scrape_job_description(
                job_url,
                use_selenium=False,
                use_playwright=bool(config.BROWSERLESS_URL),
                scraper_api_key=scraper_key,
            )
            return text[:15000] if text else "Could not fetch job description."
        except Exception as e:
            return f"Scrape failed: {str(e)}"

    @tool
    def get_user_profile(user_id: str) -> str:
        """
        Database function: retrieve a user's profile from the database.
        Returns work history, skills, education, and preferences (roles, locations).
        Use this when you need the user's saved profile for tailored answers or autofill.
        If the user provided resume text in their message, you may use extract_profile instead.

        Args:
            user_id: The user's ID (Supabase auth UUID, e.g. from the task context).
        """
        from model.profile_lookup import get_user_profile_from_db
        try:
            out = get_user_profile_from_db(user_id.strip())
            return json.dumps(out, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def analyze_resume(resume_text: str, job_description: str) -> str:
        """
        Compare a resume against a job description and return a match score plus suggestions.
        Provide the raw job description text (e.g. from scrape_job).

        Args:
            resume_text: The candidate's resume text (plain or pasted).
            job_description: The full job description text to match against.
        """
        from model.resume_analyzer import analyze_resume_and_jd
        try:
            out = analyze_resume_and_jd(
                resume_text=resume_text[:4000],
                job_description=job_description[:4000],
            )
            return json.dumps(out, indent=2)
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    @tool
    def extract_profile(resume_text: str) -> str:
        """
        Extract structured profile (work history, skills, education) from resume text.
        Use this to get a profile for generate_answer or to auto-fill forms.

        Args:
            resume_text: The candidate's resume text (plain or pasted).
        """
        from model.resume_extractor import extract_profile_from_resume
        try:
            out = extract_profile_from_resume(resume_text[:6000])
            return json.dumps(out, indent=2)
        except Exception as e:
            return f"Profile extraction failed: {str(e)}"

    @tool
    def generate_answer(
        question: str,
        work_history: str,
        skills: str,
        education: str,
        job_description: str,
    ) -> str:
        """
        Generate a tailored answer to an application question using the candidate's
        profile and the job description. Use for questions like "Why are you a good fit?"
        or "What is your biggest strength?"

        Args:
            question: The application question.
            work_history: Candidate's work history (text).
            skills: Candidate's skills (comma-separated or short text).
            education: Candidate's education (text).
            job_description: The job description text (e.g. from scrape_job).
        """
        from model.answer_generator import generate_tailored_answer
        profile = {
            "work_history": work_history,
            "skills": skills,
            "education": education,
            "additional_info": "",
        }
        try:
            return generate_tailored_answer(
                question=question,
                user_profile=profile,
                job_description=job_description[:4000],
            )
        except Exception as e:
            return f"Answer generation failed: {str(e)}"

    @tool
    def rank_jobs_for_user(user_id: str) -> str:
        """
        Get the user's profile from the preferences DB (skills, experience, interests),
        fetch candidate jobs from the job database (Indeed discover), then use DeepSeek R1
        to reason and return ranked jobs with explanations. Use when the user asks for
        job recommendations, best matches, or "rank jobs for me".

        Args:
            user_id: The user's ID (Supabase auth UUID). Must be provided in the task context.
        """
        from model.job_matches import rank_jobs_for_user as rank_jobs_for_user_impl
        try:
            result = rank_jobs_for_user_impl(user_id.strip(), max_jobs=20, max_ranked=15)
            if result.get("error"):
                return f"Ranking failed: {result['error']}"
            lines = []
            if result.get("reasoning"):
                lines.append(f"Overall reasoning: {result['reasoning']}\n")
            for r in result.get("ranked_jobs") or []:
                lines.append(
                    f"#{r.get('rank', '?')} {r.get('title', '—')} @ {r.get('company', '—')} "
                    f"(score: {r.get('score', '—')})\n{r.get('explanation', '')}\n{r.get('url', '')}"
                )
            return "\n".join(lines) if lines else "No ranked jobs returned."
        except Exception as e:
            return f"Rank jobs failed: {str(e)}"


def run_job_assistant_agent(
    task: str,
    model_id: Optional[str] = None,
    api_base: Optional[str] = None,
    api_key: Optional[str] = None,
    verbosity_level: int = 1,
) -> Dict[str, Any]:
    """
    Run the SmolAgents job assistant agent on a natural-language task.
    The agent can scrape job URLs, analyze resume vs job, and generate tailored answers.

    Args:
        task: User request, e.g. "Scrape https://linkedin.com/jobs/... and analyze my resume against it."
        model_id: Model/deployment name (default: OPENAI_MODEL).
        api_base: OpenAI-compatible base URL (default: OPENAI_BASE_URL).
        api_key: API key (default: OPENAI_API_KEY).
        verbosity_level: 0=quiet, 1=normal, 2=verbose.

    Returns:
        {"success": True, "output": "..."} or {"success": False, "error": "..."}.
    """
    if not SMOLAGENTS_AVAILABLE:
        return {
            "success": False,
            "error": "SmolAgents not installed. Run: pip install \"smolagents[openai]\"",
        }
    config = _get_config()
    if not config.OPENAI_API_KEY and not api_key:
        return {"success": False, "error": "OPENAI_API_KEY not set."}
    model = OpenAIModel(
        model_id=model_id or config.OPENAI_MODEL,
        api_base=api_base or config.get_base_url() or "https://api.openai.com/v1",
        api_key=api_key or config.OPENAI_API_KEY,
        temperature=0.3,
        max_tokens=4096,
    )
    agent = ToolCallingAgent(
        tools=[scrape_job, get_user_profile, analyze_resume, extract_profile, generate_answer, rank_jobs_for_user],
        model=model,
        verbosity_level=verbosity_level,
    )
    try:
        output = agent.run(task)
        return {"success": True, "output": str(output) if output else ""}
    except Exception as e:
        err_msg = str(e).strip() or repr(e) or (type(e).__name__ + " (no message)")
        return {"success": False, "error": err_msg}
