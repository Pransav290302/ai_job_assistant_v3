"""
Job discovery: fetch jobs from ZipRecruiter only.
"""

import logging
import os
from typing import Any, Dict, List
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# --- ZipRecruiter ---
ZIPRECRUITER_SEARCH_BASE = "https://www.ziprecruiter.com/jobs-search"


def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def _fetch_html(url: str, session: requests.Session | None = None, use_js_render: bool = False) -> str:
    """
    Fetch HTML for a URL. If SCRAPER_API_KEY is set, proxy through ScraperAPI to avoid 403/blocking.
    """
    sess = session or _make_session()
    scraper_key = os.getenv("SCRAPER_API_KEY")
    if scraper_key:
        try:
            api_url = (
                "http://api.scraperapi.com"
                f"?api_key={scraper_key}&url={quote_plus(url)}"
            )
            if use_js_render:
                api_url += "&render=true"
            r = sess.get(api_url, timeout=60)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning("ScraperAPI fetch failed for %s: %s", url[:80], e)
            return ""
    try:
        r = sess.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.warning("Direct fetch failed for %s: %s", url[:80], e)
        return ""


def discover_ziprecruiter(
    query: str,
    location: str = "",
    max_results: int = 20,
    session: requests.Session | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch job listings from ZipRecruiter search.
    Returns list of {title, company, url, snippet, source}.
    """
    jobs: List[Dict[str, Any]] = []
    q = (query or "").strip() or "jobs"
    loc = (location or "").strip()
    params: Dict[str, str] = {"search": q}
    if loc:
        params["location"] = loc
    url = ZIPRECRUITER_SEARCH_BASE + "?" + "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
    sess = session or _make_session()
    html = _fetch_html(url, session=sess, use_js_render=True)
    if not html:
        logger.warning("ZipRecruiter discovery: no HTML. Set SCRAPER_API_KEY for JS sites.")
        return jobs
    soup = BeautifulSoup(html, "html.parser")

    for a in soup.select('a[href*="/job/"], a[href*="/jobs/"], a[data-job-id]'):
        if len(jobs) >= max_results:
            break
        href = a.get("href") or ""
        if not href.startswith("http"):
            href = urljoin("https://www.ziprecruiter.com", href)
        title = (a.get_text(strip=True) or "Job")[:200]
        if len(title) < 2:
            continue
        jobs.append({
            "title": title,
            "company": "",
            "url": href,
            "snippet": "",
            "source": "ziprecruiter",
        })
    return jobs[:max_results]


def discover_jobs(
    query: str,
    location: str = "",
    max_results: int = 20,
) -> Dict[str, Any]:
    """
    Discover jobs from ZipRecruiter only.
    Returns { success, jobs, query, location, source }.
    """
    sess = _make_session()
    jobs = discover_ziprecruiter(query=query, location=location, max_results=max_results, session=sess)
    if jobs:
        logger.info("ZipRecruiter returned %d jobs", len(jobs))
    else:
        logger.warning("ZipRecruiter returned 0 jobs for query=%r location=%r. Set SCRAPER_API_KEY for JS sites.", query, location)

    return {
        "success": True,
        "jobs": jobs[:max_results],
        "query": query,
        "location": location or "(any)",
        "source": "ziprecruiter",
    }
