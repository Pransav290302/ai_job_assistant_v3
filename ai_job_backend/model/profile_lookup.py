"""
Database function to retrieve a user's profile.
Used by the agent as a tool to get profile data for tailored answers.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()


def get_user_profile_from_db(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user profile from database (Supabase: profiles + user_preferences).
    Returns a dict suitable for generate_answer (work_history, skills, education).

    Args:
        user_id: Supabase auth user UUID.

    Returns:
        Profile dict or error message.
    """
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return {
            "error": "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY for profile lookup.",
            "work_history": "",
            "skills": "",
            "education": "",
            "additional_info": "",
        }

    try:
        from supabase import create_client
        client = create_client(url, key)
    except ImportError:
        return {
            "error": "supabase package not installed. pip install supabase",
            "work_history": "",
            "skills": "",
            "education": "",
            "additional_info": "",
        }

    try:
        profile_res = (
            client.table("profiles")
            .select("first_name, last_name, email")
            .eq("id", user_id)
            .execute()
        )
        prefs_res = (
            client.table("user_preferences")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        personal_res = (
            client.table("user_personal_info")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as e:
        return {
            "error": str(e),
            "work_history": "",
            "skills": "",
            "education": "",
            "additional_info": "",
        }

    profile_list = profile_res.data if profile_res.data else []
    prefs_list = prefs_res.data if prefs_res.data else []
    personal_list = personal_res.data if personal_res.data else []
    profile = profile_list[0] if profile_list else {}
    prefs = prefs_list[0] if prefs_list else {}
    personal = personal_list[0] if personal_list else {}

    first = personal.get("first_name") or profile.get("first_name") or ""
    last = personal.get("last_name") or profile.get("last_name") or ""
    email = personal.get("email") or profile.get("email") or ""
    name = f"{first} {last}".strip() or (email.split("@")[0] if email else "")

    roles = prefs.get("roles") or []
    roles_str = ", ".join(str(r) for r in roles) if isinstance(roles, list) else str(roles)
    skills = prefs.get("skills_prefer") or []
    skills_str = ", ".join(str(s) for s in skills) if isinstance(skills, list) else str(skills)
    locations = prefs.get("locations") or []
    loc_str = personal.get("location") or (
        ", ".join(str(l) for l in locations) if isinstance(locations, list) else ""
    )

    work_history = personal.get("work_history_summary") or roles_str or "Not in database"
    education = personal.get("education_summary") or ""
    industries_prefer = prefs.get("industries_prefer") or []
    interests = ", ".join(str(x) for x in industries_prefer) if isinstance(industries_prefer, list) else str(industries_prefer or "")

    return {
        "full_name": name,
        "email": email,
        "current_title": roles_str,
        "skills": skills_str,
        "location": loc_str,
        "work_history": work_history,
        "education": education,
        "additional_info": f"Location: {loc_str}".strip() if loc_str else "",
        "interests": interests,
        "industries_prefer": industries_prefer if isinstance(industries_prefer, list) else [],
    }
