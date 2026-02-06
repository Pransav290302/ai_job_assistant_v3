"""
Quick test for DeepSeek R1 model connection.
Run from ai_job_backend directory:
    python scripts/test_model.py
"""

import os
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_backend_root))
os.chdir(_backend_root)

from dotenv import load_dotenv
load_dotenv(_backend_root / ".env")


def test_model():
    """Test DeepSeek R1 model with a minimal chat completion."""
    print("\n=== DeepSeek R1 Model Test ===\n")

    from model.utils.config import get_config
    config = get_config()

    print(f"  Model: {config.OPENAI_MODEL}")
    print(f"  Base URL: {config.get_base_url() or config.OPENAI_BASE_URL or '(default)'}")
    if config.OPENAI_API_VERSION:
        print(f"  API version (Azure): {config.OPENAI_API_VERSION}")
    print(f"  API Key: {'Set' if config.OPENAI_API_KEY else 'NOT SET'}\n")

    if not config.OPENAI_API_KEY:
        print("  FAIL: OPENAI_API_KEY not set. Add it to .env")
        return False

    try:
        base = config.get_base_url() or config.OPENAI_BASE_URL
        client = config.create_openai_client(
            api_key=config.OPENAI_API_KEY,
            base_url=base,
        )

        print("  Sending test prompt to model...")
        resp = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=50,
            temperature=0,
        )
        reply = resp.choices[0].message.content
        print(f"  Response: {reply[:200]}")
        print("\n  SUCCESS: DeepSeek R1 is working.\n")
        return True

    except Exception as e:
        print(f"  FAIL: {e}\n")
        return False


if __name__ == "__main__":
    ok = test_model()
    sys.exit(0 if ok else 1)
