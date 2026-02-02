"""
Configuration Management
Handles environment variables and application configuration.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL: Optional[str] = os.getenv('OPENAI_BASE_URL')  # Defaults to https://api.openai.com/v1
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Scraper Configuration
    USE_SELENIUM: bool = os.getenv('USE_SELENIUM', 'false').lower() == 'true'
    # FREE_TIER=true skips "playwright install chromium" - must use ScraperAPI for LinkedIn
    FREE_TIER: bool = os.getenv('FREE_TIER', 'false').lower() == 'true'
    USE_PLAYWRIGHT: bool = (not FREE_TIER) and (os.getenv('USE_PLAYWRIGHT', 'true').lower() == 'true')
    USE_STEALTH: bool = os.getenv('USE_STEALTH', 'true').lower() == 'true'  # Anti-detection
    BROWSERLESS_URL: Optional[str] = os.getenv('BROWSERLESS_URL')  # Remote browser
    # ScraperAPI: production-grade scraping, 1000 free credits/mo. Set for reliable LinkedIn/Glassdoor.
    SCRAPER_API_KEY: Optional[str] = os.getenv('SCRAPER_API_KEY')
    SELENIUM_HEADLESS: bool = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE')
    
    # API Configuration (for backend integration)
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if configuration is valid
        """
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. LLM features will not work.")
            return False
        return True


def get_config() -> Config:
    """Get application configuration instance."""
    return Config
