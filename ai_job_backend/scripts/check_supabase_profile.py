"""
Verify that the backend can fetch user preferences from Supabase.
Required for: DeepSeek R1 job ranking (rank-for-user) and agent get_user_profile tool.

Usage:
  python scripts/check_supabase_profile.py
  python scripts/check_supabase_profile.py <user_id>

If user_id is omitted, only env and connectivity are checked (no real profile).
"""

import os
import sys

# Run from backend root so model and .env are found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def main() -> None:
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    print("Supabase profile lookup check (for LLM / DeepSeek R1 flow)\n")
    print(f"  SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL): {'Set' if url else 'NOT SET'}")
    print(f"  SUPABASE_SERVICE_ROLE_KEY: {'Set' if key else 'NOT SET'}")

    if not url or not key:
        print("\n  FAIL: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in ai_job_backend/.env")
        print("  Then rank-for-user and agent get_user_profile can fetch user preferences from Supabase.")
        sys.exit(1)

    from model.profile_lookup import get_user_profile_from_db

    user_id = (sys.argv[1] or "").strip() or "00000000-0000-0000-0000-000000000000"
    print(f"\n  Fetching profile for user_id: {user_id[:8]}...")
    out = get_user_profile_from_db(user_id)

    if out.get("error"):
        print(f"\n  ERROR: {out['error']}")
        print("  Fix: Ensure Supabase URL and service_role key are correct and tables exist (profiles, user_preferences, user_personal_info).")
        sys.exit(1)

    print("  OK: Profile lookup succeeded.")
    print(f"  - current_title/roles: {out.get('current_title', '')[:60]}...")
    print(f"  - skills: {out.get('skills', '')[:60]}...")
    print(f"  - location: {out.get('location', '')}")
    print(f"  - interests/industries: {out.get('interests', '')[:60]}...")
    print("\n  DeepSeek R1 (rank-for-user and agent) can use this profile from Supabase.")
    sys.exit(0)


if __name__ == "__main__":
    main()
