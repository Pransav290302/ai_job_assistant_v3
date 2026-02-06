"""
Job matching flow: profile from preferences DB + jobs from discover (or DB)
→ DeepSeek R1 ranks and explains. Used by API and SmolAgents.
"""

import logging
from typing import Any, Dict, List, Tuple

from model.job_discovery import discover_jobs
from model.job_ranker import rank_jobs_with_reasoning
from model.profile_lookup import get_user_profile_from_db

logger = logging.getLogger(__name__)

# Max lengths for discovery URLs. Job boards and ScraperAPI expect short search terms;
# long URLs cause 500 errors (URI length limits).
MAX_DISCOVERY_QUERY_LEN = 80
MAX_DISCOVERY_LOCATION_LEN = 60


def _discovery_query_and_location(profile: Dict[str, Any]) -> Tuple[str, str]:
    """
    Build a short, discovery-friendly query and location from profile.
    Job boards (and ScraperAPI) expect human-style short phrases, not long
    comma-separated lists — long URLs cause 500/414 errors.
    """
    roles = profile.get("current_title") or ""
    if isinstance(roles, list):
        roles = (roles[0] or "software engineer") if roles else "software engineer"
    roles = (roles or "software engineer").strip() or "software engineer"
    skills = (profile.get("skills") or "").strip()
    # One short phrase: prefer first role, optionally add first skill or two
    if skills:
        parts = [s.strip() for s in skills.split(",") if s.strip()][:2]
        query = f"{roles} {' '.join(parts)}".strip()[:MAX_DISCOVERY_QUERY_LEN]
    else:
        query = roles[:MAX_DISCOVERY_QUERY_LEN]
    query = query or "software engineer"

    loc_raw = (profile.get("location") or "").strip()
    if not loc_raw:
        return query, ""
    # Single location or "Remote" when many — job boards don't support 15 cities in one search
    if "," in loc_raw:
        parts = [p.strip() for p in loc_raw.split(",") if p.strip()]
        if any("remote" in p.lower() for p in parts):
            location = "Remote"
        else:
            location = (parts[0] or loc_raw)[:MAX_DISCOVERY_LOCATION_LEN]
    else:
        location = loc_raw[:MAX_DISCOVERY_LOCATION_LEN]
    return query, location


def get_candidate_jobs_for_user(
    user_id: str,
    max_jobs: int = 60,
) -> Dict[str, Any]:
    """
    Get user profile from DB (preferences: skills, experience, interests) and
    fetch candidate jobs from discover (ZipRecruiter + DailyAIJobs + AIWorkPortal).

    Returns:
        {"profile": {...}, "jobs": [...], "query": "...", "location": "..."}
    """
    profile = get_user_profile_from_db(user_id.strip())
    if profile.get("error"):
        return {"profile": profile, "jobs": [], "query": "", "location": "", "error": profile["error"]}

    # Use short, discovery-friendly query/location so URLs stay within safe length (avoid ScraperAPI 500)
    query, location = _discovery_query_and_location(profile)

    result = discover_jobs(query=query, location=location, max_results=max_jobs)
    jobs = result.get("jobs") or []

    # Fallback: if ZipRecruiter returns no results, try broader search
    if not jobs:
        fallback_query = "software engineer" if query != "software engineer" else "developer"
        logger.info("ZipRecruiter returned 0 jobs for query=%r location=%r; trying fallback query=%r", query, location, fallback_query)
        fallback = discover_jobs(query=fallback_query, location="", max_results=max_jobs)
        jobs = fallback.get("jobs") or []
        if jobs:
            result = fallback
            query = fallback_query
            location = ""

    return {
        "profile": profile,
        "jobs": jobs,
        "query": result.get("query") or query,
        "location": result.get("location") or location,
        "error": None,
    }


def rank_jobs_for_user(
    user_id: str,
    max_jobs: int = 60,
    max_ranked: int = 50,
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
        query_used = out.get("query") or ""
        location_used = out.get("location") or "(any)"
        reasoning = (
            f"No jobs found for your profile. "
            f"Search used: \"{query_used}\" in \"{location_used}\". "
            "ZipRecruiter may have returned no listings. "
            "Try updating your preferences (roles/location) or try again later."
        )
        logger.warning("rank_jobs_for_user: no jobs from discover (query=%s, location=%s)", query_used, location_used)
        return {
            "ranked_jobs": [],
            "reasoning": reasoning,
            "profile_summary": profile,
            "query": query_used,
            "location": location_used,
            "error": None,
        }
    try:
        rank_result = rank_jobs_with_reasoning(profile, jobs, max_results=max_ranked)
        ranked_jobs = rank_result.get("ranked_jobs") or []
        reasoning = rank_result.get("reasoning") or ""
        # If LLM returned no ranked jobs but we have discoveries, pass them through so frontend shows them
        if not ranked_jobs and jobs:
            logger.info("Ranker returned 0 jobs; passing through %d discovered jobs so frontend can display them", len(jobs))
            ranked_jobs = [
                {
                    "rank": i,
                    "job_index": i - 1,
                    "title": j.get("title") or "Job",
                    "company": j.get("company") or "",
                    "url": j.get("url") or j.get("source_url") or "",
                    "snippet": j.get("snippet") or j.get("description") or "",
                    "location": j.get("location") or "",
                    "explanation": "",
                    "score": None,
                }
                for i, j in enumerate(jobs[:max_ranked], 1)
            ]
            if not reasoning:
                reasoning = f"Showing {len(ranked_jobs)} jobs from ZipRecruiter (ranking skipped)."
        return {
            "ranked_jobs": ranked_jobs,
            "reasoning": reasoning,
            "profile_summary": profile,
            "query": out.get("query") or "",
            "location": out.get("location") or "",
            "error": None,
        }
    except Exception as e:
        logger.exception("rank_jobs_for_user failed")
        # On ranker failure, still return discovered jobs so frontend can show them
        if jobs:
            logger.info("Passing through %d discovered jobs after ranker error", len(jobs))
            ranked_jobs = [
                {
                    "rank": i,
                    "job_index": i - 1,
                    "title": j.get("title") or "Job",
                    "company": j.get("company") or "",
                    "url": j.get("url") or j.get("source_url") or "",
                    "snippet": j.get("snippet") or j.get("description") or "",
                    "location": j.get("location") or "",
                    "explanation": "",
                    "score": None,
                }
                for i, j in enumerate(jobs[:max_ranked], 1)
            ]
            return {
                "ranked_jobs": ranked_jobs,
                "reasoning": f"Showing discovered jobs (ranking failed: {e}).",
                "profile_summary": profile,
                "query": out.get("query") or "",
                "location": out.get("location") or "",
                "error": None,
            }
        return {
            "ranked_jobs": [],
            "reasoning": "",
            "profile_summary": profile,
            "query": out.get("query") or "",
            "location": out.get("location") or "",
            "error": str(e),
        }
