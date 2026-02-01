"""Rate limiter for production. In-memory for single instance; use Redis for multi-instance."""
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Slightly lower limit for free tier demo to avoid hitting Supabase/Render quotas
_free_tier = os.getenv("FREE_TIER", "false").lower() == "true"
_default_limit = "20/minute" if _free_tier else "30/minute"
limiter = Limiter(key_func=get_remote_address, default_limits=[_default_limit])
