"""
Robust Job Description Scraper
Handles multiple job sites with intelligent content extraction.
"""

import re
import logging
import asyncio
from typing import Optional, Dict
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Optional Selenium imports - only import if available
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
    logger.warning("Selenium not available. Selenium-based scraping will be disabled.")

# Optional Playwright imports - works on Render with: playwright install chromium
try:
    from playwright.sync_api import sync_playwright
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available. Playwright-based scraping will be disabled.")

# Optional playwright-stealth - reduces headless detection (LinkedIn, Glassdoor)
try:
    from playwright_stealth import Stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False


class JobScraper:
    """
    Professional job scraper that handles multiple job posting sites.
    Uses intelligent content extraction to filter out navigation, ads, and footers.
    """
    
    # Site-specific selectors and patterns
    SITE_SELECTORS = {
        'linkedin': {
            'content_selectors': [
                'div.description__text',
                'div.show-more-less-html__markup',
                'section.core-section-container',
                'div[data-test-id="job-details"]'
            ],
            'exclude_selectors': [
                'nav', 'header', 'footer', '.ad', '.advertisement',
                '.social-share', '.apply-button', '.job-actions'
            ]
        },
        'indeed': {
            'content_selectors': [
                'div#jobDescriptionText',
                'div.jobsearch-jobDescriptionText',
                'div.jobsearch-JobComponent-description'
            ],
            'exclude_selectors': [
                'nav', 'header', 'footer', '.jobsearch-IndeedApplyButton',
                '.jobsearch-SerpJobLink', '.jobsearch-CompanyReview'
            ]
        },
        'greenhouse': {
            'content_selectors': [
                'div#content',
                'div.description',
                'section.content'
            ],
            'exclude_selectors': [
                'nav', 'header', 'footer', '.application-form',
                '.sidebar', '.company-info'
            ]
        },
        'glassdoor': {
            'content_selectors': [
                'div.jobDesc',
                'div.jobDescriptionContent',
                'div[data-test="jobDescriptionText"]'
            ],
            'exclude_selectors': [
                'nav', 'header', 'footer', '.apply-button',
                '.company-overview', '.salary-estimate'
            ]
        }
    }
    
    # Sites that need JavaScript rendering (LinkedIn, Glassdoor, etc.)
    JS_SITES = ("linkedin", "glassdoor")

    def __init__(self, use_selenium: bool = False, use_playwright: bool = False, headless: bool = True):
        """
        Initialize the job scraper.
        
        Args:
            use_selenium: Whether to use Selenium for JavaScript-heavy sites
            use_playwright: Whether to use Playwright (works on Render free tier with chromium)
            headless: Run browser in headless mode
        """
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _detect_site(self, url: str) -> str:
        """Detect which job site the URL belongs to."""
        domain = urlparse(url).netloc.lower()
        
        if 'linkedin.com' in domain:
            return 'linkedin'
        elif 'indeed.com' in domain:
            return 'indeed'
        elif 'greenhouse.io' in domain or 'boards.greenhouse.io' in domain:
            return 'greenhouse'
        elif 'glassdoor.com' in domain:
            return 'glassdoor'
        else:
            return 'generic'
    
    def _setup_selenium(self):
        """Initialize Selenium WebDriver if needed."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not installed. Install with: pip install selenium webdriver-manager")
        
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and normalizing.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove common noise patterns
        text = re.sub(r'(?i)(apply now|save job|share job)', '', text)
        
        return text
    
    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: list, exclude_selectors: list) -> str:
        """
        Extract job description using site-specific selectors.
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
            exclude_selectors: Selectors to exclude from results
            
        Returns:
            Extracted text content
        """
        # Remove unwanted elements first
        for exclude_sel in exclude_selectors:
            for element in soup.select(exclude_sel):
                element.decompose()
        
        # Try each selector until we find content
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Combine text from all matching elements
                text_parts = []
                for elem in elements:
                    text = elem.get_text(separator=' ', strip=True)
                    if text and len(text) > 100:  # Filter out short snippets
                        text_parts.append(text)
                
                if text_parts:
                    combined = ' '.join(text_parts)
                    return self._clean_text(combined)
        
        return ""
    
    def _extract_generic(self, soup: BeautifulSoup) -> str:
        """
        Generic extraction method for unknown sites.
        Uses heuristics to find main content.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted text content
        """
        # Remove common noise elements
        for selector in ['nav', 'header', 'footer', '.ad', '.advertisement', 
                        '.sidebar', '.menu', '.navigation', 'script', 'style']:
            for elem in soup.select(selector):
                elem.decompose()
        
        # Look for main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|description|job', re.I))
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            return self._clean_text(text)
        
        # Fallback: get body text but filter out very short paragraphs
        body = soup.find('body')
        if body:
            paragraphs = body.find_all(['p', 'div', 'section'])
            text_parts = []
            for p in paragraphs:
                text = p.get_text(separator=' ', strip=True)
                if len(text) > 50:  # Only include substantial paragraphs
                    text_parts.append(text)
            
            if text_parts:
                return self._clean_text(' '.join(text_parts))
        
        return ""
    
    def _scrape_with_requests(self, url: str) -> Optional[str]:
        """
        Scrape using requests library (faster, but doesn't handle JavaScript).
        
        Args:
            url: Job posting URL
            
        Returns:
            Extracted job description text or None
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Try lxml parser first, fallback to html.parser
            try:
                soup = BeautifulSoup(response.content, 'lxml')
            except:
                soup = BeautifulSoup(response.content, 'html.parser')
            
            site = self._detect_site(url)
            
            if site in self.SITE_SELECTORS:
                config = self.SITE_SELECTORS[site]
                text = self._extract_with_selectors(
                    soup, 
                    config['content_selectors'],
                    config['exclude_selectors']
                )
                if text:
                    return text
            
            # Fallback to generic extraction
            return self._extract_generic(soup)
            
        except Exception as e:
            logger.error(f"Error scraping with requests: {str(e)}")
            return None
    
    def _scrape_with_selenium(self, url: str) -> Optional[str]:
        """
        Scrape using Selenium (handles JavaScript-rendered content).
        
        Args:
            url: Job posting URL
            
        Returns:
            Extracted job description text or None
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available, skipping Selenium-based scraping")
            return None
            
        try:
            self._setup_selenium()
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            import time
            time.sleep(2)
            
            html = self.driver.page_source
            # Try lxml parser first, fallback to html.parser
            try:
                soup = BeautifulSoup(html, 'lxml')
            except:
                soup = BeautifulSoup(html, 'html.parser')
            
            site = self._detect_site(url)
            
            if site in self.SITE_SELECTORS:
                config = self.SITE_SELECTORS[site]
                text = self._extract_with_selectors(
                    soup,
                    config['content_selectors'],
                    config['exclude_selectors']
                )
                if text:
                    return text
            
            # Fallback to generic extraction
            return self._extract_generic(soup)
            
        except Exception as e:
            logger.error(f"Error scraping with Selenium: {str(e)}")
            return None

    def _scrape_with_playwright(self, url: str) -> Optional[str]:
        """
        Scrape using Playwright with stealth (LinkedIn, Glassdoor on Render free tier).
        Supports Browserless (6 hrs free/month) for different IPs.
        """
        if not PLAYWRIGHT_AVAILABLE:
            return None
        try:
            html = asyncio.run(self._scrape_playwright_async(url))
            if not html:
                return None
            try:
                soup = BeautifulSoup(html, "lxml")
            except Exception:
                soup = BeautifulSoup(html, "html.parser")
            site = self._detect_site(url)
            if site in self.SITE_SELECTORS:
                config = self.SITE_SELECTORS[site]
                text = self._extract_with_selectors(
                    soup, config["content_selectors"], config["exclude_selectors"]
                )
                if text:
                    return text
            return self._extract_generic(soup)
        except Exception as e:
            logger.error(f"Error scraping with Playwright: {str(e)}")
            return None

    async def _scrape_playwright_async(self, url: str) -> Optional[str]:
        """Async Playwright scrape with stealth + optional Browserless."""
        from model.utils.config import get_config
        config = get_config()
        browserless_url = config.BROWSERLESS_URL
        use_stealth = config.USE_STEALTH and STEALTH_AVAILABLE

        launch_args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1920,1080",
            ],
        }

        async with async_playwright() as p:
            if browserless_url:
                browser = await p.chromium.connect_over_cdp(browserless_url)
                logger.info("Using Browserless (remote browser)")
            else:
                browser = await p.chromium.launch(**launch_args)

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            )
            if use_stealth and STEALTH_AVAILABLE:
                await Stealth().apply_stealth_async(context)

            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)  # Allow dynamic content (LinkedIn/Glassdoor)
            html = await page.content()
            await browser.close()
        return html

    def scrape(self, url: str, force_selenium: bool = False, force_playwright: bool = False) -> Dict[str, any]:
        """
        Main scraping method. Order: requests → Playwright → Selenium.
        Playwright works on Render free tier (add 'playwright install chromium' to build).
        """
        logger.info(f"Scraping job description from: {url}")
        site = self._detect_site(url)
        needs_js = site in self.JS_SITES

        # For LinkedIn/Glassdoor: Playwright first (requests usually returns login wall)
        if needs_js and (self.use_playwright or force_playwright):
            text = self._scrape_with_playwright(url)
            if text and len(text) > 200:
                logger.info(f"Scraped {len(text)} chars using Playwright")
                return {"success": True, "text": text, "method": "playwright", "url": url}

        # For other sites: try requests first (faster)
        if not force_playwright and not force_selenium:
            text = self._scrape_with_requests(url)
            if text and len(text) > 200:
                logger.info(f"Scraped {len(text)} chars using requests")
                return {"success": True, "text": text, "method": "requests", "url": url}

        # Playwright for JS sites we missed, or as fallback
        if self.use_playwright or force_playwright:
            text = self._scrape_with_playwright(url)
            if text and len(text) > 200:
                return {"success": True, "text": text, "method": "playwright", "url": url}

        # Selenium fallback (needs Chrome - not on Render default)
        if self.use_selenium or force_selenium:
            text = self._scrape_with_selenium(url)
            if text and len(text) > 200:
                return {"success": True, "text": text, "method": "selenium", "url": url}

        logger.warning(f"Failed to extract meaningful content from {url}")
        return {
            'success': False,
            'text': None,
            'error': 'Could not extract job description content',
            'url': url
        }
    
    async def scrape_async(self, url: str, force_selenium: bool = False) -> Dict[str, any]:
        """
        Async version of scrape method for use in async routes.
        
        Args:
            url: Job posting URL
            force_selenium: Force use of Selenium even if not configured
            
        Returns:
            Dictionary with 'success', 'text', and 'error' keys
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.scrape, url, force_selenium)
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.session.close()
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def scrape_job_description(url: str, use_selenium: bool = False) -> str:
    """
    Convenience function for simple scraping use cases.
    
    Args:
        url: Job posting URL
        use_selenium: Whether to use Selenium for JavaScript-heavy sites
        
    Returns:
        Extracted job description text
        
    Raises:
        ValueError: If scraping fails
    """
    with JobScraper(use_selenium=use_selenium) as scraper:
        result = scraper.scrape(url)
        
        if result['success']:
            return result['text']
        else:
            raise ValueError(f"Failed to scrape job description: {result.get('error', 'Unknown error')}")


async def scrape_job_description_async(url: str, use_selenium: bool = False) -> str:
    """
    Async convenience function for scraping in async routes.
    
    Args:
        url: Job posting URL
        use_selenium: Whether to use Selenium for JavaScript-heavy sites
        
    Returns:
        Extracted job description text
        
    Raises:
        ValueError: If scraping fails
    """
    scraper = JobScraper(use_selenium=use_selenium)
    try:
        result = await scraper.scrape_async(url)
        if result['success']:
            return result['text']
        else:
            raise ValueError(f"Failed to scrape job description: {result.get('error', 'Unknown error')}")
    finally:
        scraper.close()
