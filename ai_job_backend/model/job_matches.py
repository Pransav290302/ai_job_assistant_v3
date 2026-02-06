"""
Job matching flow: profile from preferences DB + jobs from discover (or DB)
→ DeepSeek R1 ranks and explains. Used by API and SmolAgents.
"""

import logging
from typing import Any, Dict, List

from model.job_discovery import discover_jobs
from model.job_ranker import rank_jobs_with_reasoning
from model.profile_lookup import get_user_profile_from_db

logger = logging.getLogger(__name__)


def get_candidate_jobs_for_user(
    user_id: str,
    max_jobs: int = 20,
) -> Dict[str, Any]:
    """
    Get user profile from DB (preferences: skills, experience, interests) and
    fetch candidate jobs from discover (Indeed) using profile as query/location.

    Returns:
        {"profile": {...}, "jobs": [...], "query": "...", "location": "..."}
    """
    profile = get_user_profile_from_db(user_id.strip())
    if profile.get("error"):
        return {"profile": profile, "jobs": [], "query": "", "location": "", "error": profile["error"]}

    query = (profile.get("current_title") or "software engineer").strip() or "software engineer"
    if profile.get("skills"):
        query = f"{query} {profile.get('skills', '')}".strip()
    location = (profile.get("location") or "").strip()

    result = discover_jobs(query=query, location=location, max_results=max_jobs)
    jobs = result.get("jobs") or []
    return {
        "profile": profile,
        "jobs": jobs,
        "query": result.get("query") or query,
        "location": result.get("location") or location,
        "error": None,
    }


def rank_jobs_for_user(
    user_id: str,
    max_jobs: int = 20,
    max_ranked: int = 15,
) -> Dict[str, Any]:
    """
    Full flow: get profile from preferences DB, get candidate jobs (discover),
    ask DeepSeek R1 to reason and return ranked jobs + explanations.

    Returns:
        {
            "ranked_jobs": [{"rank": 1, "title": "...", "company": "...", "explanation": "...", "score": 8, "url": "..."}, ...],
            "reasoning": "Overall reasoning from the model.",
            "profile_summary": {...},
            "query": "...",
            "location": "...",
            "error": null or str
        }
    """
    out = get_candidate_jobs_for_user(user_id, max_jobs=max_jobs)
    profile = out.get("profile") or {}
    jobs = out.get("jobs") or []
    if out.get("error"):
        return {
            "ranked_jobs": [],
            "reasoning": "",
            "profile_summary": profile,
            "query": out.get("query") or "",
            "location": out.get("location") or "",
            "error": out["error"],
        }
    if not jobs:
        return {
            "ranked_jobs": [],
            "reasoning": "No jobs found for your profile. Try updating preferences or location.",
            "profile_summary": profile,
            "query": out.get("query") or "",
            "location": out.get("location") or "",
            "error": None,
        }
    try:
        rank_result = rank_jobs_with_reasoning(profile, jobs, max_results=max_ranked)
        return {
            "ranked_jobs": rank_result.get("ranked_jobs") or [],
            "reasoning": rank_result.get("reasoning") or "",
            "profile_summary": profile,
            "query": out.get("query") or "",
            "location": out.get("location") or "",
            "error": None,
        }
    except Exception as e:
        logger.exception("rank_jobs_for_user failed")
        return {
            "ranked_jobs": [],
            "reasoning": "",
            "profile_summary": profile,
            "query": out.get("query") or "",
            "location": out.get("location") or "",
            "error": str(e),
        }
