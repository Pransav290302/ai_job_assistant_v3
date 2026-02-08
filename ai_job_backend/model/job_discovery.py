import logging
import os
from datetime import date, datetime
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


JOOBLE_API_BASE = "https://jooble.org/api"

JOOBLE_MAX_REQUESTS_PER_DAY = 500
JOOBLE_MAX_REQUESTS_PER_CALL = 2
JOOBLE_RESULTS_PER_PAGE = 20


MAX_QUERY_LEN = 80
MAX_LOCATION_LEN = 60

_jooble_usage: Dict[str, Any] = {"date": "", "count": 0}


def _jooble_usage_check() -> bool:
    today = date.today().isoformat()
    if _jooble_usage["date"] != today:
        _jooble_usage["date"] = today
        _jooble_usage["count"] = 0
    return _jooble_usage["count"] < JOOBLE_MAX_REQUESTS_PER_DAY


def _jooble_usage_increment(by: int = 1) -> None:
    _jooble_usage["count"] = _jooble_usage.get("count", 0) + by


def _jooble_usage_remaining() -> int:
    today = date.today().isoformat()
    if _jooble_usage["date"] != today:
        return JOOBLE_MAX_REQUESTS_PER_DAY
    return max(0, JOOBLE_MAX_REQUESTS_PER_DAY - _jooble_usage["count"])


def discover_jooble(
    query: str,
    location: str = "",
    max_results: int = 60,
) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    key = (os.getenv("JOOBLE_API_KEY") or "").strip()
    if not key:
        logger.warning("JOOBLE_API_KEY not set. Get one at https://jooble.org/api/about")
        return jobs

    remaining = _jooble_usage_remaining()
    if remaining <= 0:
        logger.warning("Jooble daily limit (%d) reached. Skipping until next day.", JOOBLE_MAX_REQUESTS_PER_DAY)
        return jobs

    q = ((query or "").strip() or "jobs")[:MAX_QUERY_LEN]
    loc = ((location or "").strip())[:MAX_LOCATION_LEN]
    url = f"{JOOBLE_API_BASE}/{key}"

    requests_to_make = min(JOOBLE_MAX_REQUESTS_PER_CALL, (max_results + JOOBLE_RESULTS_PER_PAGE - 1) // JOOBLE_RESULTS_PER_PAGE)
    requests_to_make = min(requests_to_make, remaining)

    for page in range(1, requests_to_make + 1):
        if not _jooble_usage_check():
            break
        body: Dict[str, Any] = {
            "keywords": q,
            "location": loc or "Remote",
            "page": str(page),
            "ResultOnPage": str(JOOBLE_RESULTS_PER_PAGE),
            "companysearch": "false",
        }
        try:
            r = requests.post(url, json=body, timeout=15, headers={"Content-Type": "application/json"})
            _jooble_usage_increment(1)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 403:
                logger.warning("Jooble API 403: invalid or expired API key.")
            else:
                logger.warning("Jooble API request failed: %s", e)
            break
        except Exception as e:
            logger.warning("Jooble API request failed: %s", e)
            break

        raw_jobs = data.get("jobs") or []
        for j in raw_jobs:
            if len(jobs) >= max_results:
                break
            title = (j.get("title") or "Job")[:200]
            company = (j.get("company") or "")[:150]
            link = (j.get("link") or "").strip()
            if not link:
                continue
            snippet = (j.get("snippet") or "")[:500]
            jobs.append({
                "title": title,
                "company": company,
                "url": link,
                "snippet": snippet,
                "source": "jooble",
                "location": (j.get("location") or "")[:120],
                "type": (j.get("type") or "")[:50],
                "salary": (j.get("salary") or "")[:80],
            })

        if len(raw_jobs) < JOOBLE_RESULTS_PER_PAGE:
            break

    if jobs:
        logger.info("Jooble returned %d jobs (daily usage: %d/%d)", len(jobs), _jooble_usage.get("count", 0), JOOBLE_MAX_REQUESTS_PER_DAY)
    return jobs[:max_results]


def discover_jobs(
    query: str,
    location: str = "",
    max_results: int = 60,
) -> Dict[str, Any]:
    jobs = discover_jooble(query=query, location=location, max_results=max_results)
    remaining = _jooble_usage_remaining()

    return {
        "success": True,
        "jobs": jobs,
        "query": query,
        "location": location or "(any)",
        "source": "jooble" if jobs else "none",
        "sources": ["jooble"] if jobs else [],
        "jooble_remaining": remaining,
    }
