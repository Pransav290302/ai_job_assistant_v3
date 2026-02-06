"""
Job discovery: fetch jobs from ZipRecruiter, DailyAIJobs.com, and AIWorkPortal.com.
Free scraping (no paid APIs); use SCRAPER_API_KEY for JS-rendered sites if needed.
"""

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# --- ZipRecruiter ---
ZIPRECRUITER_SEARCH_BASE = "https://www.ziprecruiter.com/jobs-search"
ZIPRECRUITER_BASE = "https://www.ziprecruiter.com"

# --- Daily AI Jobs (dailyaijobs.com) ---
DAILYAIJOBS_BASE = "https://www.dailyaijobs.com"
DAILYAIJOBS_JOBS_PATH = "/"  # homepage and JS-loaded listings

# --- AI Work Portal (aiworkportal.com) ---
AIWORKPORTAL_BASE = "https://aiworkportal.com"
AIWORKPORTAL_JOBS_PATH = "/jobs"

# Cap query/location length so the ZipRecruiter URL (and thus ScraperAPI request) stays under
# server URI limits. Long URLs cause ScraperAPI 500 and job boards don't support huge search strings.
MAX_QUERY_LEN = 80
MAX_LOCATION_LEN = 60

# Only include jobs posted within this many days (filter out old / no-longer-accepting listings).
MAX_JOB_AGE_DAYS = 7


def _parse_posted_days_ago(text: str) -> Optional[int]:
    """
    Parse "posted X days ago" / "1 week ago" / "X hours ago" from card text.
    Returns approximate days ago, or None if not found / unknown.
    """
    if not text:
        return None
    text = text.lower().strip()
    # "X hours ago" -> 0 days (today)
    m = re.search(r"(\d+)\s*hours?\s*ago", text)
    if m:
        return 0
    if "today" in text or "just now" in text:
        return 0
    # "X days ago"
    m = re.search(r"(\d+)\s*days?\s*ago", text)
    if m:
        return min(int(m.group(1)), 999)
    # "1 week ago" -> 7
    if re.search(r"1\s*week\s*ago", text):
        return 7
    # "X weeks ago"
    m = re.search(r"(\d+)\s*weeks?\s*ago", text)
    if m:
        return int(m.group(1)) * 7
    # "1 month ago" or "X months ago"
    m = re.search(r"(\d+)\s*months?\s*ago", text)
    if m:
        return int(m.group(1)) * 30
    return None


def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def _fetch_html(
    url: str,
    session: Optional[requests.Session] = None,
    use_js_render: bool = False,
    instruction_set: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 60,
) -> str:
    """
    Fetch HTML for a URL. If SCRAPER_API_KEY is set, proxy through ScraperAPI.
    instruction_set: optional ScraperAPI render instructions (e.g. [{"type":"wait","value":10}]).
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
            headers = {}
            if instruction_set and use_js_render:
                headers["x-sapi-instruction_set"] = json.dumps(instruction_set)
            r = sess.get(api_url, timeout=timeout, headers=headers or None)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning("ScraperAPI fetch failed for %s: %s", url[:80], e)
            return ""
    try:
        r = sess.get(url, timeout=min(20, timeout))
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
    Query and location are capped so the request URL stays within safe length (avoids ScraperAPI 500).
    Returns list of {title, company, url, snippet, source}.
    """
    jobs: List[Dict[str, Any]] = []
    q = ((query or "").strip() or "jobs")[:MAX_QUERY_LEN]
    loc = ((location or "").strip())[:MAX_LOCATION_LEN]
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
        card_text = ""
        parent = a.parent
        for _ in range(5):
            if parent is None:
                break
            card_text = (parent.get_text(separator=" ", strip=True) or "")[:500]
            if "ago" in card_text.lower():
                break
            parent = getattr(parent, "parent", None)
        posted_days = _parse_posted_days_ago(card_text)
        if posted_days is not None and posted_days > MAX_JOB_AGE_DAYS:
            continue
        title = (a.get_text(strip=True) or "Job")[:200]
        if len(title) < 2:
            continue
        job = {"title": title, "company": "", "url": href, "snippet": "", "source": "ziprecruiter"}
        if posted_days is not None:
            job["posted_days_ago"] = posted_days
        jobs.append(job)
    return jobs[:max_results]


