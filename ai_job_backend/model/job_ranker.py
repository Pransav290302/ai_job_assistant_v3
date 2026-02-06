"""
Rank jobs using DeepSeek R1: profile (skills, experience, interests from preferences DB)
+ candidate jobs → LLM reasons and returns ranked jobs with explanations.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List

from model.utils.config import get_config

logger = logging.getLogger(__name__)


def _build_profile_summary(profile: Dict[str, Any]) -> str:
    """Turn profile dict into a short text summary for the prompt."""
    parts = []
    if profile.get("current_title") or profile.get("work_history"):
        parts.append(f"Roles/Experience: {profile.get('current_title') or profile.get('work_history') or '—'}")
    if profile.get("skills"):
        parts.append(f"Skills: {profile.get('skills', '')}")
    if profile.get("location"):
        parts.append(f"Location: {profile.get('location', '')}")
    if profile.get("education"):
        parts.append(f"Education: {profile.get('education', '')}")
    interests = profile.get("interests") or profile.get("industries_prefer") or []
    if interests:
        i_str = ", ".join(str(x) for x in interests) if isinstance(interests, list) else str(interests)
        parts.append(f"Interests/Industries: {i_str}")
    return "\n".join(parts) if parts else "No profile details."


def _jobs_to_text(jobs: List[Dict[str, Any]]) -> str:
    """Format jobs list for the prompt."""
    lines = []
    for i, j in enumerate(jobs, 1):
        title = j.get("title") or "—"
        company = j.get("company") or "—"
        loc = j.get("location") or ""
        snippet = (j.get("snippet") or j.get("description") or "")[:300]
        url = j.get("url") or j.get("source_url") or ""
        lines.append(f"[{i}] {title} @ {company} {loc}\n{snippet}\n{url}")
    return "\n\n".join(lines)


def rank_jobs_with_reasoning(
    profile: Dict[str, Any],
    jobs: List[Dict[str, Any]],
    max_results: int = 15,
) -> Dict[str, Any]:
    """
    Use DeepSeek R1 to rank jobs by fit with the user's profile (skills, experience, interests).
    Returns ranked list with explanations.

    Args:
        profile: From get_user_profile_from_db (current_title, skills, location, work_history, etc.).
        jobs: List of job dicts (title, company, url, snippet, location).
        max_results: Max number of ranked jobs to return.

    Returns:
        {
            "ranked_jobs": [{"rank": 1, "job_index": 0, "title": "...", "company": "...", "explanation": "..."}, ...],
            "reasoning": "Short overall reasoning from the model.",
            "raw_response": "..." (if parsing failed, for debugging)
        }
    """
    if not jobs:
        return {"ranked_jobs": [], "reasoning": "No jobs to rank.", "raw_response": ""}

    config = get_config()
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Cannot call DeepSeek R1.")

    profile_summary = _build_profile_summary(profile)
    jobs_text = _jobs_to_text(jobs[:50])  # cap for context

    system = (
        "You are a job-matching expert. Given a candidate's profile (roles, skills, experience, interests) "
        "and a list of job postings, rank the jobs by fit and explain why each is a good or poor match. "
        "Respond with valid JSON only, no markdown code fences."
    )
    user = f"""CANDIDATE PROFILE:
{profile_summary}

JOBS (numbered 1 to N):
{jobs_text}

Return a JSON object with exactly:
1) "reasoning": a short paragraph (1-3 sentences) explaining your overall ranking logic.
2) "ranked": an array of objects, one per job you recommend (top {max_results} max), each with:
   - "index": the job number (1-based) from the list above
   - "title": job title
   - "company": company name
   - "explanation": 1-2 sentences why this job fits (or doesn't) the candidate
   - "score": number 1-10 (10 = best fit)

Example format: {{"reasoning": "...", "ranked": [{{"index": 2, "title": "...", "company": "...", "explanation": "...", "score": 8}}, ...]}}
"""

    try:
        client = config.create_openai_client()
        completion = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        raw = (completion.choices[0].message.content or "").strip()
    except Exception as e:
        logger.error("DeepSeek R1 rank call failed: %s", e, exc_info=True)
        raise ValueError(f"LLM call failed: {e}") from e

    # Parse JSON (allow wrapped in ```json ... ```)
    json_str = raw
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        json_str = m.group(1).strip()
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        logger.warning("Rank response was not valid JSON, returning raw.")
        return {
            "ranked_jobs": [],
            "reasoning": raw[:500] if raw else "No parseable response.",
            "raw_response": raw,
        }

    reasoning = data.get("reasoning") or ""
    ranked = data.get("ranked") or []
    ranked_jobs = []
    for i, r in enumerate(ranked[:max_results], 1):
        idx = r.get("index") or (i + 1)
        job_idx = int(idx) - 1 if isinstance(idx, (int, float)) else i - 1
        orig = jobs[job_idx] if 0 <= job_idx < len(jobs) else {}
        ranked_jobs.append({
            "rank": i,
            "job_index": job_idx,
            "title": r.get("title") or orig.get("title") or "—",
            "company": r.get("company") or orig.get("company") or "—",
            "url": orig.get("url") or orig.get("source_url") or "",
            "snippet": orig.get("snippet") or orig.get("description") or "",
            "location": orig.get("location") or "",
            "explanation": r.get("explanation") or "",
            "score": r.get("score"),
        })

    return {
        "ranked_jobs": ranked_jobs,
        "reasoning": reasoning,
        "raw_response": "",
    }
