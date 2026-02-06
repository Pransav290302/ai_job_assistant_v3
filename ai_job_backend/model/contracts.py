"""
Data contracts for the AI Job Assistant (Senior Data Scientist todo).
Input/output schemas for resume scoring and tailored answers.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union


# ---- Input: UserProfile (for tailored answers) ----

class WorkHistoryEntry(TypedDict, total=False):
    company: str
    position: str
    duration: str
    responsibilities: List[str]
    achievements: List[str]


class EducationEntry(TypedDict, total=False):
    institution: str
    degree: str
    field: str
    graduation_year: int


class UserProfile(TypedDict, total=False):
    """Canonical profile for tailored answers. API accepts looser dict (strings/lists)."""
    work_history: Union[List[WorkHistoryEntry], str]
    skills: Union[List[str], str]
    education: Union[List[EducationEntry], str]
    certifications: List[str]
    summary: str
    additional_info: str


# ---- Output: ResumeScoreOutput ----

class SuggestionItem(TypedDict):
    category: str   # "skills" | "experience" | "keywords"
    suggestion: str
    priority: str   # "high" | "medium" | "low"


class ResumeScoreOutput(TypedDict, total=False):
    """Canonical output for resume vs JD analysis."""
    score: int                    # 0-100
    match_percentage: float       # 0.0-1.0
    suggestions: List[Union[SuggestionItem, str]]  # structured or legacy string list
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]          # optional, backward compat
    missing_skills: List[str]     # optional, backward compat


# ---- Scraper output (current contract) ----

def scraper_output_schema() -> Dict[str, Any]:
    """
    Current scraper returns plain text.
    Optional future: {"title", "company", "description", "requirements", "url"}.
    """
    return {
        "title": "str (optional)",
        "company": "str (optional)",
        "description": "str (main content)",
        "requirements": "str (optional)",
        "url": "str",
    }