def discover_dailyaijobs(
    query: str = "",
    max_results: int = 50,
    session: requests.Session | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch AI/ML/Data job listings from dailyaijobs.com (free).
    Site is JS-heavy; use SCRAPER_API_KEY with render=true for best results.
    Returns list of {title, company, url, snippet, source}.
    """
    jobs: List[Dict[str, Any]] = []
    sess = session or _make_session()
    url = DAILYAIJOBS_BASE + DAILYAIJOBS_JOBS_PATH
    # Job list is loaded by JS after page load; short wait so it appears (ScraperAPI instruction set)
    instruction_set = [{"type": "wait", "value": 5}]
    html = _fetch_html(
        url, session=sess, use_js_render=True, instruction_set=instruction_set, timeout=45
    )
    if not html:
        logger.warning("DailyAIJobs: no HTML. Set SCRAPER_API_KEY for JS rendering.")
        return jobs

    soup = BeautifulSoup(html, "html.parser")
    seen_urls: set = set()

    # Job links: /job/..., /jobs/..., or links with job-like paths
    for a in soup.select('a[href*="/job"], a[href*="/jobs/"], a[href*="/role"], a[href*="/listing"]'):
        if len(jobs) >= max_results:
            break
        href = (a.get("href") or "").strip()
        if not href or href in ("#", "/"):
            continue
        if not href.startswith("http"):
            href = urljoin(DAILYAIJOBS_BASE, href)
        if "/jobs" in href.rstrip("/") and href.rstrip("/").endswith("/jobs"):
            continue
        if href in seen_urls:
            continue
        # Get parent card text for posted date
        card_text = ""
        parent = a.parent
        for _ in range(5):
            if parent is None:
                break
            card_text = (parent.get_text(separator=" ", strip=True) or "")[:500]
            if "ago" in card_text.lower() or "day" in card_text.lower():
                break
            parent = getattr(parent, "parent", None)
        posted_days = _parse_posted_days_ago(card_text)
        if posted_days is not None and posted_days > MAX_JOB_AGE_DAYS:
            continue
        seen_urls.add(href)
        title = (a.get_text(strip=True) or "AI/ML Job")[:200]
        if len(title) < 3:
            continue
        job = {"title": title, "company": "", "url": href, "snippet": "", "source": "dailyaijobs"}
        if posted_days is not None:
            job["posted_days_ago"] = posted_days
        jobs.append(job)
    if jobs:
        logger.info("DailyAIJobs returned %d jobs", len(jobs))
    return jobs[:max_results]


def discover_aiworkportal(
    query: str = "",
    max_results: int = 50,
    session: requests.Session | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch AI/ML/Data job listings from aiworkportal.com (free).
    Site is JS-heavy; use SCRAPER_API_KEY with render=true for best results.
    Returns list of {title, company, url, snippet, source}.
    """
    jobs: List[Dict[str, Any]] = []
    sess = session or _make_session()
    seen_urls: set = set()

    for page_path in ["/", AIWORKPORTAL_JOBS_PATH]:
        if len(jobs) >= max_results:
            break
        url = AIWORKPORTAL_BASE + page_path
        html = _fetch_html(url, session=sess, use_js_render=True, timeout=45)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        # Job detail links: /job/slug-id (not /jobs). Get card text for "X days ago" / "1 week ago"
        for a in soup.select('a[href*="/job/"]'):
            if len(jobs) >= max_results:
                break
            href = (a.get("href") or "").strip()
            if not href.startswith("http"):
                href = urljoin(AIWORKPORTAL_BASE, href)
            if not re.match(r"^https?://[^/]+/job/[^/]+/?$", href) or href in seen_urls:
                continue
            # Get parent card text to parse posted date (e.g. "1 week ago")
            card_text = ""
            parent = a.parent
            for _ in range(5):
                if parent is None:
                    break
                card_text = (parent.get_text(separator=" ", strip=True) or "")[:500]
                if "ago" in card_text.lower():
                    break
                parent = getattr(parent, "parent", None)
            posted_days = _parse_posted_days_ago(card_text)
            if posted_days is not None and posted_days > MAX_JOB_AGE_DAYS:
                continue
            seen_urls.add(href)
            title = (a.get_text(strip=True) or "AI/ML Job").strip()[:200]
            if len(title) < 3:
                title = "AI/ML Job"
            job = {
                "title": title,
                "company": "",
                "url": href,
                "snippet": "",
                "source": "aiworkportal",
            }
            if posted_days is not None:
                job["posted_days_ago"] = posted_days
            jobs.append(job)

    if jobs:
        logger.info("AIWorkPortal returned %d jobs", len(jobs))
    return jobs[:max_results]


def discover_jobs(
    query: str,
    location: str = "",
    max_results: int = 60,
) -> Dict[str, Any]:
    """
    Discover jobs from ZipRecruiter, DailyAIJobs.com, and AIWorkPortal.com.
    - All three sources are fetched in parallel (ZipRecruiter, DailyAIJobs, AIWorkPortal at once).
    - Jobs older than MAX_JOB_AGE_DAYS (1 week) are excluded so you get enough recent jobs for matching.
    Returns { success, jobs, query, location, sources }.
    """
    sess = _make_session()
    all_jobs: List[Dict[str, Any]] = []
    seen_urls: set = set()
    # Request extra per source so after 1-week recency filter we still have enough for matching
    per_source = min(50, max(35, max_results + 20))

    # Run all three sources in parallel (total time ≈ slowest source, not sum)
    zip_jobs: List[Dict[str, Any]] = []
    daily_jobs: List[Dict[str, Any]] = []
    portal_jobs: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        fut_zip = executor.submit(
            discover_ziprecruiter,
            query=query, location=location, max_results=per_source, session=sess,
        )
        fut_daily = executor.submit(
            discover_dailyaijobs,
            query=query, max_results=per_source, session=sess,
        )
        fut_portal = executor.submit(
            discover_aiworkportal,
            query=query, max_results=per_source, session=sess,
        )
        try:
            zip_jobs = fut_zip.result()
        except Exception as e:
            logger.warning("ZipRecruiter discovery failed: %s", e)
        try:
            daily_jobs = fut_daily.result()
        except Exception as e:
            logger.warning("DailyAIJobs discovery failed: %s", e)
        try:
            portal_jobs = fut_portal.result()
        except Exception as e:
            logger.warning("AIWorkPortal discovery failed: %s", e)

    for j in zip_jobs + daily_jobs + portal_jobs:
        u = (j.get("url") or "").strip()
        if u and u not in seen_urls:
            seen_urls.add(u)
            all_jobs.append(j)

    # Keep only jobs posted within MAX_JOB_AGE_DAYS (drop old / no-longer-accepting)
    filtered = []
    for j in all_jobs:
        days = j.get("posted_days_ago")
        if days is not None and days > MAX_JOB_AGE_DAYS:
            continue
        filtered.append(j)
    # Remove internal key from response
    result_list = []
    for j in filtered[:max_results]:
        j = {k: v for k, v in j.items() if k != "posted_days_ago"}
        result_list.append(j)

    sources_used = list({j.get("source") for j in result_list if j.get("source")})
    logger.info(
        "Discovery total: %d jobs after recency filter (ZipRecruiter=%d, DailyAIJobs=%d, AIWorkPortal=%d)",
        len(result_list), len(zip_jobs), len(daily_jobs), len(portal_jobs),
    )

    return {
        "success": True,
        "jobs": result_list,
        "query": query,
        "location": location or "(any)",
        "source": sources_used[0] if sources_used else "none",
        "sources": sources_used,
    }
