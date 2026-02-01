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
