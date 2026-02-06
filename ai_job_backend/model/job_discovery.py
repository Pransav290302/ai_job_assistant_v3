"""
Job discovery: fetch new jobs from Indeed, then fallback to Glassdoor, ZipRecruiter,
and optionally Adzuna API when Indeed returns no results.
"""

import logging
import os
from typing import Any, Dict, List
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# --- Indeed ---
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
            r = sess.get(api_url, timeout=45)
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
    html = _fetch_html(url, session=sess, use_js_render=False)
    if not html:
        logger.warning("Indeed discovery: no HTML (403 or fetch failed). Set SCRAPER_API_KEY in .env to avoid blocking.")
        return jobs
    soup = BeautifulSoup(html, "html.parser")

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


# --- Glassdoor (fallback when Indeed returns 0) ---
GLASSDOOR_SEARCH_BASE = "https://www.glassdoor.com/Job/jobs.htm"

def discover_glassdoor(
    query: str,
    location: str = "",
    max_results: int = 20,
    session: requests.Session | None = None,
) -> List[Dict[str, Any]]:
    """
    Try to fetch job listings from Glassdoor search. Often returns 0 due to JS/login walls.
    Returns list of {title, company, url, snippet, source}.
    """
    jobs: List[Dict[str, Any]] = []
    q = (query or "").strip() or "jobs"
    loc = (location or "").strip()
    params: Dict[str, str] = {"keyword": q}
    if loc:
        params["locT"] = "C"
        params["locKeyword"] = loc
    url = GLASSDOOR_SEARCH_BASE + "?" + "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
    sess = session or _make_session()
    html = _fetch_html(url, session=sess, use_js_render=True)
    if not html:
        logger.warning("Glassdoor discovery: no HTML. Set SCRAPER_API_KEY for JS sites.")
        return jobs
    soup = BeautifulSoup(html, "html.parser")

    # Glassdoor often uses data attributes or specific classes; try common patterns
    for a in soup.select('a[href*="/job-listing/"], a[href*="/Job/"], a[data-test="job-link"]'):
        if len(jobs) >= max_results:
            break
        href = a.get("href") or ""
        if not href.startswith("http"):
            href = urljoin("https://www.glassdoor.com", href)
        title = (a.get_text(strip=True) or "Job")[:200]
        if len(title) < 2:
            continue
        jobs.append({
            "title": title,
            "company": "",
            "url": href,
            "snippet": "",
            "source": "glassdoor",
        })
    return jobs[:max_results]


# --- ZipRecruiter (fallback) ---
ZIPRECRUITER_SEARCH_BASE = "https://www.ziprecruiter.com/jobs-search"

def discover_ziprecruiter(
    query: str,
    location: str = "",
    max_results: int = 20,
    session: requests.Session | None = None,
) -> List[Dict[str, Any]]:
    """
    Try to fetch job listings from ZipRecruiter search.
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


# --- Adzuna API (optional; free tier with app_id/app_key) ---
ADZUNA_API_BASE = "https://api.adzuna.com/v1/api/jobs"

def discover_adzuna(
    query: str,
    location: str = "",
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """
    Fetch jobs from Adzuna API (free tier). Requires ADZUNA_APP_ID and ADZUNA_APP_KEY in env.
    Country code 'us' or 'gb'. Returns list of {title, company, url, snippet, source}.
    """
    jobs: List[Dict[str, Any]] = []
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        logger.debug("Adzuna skipped: ADZUNA_APP_ID or ADZUNA_APP_KEY not set")
        return jobs

    country = "us"
    q = (query or "").strip() or "software engineer"
    loc = (location or "").strip()
    try:
        # Adzuna: /v1/api/jobs/{country}/search/{page}?app_id=&app_key=&what=query
        params: Dict[str, str] = {"app_id": app_id, "app_key": app_key, "what": q, "results_per_page": str(min(max_results, 50))}
        if loc:
            params["where"] = loc
        url = f"{ADZUNA_API_BASE}/{country}/search/1?" + "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.warning("Adzuna API request failed: %s", e)
        return jobs

    results = data.get("results") or []
    for item in results[:max_results]:
        title = (item.get("title") or "Job")[:200]
        company = (item.get("company", {}).get("display_name") or "")[:150]
        job_url = item.get("redirect_url") or item.get("url") or ""
        desc = (item.get("description") or "")[:300]
        jobs.append({
            "title": title,
            "company": company,
            "url": job_url,
            "snippet": desc,
            "source": "adzuna",
        })
    return jobs


def discover_jobs(
    query: str,
    location: str = "",
    max_results: int = 20,
) -> Dict[str, Any]:
    """
    Discover jobs: try Indeed first, then Glassdoor, ZipRecruiter, then Adzuna API
    until we have at least some results. Uses user profile query/location.
    """
    jobs: List[Dict[str, Any]] = []
    sources_tried: List[str] = []
    sess = _make_session()

    # 1. Indeed
    indeed_jobs = discover_indeed(query=query, location=location, max_results=max_results, session=sess)
    jobs.extend(indeed_jobs)
    sources_tried.append("indeed")
    if not indeed_jobs:
        logger.info("Indeed returned 0 jobs (often 403 when no ScraperAPI). Trying Glassdoor...")
    if len(jobs) >= max_results:
        return {
            "success": True,
            "jobs": jobs[:max_results],
            "query": query,
            "location": location or "(any)",
            "source": "indeed",
        }

    # 2. Glassdoor fallback
    glassdoor_jobs = discover_glassdoor(query=query, location=location, max_results=max_results - len(jobs), session=sess)
    jobs.extend(glassdoor_jobs)
    sources_tried.append("glassdoor")
    if glassdoor_jobs:
        logger.info("Glassdoor returned %d jobs", len(glassdoor_jobs))
    elif len(jobs) == 0:
        logger.info("Glassdoor returned 0. Trying ZipRecruiter...")
    if len(jobs) >= max_results:
        return {
            "success": True,
            "jobs": jobs[:max_results],
            "query": query,
            "location": location or "(any)",
            "source": "glassdoor",
        }

    # 3. ZipRecruiter fallback
    zip_jobs = discover_ziprecruiter(query=query, location=location, max_results=max_results - len(jobs), session=sess)
    jobs.extend(zip_jobs)
    sources_tried.append("ziprecruiter")
    if zip_jobs:
        logger.info("ZipRecruiter returned %d jobs", len(zip_jobs))
    elif len(jobs) == 0:
        logger.info("ZipRecruiter returned 0. Trying Adzuna API...")
    if len(jobs) >= max_results:
        return {
            "success": True,
            "jobs": jobs[:max_results],
            "query": query,
            "location": location or "(any)",
            "source": "ziprecruiter",
        }

    # 4. Adzuna API fallback (optional; needs env keys)
    adzuna_jobs = discover_adzuna(query=query, location=location, max_results=max_results - len(jobs))
    jobs.extend(adzuna_jobs)
    sources_tried.append("adzuna")
    if adzuna_jobs:
        logger.info("Adzuna returned %d jobs", len(adzuna_jobs))

    primary = "indeed" if indeed_jobs else ("glassdoor" if glassdoor_jobs else ("ziprecruiter" if zip_jobs else ("adzuna" if adzuna_jobs else "none")))
    if not jobs:
        logger.warning("All sources returned 0 jobs (tried %s) for query=%r location=%r. Set SCRAPER_API_KEY or ADZUNA_APP_ID/ADZUNA_APP_KEY for fallbacks.", sources_tried, query, location)

    return {
        "success": True,
        "jobs": jobs[:max_results],
        "query": query,
        "location": location or "(any)",
        "source": primary,
    }
