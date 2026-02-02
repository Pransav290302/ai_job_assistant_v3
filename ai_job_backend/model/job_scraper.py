"""
Production-grade Job Description Scraper
Supports: ScraperAPI (recommended), Playwright, requests.
Handles LinkedIn, Indeed, Greenhouse, Glassdoor, and generic sites.
"""

import os
import re
import logging
import asyncio
from typing import Optional, Dict
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Optional Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Optional Playwright - works on Render with: playwright install chromium
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Optional playwright-stealth
try:
    from playwright_stealth import Stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False


# Login wall / blocked page indicators (LinkedIn, Glassdoor)
LOGIN_WALL_PATTERNS = [
    r"sign in to linkedin",
    r"join linkedin",
    r"join now",
    r"log in to glassdoor",
    r"create an account",
    r"your session has expired",
    r"please log in",
    r"you must be logged in",
    r"join to view",
]


def _is_login_wall(html: str) -> bool:
    """Detect if page is a login/signup wall instead of job content."""
    if not html or len(html) < 500:
        return True
    text = html.lower()[:8000]
    for pat in LOGIN_WALL_PATTERNS:
        if re.search(pat, text):
            return True
    return False


class JobScraper:
    """
    Production job scraper with multiple providers.
    Priority: ScraperAPI (if configured) > Playwright > requests.
    """

    SITE_SELECTORS = {
        "linkedin": {
            "content_selectors": [
                "div.description__text",
                "div.show-more-less-html__markup",
                "section.core-section-container__content",
                "div[data-test-id='job-details']",
                "div.jobs-box__html-content",
                "div.job-view-layout",
                "div.description",
                "article",
            ],
            "exclude_selectors": [
                "nav", "header", "footer", ".ad", ".advertisement",
                ".social-share", "button", "a[href*='apply']",
            ],
        },
        "indeed": {
            "content_selectors": [
                "div#jobDescriptionText",
                "div.jobsearch-jobDescriptionText",
                "div.jobsearch-JobComponent-description",
                "div.jobsearch-job-overview",
            ],
            "exclude_selectors": [
                "nav", "header", "footer", ".jobsearch-IndeedApplyButton",
            ],
        },
        "greenhouse": {
            "content_selectors": [
                "div#content",
                "div#job_description",
                "div.description",
                "section.content",
            ],
            "exclude_selectors": [
                "nav", "header", "footer", ".application-form",
            ],
        },
        "glassdoor": {
            "content_selectors": [
                "div.jobDesc",
                "div.jobDescriptionContent",
                "div[data-test='jobDescriptionText']",
                "div.desc",
            ],
            "exclude_selectors": [
                "nav", "header", "footer", ".apply-button",
            ],
        },
    }

    JS_SITES = ("linkedin", "glassdoor")

    def __init__(
        self,
        use_selenium: bool = False,
        use_playwright: bool = True,
        headless: bool = True,
        scraper_api_key: Optional[str] = None,
    ):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.headless = headless
        self.scraper_api_key = scraper_api_key
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _detect_site(self, url: str) -> str:
        domain = urlparse(url).netloc.lower()
        if "linkedin.com" in domain:
            return "linkedin"
        if "indeed.com" in domain:
            return "indeed"
        if "greenhouse.io" in domain or "boards.greenhouse.io" in domain:
            return "greenhouse"
        if "glassdoor.com" in domain:
            return "glassdoor"
        return "generic"

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        text = re.sub(r"(?i)(apply now|save job|share job|see more|see less)", "", text)
        return text.strip()

    def _extract_with_selectors(
        self,
        soup: BeautifulSoup,
        selectors: list,
        exclude_selectors: list,
    ) -> str:
        for sel in exclude_selectors:
            for el in soup.select(sel):
                el.decompose()
        for selector in selectors:
            try:
                elements = soup.select(selector)
            except Exception:
                continue
            if elements:
                parts = []
                for el in elements:
                    t = el.get_text(separator=" ", strip=True)
                    if t and len(t) > 80:
                        parts.append(t)
                if parts:
                    return self._clean_text(" ".join(parts))
        return ""

    def _extract_generic(self, soup: BeautifulSoup) -> str:
        for sel in ["nav", "header", "footer", ".ad", "script", "style"]:
            for el in soup.select(sel):
                el.decompose()
        main = soup.find("main") or soup.find("article") or soup.find(
            "div", class_=re.compile(r"content|description|job", re.I)
        )
        if main:
            return self._clean_text(main.get_text(separator=" ", strip=True))
        body = soup.find("body")
        if body:
            parts = []
            for p in body.find_all(["p", "div", "section"]):
                t = p.get_text(separator=" ", strip=True)
                if len(t) > 50:
                    parts.append(t)
            if parts:
                return self._clean_text(" ".join(parts))
        return ""

    def _parse_html(self, html: str, url: str) -> Optional[str]:
        if _is_login_wall(html):
            logger.warning("Login wall detected - page requires authentication")
            return None
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")
        site = self._detect_site(url)
        if site in self.SITE_SELECTORS:
            cfg = self.SITE_SELECTORS[site]
            text = self._extract_with_selectors(
                soup, cfg["content_selectors"], cfg["exclude_selectors"]
            )
            if text:
                return text
        return self._extract_generic(soup) or None

    def _scrape_with_scraper_api(self, url: str) -> Optional[str]:
        """ScraperAPI - production-grade, handles LinkedIn/Glassdoor."""
        if not self.scraper_api_key:
            return None
        try:
            api_url = (
                "http://api.scraperapi.com"
                f"?api_key={self.scraper_api_key}"
                f"&url={quote(url, safe='')}"
                "&render=true"  # JS rendering for LinkedIn
            )
            r = self.session.get(api_url, timeout=60)
            r.raise_for_status()
            text = self._parse_html(r.text, url)
            if text and len(text) > 200:
                logger.info(f"ScraperAPI: extracted {len(text)} chars")
                return text
        except Exception as e:
            logger.warning(f"ScraperAPI error: {e}")
        return None

    def _scrape_with_requests(self, url: str) -> Optional[str]:
        try:
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
            text = self._parse_html(r.text, url)
            if text and len(text) > 200:
                return text
        except Exception as e:
            logger.debug(f"Requests scrape failed: {e}")
        return None

    def _scrape_with_playwright(self, url: str) -> Optional[str]:
        if not PLAYWRIGHT_AVAILABLE:
            return None
        try:
            html = asyncio.run(self._playwright_async(url))
            if html:
                return self._parse_html(html, url)
        except Exception as e:
            logger.warning(f"Playwright scrape failed: {e}")
        return None

    async def _playwright_async(self, url: str) -> Optional[str]:
        from model.utils.config import get_config
        config = get_config()
        browserless_url = config.BROWSERLESS_URL
        use_stealth = getattr(config, "USE_STEALTH", True) and STEALTH_AVAILABLE

        launch = {"headless": self.headless, "args": [
            "--no-sandbox", "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]}

        async with async_playwright() as p:
            if browserless_url:
                browser = await p.chromium.connect_over_cdp(browserless_url)
            else:
                browser = await p.chromium.launch(**launch)
            ctx = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                locale="en-US",
            )
            if use_stealth and STEALTH_AVAILABLE:
                await Stealth().apply_stealth_async(ctx)
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            html = await page.content()
            await browser.close()
        return html

    def _scrape_with_selenium(self, url: str) -> Optional[str]:
        if not SELENIUM_AVAILABLE:
            return None
        try:
            self._setup_selenium()
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            import time
            time.sleep(3)
            html = self.driver.page_source
            return self._parse_html(html, url)
        except Exception as e:
            logger.warning(f"Selenium scrape failed: {e}")
            return None

    def _setup_selenium(self):
        if self.driver is None and SELENIUM_AVAILABLE:
            opts = Options()
            if self.headless:
                opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)

    def scrape(
        self,
        url: str,
        force_playwright: bool = False,
    ) -> Dict:
        """
        Scrape job description. Uses BROWSERLESS_URL (Playwright) for LinkedIn/Glassdoor.
        Priority: Playwright (Browserless) for JS sites → requests for Indeed/Greenhouse.
        """
        logger.info(f"Scraping: {url}")
        site = self._detect_site(url)
        needs_js = site in self.JS_SITES

        # Indeed/Greenhouse: requests usually works
        if not needs_js:
            text = self._scrape_with_requests(url)
            if text:
                return {"success": True, "text": text, "method": "requests", "url": url}

        # LinkedIn/Glassdoor: Playwright (BROWSERLESS_URL) only
        if self.use_playwright:
            text = self._scrape_with_playwright(url)
            if text:
                return {"success": True, "text": text, "method": "playwright", "url": url}

        # Last resort: requests for JS sites (often login wall)
        text = self._scrape_with_requests(url)
        if text:
            return {"success": True, "text": text, "method": "requests", "url": url}

        return {
            "success": False,
            "text": None,
            "error": (
                "Could not extract job description. Ensure BROWSERLESS_URL is set "
                "(wss://chrome.browserless.io?token=YOUR_TOKEN). Or paste the job manually."
            ),
            "url": url,
        }

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.session.close()
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)


async def scrape_job_description_async(
    url: str,
    use_selenium: bool = False,
    use_playwright: bool = True,
    scraper_api_key: Optional[str] = None,
) -> str:
    """Async version. Raises ValueError on failure."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: scrape_job_description(
            url, use_selenium, use_playwright, scraper_api_key
        ),
    )


def scrape_job_description(
    url: str,
    use_selenium: bool = False,
    use_playwright: bool = True,
    scraper_api_key: Optional[str] = None,
) -> str:
    """Convenience function. Raises ValueError on failure."""
    key = scraper_api_key or os.getenv("SCRAPER_API_KEY")
    scraper = JobScraper(
        use_selenium=use_selenium,
        use_playwright=use_playwright,
        scraper_api_key=key,
    )
    try:
        result = scraper.scrape(url)
        if result["success"]:
            return result["text"]
        raise ValueError(result.get("error", "Scraping failed"))
    finally:
        scraper.close()
