"""
Job discovery: fetch new jobs from Indeed (and optionally Glassdoor) search
matching user profile (query + location). Used for daily matching jobs.
"""

import logging
from typing import Any, Dict, List
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Indeed search base
INDEED_SEARCH_BASE = "https://www.indeed.com/jobs"

# Indeed search result selectors (multiple variants; Indeed changes structure often)
INDEED_JOB_CARD_SELECTORS = [
    "div.jobsearch-SerpJobCard",
    "div[data-jk]",
    "div.job_seen_beacon",
    "div.tapItem",
    "div[data-tn-component='organicJob']",
    "div.jobsearch-ResultsList > div",
    "div[class*='job_seen_beacon']",
    "div[class*='SerpJobCard']",
    "td.resultContent",
]
INDEED_TITLE_SELECTORS = [
    "a.jcs-JobTitle",
    "h2.jobTitle a",
    "a.jobtitle",
    "a[class*='jcs-JobTitle']",
    "h2[class*='jobTitle'] a",
    "a[data-jk]",
    "a[href*='viewjob']",
    "a[href*='/rc/clk']",
    "span[id*='jobTitle'] a",
]
INDEED_COMPANY_SELECTORS = [
    "span[data-testid='company-name']",
    "span.companyName",
    "div.companyName",
    "span.company",
    "span[class*='companyName']",
    "div[class*='companyName']",
    "span[class*='company']",
]
INDEED_SNIPPET_SELECTORS = [
    "div.job-snippet",
    "div.jobSummary",
    "div[class*='job-snippet']",
    "div[class*='jobSummary']",
    "div[class*='snippet']",
    "div.metadata",
    "div[class*='metadata']",
    "div[class*='salary-snippet']",
]
INDEED_LOCATION_SELECTORS = [
    "div.companyLocation",
    "div[class*='companyLocation']",
    "span[data-testid='text-location']",
]


def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def discover_indeed(
    query: str,
    location: str = "",
    max_results: int = 20,
    session: requests.Session | None = None,
) -> List[Dict[str, Any]]:
    """
    Scrape Indeed search results for jobs matching query and location.
    Returns list of {title, company, url, snippet}.
    """
    jobs: List[Dict[str, Any]] = []
    q = (query or "").strip() or "jobs"
    loc = (location or "").strip()
    params: Dict[str, str] = {"q": q}
    if loc:
        params["l"] = loc
    url = INDEED_SEARCH_BASE + "?" + "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
    sess = session or _make_session()
    try:
        r = sess.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        logger.warning(f"Indeed discovery fetch failed: {e}")
        return jobs

    cards: List[Any] = []
    for sel in INDEED_JOB_CARD_SELECTORS:
        cards = soup.select(sel)
        if cards:
            break
    if not cards:
        # Fallback: any link that looks like viewjob
        seen_urls: set = set()
        for a in soup.select('a[href*="viewjob"], a[href*="/rc/clk"]'):
            href = a.get("href") or ""
            full_url = urljoin(url, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            title = (a.get_text(strip=True) or "Job")[:200]
            if len(title) < 3:
                continue
            jobs.append({
                "title": title,
                "company": "",
                "url": full_url,
                "snippet": "",
                "source": "indeed",
            })
            if len(jobs) >= max_results:
                break
        return jobs[:max_results]

    seen_urls: set = set()
    for card in cards:
        if len(jobs) >= max_results:
            break
        title = ""
        company = ""
        job_url = ""
        snippet = ""
        for sel in INDEED_TITLE_SELECTORS:
            el = card.select_one(sel)
            if el:
                title = (el.get_text(strip=True) or "")[:200]
                href = el.get("href") or ""
                job_url = urljoin(url, href) if href else ""
                break
        for sel in INDEED_COMPANY_SELECTORS:
            el = card.select_one(sel)
            if el:
                company = (el.get_text(strip=True) or "")[:150]
                break
        for sel in INDEED_SNIPPET_SELECTORS:
            el = card.select_one(sel)
            if el:
                snippet = (el.get_text(strip=True) or "")[:300]
                break
        if job_url and job_url in seen_urls:
            continue
        if job_url:
            seen_urls.add(job_url)
        if title or job_url:
            jobs.append({
                "title": title or "Job",
                "company": company,
                "url": job_url,
                "snippet": snippet,
                "source": "indeed",
            })
    return jobs


def discover_jobs(
    query: str,
    location: str = "",
    max_results: int = 20,
) -> Dict[str, Any]:
    """
    Discover jobs from Indeed (and optionally Glassdoor) matching query and location.
    Use user profile roles/skills as query for daily matching jobs.
    """
    jobs: List[Dict[str, Any]] = []
    jobs.extend(discover_indeed(query=query, location=location, max_results=max_results))
    return {
        "success": True,
        "jobs": jobs,
        "query": query,
        "location": location or "(any)",
        "source": "indeed",
    }
