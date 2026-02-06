"""
Configuration Management
Handles environment variables and application configuration.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# Load environment variables from .env file if it exists
load_dotenv()

# Hardcoded: Azure ML DeepSeek-R1 (only model used)
# Registry: azureml://registries/azureml-deepseek/models/DeepSeek-R1/versions/1
# Inference API requires deployment name "DeepSeek-R1"
DEEPSEEK_R1_MODEL = "DeepSeek-R1"


class Config:
    """Application configuration."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL: Optional[str] = os.getenv('OPENAI_BASE_URL')
    # Model: Azure ML DeepSeek-R1 (hardcoded, no env override)
    OPENAI_MODEL: str = DEEPSEEK_R1_MODEL
    # Azure often needs api-version on requests; set OPENAI_API_VERSION in .env if LLM calls fail
    OPENAI_API_VERSION: Optional[str] = os.getenv('OPENAI_API_VERSION')
    
    # Scraper Configuration - LinkedIn/Glassdoor: use SCRAPER_API_KEY and/or BROWSERLESS_URL
    SCRAPER_API_KEY: Optional[str] = os.getenv('SCRAPER_API_KEY')  # scraperapi.com - JS rendering, no browser
    BROWSERLESS_URL: Optional[str] = os.getenv('BROWSERLESS_URL')  # wss://chrome.browserless.io?token=YOUR_TOKEN
    USE_PLAYWRIGHT: bool = bool(os.getenv('BROWSERLESS_URL'))  # True when BROWSERLESS_URL set
    USE_SELENIUM: bool = False  # Not used; Browserless only
    USE_STEALTH: bool = os.getenv('USE_STEALTH', 'true').lower() == 'true'  # Anti-detection
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE')
    
    # API Configuration (for backend integration)
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    
    @classmethod
    def get_base_url(cls) -> Optional[str]:
        """Return base URL (no query params). Use create_openai_client for Azure api-version."""
        return cls.OPENAI_BASE_URL

    @classmethod
    def create_openai_client(
        cls,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> OpenAI:
        """
        Create OpenAI client. For Azure AI Foundry, uses httpx with api-version
        query param on every request (keeps path correct).
        """
        key = api_key or cls.OPENAI_API_KEY
        url = base_url or cls.OPENAI_BASE_URL
        if not key:
            raise ValueError("OPENAI_API_KEY not set")
        if cls.OPENAI_API_VERSION and url:
            http_client = httpx.Client(params={"api-version": cls.OPENAI_API_VERSION})
            return OpenAI(api_key=key, base_url=url, http_client=http_client)
        return OpenAI(api_key=key, base_url=url)

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
