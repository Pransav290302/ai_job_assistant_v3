"""
Diagnose why dailyaijobs.com and aiworkportal.com scraping returns 0 jobs.
Run from ai_job_backend:  python scripts/diagnose_dailyai_aiworkportal.py
"""
import os
import re
import sys
from urllib.parse import quote_plus, urljoin

# Load .env and backend path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_root)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(backend_root, ".env"))
except ImportError:
    pass

import requests
from bs4 import BeautifulSoup

DAILYAIJOBS_BASE = "https://www.dailyaijobs.com"
AIWORKPORTAL_BASE = "https://aiworkportal.com"
AIWORKPORTAL_JOBS_PATH = "/jobs"


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def fetch_html(url: str, use_js_render: bool = True):
    """Returns (html, error_message). Empty html and non-empty error on failure."""
    key = os.getenv("SCRAPER_API_KEY")
    if not key:
        return "", "SCRAPER_API_KEY not set in .env"
    sess = make_session()
    api_url = f"http://api.scraperapi.com?api_key={key}&url={quote_plus(url)}"
    if use_js_render:
        api_url += "&render=true"
    try:
        r = sess.get(api_url, timeout=90)
        r.raise_for_status()
        return (r.text or ""), ""
    except Exception as e:
        return "", str(e)


def main():
    print("=" * 60)
    print("1. DAILYAIJOBS.COM")
    print("=" * 60)
    url_daily = DAILYAIJOBS_BASE + "/"
    html_daily, err_daily = fetch_html(url_daily)
    if err_daily:
        print("FETCH FAILED:", err_daily)
    else:
        print("HTML length:", len(html_daily))
        print("First 500 chars:", repr(html_daily[:500]))
        soup = BeautifulSoup(html_daily, "html.parser")
        for sel in ['a[href*="/job"]', 'a[href*="/jobs/"]', 'a[href*="/role"]', 'a[href*="/listing"]']:
            links = soup.select(sel)
            print(f"  Selector {sel!r}: {len(links)} links")
        all_a = soup.find_all("a", href=True)
        job_like = [a for a in all_a if a.get("href") and ("/job" in (a.get("href") or "") or "/role" in (a.get("href") or "") or "/listing" in (a.get("href") or ""))]
        print(f"  Any <a> with href containing job/role/listing: {len(job_like)}")
        if "Loading" in html_daily or "loading" in html_daily:
            print("  --> Page likely JS-rendered; content may be 'Loading...' until JS runs (ScraperAPI render=true may need longer wait).")

    html_portal = ""
    print()
    print("=" * 60)
    print("2. AIWORKPORTAL.COM")
    print("=" * 60)
    for path in ["/", AIWORKPORTAL_JOBS_PATH]:
        url_portal = AIWORKPORTAL_BASE + path
        print(f"  URL: {url_portal}")
        html_portal, err_portal = fetch_html(url_portal)
        if err_portal:
            print("  FETCH FAILED:", err_portal)
        else:
            print("  HTML length:", len(html_portal))
            print("  First 400 chars:", repr(html_portal[:400]))
            soup = BeautifulSoup(html_portal, "html.parser")
            job_links = soup.select('a[href*="/job/"]')
            single_job = [a for a in job_links if re.match(r"^https?://[^/]+/job/[^/]+/?$", urljoin(AIWORKPORTAL_BASE, (a.get("href") or "")))]
            print(f"  a[href*='/job/']: {len(job_links)} total, {len(single_job)} match single-job pattern")
            if "Loading" in html_portal or "loading" in html_portal:
                print("  --> Page likely JS-rendered; content may be 'Loading...' until JS runs.")
        print()

    print("=" * 60)
    print("ROOT CAUSE SUMMARY")
    print("=" * 60)
    if not os.getenv("SCRAPER_API_KEY"):
        print("- SCRAPER_API_KEY is missing; ScraperAPI is not used.")
    elif not html_daily and not err_daily:
        print("- DailyAIJobs: No HTML and no error (unexpected).")
    elif err_daily:
        print("- DailyAIJobs fetch error:", err_daily)
    if "Loading" in (html_daily or "") or "Loading" in (html_portal or ""):
        print("- Pages return 'Loading...': content is loaded by JavaScript after page load.")
        print("  ScraperAPI with render=true runs JS, but some SPA sites need extra wait time.")
        print("  ScraperAPI 'wait' or 'wait_for_selector' may be needed (check ScraperAPI docs for JS wait options).")


if __name__ == "__main__":
    main()
