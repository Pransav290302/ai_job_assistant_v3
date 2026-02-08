import os

from slowapi import Limiter
from slowapi.util import get_remote_address
_free_tier = os.getenv("FREE_TIER", "false").lower() == "true"
_default_limit = "20/minute" if _free_tier else "30/minute"
limiter = Limiter(key_func=get_remote_address, default_limits=[_default_limit])
